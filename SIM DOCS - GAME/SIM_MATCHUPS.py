from SIM_CORE import *
from SIM_SETTINGS import *
from SIM_UTILS import *
from FILE_PATHS import *
import os, sys, time, string, pandas as pd, numpy as np

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
