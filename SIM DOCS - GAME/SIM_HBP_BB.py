import pandas as pd
import numpy as np
from SIM_FUNCTIONS import *
from SIM_SCOREBOARD import *
from SIM_TEAM import *
from SIM_GAMESTATE import *
from SIM_DISPLAY_MANAGER import *
from SIM_TEXT_MANAGER import *
from SIM_HIT_RESULT import *

class Walk:
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
        outs_recorded = 0
        walk_off = False

        base_state = self.gamestate.get_base_state()  # Get the current base state

        if base_state == "BASES_LOADED":
            self.gamestate.move_runner('3RD', 'HOME')
            self.gamestate.move_runner("2ND", "3RD")
            self.gamestate.move_runner("1ST", "2ND")
            runs_scored += 1

        elif base_state == "FIRST_AND_SECOND":
            self.gamestate.move_runner("2ND", "3RD")
            self.gamestate.move_runner("1ST", "2ND")

        elif base_state == "FIRST_AND_THIRD":
            self.gamestate.move_runner("1ST", "2ND")

        elif base_state == "RUNNER_ON_FIRST":
            self.gamestate.move_runner("1ST", "2ND")

        self.gamestate.move_runner('HOME', '1ST', self.batter)

        outcome_description = self.text_manager.get_event_description("WALK", base_state)
        formatted_description = outcome_description.format(
            pitcher=self.pitcher.last_name.upper(), 
            batter=self.batter.last_name.upper()
            )
        self.outcomes.append(formatted_description)
        
        self.batter.record_at_bat(walk=True)
        self.pitcher.record_outcome(walk=True, runs=runs_scored, earned_runs=runs_scored)

        DisplayManager.display_outcome_text(self.outcomes, display_enabled=DISPLAY_TEXT)
        return hits_hit, runs_scored, outs_recorded, walk_off
    
class HitByPitch:
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
        outs_recorded = 0
        walk_off = False

        base_state = self.gamestate.get_base_state()  # Get the current base state

        if base_state == "BASES_LOADED":
            self.gamestate.move_runner('3RD', 'HOME')
            self.gamestate.move_runner("2ND", "3RD")
            self.gamestate.move_runner("1ST", "2ND")
            runs_scored += 1

        elif base_state == "FIRST_AND_SECOND":
            self.gamestate.move_runner("2ND", "3RD")
            self.gamestate.move_runner("1ST", "2ND")

        elif base_state == "FIRST_AND_THIRD":
            self.gamestate.move_runner("1ST", "2ND")

        elif base_state == "RUNNER_ON_FIRST":
            self.gamestate.move_runner("1ST", "2ND")

        self.gamestate.move_runner('HOME', '1ST', self.batter)

        outcome_description = self.text_manager.get_event_description("HBP", base_state)
        formatted_description = outcome_description.format(
            pitcher=self.pitcher.last_name.upper(), 
            batter=self.batter.last_name.upper()
            )
        self.outcomes.append(formatted_description)

        self.batter.record_at_bat(hit_by_pitch=True)
        self.pitcher.record_outcome(hit_by_pitch=True, runs=runs_scored, earned_runs=runs_scored)

        DisplayManager.display_outcome_text(self.outcomes, display_enabled=DISPLAY_TEXT)
        return hits_hit, runs_scored, outs_recorded, walk_off
