import os
from poker_algorithms import KuhnPokerCFR

with open("regrets.json", "r") as file:
    json_string = file.read()
    pokerbot = KuhnPokerCFR(json_string)

# pokerbot.train(100000, 0.05, 1E3, 1E2)
