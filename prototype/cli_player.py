from pokerkit import State

from actions import Action, ActionType


class CLIPlayer:
    def __init__(self, game_state: State) -> None:
        """Perform actions to initialize a player."""
        print("""
              ***************************
                 Begin Kuhn Poker Game
              ***************************
              """)

        self._starting_stack = game_state.stacks[0]
        self._current_stack = self._starting_stack
        return

    def get_action(self, game_state: State) -> Action:
        """Return an action to play given a game state.

        Args:
            game_state (State): the current state of the poker game

        Returns:
            Action: the action to play
        """
        my_index = game_state.actor_index
        self._current_stack = game_state.stacks[my_index]

        print("**************************************************************************************")
        print(f"Button: {'big blind' if my_index == 0 else 'none'}")
        print(f"Stack: {self._current_stack}")
        print(f"Hole Cards: {list(game_state.get_censored_hole_cards(my_index))}")
        print("**************************************************************************************")
        while True:
            action_char = input(
                "Enter a character to choose an action ('f' - fold, 'c' - call/check, 'r' - bet/raise)\n")

            if action_char == "f":
                try:
                    game_state.verify_folding()
                except ValueError:
                    print('\aCannot fold now. Choose a different action.\n')
                    continue
                else:
                    return Action(ActionType.FOLD)
            if action_char == "c":
                try:
                    game_state.verify_checking_or_calling()
                except ValueError:
                    print('\aCannot check/call now. Choose a different action.\n')
                    continue
                else:
                    return Action(ActionType.CHECK_CALL)
            if action_char == "r":
                try:
                    game_state.verify_completion_betting_or_raising_to()
                except ValueError:
                    print('\aCannot bet/raise now. Choose a different action.\n')
                    continue
                else:
                    return Action(ActionType.BET_RAISE,
                                  game_state.min_completion_betting_or_raising_to_amount)
            print("Valid options include 'f', 'c', and 'r'")

    def handle_round_over(self, game_state: State, my_index: int) -> None:
        print("**************************************************************************************")
        print(
            f"Winnings this round: {game_state.stacks[my_index] - self._current_stack}")
        self._current_stack = game_state.stacks[my_index]
        print(
            f"Winnings Overall: {self._current_stack - self._starting_stack}\n")
        print(f"Current Stack: {self._current_stack}")

        return
