from SIM_CORE import *
from SIM_SETTINGS import *
from SIM_UTILS import *
from FILE_PATHS import *
from SIM_BATTER import *
from SIM_PITCHER import *
from SIM_PLAYER import *
import os, sys, time, string, pandas as pd, numpy as np

class LineupManager:
    def __init__(self, team_name, base_path):
        self.team_name = team_name
        self.base_path = base_path
        self.players = []  # All players loaded
        self.players_used = []
        self.batting_order = []  # Batting order for the team
        self.starting_pitchers = []  # Starting pitchers list
        self.relief_pitchers = []  # Relief pitchers list
        self.required_positions = ['C', '1B', '2B', '3B', 'SS', 'LF', 'CF', 'RF', 'DH']
        self.current_batter_index = 0
        
        # Load the roster and set the batting order
        self.load_roster()
        self.set_batting_order()

    def load_roster(self):
        # Clear lists before loading
        self.players = []
        self.pitchers = []
        self.starting_pitchers = []
        self.relief_pitchers = []
        self.fielders = []  # Clear fielders list

        # Load all batters and filter by team
        bat_path = os.path.join(self.base_path, "ALT_BAT.csv")
        bat_df = pd.read_csv(bat_path)
        team_batters = bat_df[bat_df["TM"] == self.team_name]
        all_batters = Batter.load_batters(team_batters)  # assuming this method exists

        # Load all pitchers and filter by team
        pit_path = os.path.join(self.base_path, "ALT_PIT.csv")
        pit_df = pd.read_csv(pit_path)
        team_pitchers = pit_df[pit_df["TM"] == self.team_name]
        all_pitchers = Pitcher.load_pitchers(team_pitchers)  # assuming this method exists
        
        # Define the required positions
        selected_batters = []

        for position in self.required_positions:
            # Find batters for the current position
            batters_for_position = [batter for batter in all_batters if batter.position == position]
            if not batters_for_position:
                raise ValueError(f"Not enough players to fill the position: {position}")

            # Select the highest-scoring batter for the position
            best_batter = max(batters_for_position, key=lambda batter: self.calculate_batting_score(batter))
            selected_batters.append(best_batter)

        # Ensure we only have 9 players in the lineup
        self.players = selected_batters[:9]

        for pitcher in all_pitchers:
            self.pitchers.append(pitcher)
            if pitcher.position == 'SP':
                self.starting_pitchers.append(pitcher)
            elif pitcher.position == 'RP':
                self.relief_pitchers.append(pitcher)

        # Validate the roster
        if len(self.players) != 9:
            raise ValueError("Not enough or too many batters to set a lineup")

    def set_batting_order(self):
        # Sort players by batting score in descending order
        if len(self.players) >= 9:
            self.batting_order = sorted(self.players, key=lambda player: self.calculate_batting_score(player), reverse=True)
        else:
            raise ValueError("Not enough players to set a batting order")

    def calculate_batting_score(self, player):
        # Use OBP, SLG, OPS, BABIP, and ISO to calculate batting score
        obp_weight = 0.35
        slg_weight = 0.25
        ops_weight = 0.20
        babip_weight = 0.10
        iso_weight = 0.10
        
        obp = player.obp
        slg = player.slg
        ops = player.ops
        babip = player.babip
        iso = player.iso

        # Calculate and return score
        batting_score = (obp * obp_weight) + (slg * slg_weight) + (ops * ops_weight) + (babip * babip_weight) + (iso * iso_weight)
        return batting_score

    def get_next_batter(self):
        batter = self.batting_order[self.current_batter_index]
        self.current_batter_index = (self.current_batter_index + 1) % len(self.batting_order)
        
        # Add the batter to players_used if they aren't already in the list
        if batter not in self.players_used:
            self.players_used.append(batter)

        return batter
