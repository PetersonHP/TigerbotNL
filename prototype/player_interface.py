from pokerkit import State

from actions import Action, ActionType


class Player:
    def __init__(self, game_state: State) -> None:
        """Perform actions to initialize a player."""
        pass

    def get_action(self, game_state: State) -> Action:
        """Return an action to play given a game state.

        Args:
            game_state (State): the current state of the poker game

        Returns:
            Action: the action to play
        """
        pass

    def handle_round_over(self, game_state: State, my_index: int) -> None:
        """Actions to perform at the end of a round"""
        pass