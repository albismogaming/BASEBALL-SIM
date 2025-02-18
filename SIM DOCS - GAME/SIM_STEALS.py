import pandas as pd
import numpy as np
import sys
import os
from SIM_FUNCTIONS import *
from SIM_SCOREBOARD import *
from SIM_TEAM import *
from SIM_SETTINGS import *
from SIM_GAMESTATE import *
from SIM_UTILS import *
from SIM_DISPLAY_MANAGER import *
from SIM_TEXT_MANAGER import *
from SIM_HIT_RESULT import *

class BaseStealing:
    def __init__(self, gamestate, pitcher, batter, runners=None, fielding_team=None, **kwargs):
        self.gamestate = gamestate  # ✅ Game state access
        self.pitcher = pitcher  # ✅ Pitcher involved in the play
        self.batter = batter  # ✅ Batter involved in the play
        self.runners = self.gamestate.set_runners_on_base() if runners is None else runners  # ✅ Get current base runners
        self.fielding_team = fielding_team  # ✅ Fielding team (if applicable)
        self.outcomes = []  # ✅ Stores event text descriptions
        self.text_manager = TextManager()  # ✅ Manages outcome descriptions
        self.kwargs = kwargs  # ✅ Capture additional parameters if needed

    def execute(self):
        hits_hit = 0
        runs_scored = 0
        outs_recorded = 0
        walk_off = False
        
        base_state = self.gamestate.get_base_state()

        if base_state == 'RUNNER_ON_FIRST':
            rand_val = np.random.random()
            stealing_prob = adjust_probability(STEALING_CHANCE, self.runners.get('1ST').speed)

            if rand_val < stealing_prob:
                self.gamestate.move_runner('1ST', '2ND')
                outcome_description = self.text_manager.get_event_description("STEAL", "SUCCESSFUL")
            else:
                self.gamestate.move_runner('1ST', 'OUT')
                outs_recorded += 1 
                outcome_description = self.text_manager.get_event_description("STEAL", "CAUGHT")

        elif base_state == 'FIRST_AND_THIRD':
            rand_val = np.random.random()
            stealing_prob = adjust_probability(STEALING_CHANCE, self.runners.get('1ST').speed)

            if rand_val < stealing_prob:
                self.gamestate.move_runner('1ST', '2ND')
                outcome_description = self.text_manager.get_event_description("STEAL", "SUCCESSFUL")
            else:
                self.gamestate.move_runner('1ST', 'OUT')
                outs_recorded += 1
                outcome_description = self.text_manager.get_event_description("STEAL", "CAUGHT")

        formatted_description = outcome_description.format(
            runner=self.runners.get('1ST').last_name.upper(), 
            pitcher=self.pitcher.last_name.upper(), 
            batter=self.batter.last_name.upper()
            )
        
        self.outcomes.append(formatted_description)
        self.pitcher.record_outcome(sb_second=True, outs=outs_recorded)

        DisplayManager.display_outcome_text(self.outcomes, display_enabled=DISPLAY_TEXT)
        return hits_hit, runs_scored, outs_recorded, walk_off