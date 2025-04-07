from SIM_CORE import *
from SIM_SETTINGS import *
from SIM_UTILS import *
from FILE_PATHS import *
from SIM_DISPLAY_MANAGER import *
import os, sys, time, string, pandas as pd, numpy as np

class SimulateGame:
    def __init__(self, league, predefined_teams=None, use_predefined=False, seed=None):
        self.league = league
        self.use_predefined = use_predefined
        self.predefined_teams = predefined_teams
        self.team_selector = SelectTeam()
        
        # Pass predefined_teams and use_predefined to initialize_teams
        self.away_team, self.home_team = self.initialize_teams()
        self.gamestate = GameState(self.away_team, self.home_team, league)
        self.scoreboard = Scoreboard(self.gamestate)
        self.display_manager = DisplayManager(self.scoreboard, DISPLAY_TOGGLE)
        self.matchups = {}
        self.seed = initialize_random_seed(seed)

    def initialize_teams(self):
        """Initialize teams based on predefined teams or user selection."""
        if self.use_predefined and self.predefined_teams:
            away_team, home_team = self.predefined_teams
        else:
            away_team, home_team = self.team_selector.user_selection() 
        
        base_path = TEAM_PATH
        away_team = self.setup_team(away_team, base_path)
        home_team = self.setup_team(home_team, base_path)
        return away_team, home_team

    def setup_team(self, team_name, base_path):
        """Load and display team roster from the specified path."""
        team = Team(team_name, base_path)
        team.load_roster()
        team.select_starting_pitcher(manual_selection=True)
        team.display_roster()
        print()
        long_wait()
        return team

    def play_ball(self):
        self.scoreboard.playball_intro()
        
        while not self.gamestate.is_game_over:
            self.display_manager.display_start_inning()
            self.gamestate.top_or_bottom = "TOP"

            # Create the half inning simulation for the top of the inning
            top_half_inning = HalfInning(batting_team=self.away_team, pitching_team=self.home_team, fielding_team=self.home_team, gamestate=self.gamestate, scoreboard=self.scoreboard, league=self.league, home_team=self.home_team, matchups=self.matchups)
            top_half_inning.half_inning()

            if self.gamestate.end_of_game():
                break

            self.display_manager.display_middle_inning()

            # Simulate the bottom half of the inning
            self.gamestate.top_or_bottom = "BOT"
            bottom_half_inning = HalfInning(batting_team=self.home_team, pitching_team=self.away_team, fielding_team=self.away_team, gamestate=self.gamestate, scoreboard=self.scoreboard, league=self.league, home_team=self.home_team, matchups=self.matchups)
            bottom_half_inning.half_inning()

            if self.gamestate.end_of_game():
                break

            self.display_manager.display_end_inning()
            self.gamestate.toggle_inning()
        self.scoreboard.final()
        self.scoreboard.boxscore()
        self.away_team.display_stats()
        self.home_team.display_stats()
        exit_button()

if __name__ == "__main__":
    print(rgb_colored("WELCOME TO AL BISMOS BASEBALL SIMULATOR 24\n", GOLD, align='center', width=83))
    league = LeagueAverages()
    away = "NYY"
    home = "LAD"
    predefined_teams = (away, home)
    simulation_game = SimulateGame(league, predefined_teams=predefined_teams, use_predefined=True, seed=RAND_SEED)
    print()
    start = time.time()
    simulation_game.play_ball()
    finish = time.time()
    print(finish - start)



