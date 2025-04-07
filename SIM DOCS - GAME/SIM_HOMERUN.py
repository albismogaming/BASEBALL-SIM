from SIM_CORE import *
from SIM_SETTINGS import *
from SIM_UTILS import *
from FILE_PATHS import *
from SIM_DISPLAY_MANAGER import *
from SIM_HIT_RESULT import *
from SIM_TEXT_MANAGER import *
from SIM_SCENARIO_MANAGER import *
import os, sys, time, string, pandas as pd, numpy as np

class Homerun:
    def __init__(self, gamestate, league, pitcher, batter, runners=None, fielding_team=None, **kwargs):
        self.gamestate = gamestate  # ✅ Game state access
        self.league = league  # ✅ League-wide stats access
        self.pitcher = pitcher  # ✅ Pitcher involved in the play
        self.batter = batter  # ✅ Batter involved in the play
        self.runners = self.gamestate.set_runners_on_base() if runners is None else runners  # ✅ Get current base runners
        self.fielding_team = fielding_team  # ✅ Fielding team (if applicable)
        self.outcomes = []  # ✅ Stores event text descriptions
        self.text_manager = TextManager()  # ✅ Manages outcome descriptions
        self.hit_information = HitInformation(gamestate, league, pitcher, batter, None)  # ✅ Handles hit data
        self.kwargs = kwargs  # ✅ Capture additional parameters if needed

    def execute(self):
        hits_hit = 1
        num_runners = sum(1 for runner in self.runners.values() if runner)
        runs_scored = num_runners + 1  # The batter also scores
        outs_recorded = 0
        walk_off = False

        base_state = self.gamestate.get_base_state()
        batter_side = get_batter_side(self.batter, self.pitcher)
        hit_direction, batted_ball_type, hit_location = self.hit_information.determine_hit_information("HOMERUN", batter_side)

        outcome_description = self.text_manager.get_event_description("HOMERUN", base_state, batter_side, hit_location)
        formatted_description = outcome_description.format(
            pitcher=self.pitcher.last_name.upper(), 
            batter=self.batter.last_name.upper()
            )
        self.outcomes.append(formatted_description)

        if runs_scored == 1:
            self.outcomes.append(f"\n{self.batter.last_name.upper()} HITS A SOLO HOMERUN!")
        elif runs_scored == 2:
            self.outcomes.append(f"\n{self.batter.last_name.upper()} HITS A TWO-RUN HOMERUN!")
        elif runs_scored == 3:
            self.outcomes.append(f"\n{self.batter.last_name.upper()} HITS A THREE-RUN HOMERUN!")
        elif runs_scored == 4:
            self.outcomes.append(f"\n{self.batter.last_name.upper()} HITS A GRANDSLAM HOMERUN!")

        # Clear all bases (redundant with the above loop but ensures bases are cleared)
        self.gamestate.bases = {'1ST': None, '2ND': None, '3RD': None}

        self.batter.record_at_bat(hit_type="homerun")
        self.pitcher.record_outcome(hit_type="homerun", runs=runs_scored, earned_runs=runs_scored)

        DisplayManager.display_outcome_text(self.outcomes, display_enabled=DISPLAY_TEXT)
        return hits_hit, runs_scored, outs_recorded, walk_off


