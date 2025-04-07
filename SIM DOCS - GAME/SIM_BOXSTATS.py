from SIM_CORE import *
from SIM_SETTINGS import *
from SIM_UTILS import *
from FILE_PATHS import *
from SIM_PLAYER import *
from SIM_BATTER import *
from SIM_PITCHER import *
from tabulate import tabulate
import os, sys, time, string, pandas as pd, numpy as np

class BoxScoreDisplay:
    def __init__(self, team):
        self.team = team
        self.batter_headers = ["BATTERS", "POS", "AB", "H", "1B", "2B", "3B", "HR", "SO", "BB", "HBP", "AVG"]
        self.pitcher_headers = ["PITCHERS", "POS", "IP", "P", "H", "R", "ER", "HR", "SO", "BB", "HBP", "ERA"]
        self.batter_column_widths = [14, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 7]  # Set fixed column widths
        self.pitcher_column_widths = [14, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 7]  # Set fixed column widths

    def format_row(self, row, widths):
        return "" + "".join(f"{str(item):<{widths[i]}}" for i, item in enumerate(row)) + ""

    def calculate_batter_totals(self, batters):
        totals = ["TOTALS", "", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0]
        for batter in batters:
            stats = batter.get_stats_as_list()
            for i in range(2, 11):
                totals[i] += int(stats[i])
        totals[11] = f"{totals[3] / totals[2]:.3f}" if totals[2] > 0 else "0.000"
        return totals

    def calculate_pitcher_totals(self, pitchers_used):
        totals = ["TOTALS", "", 0.0, 0, 0, 0, 0, 0, 0, 0, 0, "0.000"]
        total_outs = 0  # To track total outs for innings pitched

        for pitcher in pitchers_used:
            stats = pitcher.get_stats_as_list()
            for i in range(2, 11):
                if i == 2:
                    # Convert innings pitched from string "X.Y" to total outs
                    innings_pitched_str = stats[i]
                    full_innings, additional_outs = map(int, innings_pitched_str.split('.'))
                    total_outs += full_innings * 3 + additional_outs
                elif i == 6:
                    totals[i] += int(stats[i])  # Earned runs can be a float
                else:
                    totals[i] += int(stats[i])

        # Calculate total innings pitched as a float and round to one decimal place
        total_full_innings = total_outs // 3
        total_additional_outs = total_outs % 3
        total_innings_pitched = total_full_innings + total_additional_outs / 3.0
        totals[2] = round(total_innings_pitched, 1)

        # Calculate ERA
        total_earned_runs = totals[6]
        if total_innings_pitched > 0:
            era = (total_earned_runs / total_innings_pitched) * 9
            totals[11] = f"{round(era, 3):.3f}"  # Format the ERA to three decimal places as a string
        else:
            totals[11] = "0.000"  # Return "0.000" when there are no innings pitched

        # Convert innings pitched back to string "X.Y" for display
        full_innings_str = int(totals[2])
        additional_outs_str = int(round((totals[2] - full_innings_str) * 3))
        totals[2] = f"{full_innings_str}.{additional_outs_str}"

        return totals

    def display_batter_stats(self, batters):
        # # Prepare batter header and separators
        batter_header_line = self.format_row(self.batter_headers, self.batter_column_widths)
        print(f"{rgb_colored((batter_header_line), YELLOW)}")
        print(rgb_colored("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■".format(self.team), ASH_GRAY))
        for batter in batters:
            print_delay(rgb_colored(self.format_row(batter.get_stats_as_list(), self.batter_column_widths), BONE))

        # Print batter totals
        batter_totals = self.calculate_batter_totals(batters)
        print(f"{rgb_colored(self.format_row(batter_totals, self.batter_column_widths), LIGHT_RED)}")

    def display_pitcher_stats(self, pitchers):
        # # Prepare pitcher header and separators
        pitcher_header_line = self.format_row(self.pitcher_headers, self.pitcher_column_widths)
        print(f"{rgb_colored((pitcher_header_line), YELLOW)}")
        print(rgb_colored("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■".format(self.team), ASH_GRAY))
        for pitcher in pitchers:
            print_delay(rgb_colored(self.format_row(pitcher.get_stats_as_list(), self.pitcher_column_widths), BONE))

        # Print pitcher totals
        pitcher_totals = self.calculate_pitcher_totals(pitchers)
        print(f"{rgb_colored(self.format_row(pitcher_totals, self.pitcher_column_widths), LIGHT_RED)}")

    def display_team_stats(self):
        batters = [player for player in self.team.lineup_manager.players_used if isinstance(player, Batter)]
        if not batters:
            print("No batters found in the lineup.")
        pitchers = [player for player in self.team.pitching_manager.pitchers_used if isinstance(player, Pitcher)]
        div1 = rgb_colored(f"┃┃", ASH_GRAY)
        message = " ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■   {} BOX STATS   ■■■■■■■■■■■■■■■■■■■■■■■■■■■ ".format(self.team)

        header = f"""
{rgb_colored(f'┏┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳┓', ASH_GRAY)}
{div1}{rgb_colored(message, WHITE)}{div1}
{rgb_colored(f'┗┻━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┻┛', ASH_GRAY)}"""

        print(header)
        self.display_batter_stats(batters)
        print(rgb_colored("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■".format(self.team), ASH_GRAY))
        self.display_pitcher_stats(pitchers)
        print(rgb_colored("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■".format(self.team), ASH_GRAY))
