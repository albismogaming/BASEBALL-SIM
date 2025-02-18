import pandas as pd
import numpy as np
import sys
import os
from SIM_UTILS import *
from SIM_FUNCTIONS import *
from SIM_SCOREBOARD import *
from SIM_GAMESTATE import *
from SIM_SETTINGS import *
from SIM_DISPLAY_MANAGER import *
from SIM_TEXT_MANAGER import *
from SIM_HIT_RESULT import *

class Lineout:
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
        hits_hit = 0
        runs_scored = 0
        outs_recorded = 1
        walk_off = False

        batter_side = get_batter_side(self.batter, self.pitcher)
        # Get a randomly selected hit location and fielder position
        hit_direction, batted_ball_type, hit_location = self.hit_information.determine_hit_information("LINEOUT", batter_side)

        self.outcomes.append(f"{self.batter.last_name.upper()} HITS A HARD LINER BUT THEY ARE THERE TO FIELD IT FOR THE OUT!")

        self.gamestate.move_runner("HOME", "OUT", self.batter)

        self.batter.record_at_bat(hit_type="lineout")
        self.pitcher.record_outcome(hit_type="lineout", outs=outs_recorded)

        DisplayManager.display_outcome_text(self.outcomes, display_enabled=DISPLAY_TEXT)
        return hits_hit, runs_scored, outs_recorded, walk_off
