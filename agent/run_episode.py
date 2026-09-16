import argparse
import json
import sqlite3
from pathlib import Path

from heuristic_agent import HeuristicAgent
from game.dungeon import DungeonGame


DB_PATH = Path(__file__).parent.parent / "logs" / "runs.db"


def create_database():
    """Create the SQLite database and required tables."""

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS episodes (
            episode_id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_type TEXT NOT NULL,
            seed_bugs INTEGER NOT NULL,
            outcome TEXT,
            total_steps INTEGER NOT NULL,
            total_reward REAL NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS steps (
            step_id INTEGER PRIMARY KEY AUTOINCREMENT,
            episode_id INTEGER NOT NULL,
            step_number INTEGER NOT NULL,
            state TEXT NOT NULL,
            action TEXT NOT NULL,
            reward REAL NOT NULL,
            done INTEGER NOT NULL,
            info TEXT,
            FOREIGN KEY (episode_id) REFERENCES episodes(episode_id)
        )
    """)

    conn.commit()
    return conn


def run_episode(agent, conn, episode_number, max_steps, seed_bugs):
    """Run one game episode and store its execution data."""

    game = DungeonGame(seed_bugs=seed_bugs)
    state = game.reset()

    total_reward = 0
    outcome = "timeout"

    step_records = []

    for step_number in range(1, max_steps + 1):

        if state["done"]:
            break

        action = agent.choose_action(state)

        if action is None:
            outcome = "no_action"
            break

        next_state, reward, done, info = game.step(action)

        total_reward += reward

        step_records.append({
            "step_number": step_number,
            "state": state,
            "action": action,
            "reward": reward,
            "done": done,
            "info": info
        })

        state = next_state

        if done:
            outcome = info.get("outcome", "finished")
            break

    total_steps = len(step_records)

    cursor = conn.execute(
        """
        INSERT INTO episodes
        (agent_type, seed_bugs, outcome, total_steps, total_reward)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            "heuristic",
            int(seed_bugs),
            outcome,
            total_steps,
            total_reward
        )
    )

    episode_id = cursor.lastrowid

    for record in step_records:
        conn.execute(
            """
            INSERT INTO steps
            (episode_id, step_number, state, action, reward, done, info)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                episode_id,
                record["step_number"],
                json.dumps(record["state"]),
                record["action"],
                record["reward"],
                int(record["done"]),
                json.dumps(record["info"])
            )
        )

    conn.commit()

    print(
        f"Episode {episode_number}: "
        f"outcome={outcome}, "
        f"steps={total_steps}, "
        f"reward={total_reward}"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Run automated dungeon playtesting."
    )

    parser.add_argument(
        "--agent",
        choices=["heuristic"],
        default="heuristic"
    )

    parser.add_argument(
        "--episodes",
        type=int,
        default=1
    )

    parser.add_argument(
        "--max-steps",
        type=int,
        default=50
    )

    parser.add_argument(
        "--seed-bugs",
        action="store_true"
    )

    args = parser.parse_args()

    conn = create_database()

    try:
        if args.agent == "heuristic":
            agent = HeuristicAgent()

        print("Starting automated playtesting...")
        print(f"Agent: {args.agent}")
        print(f"Episodes: {args.episodes}")
        print(f"Maximum steps: {args.max_steps}")
        print(f"Bug seeding: {args.seed_bugs}")
        print()

        for episode_number in range(1, args.episodes + 1):
            run_episode(
                agent=agent,
                conn=conn,
                episode_number=episode_number,
                max_steps=args.max_steps,
                seed_bugs=args.seed_bugs
            )

        print()
        print(f"Results stored in: {DB_PATH}")

    finally:
        conn.close()


if __name__ == "__main__":
    main()