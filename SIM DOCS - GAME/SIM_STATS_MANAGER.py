import os
import pandas as pd
import numpy as np
import time
import math
from SIM_FUNCTIONS import *
from SIM_UTILS import *
from SIM_SETTINGS import *

class StatsManager:
    def __init__(self):
        self.batter_stats = {}  # Key: batter object, Value: stat dictionary
        self.pitcher_stats = {}  # Key: pitcher object, Value: stat dictionary

    def get_all_batter_stats(self):
        """Returns all tracked batter statistics."""
        return self.batter_stats

    def get_all_pitcher_stats(self):
        """Returns all tracked pitcher statistics."""
        return self.pitcher_stats

    def initialize_batter_stats(self, batter):
        """Ensures a batter has an entry in stats before updating."""
        if batter.player_id not in self.batter_stats:
            self.batter_stats[batter.player_id] = {
                "name": batter.last_name.upper(),  # ✅ Store batter's name
                "position": batter.position,       # ✅ Store batter's position
                "at_bats": 0, "hits": 0, "single": 0, "double": 0, "triple": 0, "home_run": 0,
                "strikeouts": 0, "walks": 0, "hit_by_pitch": 0, "runs": 0, "rbi": 0
            }

    def initialize_pitcher_stats(self, pitcher):
        """Ensures a pitcher has an entry in stats before updating."""
        if pitcher.player_id not in self.pitcher_stats:
            self.pitcher_stats[pitcher.player_id] = {
                "name": pitcher.last_name.upper(),  # ✅ Store pitcher's name
                "position": pitcher.position,       # ✅ Store pitcher's position
                "pitches_thrown": 0, "innings_pitched": 0, "strikeouts": 0, "walks": 0, "hit_by_pitch": 0,
                "hits_allowed": 0, "home_runs_allowed": 0, "runs_allowed": 0, "earned_runs": 0, "outs_recorded": 0, 
                "wild_pitches": 0, "passed_balls": 0
            }

    def record_batter_stat(self, batter, stat_type, value):
        """Tracks per-game stats for each batter using the Batter object."""
        self.initialize_batter_stats(batter)
        self.batter_stats[batter.player_id][stat_type] += value


    def record_pitcher_stat(self, pitcher, stat_type, value):
        """Updates a specific pitcher stat using player_id as key."""
        self.initialize_pitcher_stats(pitcher)  # ✅ Ensure pitcher is initialized
        self.pitcher_stats[pitcher.player_id][stat_type] += value  # ✅ Use player_id as the key


    def calculate_batter_stat(self, batter, stat_type):
        """Calculates batting stats like AVG, OBP, and SLG."""
        stats = self.batter_stats.get(batter, {})

        if stat_type == "AVG":  # Batting Average = Hits / At-Bats
            if stats.get("at_bats", 0) > 0:
                return stats["hits"] / stats["at_bats"]
            return 0.0

        elif stat_type == "OBP":  # On-Base Percentage = (H + BB + HBP) / (AB + BB + HBP)
            total_plate_appearances = stats.get("at_bats", 0) + stats.get("walks", 0) + stats.get("hit_by_pitch", 0)
            if total_plate_appearances > 0:
                return (stats["hits"] + stats["walks"] + stats["hit_by_pitch"]) / total_plate_appearances
            return 0.0

        elif stat_type == "SLG":  # Slugging % = (1B + 2*2B + 3*3B + 4*HR) / AB
            if stats.get("at_bats", 0) > 0:
                total_bases = (stats["singles"] + 2 * stats["doubles"] + 3 * stats["triples"] + 4 * stats["home_runs"])
                return total_bases / stats["at_bats"]
            return 0.0

        return None  # Invalid stat type

    def reset_batter_stats(self):
        """Resets all batter stats for a new game."""
        self.batter_stats = {}  # Clears all stored batter stats

    def calculate_innings_pitched(self, pitcher):
        """Calculates innings pitched in proper format (e.g., 5.2 for 5 2/3 innings)."""
        self.initialize_pitcher_stats(pitcher)

        total_outs = self.pitcher_stats[pitcher].get('outs_recorded', 0)
        full_innings = total_outs // 3
        additional_outs = total_outs % 3

        # Store innings pitched as a formatted string (5.2 format)
        return f"{full_innings}.{additional_outs}"

    def get_era(self, pitcher):
        """Calculates Earned Run Average (ERA)."""
        self.initialize_pitcher_stats(pitcher)

        outs_recorded = self.pitcher_stats[pitcher].get('outs_recorded', 0)
        full_innings = outs_recorded // 3
        additional_outs = outs_recorded % 3
        total_innings_pitched = full_innings + additional_outs / 3.0

        # Calculate ERA only if there are innings pitched
        if total_innings_pitched > 0:
            era = (self.pitcher_stats[pitcher]['earned_runs'] / total_innings_pitched) * 9
            return f"{era:.3f}"  # Format to three decimal places
        else:
            return "0.000"  # No innings pitched = ERA of 0.000