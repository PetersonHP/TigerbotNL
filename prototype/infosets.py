"""Methods and classes related to information sets"""
import json
import pickle
from typing import Any

from pokerkit import State

from actions import ActionType

class InfoSet:
    def __init__(self, state: State, player_index: int):
        """Create an information set object for a state from the perspective of a player"""
        opponent_index = 1 if player_index == 0 else 0

        # set fields based on available knowledge
        self.hole_cards = tuple(state.hole_cards[player_index])     #3
        self.am_opening= state.opener_index == player_index     #2
        self.my_bet = state.bets[player_index]  #2
        self.opponent_bet = state.bets[opponent_index]  #2
        self.pot_amount = state.pot_amounts


class InfoSetMap:
    """Maps information sets to dict[ActionType, float]
    
    This class is useful for efficiently storing and retrieving regrets and 
    strategies as associated with information sets.
    """
    def __init__(self, filename: str | None = None):
        """Create an empty information set map or populate a new one from a file"""
        if filename is not None:
            with open(filename, 'rb') as file:
                self._root = pickle.load(file)
        else:
            self._root = {}

    def set_action(self, key: InfoSet, act: ActionType, val: float) -> None:
        """Set the float value associated with an action in an information set"""


    def get(self, key: InfoSet) -> dict[ActionType, float]:
        """Get the dict[ActionType, float] associated with an information set"""
        pass

    def save_to_file(self, filename: str) -> None:
        """Save this information set map to a file for future use"""
        with open(filename, 'wb') as file:
            pickle.dump(self._root, file)

    def _convert_keys_to_str(self, obj: dict | list | Any):
        """Private, recursive helper method to convert all keys to printable strings"""
        if isinstance(obj, dict):
            return {str(k): self._convert_keys_to_str(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self._convert_keys_to_str(item) for item in obj]
        return obj

    def to_string(self) -> str:
        """Create a JSON string based on this data structure"""
        str_keys = self._convert_keys_to_str(self._root)
        result = json.dumps(str_keys)
        return result
