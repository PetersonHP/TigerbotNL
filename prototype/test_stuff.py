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
from infosets import InfoSet, InfoSetMap

table = InfoSetMap()


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

current_info = InfoSet(base_state, 0)
table.set_action(current_info, ActionType.CHECK_CALL, 3.0)
# table.set(base_state, ActionType.BET_RAISE, 0, 1)

base_state.complete_bet_or_raise_to()

current_info = InfoSet(base_state, 0)
table.set_action(current_info, ActionType.FOLD, 57.68)

print(table.to_string())
print()
