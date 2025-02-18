import numpy as np
import pandas as pd
import sys
import os
from termcolor import colored
from SIM_FUNCTIONS import *
from SIM_ATBAT import *
from SIM_ABPROBS import *
from SIM_LGDATA import *
from SIM_TEAM import *
from SIM_SCOREBOARD import *
from SIM_SETTINGS import *
from SIM_PLAYER import *
from SIM_BATTER import *
from SIM_PITCHER import *
from SIM_SINGLE import *
from SIM_DOUBLE import *
from SIM_TRIPLE import *
from SIM_HOMERUN import *
from SIM_HBP_BB import *
from SIM_STRIKEOUTS import *
from SIM_POPOUTS import *
from SIM_GROUNDOUTS import *
from SIM_FLYOUTS import *
from SIM_LINEOUTS import *
from SIM_PICKOFFS import *
from SIM_WP_PB import *
from SIM_STEALS import *
from SIM_GAMESTATE import *
from SIM_PITCH_MANAGER import *
from SIM_LINEUP_MANAGER import *
from SIM_DISPLAY_MANAGER import *

class HalfInning:
    def __init__(self, batting_team, pitching_team, fielding_team, gamestate, scoreboard, league, home_team, matchups):
        self.batting_team = batting_team
        self.pitching_team = pitching_team
        self.fielding_team = fielding_team
        self.gamestate = gamestate
        self.scoreboard = scoreboard
        self.league = league
        self.home_team = home_team
        self.matchups = matchups
        self.display_manager = DisplayManager(self.scoreboard, DISPLAY_TOGGLE)


    def half_inning(self):
        self.gamestate.reset_inning()
        self.display_manager.display_scoreboard()

        while not self.gamestate.is_inning_over:
            batter = self.batting_team.lineup_manager.get_next_batter()
            pitcher = self.pitching_team.pitching_manager.get_current_pitcher()
            at_bat = AtBat(batter, pitcher, self.league, self.home_team, self.gamestate, self.scoreboard, self.matchups)

            # Step 1: Simulate the main at-bat outcome first
            outcome, pitches_thrown, pitch_sequence, at_bat_complete, hits_hit, runs_scored, outs_recorded, walk_off = at_bat.simulate_at_bat()

            pitcher.stats['pitches_thrown'] += pitches_thrown

            # Check for walk-off win condition to immediately end the inning
            if self.gamestate.is_walk_off_scenario():
                self.gamestate.set_walk_off()
                print(colored(f"🎉🎉🎉🎉🎉🎉🎉\n!WALK-OFF WIN!\n🎉🎉🎉🎉🎉🎉🎉", 'white', attrs=['bold', 'blink']))
                long_wait()
                break

            # End the inning if three outs are recorded or other inning-ending conditions
            if self.gamestate.end_inning():
                break

            # Check for pitching change if inning continues
            if not self.gamestate.is_inning_over:
                self.pitching_team.pitching_manager.check_for_pitching_change(self.gamestate.current_inning, self.gamestate, self.scoreboard)

        return {
            "walk_off": self.gamestate.is_walk_off,
            "score": [self.gamestate.stats['away_team']['score'], self.gamestate.stats['home_team']['score']],
            "outs": self.gamestate.outs,
            "hits": [self.gamestate.stats['away_team']['hits'], self.gamestate.stats['home_team']['hits']],
            "bases": self.gamestate.bases.copy(),
            "runs_scored": self.gamestate.runs_scored,
            "hits_hit": self.gamestate.hits_hit,
        }