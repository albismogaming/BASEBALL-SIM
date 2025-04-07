from SIM_CORE import *
from SIM_SETTINGS import *
from SIM_UTILS import *
from FILE_PATHS import *
from SIM_DISPLAY_MANAGER import *
from SIM_HIT_RESULT import *
from SIM_TEXT_MANAGER import *
from SIM_SCENARIO_MANAGER import *
import os, sys, time, string, pandas as pd, numpy as np

class Double:
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
        
        base_state = self.gamestate.get_base_state()
        batter_side = get_batter_side(self.batter, self.pitcher)
        hit_direction, batted_ball_type, hit_location = self.hit_information.determine_hit_information("DOUBLE", batter_side)
        runner_probs  = self.scenario_manager.get_probabilities("SINGLE", base_state, batter_side, batted_ball_type, hit_direction, hit_location)

        self.outcomes.append(f"{self.batter.last_name.upper()} HITS A DOUBLE AND JOGS INTO 2ND!")

        if base_state == 'BASES_LOADED':
            rand_val = np.random.random()

            score_prob = adjust_probability(runner_probs.get("R1_scr", 0), self.runners.get('1ST').speed)
            out_prob = rev_adjust_probability(runner_probs.get("R1_out", 0), self.runners.get('1ST').speed)

            if rand_val < score_prob:
                self.outcomes.append("RUNNER ON 1ST HUSTLES HOME AND SCORES! 3 RUNS SCORED!")
                self.gamestate.move_runner('3RD', 'HOME')
                self.gamestate.move_runner('2ND', 'HOME')
                self.gamestate.move_runner('1ST', 'HOME')
                runs_scored += 3

            elif rand_val < score_prob + out_prob:
                self.gamestate.move_runner('3RD', 'HOME')
                self.gamestate.move_runner('2ND', 'HOME')
                self.gamestate.move_runner('1ST', 'OUT')
                runs_scored += 2
                outs_recorded += 1
                self.outcomes.append("RUNNER ON 1ST IS THROWN OUT AT HOME! 2 RUNS WILL SCORE!")
            
            else:
                self.gamestate.move_runner('3RD', 'HOME')
                self.gamestate.move_runner('2ND', 'HOME')              
                self.gamestate.move_runner('1ST', '3RD')
                runs_scored += 2
                self.outcomes.append("RUNNER ON 1ST ADVANCES TO 3RD! 2 RUNS WILL COME HOME TO SCORE!")

        elif base_state == 'SECOND_AND_THIRD':
            self.gamestate.move_runner('3RD', 'HOME')
            self.gamestate.move_runner('2ND', 'HOME')
            runs_scored += 2
            self.outcomes.append("RUNNER ON 3RD & 2ND BOTH SCORE!")

        elif base_state == 'FIRST_AND_THIRD':
            rand_val = np.random.random()
            score_prob = adjust_probability(runner_probs.get("R1_scr", 0), self.runners.get('1ST').speed)
            out_prob = rev_adjust_probability(runner_probs.get("R1_out", 0), self.runners.get('1ST').speed)

            if rand_val < score_prob:
                self.outcomes.append("RUNNER ON 3RD & 1ST BOTH SCORE! 2 RUNS SCORED!")
                self.gamestate.move_runner('3RD', 'HOME')
                self.gamestate.move_runner('1ST', 'HOME')
                runs_scored += 2

            elif rand_val < score_prob + out_prob:
                self.gamestate.move_runner('3RD', 'HOME')
                self.gamestate.move_runner('1ST', 'OUT')
                runs_scored += 1
                outs_recorded += 1
                self.outcomes.append("RUNNER ON 3RD WILL TROT IN AND SCORE! RUNNER ON 1ST IS THROWN OUT AT HOME!")

            else:
                self.gamestate.move_runner('3RD', 'HOME')
                self.gamestate.move_runner('1ST', '3RD')
                runs_scored += 1
                self.outcomes.append("RUNNER ON 3RD WILL SCORE! RUNNER ON 1ST ADVANCES TO 3RD!")

        elif base_state == 'FIRST_AND_SECOND':
            rand_val = np.random.random()
            score_prob = adjust_probability(runner_probs.get("R1_scr", 0), self.runners.get('1ST').speed)
            out_prob = rev_adjust_probability(runner_probs.get("R1_out", 0), self.runners.get('1ST').speed)

            if rand_val < score_prob:
                self.gamestate.move_runner('2ND', 'HOME')
                self.gamestate.move_runner('1ST', 'HOME')
                runs_scored += 2
                self.outcomes.append("RUNNERS ON 1ST & 2ND SCORE! 2 RUNS ARE IN!")

            elif rand_val < score_prob + out_prob:
                self.gamestate.move_runner('2ND', 'HOME')
                self.gamestate.move_runner('1ST', 'OUT')
                runs_scored += 1
                outs_recorded += 1
                self.outcomes.append("RUNNER ON 1ST IS THROWN OUT AT HOME!")
                
            else:
                self.gamestate.move_runner('2ND', 'HOME')
                self.gamestate.move_runner('1ST', '3RD')
                runs_scored += 1
                self.outcomes.append("RUNNER ON 1ST ADVANCES TO 3RD!")

        elif base_state == 'RUNNER_ON_THIRD':
            self.gamestate.move_runner('3RD', 'HOME')
            runs_scored += 1
            self.outcomes.append("RUNNER ON 3RD SCORES EASILY!")

        elif base_state == 'RUNNER_ON_SECOND':
            self.gamestate.move_runner('2ND', 'HOME')
            runs_scored += 1
            self.outcomes.append("RUNNER ON 2ND SCORES WITH NO CONTEST!")

        elif base_state == 'RUNNER_ON_FIRST':
            rand_val = np.random.random()

            score_prob = adjust_probability(runner_probs.get("R1_scr", 0), self.runners.get('1ST').speed)
            out_prob = rev_adjust_probability(runner_probs.get("R1_out", 0), self.runners.get('1ST').speed)

            if rand_val < score_prob:
                self.gamestate.move_runner('1ST', 'HOME')
                runs_scored += 1
                self.outcomes.append("RUNNER ON 1ST SCORES!")
                
            elif rand_val < score_prob + out_prob:
                self.gamestate.move_runner('1ST', '3RD')
                self.outcomes.append("RUNNER ON 1ST ADVANCES TO 3RD!")
            else:
                self.gamestate.move_runner('1ST', 'OUT')
                outs_recorded += 1
                self.outcomes.append("RUNNER ON 1ST IS THROWN OUT AT HOME!")

        self.gamestate.move_runner('HOME', '2ND', self.batter)

        self.batter.record_at_bat(hit_type="double")
        self.pitcher.record_outcome(hit_type="double", runs=runs_scored, earned_runs=runs_scored, outs=outs_recorded)

        DisplayManager.display_outcome_text(self.outcomes, display_enabled=DISPLAY_TEXT)
        return hits_hit, runs_scored, outs_recorded, walk_off
