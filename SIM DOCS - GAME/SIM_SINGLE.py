import pandas as pd
import numpy as np
import sys
import os
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

class Single:
    def __init__(self, gamestate, league, pitcher, batter, runners=None, fielding_team=None, **kwargs):
        self.gamestate = gamestate  # ✅ Game state access
        self.league = league  # ✅ League-wide stats access
        self.pitcher = pitcher  # ✅ Pitcher involved in the play
        self.batter = batter  # ✅ Batter involved in the play
        self.runners = self.gamestate.set_runners_on_base() if runners is None else runners  # ✅ Get base runners
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
        
        base_state = self.gamestate.get_base_state()
        batter_side = get_batter_side(self.batter, self.pitcher)
        hit_direction, batted_ball_type, hit_location = self.hit_information.determine_hit_information("SINGLE", batter_side)
        runner_probs  = self.scenario_manager.get_probabilities("SINGLE", base_state, batter_side, batted_ball_type, hit_direction, hit_location)

        self.outcomes.append(f"{self.batter.last_name.upper()} HITS A SINGLE AND TAKES FIRST BASE!")

        if base_state == 'BASES_LOADED':
            rand_val = np.random.random()
            score_prob = adjust_probability(runner_probs.get("R2_scr", 0), self.runners.get('2ND').speed)
            out_prob = rev_adjust_probability(runner_probs.get("R2_out", 0), self.runners.get('2ND').speed)

            if rand_val < score_prob:
                self.gamestate.move_runner('3RD', 'HOME')
                self.gamestate.move_runner('2ND', 'HOME')
                self.gamestate.move_runner('1ST', '2ND')
                runs_scored += 2
                self.outcomes.append("RUNNERS ON 3RD & 2ND WILL COME AROUND AND BOTH SCORE!")

            elif rand_val < (score_prob + out_prob):
                self.gamestate.move_runner('3RD', 'HOME')
                self.gamestate.move_runner('2ND', 'OUT')
                self.gamestate.move_runner('1ST', '2ND')
                runs_scored += 1
                outs_recorded += 1
                self.outcomes.append("RUNNER ON 3RD SCORES, RUNNER ON 2ND IS THROWN OUT AT HOME, RUNNER ON 1ST MOVES TO 2ND!")
            
            else:
                self.gamestate.move_runner('3RD', 'HOME')
                self.gamestate.move_runner('2ND', '3RD')
                self.gamestate.move_runner('1ST', '2ND')
                runs_scored += 1 
                self.outcomes.append("RUNNER ON 3RD SCORES, RUNNERS MOVE UP ONE BASE!")

        elif base_state == 'SECOND_AND_THIRD':
            rand_val = np.random.random()
            score_prob = adjust_probability(runner_probs.get("R2_scr", 0), self.runners.get('2ND').speed)
            out_prob = rev_adjust_probability(runner_probs.get("R2_out", 0), self.runners.get('2ND').speed)

            if rand_val < score_prob:
                self.gamestate.move_runner('3RD', 'HOME')
                self.gamestate.move_runner('2ND', 'HOME')
                runs_scored += 2
                self.outcomes.append("RUNNERS ON 3RD & 2ND WILL BOTH SCORE! 2 RUNS SCORED!")

            elif rand_val < (score_prob + out_prob):
                self.gamestate.move_runner('3RD', 'HOME')
                self.gamestate.move_runner('2ND', 'OUT')
                runs_scored += 1
                self.outcomes.append("RUNNER ON 3RD SCORES! 1 RUN SCORED! RUNNER ON 2ND IS THROWN OUT AT HOME!")

            else:
                self.gamestate.move_runner('3RD', 'HOME')
                self.gamestate.move_runner('2ND', '3RD')
                runs_scored += 1
                self.outcomes.append("RUNNER ON 3RD SCORES! 1 RUN SCORED! RUNNER ON 2ND ADVANCES TO 3RD!")

        elif base_state == 'FIRST_AND_THIRD':
            rand_val = np.random.random()
            advance_prob = adjust_probability(runner_probs.get("R1_adv", 0), self.runners.get('1ST').speed)
            out_prob = rev_adjust_probability(runner_probs.get("R1_out", 0), self.runners.get('1ST').speed)

            if rand_val < advance_prob:
                self.gamestate.move_runner('3RD', 'HOME')
                self.gamestate.move_runner('1ST', '3RD')
                runs_scored += 1
                self.outcomes.append("RUNNER ON 3RD WILL COME HOME TO SCORE! RUNNER ON 1ST ADVANCES TO 3RD!")

            elif rand_val < (advance_prob + out_prob):
                self.gamestate.move_runner('3RD', 'HOME')
                self.gamestate.move_runner('1ST', 'OUT')
                runs_scored += 1
                outs_recorded += 1
                self.outcomes.append("RUNNER ON 3RD WILL COME HOME TO SCORE! RUNNER ON 1ST IS THROWN OUT TRYING TO ADVANCE TO 3RD!")
            
            else:
                self.gamestate.move_runner('3RD', 'HOME')
                self.gamestate.move_runner('1ST', '2ND')
                runs_scored += 1
                self.outcomes.append("RUNNER ON 3RD WILL COME HOME TO SCORE! RUNNER ON 1ST ADVANCES TO 2ND!")

        elif base_state == 'FIRST_AND_SECOND':
            rand_val = np.random.random()

            score_prob = adjust_probability(runner_probs.get("R2_scr", 0), self.runners.get('2ND').speed)
            out_prob = rev_adjust_probability(runner_probs.get("R2_out", 0), self.runners.get('2ND').speed)

            if rand_val < score_prob:
                self.gamestate.move_runner('2ND', 'HOME')
                self.gamestate.move_runner('1ST', '2ND')
                runs_scored += 1
                self.outcomes.append("RUNNER ON 2ND SCORES! 1 RUN SCORED!")

            elif rand_val < (score_prob + out_prob):
                self.gamestate.move_runner('2ND', 'OUT')
                self.gamestate.move_runner('1ST', '2ND')
                outs_recorded += 1
                self.outcomes.append("RUNNER ON 2ND IS THROWN OUT AT HOME!")

            else:
                self.gamestate.move_runner('2ND', '3RD')
                self.gamestate.move_runner('1ST', '2ND')
                self.outcomes.append("RUNNERS MOVE UP 90FT!")

        elif base_state == 'RUNNER_ON_THIRD':
            self.gamestate.move_runner('3RD', 'HOME')
            self.outcomes.append('BASE HIT! RUNNER ON THIRD WILL COME HOME TO SCORE! 1 RUN SCORED!')

        elif base_state == 'RUNNER_ON_SECOND':
            rand_val = np.random.random()
            score_prob = adjust_probability(runner_probs.get("R2_scr", 0), self.runners.get('2ND').speed)
            out_prob = rev_adjust_probability(runner_probs.get("R2_out", 0), self.runners.get('2ND').speed)

            if rand_val < score_prob:
                self.gamestate.move_runner('2ND', 'HOME')
                runs_scored += 1
                self.outcomes.append("RUNNER ON 2ND SCORES! 1 RUN SCORED!")

            elif rand_val < (score_prob + out_prob):
                self.gamestate.move_runner('2ND', 'OUT')
                outs_recorded += 1
                self.outcomes.append("RUNNER ON 2ND IS THROWN OUT AT HOME!")

            else:
                self.gamestate.move_runner('2ND', '3RD')
                self.outcomes.append("RUNNER ON 2ND ADVANCES TO 3RD!")

        elif base_state == 'RUNNER_ON_FIRST':
            rand_val = np.random.random()
            advance_prob = adjust_probability(runner_probs.get("R1_adv", 0), self.runners.get('1ST').speed)
            out_prob = rev_adjust_probability(runner_probs.get("R1_out", 0), self.runners.get('1ST').speed)

            if rand_val < advance_prob:
                self.gamestate.move_runner('1ST', '3RD')
                self.outcomes.append("RUNNER ON 1ST ADVANCES TO 3RD!")

            elif rand_val < (advance_prob + out_prob):
                self.gamestate.move_runner('1ST', 'OUT')
                outs_recorded += 1
                self.outcomes.append("RUNNER ON 1ST OUT TRYING TO ADVANCE TO 3RD!")

            else:
                self.gamestate.move_runner('1ST', '2ND')
                self.outcomes.append("RUNNER ON 1ST ADVANCES TO 2ND!")

        self.gamestate.move_runner('HOME', '1ST', self.batter)

        self.batter.record_at_bat(hit_type="single")
        self.pitcher.record_outcome(hit_type="single", runs=runs_scored, earned_runs=runs_scored, outs=outs_recorded)

        DisplayManager.display_outcome_text(self.outcomes, display_enabled=DISPLAY_TEXT)
        return hits_hit, runs_scored, outs_recorded, walk_off

