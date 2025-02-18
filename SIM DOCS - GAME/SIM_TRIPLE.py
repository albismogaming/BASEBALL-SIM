import pandas as pd
import numpy as np
from SIM_FUNCTIONS import *
from SIM_SCOREBOARD import *
from SIM_TEAM import *
from SIM_SETTINGS import *
from SIM_GAMESTATE import *
from SIM_SCENARIO_MANAGER import *
from SIM_UTILS import *
from SIM_DISPLAY_MANAGER import *
from SIM_TEXT_MANAGER import *
from SIM_HIT_RESULT import *

class Triple:
    def __init__(self, gamestate, league, pitcher, batter, runners=None, fielding_team=None, **kwargs):
        self.gamestate = gamestate  # ✅ Game state access
        self.league = league  # ✅ League-wide stats access
        self.pitcher = pitcher  # ✅ Pitcher involved in the play
        self.batter = batter  # ✅ Batter involved in the play
        self.runners = self.gamestate.set_runners_on_base() if runners is None else runners  # ✅ Get current base runners
        self.fielding_team = fielding_team  # ✅ Fielding team (if applicable)
        self.outcomes = []  # ✅ Stores event text descriptions
        self.text_manager = TextManager()  # ✅ Manages outcome descriptions
        self.scenario_manager = ScenarioManager()
        self.hit_information = HitInformation(gamestate, league, pitcher, batter, None)  # ✅ Handles hit data
        self.kwargs = kwargs  # ✅ Capture additional parameters if needed

    def execute(self):
        hits_hit = 1
        runs_scored = 0
        outs_recorded = 0
        walk_off = False
        
        # Determine the effective batter side (handling switch hitters)
        batter_side = get_batter_side(self.batter, self.pitcher)
        base_state = self.gamestate.get_base_state()
        hit_direction, batted_ball_type, hit_location = self.hit_information.determine_hit_information("TRIPLE", batter_side)
        runner_probs  = self.scenario_manager.get_probabilities("TRIPLE", base_state, batter_side, batted_ball_type, hit_direction, hit_location)

        self.outcomes.append(f"{self.batter.last_name.upper()} RACES AROUND THE BASES AND SLIDES INTO 3RD!")
        
        if  base_state == 'BASES_LOADED':
            rand_val = np.random.random()
            score_prob = adjust_probability(runner_probs.get("R1_scr", 0), self.runners.get('1ST').speed)

            if rand_val < score_prob:
                self.gamestate.move_runner('3RD', 'HOME')
                self.gamestate.move_runner('2ND', 'HOME')
                self.gamestate.move_runner('1ST', 'HOME')
                runs_scored += 3
                self.outcomes.append("BASES CLEARNING TRIPLE! 3 RUNS SCORED!")

            else:
                self.gamestate.move_runner('3RD', 'HOME')
                self.gamestate.move_runner('2ND', 'HOME')
                self.gamestate.move_runner('1ST', 'OUT')
                runs_scored += 2
                outs_recorded += 1
                self.outcomes.append("RUNNER ON 1ST IS THROWN OUT AT HOME! 2 RUNS SCORED!")

        elif base_state == 'SECOND_AND_THIRD':
            self.gamestate.move_runner('3RD', 'HOME')
            self.gamestate.move_runner('2ND', 'HOME')
            runs_scored += 2
            self.outcomes.append("RUNNERS ON 2ND & 3RD BOTH SCORE!")

        elif base_state == 'FIRST_AND_THIRD':
            rand_val = np.random.random()
            score_prob = adjust_probability(runner_probs.get("R1_scr", 0), self.runners.get('1ST').speed)

            if rand_val < score_prob:
                self.gamestate.move_runner('3RD', 'HOME')
                self.gamestate.move_runner('1ST', 'HOME')
                runs_scored += 2
                self.outcomes.append("RUNNERS ON 1ST & 3RD BOTH SCORE! 2 RUNS SCORED!")

            else:
                self.gamestate.move_runner('3RD', 'HOME')
                self.gamestate.move_runner('1ST', 'OUT')
                runs_scored += 1
                outs_recorded += 1
                self.outcomes.append("RUNNER ON 3RD WILL SCORE! RUNNER ON 1ST IS THROWN OUT AT HOME!")

        elif base_state == 'FIRST_AND_SECOND':
            rand_val = np.random.random()
            score_prob = adjust_probability(runner_probs.get("R1_scr", 0), self.runners.get('1ST').speed)
            
            if rand_val < score_prob:
                self.gamestate.move_runner('2ND', 'HOME')
                self.gamestate.move_runner('1ST', 'HOME')
                runs_scored += 2
                self.outcomes.append("RUNNER ON 2ND & 1ST BOTH SCORE! 2 RUNS SCORED!")
            else:
                self.gamestate.move_runner('2ND', 'HOME')
                self.gamestate.move_runner('1ST', 'OUT')
                runs_scored += 1
                outs_recorded += 1                
                self.outcomes.append("RUNNER ON 2ND WILL SCORE! RUNNER ON 1ST IS THROWN OUT AT HOME!")

        elif base_state == 'RUNNER_ON_THIRD':
            self.gamestate.move_runner('3RD', 'HOME')
            runs_scored += 1
            self.outcomes.append("RUNNER ON 3RD WILL SCORE! 1 RUN SCORED!")

        elif base_state == 'RUNNER_ON_SECOND':
            self.gamestate.move_runner('2ND', 'HOME')
            runs_scored += 1
            self.outcomes.append("RUNNER ON 2ND WILL SCORE! 1 RUN SCORED!")

        elif base_state == 'RUNNER_ON_FIRST':
            rand_val = np.random.random()
            score_prob = adjust_probability(runner_probs.get("R1_scr", 0), self.runners.get('1ST').speed)

            if rand_val < score_prob:
                self.gamestate.move_runner('1ST', 'HOME')
                runs_scored += 1
                self.outcomes.append("RUNNER ON 1ST WILL SCORE! 1 RUN SCORED!")
            else:
                self.gamestate.move_runner('1ST', 'OUT')
                outs_recorded += 1
                self.outcomes.append("RUNNER ON 1ST IS THROWN OUT AT HOME!")

        self.gamestate.move_runner('HOME', '3RD', self.batter)

        self.batter.record_at_bat(hit_type="triple")
        self.pitcher.record_outcome(hit_type="triple", runs=runs_scored, earned_runs=runs_scored, outs=outs_recorded)

        DisplayManager.display_outcome_text(self.outcomes, display_enabled=DISPLAY_TEXT)
        return hits_hit, runs_scored, outs_recorded, walk_off

