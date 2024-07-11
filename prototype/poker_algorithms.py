import copy
import random
from typing import Callable

from pokerkit import (
    Automation,
    BettingStructure,
    Deck,
    KuhnPokerHand,
    Opening,
    State,
    Street,
)

from actions import ActionType


# list of child nodes (take action -> other stuff happens -> new InfoSet)
# terminal? -> rrrexpected reward?
class KuhnPokerCFR:

    # -------------------------------------------------------------------------
    class _InfoSetTable:
        """Associates info sets with probability distributions over actions"""

        def __init__(self):
            self._root = {}
            pass

        def get(self,
                state: State,
                index: int) -> dict[ActionType, float] | None:

            if state.actor_index != index:
                raise ValueError("The player to act must be the same as the "
                                 + "player to whom this regret table belongs.")

            current = self._root
            # index
            next_node = current.get(index)
            if next_node is not None:
                current = next_node
            else:
                return None
            # hole_cards[index]
            cards = tuple(state.hole_cards[index])
            next_node = current.get(cards)
            if next_node is not None:
                current = next_node
            else:
                return None
            # antes
            next_node = current.get(state.antes)
            if next_node is not None:
                current = next_node
            else:
                return None
            # bets
            bets = tuple(state.bets)
            next_node = current.get(bets)
            if next_node is not None:
                current = next_node
            else:
                return None
            # action type
            return current

        def set(self,
                state: State,
                action: ActionType,
                index: int,
                new_val: float) -> None:

            if state.actor_index != index:
                raise ValueError("The player to act must be the same as the "
                                 + "player to whom this regret table belongs.")

            current = self._root
            # index
            next_node = current.get(index)
            if next_node is not None:
                current = next_node
            else:
                current[index] = {
                    tuple(state.hole_cards[index]): {
                        state.antes: {
                            tuple(state.bets): {
                                action: new_val
                            }
                        }
                    }
                }
                return
            # hole cards
            cards = tuple(state.hole_cards[index])
            next_node = current.get(cards)
            if next_node is not None:
                current = next_node
            else:
                current[cards] = {
                    state.antes: {
                        tuple(state.bets): {
                            action: new_val
                        }
                    }
                }
                return
            # antes
            next_node = current.get(state.antes)
            if next_node is not None:
                current = next_node
            else:
                current[state.antes] = {
                    tuple(state.bets): {
                        action: new_val
                    }
                }
                return
            # bets
            bets = tuple(state.bets)
            next_node = current.get(bets)
            if next_node is not None:
                current = next_node
            else:
                current[bets] = {
                    action: new_val
                }
                return
            # action
            current[action] = new_val

        def update(self,
                   state: State,
                   action: ActionType,
                   index: int,
                   expression: Callable[[float, float], float],
                   k: float) -> None:

            action_distribution = self.get(state, index)
            action_distribution[action] = \
                expression(action_distribution[action], k)
    # -------------------------------------------------------------------------

    def __init__(self) -> None:
        self._base_state = State(
            # automations
            (
                Automation.ANTE_POSTING,
                Automation.BET_COLLECTION,
                Automation.BLIND_OR_STRADDLE_POSTING,
                Automation.CARD_BURNING,
                Automation.BOARD_DEALING,
                Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
                Automation.HAND_KILLING,
                Automation.CHIPS_PUSHING,
                Automation.CHIPS_PULLING,
            ),
            Deck.KUHN_POKER,  # deck
            (KuhnPokerHand,),  # hand types
            # streets
            (
                Street(
                    False,  # card burning
                    (False,),  # hole card dealing statuses
                    0,  # board dealing count
                    False,  # standing pat or discarding
                    Opening.POSITION,  # who opens the betting?
                    1,  # min bet
                    None,  # maximum number of completions/bettings/raisings
                ),
            ),
            BettingStructure.FIXED_LIMIT,  # betting structure
            True,  # ``False`` for big blind ante, otherwise ``True``
            (1,) * 2,  # ante
            (0,) * 2,  # blind or straddles
            0,  # bring-in
            (0,) * 0,  # starting stacks
            2,  # number of players
        )

    def train(self, epochs: int) -> None:
        regrets = [self._InfoSetTable(), self._InfoSetTable()]

        for current_epoch in range(epochs):
            state = copy.deepcopy(self._base_state)

            # shuffle deck
            state.deck_cards = random.sample(
                self._base_state.deck_cards, k=len(self._base_state.deck_cards))
            for i in range(len(regrets)):
                state.deal_hole()

            # determine player order
            if current_epoch % 2 == 0:
                player_order = [0, 1]
            else:
                player_order = [1, 0]

            # play hand
            while (state.status):
                player_to_update = player_order[state.actor_index]
                walk_trees(state, player_to_update, 1.0)
                # TODO working here

                current_action = None   # TODO get player action

                match current_action.get_type():
                    case ActionType.FOLD:
                        state.fold()
                    case ActionType.CHECK_CALL:
                        state.check_or_call()
                    case ActionType.BET_RAISE:
                        state.complete_bet_or_raise_to(
                            current_action.get_amount())
                    case _:
                        raise ValueError("Unable to process player action.")

    def load_regrets_from_file():
        pass

    def save_regrets_to_file():
        pass

    def available_actions(state: State) -> list[ActionType]:
        result = []

        if state.can_fold():
            result.append(ActionType.FOLD)
        if state.can_check_or_call():
            result.append(ActionType.CHECK_CALL)
        if state.can_complete_bet_or_raise_to():
            result.append(ActionType.BET_RAISE)

        return result

    def evaluate_strategy(table: _InfoSetTable,
                          state: State,
                          index: int) -> dict[ActionType, float]:
        """Returns a probability distribution over all possible actions
        given an information set"""
        regret_set = table.get(state, index)

        result = {}
        action_list = KuhnPokerCFR.available_actions(state)
        if regret_set is None:
            for action in action_list:
                result[action] = 1 / len(action_list)
        else:
            regret_sum = sum(regret_set.values())
            if regret_sum == 0:
                for action in action_list:
                    result[action] = 1 / len(action_list)
            else:
                for action in action_list:
                    current_regret = (table.get(state, index)).get(action)
                    result[action] = \
                        current_regret / regret_sum if current_regret is not None else 0

        return result
