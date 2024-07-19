"""Interface to represent HUNL players"""
from pokerkit import State

from actions import Action
from infosets import InfoSet


class Player:
    """Represents a HUNL player. Send it InfoSets, receive Actions"""

    def __init__(self, game_state: State) -> None:
        """Initialize a player"""

    def get_action(self, info: InfoSet) -> Action:
        """Return an action to play given an InfoSet

        Args:
            info (InfoSet): all knowledge of the current game available 
                            to the player

        Returns:
            Action: the action to play
        """

    def handle_round_over(self, game_state: State, my_index: int) -> None:
        """Things to do at the end of a round"""
