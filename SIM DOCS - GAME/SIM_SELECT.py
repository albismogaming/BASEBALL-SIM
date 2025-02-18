import numpy as np
import pandas as pd
import os
from itertools import zip_longest
from collections import namedtuple
from SIM_FUNCTIONS import *
from SIM_TEAM import Team
from FILE_PATHS import *
from SIM_SETTINGS import *

# Define a structured TeamData tuple
TeamData = namedtuple("TeamData", ["league", "abbr", "market", "team_name", "wins", "losses", "folder_path"])

class SelectTeam:
    def __init__(self, csv_file="TEAMS.csv"):
        self.csv_file = csv_file
        self.teams = self.load_teams()

    def load_teams(self):
        """Load teams from CSV into a dictionary with abbreviations as keys."""
        try:
            teams_df = pd.read_csv(os.path.join(TEAM_PATH, self.csv_file))

            # Convert into dictionary format for fast lookup
            teams_dict = {
                row["abbr"]: TeamData(
                    row["league"], row["abbr"], row["market"], 
                    row["team_name"], row["wins"], row["losses"],
                    os.path.join(TEAM_PATH, row["abbr"])  # Generate folder path dynamically
                )
                for _, row in teams_df.iterrows()
            }

            return teams_dict
        except FileNotFoundError:
            print("ERROR: teams.csv file not found! Ensure the file is in the correct directory.")
            return {}

    def display_available_teams(self):
        """Display available teams split into AL and NL side by side."""
        al_teams = [(abbr, team) for abbr, team in self.teams.items() if team.league == "AL"]
        nl_teams = [(abbr, team) for abbr, team in self.teams.items() if team.league == "NL"]

        # Ensure both lists are the same length by padding with empty values
        max_len = max(len(al_teams), len(nl_teams))
        al_teams.extend([("", None)] * (max_len - len(al_teams)))
        nl_teams.extend([("", None)] * (max_len - len(nl_teams)))

        print(rgb_colored(f"{'⚾️ SELECT TEAMS ⚾️':^83}", WHITE))

        # Header for both leagues
        header = f"{rgb_colored('AMERICAN LEAGUE', RED, align='center', width=40)} {rgb_colored('|', WHITE)} {rgb_colored('NATIONAL LEAGUE', BLUE, align='center', width=40)}"
        
        sub_header = f"""{"ABB":<5} {"TEAM NAME":<24} {"Ws - Ls":<7} {"|":^5} {"ABB":<5} {"TEAM NAME":<24} {"Ws - Ls":<7}"""

        print(rgb_colored("━"*85, WHITE))
        print(header)
        print(rgb_colored("━"*85, WHITE))
        print(rgb_colored(sub_header, GOLDEN_YELLOW))
        print(rgb_colored("━"*85, WHITE))

        # Print teams side by side
        for (al_abbr, al_team), (nl_abbr, nl_team) in zip(al_teams, nl_teams):
            al_team_str = f"{al_abbr:<5} {f'{al_team.market} {al_team.team_name}':<24} {al_team.wins:2} - {al_team.losses:<3}" if al_team else ""
            nl_team_str = f"{nl_abbr:<5} {f'{nl_team.market} {nl_team.team_name}':<24} {nl_team.wins:2} - {nl_team.losses:<3}" if nl_team else ""
            print(f"{rgb_colored(al_team_str, LIGHT_RED)} {rgb_colored('|', WHITE, align='center', width=4)} {rgb_colored(nl_team_str, LIGHT_BLUE)}")

        print(rgb_colored("━"*85, WHITE))

    def get_team(self, team_abbr):
        """Retrieve the team dictionary based on abbreviation."""
        return self.teams.get(team_abbr, None)

    def user_selection(self, predefined_teams=None, use_predefined=False):
        """
        Allow user to select teams or use predefined teams.
        If predefined_teams is provided, it returns those teams immediately.
        """
        if use_predefined and predefined_teams:
            return self.get_team(predefined_teams[0]), self.get_team(predefined_teams[1])

        while True:
            self.display_available_teams()
            
            away_abbr = input(rgb_colored("\n⚾️ SELECT THE AWAY TEAM ABB: ", WHITE)).upper()
            home_abbr = input(rgb_colored("\n⚾️ SELECT THE HOME TEAM ABB: ", WHITE)).upper()

            # ✅ Lookup team objects from dictionary
            away_team = self.teams.get(away_abbr, None)
            home_team = self.teams.get(home_abbr, None)

            # ✅ Ensure valid selections & prevent duplicate choices
            if away_team and home_team and away_abbr != home_abbr:
                print(rgb_colored(f"\n⚾️ LOADING {f'{away_team.market} {away_team.team_name}':24} (AWAY).......", WHITE))
                print(rgb_colored(f"\n⚾️ LOADING {f'{home_team.market} {home_team.team_name}':24} (HOME).......\n", WHITE))
                return away_team.abbr, home_team.abbr  # ✅ Return full team objects (TeamData)
            else:
                print("❌ ERROR: INVALID INPUT OR DUPLICATE TEAMS. SELECT AGAIN.")