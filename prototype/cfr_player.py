from poker_algorithms import KuhnPokerCFR
from pokerkit import State

from actions import Action

class CFRPlayer:

    def __init__(self, game_state: State, regrets_file: None | str=None) -> None:
        """Perform actions to initialize a player."""
        self._strategy = KuhnPokerCFR()
        if regrets_file is None:
            self._strategy.train(10000, 0.05, 1E3, 1E2)
        else:
            self._strategy.load_regrets_from_file(regrets_file)

    def get_action(self, game_state: State) -> Action:
        """Return an action to play given a game state.

        Args:
            game_state (State): the current state of the poker game

        Returns:
            Action: the action to play
        """
        return self._strategy.play(game_state)

    def handle_round_over(self, game_state: State, my_index: int) -> None:
        """Actions to perform at the end of a round"""