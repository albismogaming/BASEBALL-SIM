import pandas as pd
import numpy as np
from SIM_FUNCTIONS import *
from SIM_SCOREBOARD import *
from SIM_GAMESTATE import *
from SIM_SETTINGS import *
from SIM_DISPLAY_MANAGER import *
from SIM_TEXT_MANAGER import *
from SIM_HIT_RESULT import *

class Pickoff1st:
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

        rand_val = np.random.random()
        if rand_val < PICKOFF_PROB:
            self.gamestate.move_runner('1ST', 'OUT')
            outs_recorded += 1 
            outcome_description = self.text_manager.get_event_description("PICKOFF_1ST", "OUT")
        else:
            outcome_description = self.text_manager.get_event_description("PICKOFF_1ST", "SAFE")

        formatted_description = outcome_description.format(
            runner=self.runners.get('1ST').last_name.upper(), 
            pitcher=self.pitcher.last_name.upper(), 
            batter=self.batter.last_name.upper()
            )
        self.outcomes.append(formatted_description)

        self.pitcher.record_outcome(po_first=True, outs=outs_recorded)

        DisplayManager.display_outcome_text(self.outcomes, display_enabled=DISPLAY_TEXT)
        return hits_hit, runs_scored, outs_recorded, walk_off

class Pickoff2nd:
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

        rand_val = np.random.random()
        if rand_val < PICKOFF_PROB:
            self.gamestate.move_runner('2ND', 'OUT')
            outs_recorded += 1
            outcome_description = self.text_manager.get_event_description("PICKOFF_2ND", "OUT")
        else:
            outcome_description = self.text_manager.get_event_description("PICKOFF_2ND", "SAFE")
        
        formatted_description = outcome_description.format(
            runner=self.runners.get('2ND').last_name.upper(), 
            pitcher=self.pitcher.last_name.upper(), 
            batter=self.batter.last_name.upper()
            )
        self.outcomes.append(formatted_description)

        self.pitcher.record_outcome(po_second=True, outs=outs_recorded)

        DisplayManager.display_outcome_text(self.outcomes, display_enabled=DISPLAY_TEXT)
        return hits_hit, runs_scored, outs_recorded, walk_off