class DungeonGame:
    """
    Simple turn-based grid dungeon game for automated playtesting.

    The game exposes a fixed state/action interface:
        reset() -> state
        step(action) -> (state, reward, done, info)
    """

    ACTIONS = ["up", "down", "left", "right", "attack", "wait"]

    def __init__(self, seed_bugs=False):
        self.seed_bugs = seed_bugs
        self.reset()

    def reset(self):
        self.player_pos = [0, 0]
        self.enemy_pos = [2, 2]

        self.health = 3
        self.enemy_health = 2

        self.goal = [4, 4]
        self.done = False
        self.turn = 0

        self.max_health = 3

        return self.get_state()

    def get_state(self):
        return {
            "player_position": tuple(self.player_pos),
            "enemy_position": tuple(self.enemy_pos),
            "goal_position": tuple(self.goal),
            "health": self.health,
            "enemy_health": self.enemy_health,
            "turn": self.turn,
            "done": self.done,
            "legal_actions": self.get_legal_actions(),
        }

    def get_legal_actions(self):
        return self.ACTIONS.copy()

    def step(self, action):
        if self.done:
            return self.get_state(), 0, True, {"message": "Game already finished"}

        if action not in self.ACTIONS:
            raise ValueError(f"Invalid action: {action}")

        self.turn += 1
        reward = 0
        info = {}

        if action in ["up", "down", "left", "right"]:
            self._move(action)

        elif action == "attack":
            if self._adjacent_to_enemy():
                self.enemy_health -= 1
                reward = 1

                if self.enemy_health <= 0:
                    info["enemy_defeated"] = True

        elif action == "wait":
            reward = 0

        # Enemy damages the player when adjacent.
        if self._adjacent_to_enemy() and self.enemy_health > 0:
            damage = 1

            # Seeded damage-spike bug.
            if self.seed_bugs:
                damage = 2

            self.health -= damage
            info["damage_taken"] = damage

        # Seeded wall-exploit bug.
        if self.seed_bugs:
            if self.player_pos[0] < 0 or self.player_pos[0] > 4:
                info["wall_exploit"] = True

            if self.player_pos[1] < 0 or self.player_pos[1] > 4:
                info["wall_exploit"] = True

        # Lose condition.
        if self.health <= 0:
            self.done = True
            reward = -1
            info["outcome"] = "loss"

        # Win condition.
        elif self.player_pos == self.goal:
            self.done = True
            reward = 10
            info["outcome"] = "win"

        return self.get_state(), reward, self.done, info

    def _move(self, action):
        row, col = self.player_pos

        if action == "up":
            row -= 1
        elif action == "down":
            row += 1
        elif action == "left":
            col -= 1
        elif action == "right":
            col += 1

        # Normal collision handling.
        if not self.seed_bugs:
            row = max(0, min(4, row))
            col = max(0, min(4, col))

        self.player_pos = [row, col]

    def _adjacent_to_enemy(self):
        distance = (
            abs(self.player_pos[0] - self.enemy_pos[0])
            + abs(self.player_pos[1] - self.enemy_pos[1])
        )

        return distance <= 1