import numpy as np
import pandas as pd
import time
from termcolor import colored
from collections import OrderedDict
from SIM_FUNCTIONS import *
from SIM_LGDATA import *
from SIM_TEAM import *
from SIM_SETTINGS import *
from SIM_SCOREBOARD import *
from SIM_WP_PB import *


class MatchupManager:
    def __init__(self, batter, pitcher, matchups):
        self.batter = batter
        self.pitcher = pitcher
        self.matchups = matchups
        self.update_matchups()

    def update_matchups(self):
        # Create a key for the batter-pitcher pair
        matchup_key = (self.batter.player_id, self.pitcher.player_id)
        if matchup_key not in self.matchups:
            self.matchups[matchup_key] = 0
        self.matchups[matchup_key] += 1

    def get_matchup_count(self):
        # Return the count of matchups between the batter and pitcher
        matchup_key = (self.batter.player_id, self.pitcher.player_id)
        return self.matchups.get(matchup_key, 0)

    def adjust_probability_for_matchups(self, base_probability, matchup_count, is_batter=True):
        factor = (2 ** matchup_count - 1)
        if is_batter:
            return min(1, base_probability * (1 + 0.007 * factor))  # Batter gets a boost with more matchups
        else:
            return max(0, base_probability * (1 - 0.007 * factor))  # Pitcher gets a reduction with more matchups
