import pytest

from game.dungeon import DungeonGame


def test_game_initializes_correctly():
    game = DungeonGame()

    state = game.reset()

    assert state["player_position"] == (0, 0)
    assert state["health"] == 3
    assert state["enemy_health"] == 2
    assert state["done"] is False


def test_legal_actions_are_available():
    game = DungeonGame()

    state = game.reset()

    assert "up" in state["legal_actions"]
    assert "down" in state["legal_actions"]
    assert "left" in state["legal_actions"]
    assert "right" in state["legal_actions"]
    assert "attack" in state["legal_actions"]
    assert "wait" in state["legal_actions"]


def test_player_can_move():
    game = DungeonGame()

    game.reset()
    state, reward, done, info = game.step("right")

    assert state["player_position"] == (0, 1)
    assert done is False


def test_invalid_action_is_rejected():
    game = DungeonGame()

    game.reset()

    with pytest.raises(ValueError):
        game.step("fly")


def test_player_can_reach_goal():
    game = DungeonGame()

    game.reset()

    # Move from (0,0) to (4,4)
    for _ in range(4):
        game.step("right")

    for _ in range(4):
        state, reward, done, info = game.step("down")

    assert state["player_position"] == (4, 4)
    assert done is True
    assert reward == 10
    assert info["outcome"] == "win"


def test_bug_seeded_damage_spike():
    normal_game = DungeonGame(seed_bugs=False)
    buggy_game = DungeonGame(seed_bugs=True)

    normal_game.reset()
    buggy_game.reset()

    # Move next to the enemy at (2, 2)
    normal_game.step("right")
    normal_game.step("right")

    buggy_game.step("right")
    buggy_game.step("right")

    # Moving down to (2,1) places the player next to the enemy.
    normal_state, _, _, normal_info = normal_game.step("down")
    buggy_state, _, _, buggy_info = buggy_game.step("down")

    # Normal game deals 1 damage; seeded bug deals 2 damage.
    assert normal_info["damage_taken"] == 1
    assert buggy_info["damage_taken"] == 2

    assert normal_state["health"] == 2
    assert buggy_state["health"] == 1