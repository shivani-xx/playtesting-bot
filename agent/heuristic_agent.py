class HeuristicAgent:
    """
    Rule-based agent for the dungeon game.

    Decision priority:
    1. Retreat if health is critically low.
    2. Attack if the enemy is adjacent.
    3. Move towards the goal.
    4. Wait as a safe fallback.
    """

    def choose_action(self, state):
        legal_actions = state.get("legal_actions")

        # No legal actions available.
        if legal_actions is None or len(legal_actions) == 0:
            return None

        health = state.get("health", 0)
        player = state.get("player_position")
        enemy = state.get("enemy_position")
        goal = state.get("goal_position")

        # Rule 1: Retreat when health is critically low.
        if health <= 1:
            action = self._retreat(player, enemy, legal_actions)

            if action is not None:
                return action

        # Rule 2: Attack when next to the enemy.
        if player is not None and enemy is not None:
            distance = (
                abs(player[0] - enemy[0])
                + abs(player[1] - enemy[1])
            )

            if distance <= 1 and "attack" in legal_actions:
                return "attack"

        # Rule 3: Move towards the goal.
        if player is not None and goal is not None:
            action = self._move_towards_goal(
                player,
                goal,
                legal_actions
            )

            if action is not None:
                return action

        # Rule 4: Safe fallback.
        if "wait" in legal_actions:
            return "wait"

        # Final fallback: always return a legal action.
        return legal_actions[0]

    def _retreat(self, player, enemy, legal_actions):
        """
        Move away from the enemy when health is low.
        """

        if player is None or enemy is None:
            return None

        row, col = player
        enemy_row, enemy_col = enemy

        if enemy_row > row and "up" in legal_actions:
            return "up"

        if enemy_row < row and "down" in legal_actions:
            return "down"

        if enemy_col > col and "left" in legal_actions:
            return "left"

        if enemy_col < col and "right" in legal_actions:
            return "right"

        return None

    def _move_towards_goal(self, player, goal, legal_actions):
        """
        Select a legal movement that reduces the distance to the goal.
        """

        row, col = player
        goal_row, goal_col = goal

        if row < goal_row and "down" in legal_actions:
            return "down"

        if row > goal_row and "up" in legal_actions:
            return "up"

        if col < goal_col and "right" in legal_actions:
            return "right"

        if col > goal_col and "left" in legal_actions:
            return "left"

        return None