from pokerkit import (
    State,
    Automation,
    Deck,
    KuhnPokerHand,
    Street,
    Opening,
    BettingStructure
)

from actions import ActionType
from poker_algorithms import KuhnPokerCFR

table = KuhnPokerCFR._InfoSetTable()

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

base_state.deal_hole()
base_state.deal_hole()

# table.set(base_state, ActionType.CHECK_CALL, 0, 3)
# table.set(base_state, ActionType.BET_RAISE, 0, 1)
# table.set(base_state, ActionType.FOLD, 0, 57)

base_state.complete_bet_or_raise_to()

add = lambda a, b: a / b
# table.update(base_state, ActionType.FOLD, 0, add, 12)


print(table._root)
print()
strategy = KuhnPokerCFR.evaluate_strategy(table, base_state, 1)
print(strategy)
