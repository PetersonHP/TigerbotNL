from random import choices

from pokerkit import State
from pokerkit.utilities import Rank

from player_interface import Player
from actions import Action, ActionType


class NaivePlayer(Player):
    def __init__(self, game_state: State) -> None:
        return

    def get_action(self, game_state: State) -> Action:
        strategy = {
            ActionType.FOLD: 0.0,
            ActionType.CHECK_CALL: 0.0,
            ActionType.BET_RAISE: 0.0,
        }
        my_index = game_state.actor_index

        # assess action choices
        my_cards = list(game_state.hole_cards[my_index])
        if my_cards[0].rank == Rank.KING:
            if game_state.can_complete_bet_or_raise_to(
                    game_state.min_completion_betting_or_raising_to_amount):
                strategy[ActionType.BET_RAISE] = 1.0
            elif game_state.can_check_or_call():
                strategy[ActionType.CHECK_CALL] = 1.0
            else:
                strategy[ActionType.FOLD] = 1.0
        elif my_cards[0].rank == Rank.QUEEN:
            if game_state.can_check_or_call():
                strategy[ActionType.CHECK_CALL] = 1.0
            else:
                strategy[ActionType.FOLD] = 1.0
        elif my_cards[0].rank == Rank.JACK:
            if game_state.can_fold():
                strategy[ActionType.FOLD] = 1.0
            else:
                strategy[ActionType.CHECK_CALL] = 1.0

        # build and return an action by sampling from strategy
        chosen_type = choices(list(strategy.keys()), weights=strategy.values(), k=1)[0]
        if chosen_type == ActionType.BET_RAISE:
            result = Action(chosen_type, game_state.min_completion_betting_or_raising_to_amount)
        else:
            result = Action(chosen_type)

        return result

    def handle_round_over(self, game_state: State, my_index: int) -> None:
        return
