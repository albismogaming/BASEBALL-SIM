from SIM_CORE import *
from SIM_SETTINGS import *
from SIM_UTILS import *
from FILE_PATHS import *
from SIM_DISPLAY_MANAGER import *
from SIM_HIT_RESULT import *
from SIM_TEXT_MANAGER import *
from SIM_SCENARIO_MANAGER import *
import os, sys, time, string, pandas as pd, numpy as np

class Groundout:
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
        hits_hit = 0
        runs_scored = 0
        outs_recorded = 0
        walk_off = False
        
        base_state = self.gamestate.get_base_state()
        batter_side = get_batter_side(self.batter, self.pitcher)
        hit_direction, batted_ball_type, hit_location = self.hit_information.determine_hit_information("GROUNDOUT", batter_side)
        runner_probs  = self.scenario_manager.get_probabilities("GROUNDOUT", base_state, batter_side, batted_ball_type, hit_direction, hit_location)

        self.outcomes.append(f"{self.batter.last_name.upper()} CHOPS ONE ON THE GROUND!")

        # Scenario: Bases loaded with less than two outs
        if base_state == "BASES_LOADED" and self.gamestate.outs < 2:
            rand_val = np.random.random()
            team_trailing_by_two = team_trailing_by_two = self.gamestate.is_team_trailing_by_two()
            double_play_chance = rev_adjust_probability(0.52, self.runners.get('1ST').speed)

            if rand_val < double_play_chance:
                outs_recorded += 2
                if self.gamestate.current_inning >= 8 and team_trailing_by_two:
                    double_play_scenarios = ["home_first", "home_third"]
                    double_play_weights = [0.80, 0.20]
                    double_play_scenario = np.random.choice(double_play_scenarios, p=double_play_weights)
                else:
                    double_play_scenarios = ["home_first", "home_third", "third_first", "second_first", "third_second"]
                    double_play_weights = [0.20, 0.02, 0.04, 0.72, 0.02]
                    double_play_scenario = np.random.choice(double_play_scenarios, p=double_play_weights)

                if double_play_scenario == "home_first":
                    if self.gamestate.outs == 1:
                        self.gamestate.move_runner('3RD', 'OUT')
                        self.gamestate.move_runner('2ND', '3RD')
                        self.gamestate.move_runner('1ST', '2ND')
                        self.gamestate.move_runner('HOME', 'OUT', self.batter)
                        self.outcomes.append("RUNNER OUT AT HOME & 1ST! DOUBLE PLAY! (X-2-3) THAT WILL END THE INNING!")
                    else:
                        self.gamestate.move_runner('3RD', 'OUT')
                        self.gamestate.move_runner('2ND', '3RD')
                        self.gamestate.move_runner('1ST', '2ND')
                        self.gamestate.move_runner('HOME', 'OUT', self.batter)
                        self.outcomes.append("RUNNER OUT AT HOME & 1ST! DOUBLE PLAY! (X-2-3)")                      

                elif double_play_scenario == "home_third":
                    if self.gamestate.outs == 1:
                        self.gamestate.move_runner('3RD', 'OUT')
                        self.gamestate.move_runner('2ND', 'OUT')
                        self.gamestate.move_runner('1ST', '2ND')
                        self.gamestate.move_batter(self.batter, '1ST') 
                        self.outcomes.append("RUNNER OUT AT HOME & 3RD! DOUBLE PLAY! (X-2-5) THAT WILL END THE INNING!")
                    else:
                        self.gamestate.move_runner('3RD', 'OUT')
                        self.gamestate.move_runner('2ND', 'OUT')
                        self.gamestate.move_runner('1ST', '2ND')
                        self.gamestate.move_runner('HOME', '1ST', self.batter)
                        self.outcomes.append("RUNNER OUT AT HOME & 3RD! DOUBLE PLAY! (X-2-5) NO RUNS SCORE!")

                elif double_play_scenario == "third_first":
                    if self.gamestate.outs == 1:
                        self.gamestate.move_runner('3RD', 'HOME')
                        self.gamestate.move_runner('2ND', 'OUT')
                        self.gamestate.move_runner('1ST', '2ND')
                        self.gamestate.move_runner('HOME', 'OUT', self.batter)
                        self.outcomes.append("RUNNER OUT AT 3RD & 1ST! DOUBLE PLAY! (X-5-3) THAT WILL END THE INNING!")
                    else:
                        self.gamestate.move_runner('3RD', 'HOME')
                        self.gamestate.move_runner('2ND', 'OUT')
                        self.gamestate.move_runner('1ST', '2ND')
                        self.gamestate.move_runner('HOME', 'OUT', self.batter)
                        runs_scored += 1
                        self.outcomes.append("RUNNER OUT AT 3RD & 1ST! DOUBLE PLAY! (X-5-3) 1 RUN SCORES!")

                elif double_play_scenario == "second_first":
                    if self.gamestate.outs == 1:
                        self.gamestate.move_runner('3RD', 'HOME')
                        self.gamestate.move_runner('2ND', '3RD')
                        self.gamestate.move_runner('1ST', 'OUT')
                        self.gamestate.move_runner('HOME', 'OUT', self.batter)
                        self.outcomes.append("RUNNER OUT AT 2ND & 1ST! DOUBLE PLAY! (X-4-3) THAT WILL END THE INNING!")
                    else:
                        self.gamestate.move_runner('3RD', 'HOME')
                        self.gamestate.move_runner('2ND', '3RD')
                        self.gamestate.move_runner('1ST', 'OUT')
                        self.gamestate.move_runner('HOME', 'OUT', self.batter)
                        runs_scored += 1
                        self.outcomes.append("RUNNER OUT AT 2ND & 1ST! DOUBLE PLAY! (X-4-3) 1 RUN SCORES!")

                elif double_play_scenario == "third_second":
                    if self.gamestate.outs == 1:
                        self.gamestate.move_runner('3RD', 'HOME')
                        self.gamestate.move_runner('2ND', 'OUT')
                        self.gamestate.move_runner('1ST', 'OUT')
                        self.gamestate.move_runner('HOME', '1ST', self.batter)
                        self.outcomes.append("RUNNER OUT AT 3RD & 2ND! DOUBLE PLAY! (X-5-4) THAT WILL END THE INNING!")
                    else:
                        self.gamestate.move_runner('3RD', 'HOME')
                        self.gamestate.move_runner('2ND', 'OUT')
                        self.gamestate.move_runner('1ST', 'OUT')
                        self.gamestate.move_runner('HOME', '1ST', self.batter)
                        runs_scored += 1
                        self.outcomes.append("RUNNER OUT AT 3RD & 2ND! DOUBLE PLAY! (X-5-4) 1 RUN SCORES!")

            else:
                outs_recorded += 1
                if self.gamestate.current_inning >= 8 and team_trailing_by_two:
                    base_out_scenarios = ["home"]
                    base_out_weights = [1.0]
                    base_out_scenario = np.random.choice(base_out_scenarios, p=base_out_weights)               
                else:
                    base_out_scenarios = ["home", "second", "first", "third"]
                    base_out_weights = [0.43, 0.37, 0.18, 0.02]
                    base_out_scenario = np.random.choice(base_out_scenarios, p=base_out_weights)

                if base_out_scenario == "home":
                    self.gamestate.move_runner('3RD', 'OUT')
                    self.gamestate.move_runner('2ND', '3RD')
                    self.gamestate.move_runner('1ST', '2ND')
                    self.gamestate.move_runner('HOME', '1ST', self.batter) 
                    self.outcomes.append("THEY WILL GET THE OUT AT HOME! RUNNER SAFE AT 1ST! NO RUNS SCORE!")

                elif base_out_scenario == "second":
                    self.gamestate.move_runner('3RD', 'HOME')
                    self.gamestate.move_runner('2ND', '3RD')
                    self.gamestate.move_runner('1ST', 'OUT')
                    self.gamestate.move_runner('HOME', '1ST', self.batter)
                    runs_scored += 1
                    self.outcomes.append("OUT AT 2ND! RUNNER ON 3RD SCORES! RUNNER SAFE AT FIRST!")

                elif base_out_scenario == "first":
                    self.gamestate.move_runner('3RD', 'HOME')
                    self.gamestate.move_runner('2ND', '3RD')
                    self.gamestate.move_runner('1ST', '2ND')
                    self.gamestate.move_runner('HOME', 'OUT', self.batter)
                    runs_scored += 1
                    self.outcomes.append("OUT AT 1ST! RUNNER ON 3RD SCORES! RUNNER ON 1ST ADVANCES TO 2ND!")

                else:  # "third"
                    self.gamestate.move_runner('3RD', 'HOME')
                    self.gamestate.move_runner('2ND', 'OUT')
                    self.gamestate.move_runner('1ST', '2ND')
                    self.gamestate.move_runner('HOME', '1ST', self.batter)
                    runs_scored += 1
                    self.outcomes.append("OUT AT 3RD! RUNNER ON 3RD SCORES! RUNNER ON 1ST ADVANCES TO 2ND! RUNNER SAFE AT FIRST!")

        elif base_state == "SECOND_AND_THIRD" and self.gamestate.outs < 2:
            rand_val = np.random.random()
            scoring_chance_third = 0.62
            holding_chance_third = 0.37

            # Adjust probabilities slightly based on runner speed
            scoring_chance_third = adjust_probability(scoring_chance_third, self.runners.get('3RD').speed)
            holding_chance_third = adjust_probability(holding_chance_third, self.runners.get('3RD').speed)

            if rand_val < scoring_chance_third:  # 26% chance of runner on third scoring
                self.gamestate.move_runner('3RD', 'HOME')
                self.gamestate.move_runner('HOME', 'OUT', self.batter)
                outs_recorded += 1
                runs_scored += 1
                self.outcomes.append("THEY WILL GRAB THE EASY OUT AT 1ST! RUNNER ON 3RD SCORES! 1 RUN SCORED!")

                # Sub-probabilities for runner on second
                sub_rand_val = np.random.random()
                advance_chance = 0.77

                if sub_rand_val < advance_chance:  # 63% chance of runner on second moving to third
                    self.gamestate.move_runner('2ND', '3RD')
                    self.outcomes.append("RUNNER ON 2ND ADVANCES TO 3RD!")
                else:  # 37% chance of runner on second holding
                    self.outcomes.append("RUNNER ON 2ND HOLDS AT 2ND!")

            elif rand_val < scoring_chance_third + holding_chance_third:  # 65% chance of runner on third holding
                self.gamestate.move_runner('HOME', 'OUT', self.batter) 
                outs_recorded += 1
                self.outcomes.append("THEY HOLD THE RUNNER AT 3RD AND FIRE IT TO 1ST FOR THE OUT!")

            else:  # 9% chance of runner on third thrown out at home
                self.gamestate.move_runner('3RD', 'OUT')
                self.gamestate.move_runner('HOME', '1ST', self.batter)
                outs_recorded += 1
                self.outcomes.append("RUNNER ON 3RD IS THROWN OUT AT HOME! BATTER REACHES FIRST SAFELY!")

                # Sub-probabilities for runner on second
                sub_rand_val = np.random.random()
                if sub_rand_val < 0.22:  # 22% chance of runner on second holding at second
                    self.outcomes.append("RUNNER ON 2ND HOLDS AT 2ND!")
                else:  # 78% chance of runner on second moving to third
                    self.gamestate.move_runner('2ND', '3RD')
                    self.outcomes.append("RUNNER ON 2ND ADVANCES TO 3RD!")

        elif base_state == "FIRST_AND_SECOND" and self.gamestate.outs < 2:
            rand_val = np.random.random()
            double_play = 0.45
            double_play_chance = rev_adjust_probability(double_play, self.runners.get('1ST').speed)  # Adjusted for the runner's speed

            if rand_val < double_play_chance:  # Double play
                outs_recorded += 2
                rand_val = np.random.random()
                if rand_val < 0.28:  # 28% chance of advancing the runner from second to third
                    if self.gamestate.outs == 1:
                        self.gamestate.move_runner('2ND', '3RD')
                        self.gamestate.move_runner('1ST', 'OUT')
                        self.gamestate.move_runner('HOME', 'OUT', self.batter)
                        self.outcomes.append("DOUBLE PLAY OUT AT SECOND AND FIRST! THAT WILL END THE INNING!")
                    else:
                        self.gamestate.move_runner('2ND', '3RD')
                        self.gamestate.move_runner('1ST', 'OUT')
                        self.gamestate.move_runner('HOME', 'OUT', self.batter)
                        self.outcomes.append("DOUBLE PLAY OUT AT SECOND AND FIRST! RUNNER ON 2ND ADVANCES TO 3RD!")

                elif rand_val < 0.98:  # 70% chance of double play out at third and second
                    if self.gamestate.outs == 1:
                        self.gamestate.move_runner('2ND', 'OUT')
                        self.gamestate.move_runner('1ST', 'OUT')
                        self.gamestate.move_runner('HOME', '1ST', self.batter)
                        self.outcomes.append("DOUBLE PLAY OUT AT THIRD AND SECOND! THAT WILL END THE INNING!")
                    else:
                        self.gamestate.move_runner('2ND', 'OUT')
                        self.gamestate.move_runner('1ST', 'OUT')
                        self.gamestate.move_runner('HOME', '1ST', self.batter)
                        self.outcomes.append("DOUBLE PLAY OUT AT THIRD AND SECOND! RUNNER SAFE AT FIRST!")

                else:  # 2% chance of double play out at third and first, runner on first moves to second
                    if self.gamestate.outs == 1:
                        self.gamestate.move_runner('2ND', 'OUT')
                        self.gamestate.move_runner('1ST', '2ND')
                        self.gamestate.move_runner('HOME', 'OUT', self.batter)
                        self.outcomes.append("DOUBLE PLAY OUT AT THIRD AND FIRST! THAT WILL END THE INNING!")
                    else:
                        self.gamestate.move_runner('2ND', 'OUT')
                        self.gamestate.move_runner('1ST', '2ND')
                        self.gamestate.move_runner('HOME', 'OUT', self.batter)
                        self.outcomes.append("DOUBLE PLAY OUT AT THIRD AND FIRST! RUNNER ON 1ST ADVANCES TO 2ND!")
            
            else:  # Base out scenarios
                outs_recorded += 1
                rand_val = np.random.random()
                if rand_val < 0.37:  # 37% chance of runner from second to third, runner on first out at second
                    self.gamestate.move_runner('2ND', '3RD')
                    self.gamestate.move_runner('1ST', 'OUT')
                    self.gamestate.move_runner('HOME', '1ST', self.batter)
                    self.outcomes.append("RUNNER FROM 2ND TO 3RD, RUNNER ON 1ST OUT AT 2ND, BATTER TO 1ST!")
                elif rand_val < 0.50:  # 13% chance of runner from second out at third, runner on first safe at second
                    self.gamestate.move_runner('2ND', 'OUT')
                    self.gamestate.move_runner('1ST', '2ND')
                    self.gamestate.move_runner('HOME', '1ST', self.batter)
                    self.outcomes.append("RUNNER FROM 2ND OUT AT 3RD, RUNNER ON 1ST SAFE AT 2ND, BATTER TO 1ST!")
                else:  # 50% chance of runner on second to third, runner on first to second, and batter out at first
                    self.gamestate.move_runner('2ND', '3RD')
                    self.gamestate.move_runner('1ST', '2ND')
                    self.gamestate.move_runner('HOME', 'OUT', self.batter)
                    self.outcomes.append("RUNNER ON 2ND TO 3RD, RUNNER ON 1ST TO 2ND, BATTER OUT AT 1ST!")

        elif base_state == "FIRST_AND_THIRD" and self.gamestate.outs < 2:
            rand_val = np.random.random()
            double_play = 0.45
            double_play_chance = rev_adjust_probability(double_play, self.runners.get('1ST').speed)

            if rand_val < double_play_chance:
                outs_recorded += 2
                if self.gamestate.outs == 1:
                    self.gamestate.move_runner('3RD', 'HOME')
                    self.gamestate.move_runner('1ST', 'OUT')
                    self.gamestate.move_runner('HOME', 'OUT', self.batter)
                    self.outcomes.append("THROWS TO 2ND, OVER TO 1ST! DOUBLE PLAY (X-4-3)! THAT WILL END THE INNING!")
                else:
                    self.gamestate.move_runner('3RD', 'HOME')
                    self.gamestate.move_runner('1ST', 'OUT')
                    self.gamestate.move_runner('HOME', 'OUT', self.batter)
                    runs_scored += 1
                    self.outcomes.append("GETS THE OUT AT 2ND, THROW OVER TO 1ST! DOUBLE PLAY (X-4-3)!")
            else:
                outs_recorded += 1
                rand_val = np.random.random()
                if rand_val < 0.34:  # 34% chance of out at second, batter safe at first, runner on third scores
                    self.gamestate.move_runner('3RD', 'HOME')
                    self.gamestate.move_runner('1ST', 'OUT')
                    self.gamestate.move_runner('HOME', '1ST', self.batter)
                    runs_scored += 1
                    self.outcomes.append("GETS THE OUT AT 2ND! THROW OVER TO FIRST...SAFE! RUNNER ON 3RD SCORES!")
                elif rand_val < 0.65:  # 31% chance of out at first, runner on third scores
                    self.gamestate.move_runner('3RD', 'HOME')
                    self.gamestate.move_runner('1ST', '2ND')
                    self.gamestate.move_runner('HOME', 'OUT', self.batter)
                    runs_scored += 1
                    self.outcomes.append("OUT AT 1ST! RUNNER ON 3RD SCORES! RUNNER ON 1ST ADVANCES TO 2ND!")
                elif rand_val < 0.87:  # 22% chance of out at home, safe at second and first
                    self.gamestate.move_runner('3RD', 'OUT')
                    self.gamestate.move_runner('1ST', '2ND')
                    self.gamestate.move_runner('HOME', '1ST', self.batter)
                    self.outcomes.append("OUT AT HOME! RUNNER ON 1ST ADVANCES TO 2ND! BATTER SAFE AT FIRST!")
                elif rand_val < 0.97:  # 10% chance of out at first, safe at second, runner on third holds
                    self.gamestate.move_runner('3RD', '3RD')
                    self.gamestate.move_runner('1ST', '2ND')
                    self.gamestate.move_runner('HOME', 'OUT', self.batter)
                    self.outcomes.append("OUT AT 1ST! RUNNER ON 3RD HOLDS! RUNNER ON 1ST ADVANCES TO 2ND!")
                else:  # 3% chance of out at second, batter safe at first, runner on third holds
                    self.gamestate.move_runner('3RD', '3RD')
                    self.gamestate.move_runner('1ST', 'OUT')
                    self.gamestate.move_runner('HOME', '1ST', self.batter)
                    self.outcomes.append("OUT AT 2ND! RUNNER ON 3RD HOLDS! RUNNER SAFE AT FIRST!")

        elif base_state == "RUNNER_ON_FIRST" and self.gamestate.outs < 2:
            rand_val = np.random.random()
            double_play_chance = rev_adjust_probability(runner_probs.get("R1_out", 0), self.runners.get('1ST').speed)

            if rand_val < double_play_chance:  # 23% chance of double play
                outs_recorded += 2
                if self.gamestate.outs == 1:
                    self.gamestate.move_runner('1ST', 'OUT')
                    self.gamestate.move_runner('HOME', 'OUT', self.batter)                    
                    self.outcomes.append("TO 2ND, TO 1ST! INNING ENDING DOUBLE PLAY (X-4-3)!")
                else:
                    self.gamestate.move_runner('1ST', 'OUT')
                    self.gamestate.move_runner('HOME', 'OUT', self.batter) 
                    self.outcomes.append("TO 2ND, TO 1ST! DOUBLE PLAY (X-4-3)!")
            # If no double play, proceed to other fielding outcomes
            else:
                outs_recorded += 1
                rand_val = np.random.random()
                if rand_val < 0.79:
                    self.gamestate.move_runner('1ST', 'OUT')
                    self.gamestate.move_runner('HOME', '1ST', self.batter) 
                    self.outcomes.append("OUT AT 2ND! RUNNER SAFE AT FIRST!")
                else:
                    self.gamestate.move_runner('1ST', '2ND')
                    self.gamestate.move_runner('HOME', 'OUT', self.batter) 
                    self.outcomes.append("OUT AT 1ST! RUNNER ON 1ST ADVANCES TO 2ND!")

        elif base_state == "RUNNER_ON_SECOND" and self.gamestate.outs < 2:
            rand_val = np.random.random()
            advance_prob = adjust_probability(runner_probs.get("R2_adv", 0), self.runners.get('2ND').speed)
            out_prob = adjust_probability(runner_probs.get("R2_adv", 0), self.runners.get('2ND').speed)

            if rand_val < advance_prob:  # 55% chance of advancing to third, runner out at first
                self.gamestate.move_runner('2ND', '3RD')
                self.gamestate.move_runner('HOME', 'OUT', self.batter)
                outs_recorded += 1
                self.outcomes.append("THEY WILL GRAB THE EASY OUT AT 1ST! RUNNER ON 2ND ADVANCES TO 3RD!")
            elif rand_val < advance_prob + out_prob:  # 39% chance of holding at second, runner out at first
                self.gamestate.move_runner('2ND', 'OUT')
                self.gamestate.move_runner('HOME', '1ST', self.batter)
                outs_recorded += 1
                self.outcomes.append("RUNNER ON 2ND IS THROWN OUT AT 3RD! BATTER REACHES FIRST SAFELY!")
            else:  # 6% chance of runner on second out and batter safe at first
                self.gamestate.move_runner('2ND', '2ND')
                self.gamestate.move_runner('HOME', 'OUT', self.batter)
                outs_recorded += 1
                self.outcomes.append("THEY HOLD THE RUNNER AT 2ND AND FIRE IT TO 1ST FOR THE OUT!")

        elif base_state == "RUNNER_ON_THIRD" and self.gamestate.outs < 2:
            rand_val = np.random.random()
            scoring_prob = adjust_probability(runner_probs.get("R3_scr", 0), self.runners.get('3RD').speed)
            out_prob = adjust_probability(runner_probs.get("R3_out", 0), self.runners.get('3RD').speed)

            if rand_val < scoring_prob:  # 33% chance of scoring, runner out at first
                self.gamestate.move_runner('3RD', 'HOME')
                self.gamestate.move_runner('HOME', 'OUT', self.batter)
                outs_recorded += 1
                runs_scored += 1
                self.outcomes.append("THEY WILL GRAB THE EASY OUT AT 1ST! RUNNER ON 3RD HUSTLES TO THE PLATE! 1 RUN SCORED!")
            elif rand_val < scoring_prob + out_prob:  # 52% chance of holding at third, runner out at first
                self.gamestate.move_runner('3RD', 'OUT')
                self.gamestate.move_runner('HOME', '1ST', self.batter)
                outs_recorded += 1 
                self.outcomes.append("RUNNER ON 3RD IS THROWN OUT AT HOME! BATTER REACHES FIRST SAFELY!")
            else:  # 15% chance of runner on third out and batter safe at first
                self.gamestate.move_runner('3RD', '3RD')
                self.gamestate.move_runner('HOME', 'OUT', self.batter)
                outs_recorded += 1 
                self.outcomes.append("THEY HOLD THE RUNNER AT 3RD AND FIRE IT TO 1ST FOR THE OUT!")

        else:
            self.gamestate.move_runner('HOME', 'OUT', self.batter)
            outs_recorded += 1
            self.outcomes.append("THEY THROW OVER TO FIRST IN TIME FOR THE OUT!")

        self.batter.record_at_bat()
        self.pitcher.record_outcome(hit_type="groundout", runs=runs_scored, earned_runs=runs_scored, outs=outs_recorded)
        
        DisplayManager.display_outcome_text(self.outcomes, display_enabled=DISPLAY_TEXT)
        return hits_hit, runs_scored, outs_recorded, walk_off