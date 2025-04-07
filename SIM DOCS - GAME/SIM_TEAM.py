from SIM_CORE import *
from SIM_SETTINGS import *
from SIM_UTILS import *
from FILE_PATHS import *
import os, sys, time, string, pandas as pd, numpy as np

class Team:
    def __init__(self, team_name, base_path):
        self.team_name = team_name
        self.base_path = base_path
        self.wins = 0
        self.loss = 0
        self.lineup_manager = LineupManager(self.team_name, self.base_path)
        self.pitching_manager = PitchingManager(self.lineup_manager.starting_pitchers, self.lineup_manager.relief_pitchers)

    def __str__(self):
        return self.team_name  # This will return the team name when the object is printed

    def load_roster(self):
        self.lineup_manager.load_roster()
    
    def select_starting_pitcher(self, manual_selection=None):
        """Select a starting pitcher and display team name."""
        print(rgb_colored(f"SELECT STARTING PITCHER FOR {self.team_name.upper()}:", WHITE))
        return self.pitching_manager.select_starting_pitcher(manual_selection)

    def set_batting_order(self):
        self.lineup_manager.set_batting_order()

    def get_next_batter(self):
        return self.lineup_manager.get_next_batter()

    def get_current_pitcher(self):
        return self.pitching_manager.get_current_pitcher()

    def pitching_change(self, current_inning):
        self.pitching_manager.make_pitching_change(current_inning)

    def display_stats(self):
        box_score_display = BoxScoreDisplay(self)
        box_score_display.display_team_stats()

    def format_player_line(self, player, index):
        return rgb_colored("[{:<1}] {:<2} - {:<14} {:<5.3f}".format(index + 1, player.position, player.last_name.upper(), player.average), WHITE)

    def format_pitcher_line(self, pitcher, index):
        return rgb_colored("[{:<1}] {:<2} - {:<14} {:<5.3f}".format(index + 1, pitcher.position, pitcher.last_name.upper(), pitcher.average), WHITE)

    def print_boxed_content(self, content):
        for line in content:
            print(line)

    def display_roster(self):
        print(rgb_colored("\n■■■  {} STARTING LINEUP  ■■■".format(self.team_name), GOLD))
        print(rgb_colored("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■", WHITE))

        short_wait()

        if not self.lineup_manager.players:
            print("No batters loaded.")
        else:
            # Loop through each player in the batting order, printing one at a time with a pause
            for index, player in enumerate(self.lineup_manager.batting_order):
                batter_line = self.format_player_line(player, index)
                self.print_boxed_content([batter_line])  # Print each player with boxed formatting
                short_wait()  # Pause between each player

        if not self.pitching_manager.current_pitcher:
            print("No starting pitcher selected.")
        else:
            # Print the starting pitcher separately with a pause
            pitcher_line = self.format_pitcher_line(self.pitching_manager.current_pitcher, 1)
            self.print_boxed_content([pitcher_line])
            short_wait()

        print(rgb_colored("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■", WHITE))
