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
# terminal? -> expected reward?
class KuhnPokerCFR:

    # -------------------------------------------------------------------------
    class _InfoSetTable:
        """Associates info sets with probability distributions over actions"""

        def __init__(self):
            self._root = {}

        def get(self,
                state: State,
                index: int) -> dict[ActionType, float] | None:

            # if state.actor_index != index:
            #     raise ValueError("The player to act must be the same as the "
            #                      + "player to whom this regret table belongs.")

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

            # if state.actor_index != index:
            #     raise ValueError("The player to act must be the same as the "
            #                      + "player to whom this regret table belongs.")

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

    _STARTING_STACK_SIZE = 2

    def __init__(self) -> None:
        self._regrets = None
        self._strategy = None

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
            (KuhnPokerCFR._STARTING_STACK_SIZE,) * 2,  # starting stacks
            2,  # number of players
        )

    def train(self, epochs: int, epsilon: float, tau: float, beta: float) -> None:
        """Train the model using Monte Carlo Counterfactual Regret Minimization
        
        Algorithm based on Gibson, et al. (2012)
        """
        regrets = KuhnPokerCFR._InfoSetTable()
        cumulative_profile = KuhnPokerCFR._InfoSetTable()

        for current_epoch in range(epochs):
            state = copy.deepcopy(self._base_state)

            # shuffle deck and deal hold cards
            state.deck_cards = random.sample(
                self._base_state.deck_cards, k=len(self._base_state.deck_cards))
            state.deal_hole()
            state.deal_hole()

            # determine player order
            if current_epoch % 2 == 0:
                player_order = [0, 1]
            else:
                player_order = [1, 0]

            # stochastically walk the tree and update regrets and cumulative profile
            KuhnPokerCFR.walk_tree(state,
                      player_order[state.actor_index],
                      1.0,
                      epsilon,
                      tau,
                      beta,
                      regrets,
                      cumulative_profile)
            
        self._regrets = regrets
        self._strategy = cumulative_profile

        # DEBUG
        print(regrets._root)

    @staticmethod
    def walk_tree(base_state: State,
                  player_index: int,
                  sample_prob: float,
                  epsilon: float,
                  tau: float,
                  beta: float,
                  regrets: _InfoSetTable,
                  cumulative_profile: _InfoSetTable) -> float:
        """Stochastically walk the tree and update regrets and cumulative profile"""

        # handle terminal state
        if not base_state.status:
            return (base_state.stacks[player_index] -
                    KuhnPokerCFR._STARTING_STACK_SIZE) / sample_prob

        current_strategy = KuhnPokerCFR.regret_matching(regrets, base_state, player_index)

        # handle opponent state
        if base_state.actor_index != player_index:
            # update cumulative profile (after player's turn)
            for action, action_probability in current_strategy.items():
                old_dist = cumulative_profile.get(
                    base_state, player_index)
                if old_dist is None:
                    new_prob = 0 + (action_probability / sample_prob)
                else:
                    new_prob = old_dist[action] + (action_probability / sample_prob)
                cumulative_profile.set(base_state, action, player_index, new_prob)
            # play opponent action
            new_action = KuhnPokerCFR.sample_action(current_strategy)
            new_state = copy.deepcopy(base_state)
            KuhnPokerCFR.play_action(new_state, new_action)
            return KuhnPokerCFR.walk_tree(new_state,
                                          player_index,
                                          sample_prob,
                                          epsilon,
                                          tau,
                                          beta,
                                          regrets,
                                          cumulative_profile)

        # handle player state (update regrets)
        # TODO handle when cumulative_strategy is None
        cumulative_strategy = cumulative_profile.get(base_state, player_index)
        # if informantion set unseen, set cumulative profile to 0
        # TODO here
        if cumulative_strategy is None:
            for action in KuhnPokerCFR.available_actions(base_state):
                cumulative_profile.set(base_state, action, player_index, 0)
            cumulative_strategy = cumulative_profile.get(base_state, player_index)

        cumulative_profile_sum = sum(cumulative_strategy.values())
        action_values = {}
        for action, action_probability in current_strategy.items():
            probability_to_walk_path = max(
                epsilon,
                (beta + cumulative_strategy[action])
                / (beta + cumulative_profile_sum)
            )
            action_values[action] = 0
            if random.random() < probability_to_walk_path:
                new_state = copy.deepcopy(base_state)
                KuhnPokerCFR.play_action(new_state, action)
                action_values[action] = KuhnPokerCFR.walk_tree(new_state,
                                        player_index,
                                        min(1, sample_prob),
                                        epsilon,
                                        tau,
                                        beta,
                                        regrets,
                                        cumulative_profile)
        for action, action_probability in current_strategy.items():
            new_regret = regrets.get(base_state, player_index)[action]
            regrets.set(base_state, action, player_index, new_regret)
        new_state_value = 0
        for action, value in action_values.items():
            new_state_value += current_strategy[action] * value
        return new_state_value

    def load_regrets_from_file(self):
        """Load a regret table from a file"""

    def save_regrets_to_file(self):
        """Save a regret table from a file"""

    @staticmethod
    def play_action(state: State, action: ActionType) -> None:
        """Play the given action from the state"""
        match action:
            case ActionType.FOLD:
                state.fold()
            case ActionType.CHECK_CALL:
                state.check_or_call()
            case ActionType.BET_RAISE:
                state.complete_bet_or_raise_to(
                    state.min_completion_betting_or_raising_to_amount)
            case _:
                raise ValueError("Unable to process player action.")

    @staticmethod
    def sample_action(strategy: dict[ActionType, float]) -> ActionType:
        """Sample an action from a strategy"""
        actions = list(strategy.keys())
        probabilities = strategy.values()
        return random.choices(actions, weights=probabilities, k=1)[0]

    @staticmethod
    def available_actions(state: State) -> list[ActionType]:
        """Returns a list of available actions at a state"""
        result = []

        if state.can_fold():
            result.append(ActionType.FOLD)
        if state.can_check_or_call():
            result.append(ActionType.CHECK_CALL)
        if state.can_complete_bet_or_raise_to():
            result.append(ActionType.BET_RAISE)

        return result

    @staticmethod
    def regret_matching(table: _InfoSetTable,
                          state: State,
                          index: int) -> dict[ActionType, float]:
        """Returns a probability distribution over all possible actions
        given an information set and a regret table"""
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
