from random import choice

from pokerkit import State

from player_interface import Player
from actions import Action, ActionType


class RandomPlayer(Player):
    def __init__(self):
        return

    def get_action(self, game_state: State) -> Action:
        available_actions = []

        # assess action choices
        if game_state.can_fold:
            available_actions.append(ActionType.FOLD)
        if game_state.can_check_or_call:
            available_actions.append(ActionType.CHECK_CALL)
        if game_state.can_complete_bet_or_raise_to(
                game_state.min_completion_betting_or_raising_to_amount):
            available_actions.append(ActionType.BET_RAISE)

        if len(available_actions) == 0:
            raise ValueError("No valid actions.")

        # build and return an action randomly
        chosen_type = choice(available_actions)
        if (chosen_type == ActionType.BET_RAISE):
            result = Action(
                chosen_type,
                game_state.min_completion_betting_or_raising_to_amount)
        else:
            result = Action(chosen_type)

        return result
