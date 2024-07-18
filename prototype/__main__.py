import copy
import logging
import random
import sys

import numpy as np
from pokerkit import (
    Automation,
    BettingStructure,
    Deck,
    KuhnPokerHand,
    Opening,
    State,
    Street,
)

from actions import Action, ActionType
from random_player import RandomPlayer
from cfr_player import CFRPlayer
from cli_player import CLIPlayer
from naive_player import NaivePlayer

logging.basicConfig(level=logging.DEBUG)


def main():
    if len(sys.argv) != 2:
        print("Rounds to play must be specified as the first argument.")
        sys.exit()

    # Kuhn poker game state
    base_state = State(
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
        (KuhnPokerHand,),  # hand types (high/low-split will have two types)
        # streets
        (
            Street(
                False,  # card burning
                (False,),  # hole card dealing statuses (False for face-down)
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
        (2,) * 2,  # starting stacks
        2,  # number of players
    )

    rounds_to_play = int(sys.argv[1])
    # specify player types
    player_list = [
        RandomPlayer(base_state),
        CFRPlayer(base_state, "r1mil-new.reg")
    ]

    # play rounds
    payoffs = [[], []]
    for round_num in range(rounds_to_play):
        state = copy.deepcopy(base_state)

        # deal
        state.deck_cards = random.sample(
            base_state.deck_cards, k=len(base_state.deck_cards))
        for i in range(len(player_list)):
            state.deal_hole()

        # determine player order
        if round_num % 2 == 0:
            player_order = [0, 1]
        else:
            player_order = [1, 0]

        # play hand
        while state.status:
            current_action = \
                player_list[player_order[state.actor_index]].get_action(state)

            if isinstance(current_action, Action):
                current_action = current_action.get_type()
            elif isinstance(current_action, ActionType):
                pass
            else:
                raise ValueError("Invalid action returned by player.")

            match current_action:
                case ActionType.FOLD:
                    logging.debug("Player %d folds.",
                                  (player_order[state.actor_index] + 1))
                    state.fold()
                case ActionType.CHECK_CALL:
                    logging.debug("Player %d checks/calls",
                                  (player_order[state.actor_index] + 1))
                    state.check_or_call()
                case ActionType.BET_RAISE:
                    logging.debug("Player %d bets/raises.",
                                  (player_order[state.actor_index] + 1))
                    state.complete_bet_or_raise_to(state.min_completion_betting_or_raising_to_amount)
                case _:
                    raise ValueError("Unable to process player action.")

        # finish hand
        # DEBUG
        print(f"({state.stacks[0] - 2}, {state.stacks[1] - 2})")

        # TODO fix
        index = 0
        for player in player_list:
            player.handle_round_over(state, index)
            index += 1
        payoffs[0].append(state.payoffs[player_order[0]])
        payoffs[1].append(state.payoffs[player_order[1]])
        print(f"Winnings this round: {payoffs[0][-1]}")

    # print stats
    print("Game Statistics:")

    print("Player 1:")
    print(f"  Mean Payoff: {np.mean(payoffs[0])}")
    print(f"  Payoff Standard Deviation: {np.std(payoffs[0])}")
    print(f"  Net Winnings: {np.sum(payoffs[0])}")

    print("Player 2:")
    print(f"  Mean Payoff: {np.mean(payoffs[1])}")
    print(f"  Payoff Standard Deviation: {np.std(payoffs[1])}")
    print(f"  Net Winnings: {np.sum(payoffs[1])}")


if __name__ == "__main__":
    main()
