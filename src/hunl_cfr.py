"""Model to approximate Nash equilibrium play in an incomplete information 
extended form game using average strategy sampling Monte Carlo counterfactual 
regret minimization. Customized for heads-up, no-limit Texas Hold'em"""
from util.actions import Action
from util.infosets import InfoSet, InfoSetMap

from pokerkit import State


def _walk_tree(base_state: State,
               player_index: int,
               sample_prob: float,
               epsilon: float,
               tau: float,
               beta: float,
               regrets: InfoSetMap,
               cumulative_profile: InfoSetMap) -> float:
    """Perform an iteration of MCCFR
    
    Args:
        base_state (State): the state (history) at the root of the subtree 
                            that will be traversed on this method call
        player_index (int): the index of the player to act at this history
        sample_prob (float): the probability of sampling this history
        epsilon (float): see HeadsUpNLCFR.train()
        tau (float): see HeadsUpNLCFR.train()
        beta (float): see HeadsUpNLCFR.train()
        regrets (InfoSetMap): a data structure associating regret values with 
                            actions at InfoSets
        cumulative_profile (InfoSetMap): a table associating InfoSets with 
                            action probability distributions

    Returns:
        float: the approximated utility of the given base state
    """


class HeadsUpNLCFR:
    """Object to represent an MCCFR model. Regrets can be trained from scratch 
    or loaded from a file. Strategies can be derived from trained regrets given 
    an InfoSet"""

    def __init__(self, regrets_filename: str | None = None) -> None:
        pass

    def train(self, epochs: int, epsilon: float, tau: float, beta: float) -> None:
        """Train the model

        Args:
            epochs (int): number of tree walks to perform from the root
            epsilon (float): base subtree exploration probability
            tau (float): threshold parameter - any action taken with 
                        probability at least 1/tau by the average strategy 
                        will always be sampled
            beta (float): bonus parameter - increases the rate of exploration 
                        during early AS iterations

        Algorithm implementation based on Gibson et al. (2012).
        """

    def load_regrets_from_file(self, filename: str):
        """Load a regret table from a file

        Args:
            filename (str): the name of the file to load from
        """

    def save_regrets_to_file(self):
        """Save a regret table from a file"""
