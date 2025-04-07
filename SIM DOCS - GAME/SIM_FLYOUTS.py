from SIM_CORE import *
from SIM_SETTINGS import *
from SIM_UTILS import *
from FILE_PATHS import *
from SIM_DISPLAY_MANAGER import *
from SIM_HIT_RESULT import *
from SIM_TEXT_MANAGER import *
from SIM_SCENARIO_MANAGER import *
import os, sys, time, string, pandas as pd, numpy as np

class Flyout:
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

        base_state = self.gamestate.get_base_state()
        batter_side = get_batter_side(self.batter, self.pitcher)
        hit_direction, batted_ball_type, hit_location = self.hit_information.determine_hit_information("FLYOUT", batter_side)

        self.outcomes.append("LIFTS AN EASY FLYBALL, CAUGHT FOR A ROUTINE OUT!")

        if base_state == 'RUNNER_ON_THIRD' and self.gamestate.outs < 2:
            rand_val = np.random.random()
            tag_chance = adjust_probability(0.80, self.runners.get('3RD').speed)
            throw_out_chance = adjust_probability(0.03, self.runners.get('3RD').speed)

            if rand_val < tag_chance:
                self.gamestate.move_runner('3RD', 'HOME')
                runs_scored += 1
                self.outcomes.append("SAC FLY! RUNNER ON 3RD TAGS AND SCORES! 1 RUN SCORED")
            elif rand_val < tag_chance + throw_out_chance:
                self.gamestate.move_runner('3RD', 'OUT')
                outs_recorded += 1
                self.outcomes.append("RUNNER ON 3RD IS THROWN OUT AT HOME! DOUBLE PLAY!")
            else:
                self.outcomes.append("RUNNER HELD AT 3RD!")

        elif base_state == 'RUNNER_ON_SECOND' and self.gamestate.outs < 2:
            rand_val = np.random.random()
            tag_chance = adjust_probability(0.35, self.runners.get('2ND').speed)
            throw_out_chance = adjust_probability(0.02, self.runners.get('2ND').speed)

            if rand_val < tag_chance:
                self.gamestate.move_runner('2ND', '3RD')
                self.outcomes.append("RUNNER TAGS AND ADVANCES TO 3RD!")
            elif rand_val < tag_chance + throw_out_chance:
                self.gamestate.move_runner('2ND', 'OUT')
                outs_recorded += 1
                self.outcomes.append("RUNNER TAGS BUT IS THROWN OUT TRYING TO ADVANCE TO 3RD!")
            else:
                self.outcomes.append("RUNNER HOLDS AT 2ND!")

        elif base_state == 'FIRST_AND_SECOND' and self.gamestate.outs < 2:
            rand_val = np.random.random()
            tag_chance = adjust_probability(0.35, self.runners.get('2ND').speed)
            throw_out_chance = adjust_probability(0.02, self.runners.get('2ND').speed)

            if rand_val < tag_chance:
                self.gamestate.move_runner('2ND', '3RD')
                self.outcomes.append("RUNNER TAGS AND ADVANCES TO 3RD!")
            elif rand_val < tag_chance + throw_out_chance:
                self.gamestate.move_runner('2ND', 'OUT')
                outs_recorded += 1
                self.outcomes.append("RUNNER TAGS BUT IS THROWN OUT TRYING TO ADVANCE TO 3RD!")
            else:
                self.outcomes.append("RUNNER HOLDS AT 2ND!")

        elif base_state == 'FIRST_AND_THIRD' and self.gamestate.outs < 2:
            rand_val = np.random.random()
            tag_chance = adjust_probability(0.80, self.runners.get('3RD').speed)
            throw_out_chance = adjust_probability(0.03, self.runners.get('3RD').speed)

            if rand_val < tag_chance:
                self.gamestate.move_runner('3RD', 'HOME')
                runs_scored += 1
                self.outcomes.append("RUNNER TAGS AND ADVANCES TO HOME! 1 RUN SCORES!")
            elif rand_val < tag_chance + throw_out_chance:
                self.gamestate.move_runner('3RD', 'OUT')
                outs_recorded += 1
                self.outcomes.append("RUNNER TAGS BUT IS THROWN OUT TRYING TO ADVANCE TO HOME!")
            else:
                self.outcomes.append("RUNNER HOLDS AT 3RD!")

        elif base_state == 'SECOND_AND_THIRD' and self.gamestate.outs < 2:
            rand_val_third = np.random.random()
            tag_chance_third = adjust_probability(0.80, self.runners.get('3RD').speed)
            throw_out_chance_third = adjust_probability(0.03, self.runners.get('3RD').speed)

            if rand_val_third < tag_chance_third:
                self.gamestate.move_runner('3RD', 'HOME')
                runs_scored += 1
                self.outcomes.append("RUNNER ON 3RD TAGS AND CROSSES THE PLATE! 1 RUN SCORES!")
            elif rand_val_third < tag_chance_third + throw_out_chance_third:
                self.gamestate.move_runner('3RD', 'OUT')
                outs_recorded += 1
                self.outcomes.append("RUNNER ON 3RD TAGS BUT IS THROWN OUT AT HOME!")
            else:
                self.outcomes.append("RUNNER HELD AT 3RD!")

            if self.runners.get('2ND'):
                rand_val_second = np.random.random()
                tag_chance_second = adjust_probability(0.55, self.runners.get('2ND').speed)
                throw_out_chance_second = adjust_probability(0.01, self.runners.get('2ND').speed)

                if rand_val_third < tag_chance_third:  # Only proceed if runner on 3rd tagged up
                    if rand_val_second < tag_chance_second:
                        self.gamestate.move_runner('2ND', '3RD')
                        self.outcomes.append("RUNNER ON 2ND TAGS AND ADVANCES TO 3RD!")
                    elif rand_val_second < tag_chance_second + throw_out_chance_second:
                        self.gamestate.move_runner('2ND', 'OUT')
                        outs_recorded += 1
                        self.outcomes.append("RUNNER ON 2ND TAGS BUT IS THROWN OUT TRYING TO ADVANCE!")
                    else:
                        self.outcomes.append("RUNNER HOLDS AT 2ND!")
                else:
                    self.outcomes.append("RUNNER HOLDS AT 2ND!")


        elif base_state == 'BASES_LOADED' and self.gamestate.outs < 2:
            rand_val_third = np.random.random()
            tag_chance_third = adjust_probability(0.80, self.runners.get('3RD').speed)
            throw_out_chance_third = adjust_probability(0.03, self.runners.get('3RD').speed)

            if rand_val_third < tag_chance_third:
                self.gamestate.move_runner('3RD', 'HOME')
                runs_scored += 1
                self.outcomes.append("SAC FLY! RUNNER SCORES FROM 3RD! 1 RUN SCORED!")
                
                # Handle runner on 2ND only if runner on 3RD tags
                rand_val_second = np.random.random()
                tag_chance_second = adjust_probability(0.55, self.runners.get('2ND').speed)
                throw_out_chance_second = adjust_probability(0.01, self.runners.get('2ND').speed)

                if rand_val_second < tag_chance_second:
                    self.gamestate.move_runner('2ND', '3RD')
                    self.outcomes.append("RUNNER ON 2ND TAGS AND ADVANCES TO 3RD!")
                elif rand_val_second < tag_chance_second + throw_out_chance_second:
                    self.gamestate.move_runner('2ND', 'OUT')
                    outs_recorded += 1
                    self.outcomes.append("RUNNER ON 2ND TAGS BUT IS THROWN OUT TRYING TO ADVANCE!")
                else:
                    self.outcomes.append("RUNNER HOLDS AT 2ND!")

            elif rand_val_third < tag_chance_third + throw_out_chance_third:
                self.gamestate.move_runner('3RD', 'OUT')
                outs_recorded += 1
                self.outcomes.append("\nRUNNER ON 3RD TAGS BUT THROWN OUT AT HOME! DOUBLE PLAY!")
            else:
                self.outcomes.append("\nRUNNER ON 3RD HOLDS!")

            if self.runners.get('1ST'):
                if not self.runners.get('2ND'):  # Runner on 2nd didn't advance or was thrown out
                    rand_val_first = np.random.random()
                    advance_chance_first = adjust_probability(0.08, self.runners.get('1ST').speed)
                    throw_out_chance_first = rev_adjust_probability(0.01, self.runners.get('1ST').speed)

                    if rand_val_first < advance_chance_first:
                        self.gamestate.move_runner('1ST', '2ND')
                        self.outcomes.append("\nRUNNER ON 1ST ADVANCES TO 2ND!")
                    elif rand_val_first < advance_chance_first + throw_out_chance_first:
                        self.gamestate.move_runner('1ST', 'OUT')
                        outs_recorded += 1
                        self.outcomes.append("\nRUNNER ON 1ST IS THROWN OUT TRYING TO ADVANCE TO 2ND!")
                    else:
                        self.outcomes.append("\nRUNNER ON 1ST HOLDS!")
                else:  # If runner on 2ND advanced or held
                    self.gamestate.move_runner('1ST', '2ND')
                    self.outcomes.append("\nRUNNER ON 1ST ADVANCES TO 2ND!")

        outs_recorded += 1
        self.gamestate.move_runner('HOME', 'OUT', self.batter)

        self.batter.record_at_bat()
        self.pitcher.record_outcome(hit_type="flyout", runs=runs_scored, earned_runs=runs_scored, outs=outs_recorded)
        
        DisplayManager.display_outcome_text(self.outcomes, display_enabled=DISPLAY_TEXT)
        return hits_hit, runs_scored, outs_recorded, walk_off