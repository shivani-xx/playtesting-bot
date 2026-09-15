from agent.heuristic_agent import HeuristicAgent


def test_agent_retreats_when_health_is_low():
    agent = HeuristicAgent()

    state = {
        "health": 1,
        "player_position": (2, 2),
        "enemy_position": (2, 3),
        "goal_position": (4, 4),
        "legal_actions": ["left", "right", "up", "down", "wait"]
    }

    action = agent.choose_action(state)

    assert action == "left"


def test_agent_attacks_adjacent_enemy():
    agent = HeuristicAgent()

    state = {
        "health": 5,
        "player_position": (2, 2),
        "enemy_position": (2, 3),
        "goal_position": (4, 4),
        "legal_actions": ["left", "right", "attack", "wait"]
    }

    action = agent.choose_action(state)

    assert action == "attack"


def test_agent_moves_towards_goal():
    agent = HeuristicAgent()

    state = {
        "health": 5,
        "player_position": (2, 2),
        "enemy_position": (4, 4),
        "goal_position": (2, 4),
        "legal_actions": ["left", "right", "wait"]
    }

    action = agent.choose_action(state)

    assert action == "right"


def test_agent_handles_no_legal_actions():
    agent = HeuristicAgent()

    state = {
        "health": 5,
        "player_position": (2, 2),
        "enemy_position": (4, 4),
        "goal_position": (2, 4),
        "legal_actions": []
    }

    action = agent.choose_action(state)

    assert action is None


def test_agent_returns_only_legal_action():
    agent = HeuristicAgent()

    state = {
        "health": 5,
        "player_position": (2, 2),
        "enemy_position": (4, 4),
        "goal_position": (4, 4),
        "legal_actions": ["wait"]
    }

    action = agent.choose_action(state)

    assert action in state["legal_actions"]