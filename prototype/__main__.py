import copy
import sys

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
from random_player import RandomPlayer


def main():
    # Kuhn poker game state
    base_state = State(
        # automations
        (
            Automation.ANTE_POSTING,
            Automation.BET_COLLECTION,
            Automation.BLIND_OR_STRADDLE_POSTING,
            Automation.CARD_BURNING,
            Automation.HOLE_DEALING,
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
    player_list = [RandomPlayer(), RandomPlayer()]

    # play rounds
    for round_num in range(rounds_to_play):
        state = copy.deepcopy(base_state)

        while (state.status):
            current_action = player_list[state.actor_index].get_action(state)
            match current_action.get_type():
                case ActionType.FOLD:
                    state.fold()
                case ActionType.CHECK_CALL:
                    state.check_or_call()
                case ActionType.BET_RAISE:
                    state.complete_bet_or_raise_to(current_action.get_amount())
                case _:
                    raise ValueError("Unable to process player action.")

        # TODO get round winnings, log, record

    # print stats
    # print("Game Statistics:")

    # print("Player 1:")
    # print(f"  Mean Payoff: {stats[0].payoff_mean}")
    # print(f"  Payof Standard Deviation: {stats[0].payoff_stdev}")
    # print(f"  Net Winnings: {stats[0].payoff_sum}")

    # print("Player 2:")
    # print(f"  Mean Payoff: {stats[1].payoff_mean}")
    # print(f"  Payof Standard Deviation: {stats[1].payoff_stdev}")
    # print(f"  Net Winnings: {stats[1].payoff_sum}")


if __name__ == "__main__":
    main()
