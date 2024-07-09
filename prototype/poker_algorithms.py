from typing import Any, Callable

from pokerkit import State

from actions import ActionType


# list of child nodes (take action -> other stuff happens -> new InfoSet)
# terminal? -> rrrexpected reward?
class KuhnPokerCFR:
    def __init__(self, iterations: int) -> None:
        self._strategies = []
        self.iterations = iterations
        pass

    def train():

        pass

    def get_actions():
        """Returns a probability distribution over all possible actions
        given an information set"""
        pass

    def load_regrets_from_file():
        pass

    def save_regrets_to_file():
        pass

    class _RegretTable:
        """Associates info sets with probability distributions over actions"""

        def __init__(self):
            self._root = {}
            pass

        def get(self,
                        state: State,
                        index: int) -> dict[ActionType, float]:

            if state.actor_index != index:
                raise ValueError("The player to act must be the same as the "
                                 + "player to whom this regret table belongs.")

            current = self._root

            # hole_cards[index]

            # antes

            # bets

            # checking or calling amount?

            # completion_betting_or_raising_amount?

        def set(self, state: State, action: ActionType, index: int) -> None:
            if state.actor_index != index:
                raise ValueError("The player to act must be the same as the "
                                 + "player to whom this regret table belongs.")
            
            current = self._root
            



        def update(self,
                          state: State,
                          action: ActionType,
                          expression: Callable[[float, float], float]) -> None:
            pass
