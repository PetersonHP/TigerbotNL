from poker_algorithms import KuhnPokerCFR

pokerbot = KuhnPokerCFR()
pokerbot.train(1000000, 0.05, 1E3, 1E2)

pokerbot.save_regrets_to_file()