from enum import Enum, auto


class ActionType(Enum):
    FOLD = auto()
    CHECK_CALL = auto()
    BET_RAISE = auto()


class Action():
    def __init__(self, type: ActionType, amount: int = 0):
        """Create an action.

        Args:
            type (ActionType): the type of action
            amount (int): the amount to raise (if applicable)
        """

        self._type = type
        self._amount = amount

    def get_type(self):
        """Return the type of this action.

        Returns:
            ActionType: the type of this action
        """
        return self._type

    def get_amount(self):
        """Return the amount raised if this action is a BET_RAISE.

        Returns:
            int: the chip amount raised
        """
        return self._amount
