import pandas as pd
import numpy as np
import sys
import os
from SIM_FUNCTIONS import *
from SIM_SCOREBOARD import *
from SIM_TEAM import *
from SIM_GAMESTATE import *
from SIM_DISPLAY_MANAGER import *
from SIM_TEXT_MANAGER import *
from SIM_HIT_RESULT import *

class WildPitch:
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
        
        if base_state == "BASES_LOADED":
            self.gamestate.move_runner('3RD', 'HOME')
            self.gamestate.move_runner("2ND", "3RD")
            self.gamestate.move_runner("1ST", "2ND")
            runs_scored += 1

        elif base_state == "FIRST_AND_SECOND":
            self.gamestate.move_runner("2ND", "3RD")
            self.gamestate.move_runner("1ST", "2ND")

        elif base_state == "FIRST_AND_THIRD":
            self.gamestate.move_runner('3RD', 'HOME')
            self.gamestate.move_runner("1ST", "2ND")
            runs_scored += 1

        elif base_state == "SECOND_AND_THIRD":
            self.gamestate.move_runner('3RD', 'HOME')
            self.gamestate.move_runner("2ND", "3RD")
            runs_scored += 1

        elif base_state == "RUNNER_ON_FIRST":
            self.gamestate.move_runner("1ST", "2ND")

        elif base_state == "RUNNER_ON_SECOND":
            self.gamestate.move_runner("2ND", "3RD")

        elif base_state == "RUNNER_ON_THIRD":
            self.gamestate.move_runner('3RD', 'HOME')
            runs_scored += 1

        else:
            pass

        outcome_description = self.text_manager.get_event_description("WILDPITCH", base_state)
        formatted_description = outcome_description.format(
            pitcher=self.pitcher.last_name.upper(), 
            batter=self.batter.last_name.upper()
            )
        self.outcomes.append(formatted_description)
        self.pitcher.record_outcome(wild_pitch=True, runs=runs_scored, earned_runs=runs_scored)

        DisplayManager.display_outcome_text(self.outcomes, display_enabled=DISPLAY_TEXT)
        return hits_hit, runs_scored, outs_recorded, walk_off

class PassedBall:
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
        
        if base_state == "BASES_LOADED":
            self.gamestate.move_runner('3RD', 'HOME')
            self.gamestate.move_runner("2ND", "3RD")
            self.gamestate.move_runner("1ST", "2ND")
            runs_scored += 1

        elif base_state == "FIRST_AND_SECOND":
            self.gamestate.move_runner("2ND", "3RD")
            self.gamestate.move_runner("1ST", "2ND")

        elif base_state == "FIRST_AND_THIRD":
            self.gamestate.move_runner('3RD', 'HOME')
            self.gamestate.move_runner("1ST", "2ND")
            runs_scored += 1

        elif base_state == "SECOND_AND_THIRD":
            self.gamestate.move_runner('3RD', 'HOME')
            self.gamestate.move_runner("2ND", "3RD")
            runs_scored += 1

        elif base_state == "RUNNER_ON_FIRST":
            self.gamestate.move_runner("1ST", "2ND")

        elif base_state == "RUNNER_ON_SECOND":
            self.gamestate.move_runner("2ND", "3RD")

        elif base_state == "RUNNER_ON_THIRD":
            self.gamestate.move_runner('3RD', 'HOME')
            runs_scored += 1

        else:
            pass

        outcome_description = self.text_manager.get_event_description("PASSEDBALL", base_state)
        formatted_description = outcome_description.format(
            pitcher=self.pitcher.last_name.upper(), 
            batter=self.batter.last_name.upper()
            )
        self.outcomes.append(formatted_description)
        self.pitcher.record_outcome(passed_ball=True, runs=runs_scored, earned_runs=runs_scored)

        DisplayManager.display_outcome_text(self.outcomes, display_enabled=DISPLAY_TEXT)
        return hits_hit, runs_scored, outs_recorded, walk_off