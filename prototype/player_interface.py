from pokerkit import State

from actions import Action


class Player:
    def __init__(self):
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
