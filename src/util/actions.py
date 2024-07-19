"""Enum type to represent actions in HUNL"""
from enum import Enum


class Action(Enum):
    """Action set based on SlumBot's Action set"""
    FOLD = 0
    CHECK_CALL = 1
    ALL_IN = 2
    BET_MIN = 3
    BET_HALF = 4
    BET_FULL = 5
