import json
import os
from poker_algorithms import KuhnPokerCFR

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "regrets.json"), "r") as file:
    json_string = file.read()
    print(json.dumps(json_string))
    pokerbot = KuhnPokerCFR(json_string)

# pokerbot.train(100000, 0.05, 1E3, 1E2)
