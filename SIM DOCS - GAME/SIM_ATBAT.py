import numpy as np
import pandas as pd
import time
from termcolor import colored
from collections import OrderedDict
from SIM_FUNCTIONS import *
from SIM_LGDATA import *
from SIM_TEAM import *
from SIM_SETTINGS import *
from SIM_SCOREBOARD import *
from SIM_ABPROBS import *
from SIM_GEN_PIT_SEQ import *
from SIM_HIT_RESULT import *
from SIM_GAMESTATE import *
from SIM_UTILS import *
from COLOR_CODES import *
from SIM_DISPLAY_MANAGER import *

class AtBat:
    def __init__(self, batter, pitcher, league, home_team, gamestate, scoreboard, matchups):
        self.batter = batter
        self.pitcher = pitcher
        self.league = league
        self.home_team = home_team
        self.gamestate = gamestate
        self.scoreboard = scoreboard
        self.matchup_manager = MatchupManager(batter, pitcher, matchups)
        self.probability_adjuster = ProbabilityAdjuster(batter, pitcher, league, gamestate, home_team, self.matchup_manager)
        self.pitch_sequence = PitchSequence(league, gamestate, pitcher, batter)
        self.hit_information = HitInformation(self.gamestate, self.league, self.pitcher, self.batter, self.home_team)

        self.display_manager = DisplayManager(self.scoreboard, DISPLAY_TOGGLE)
        self.pitch_code_mapping = PITCH_CODE_MAP

    def simulate_at_bat(self):
        """Simulate a full at-bat, handling pitch-by-pitch processing, micro-events, and the final outcome."""

        count_balls = self.gamestate.balls
        count_strikes = self.gamestate.strikes
        pickoff_attempts = self.gamestate.pickoffs
        at_bat_complete = False
        pitch_number = 1
        pitch_sequence_display = []
        
        # Calculate advantage for batter/pitcher display
        advantage = self.probability_adjuster.calculate_advantage(self.gamestate.current_inning, self.gamestate.score_difference)

        # Generate pitch sequence with pickoffs and micro-events
        outcome = self.handle_macro_event()
        event_type = self.pitch_sequence.classify_pitch_event_type(outcome)
        pitches_thrown = self.pitch_sequence.determine_pitch_count(event_type)
        pitch_sequence = list(self.pitch_sequence.select_random_pitch_sequence(event_type, pitches_thrown))

        self.display_manager.display_matchup(self.batter, self.pitcher, advantage)
        for i, pitch_code in enumerate(pitch_sequence):

            is_last_pitch = (i == len(pitch_sequence) - 1)
            count_display = f"{count_balls}-{count_strikes}"

            if pickoff_attempts < (PICKOFFS):
                pickoff_base = self.gamestate.check_for_pickoff()
                if pickoff_base:
                    # Generate pickoff text directly and append to display sequence
                    pickoff_text = f"PICKOFF {pickoff_base}ND" if pickoff_base == '2' else f"PICKOFF {pickoff_base}ST"
                    pickoff_color = STEEL_BLUE

                    DisplayManager.display_pitch_sequence([(count_display, pickoff_text, pickoff_color)], starting_pitch_number=pitch_number, display_enabled=DISPLAY_PITCH)
                    self.display_manager.display_scoreboard_bar()
                    hits_hit, runs_scored, outs_recorded, walk_off = self.execute_micro_event(pickoff_base)
                    pickoff_attempts += 1

                    self.display_manager.display_scoreboard()

                    if self.gamestate.end_inning():
                        at_bat_complete = True
                        break

                    self.display_manager.display_matchup(self.batter, self.pitcher, advantage)

            if pitch_code == 'B':
                wild_pitch = self.gamestate.check_for_wild_pitch_or_passed_ball()
                if wild_pitch:
                    wild_pitch_text = "WILD PITCH"
                    wild_pitch_color = BLOOD_RED
                    
                    # Display the wild pitch event and process runner advancement
                    DisplayManager.display_pitch_sequence([(count_display, wild_pitch_text, wild_pitch_color)], starting_pitch_number=pitch_number, display_enabled=DISPLAY_PITCH)
                    count_balls, count_strikes = self.gamestate.update_count(pitch_code, count_balls, count_strikes)
                    self.display_manager.display_scoreboard_bar()
                    hits_hit, runs_scored, outs_recorded, walk_off = self.execute_micro_event(wild_pitch)  # Execute the wild pitch event

                    self.display_manager.display_scoreboard()

                    # Check if the inning is complete after the wild pitch
                    if self.gamestate.end_inning():
                        at_bat_complete = True
                        break

                    self.display_manager.display_matchup(self.batter, self.pitcher, advantage)
                    continue

            if pitch_code != 'F' and not is_last_pitch:
                steal_attempt = self.gamestate.check_for_stealing(pitch_code)
                if steal_attempt:
                    if pitch_code == 'B':
                        steal_text = "BALL"
                        steal_color = PASTEL_GREEN
                    elif pitch_code == 'S':
                        steal_text = "STRIKE SWINGING"
                        steal_color = PASTEL_RED
                    elif pitch_code == 'C':
                        steal_text = "CALLED STRIKE"
                        steal_color = PASTEL_RED
                        
                    # Display the steal event and update the game state
                    DisplayManager.display_pitch_sequence([(count_display, steal_text, steal_color)], starting_pitch_number=pitch_number, display_enabled=DISPLAY_PITCH)
                    count_balls, count_strikes = self.gamestate.update_count(pitch_code, count_balls, count_strikes)
                    self.display_manager.display_scoreboard_bar()
                    hits_hit, runs_scored, outs_recorded, walk_off = self.execute_micro_event(steal_attempt)  # Execute the steal event
                    
                    self.display_manager.display_scoreboard()

                    # Check if the inning is complete after the steal attempt
                    if self.gamestate.end_inning():
                        at_bat_complete = True
                        break

                    self.display_manager.display_matchup(self.batter, self.pitcher, advantage)
                    continue

            # If no micro-events, process the pitch normally
            pitch, color = self.pitch_code_mapping.get(pitch_code, ('Unknown pitch', 'white'))
            pitch_sequence_display.append((count_display, pitch, color))
            DisplayManager.display_pitch_sequence([(count_display, pitch, color)], starting_pitch_number=pitch_number, display_enabled=DISPLAY_PITCH)
            count_balls, count_strikes = self.gamestate.update_count(pitch_code, count_balls, count_strikes)

            if pitch_code == 'S' and is_last_pitch:
                outcome = "SWINGING STRIKEOUT"

            if pitch_code == 'C' and is_last_pitch:
                outcome = "CALLED STRIKEOUT"

            # Check if the at-bat is complete due to a walk or strikeout
            if count_strikes == 3 and pitch_code not in ['F']:
                at_bat_complete = True
                break
            if count_balls == 4:
                at_bat_complete = True
                break

            pitch_number += 1
            short_wait()

        # Process the macro event as usual if inning did not end
        self.display_manager.display_scoreboard_bar()
        if not at_bat_complete:
            hits_hit, runs_scored, outs_recorded, walk_off = self.gamestate.process_macro_event(outcome, self.batter, self.pitcher, self.gamestate.set_runners_on_base())
            
            self.gamestate.update_outs(outs_recorded)
            self.gamestate.update_score(hits_hit, runs_scored)
            pickoff_attempts = 0

            self.display_manager.display_scoreboard()
        
        return outcome, pitches_thrown, pitch_sequence, at_bat_complete, hits_hit, runs_scored, outs_recorded, walk_off

    def handle_macro_event(self):
        # Calculate advantage and factors
        advantage = self.probability_adjuster.calculate_advantage(self.gamestate.current_inning, self.gamestate.score_difference)
        factors = self.probability_adjuster.initialize_factors(advantage)
        probabilities = self.probability_adjuster.calculated_probability(POSITIVE_OUTCOMES, self.batter.hit_outcomes, self.pitcher.hit_outcomes, self.league.hit_outcomes, factors)

        probabilities['OUT'] = max(0, 1 - sum(probabilities.values()))
        outcome = np.random.choice(list(probabilities.keys()), p=list(probabilities.values()))

        if outcome == 'OUT':
            outcome = self.handle_negative_outcome()
        return outcome

    def handle_negative_outcome(self):
        batter = self.batter.hit_outcomes
        pitcher = self.pitcher.hit_outcomes
        league = self.league.hit_outcomes
        outcomes = ['GROUNDOUT', 'FLYOUT', 'LINEOUT']

        out_probabilities = {}
        for outcome in outcomes:
            out_prob = self.probability_adjuster.calculated_base_probability(
                batter.get(outcome, 0), 
                pitcher.get(outcome, 0), 
                league.get(outcome, 0)
            )
            out_probabilities[outcome] = max(0, out_prob)

        # Calculate the complement for 'POPOUT' as the remaining probability
        total_prob = sum(out_probabilities.values())
        out_probabilities['POPOUT'] = max(0, 1 - total_prob)

        # Normalize to ensure all probabilities sum to 1
        total = sum(out_probabilities.values())
        if total > 0:  # Avoid division by zero
            out_probabilities = {outcome: prob / total for outcome, prob in out_probabilities.items()}

        # Randomly select an outcome based on probabilities
        outcome = np.random.choice(list(out_probabilities.keys()), p=list(out_probabilities.values()))
        return outcome

    def execute_micro_event(self, pitch_code):
        """Execute the appropriate micro-event based on the pitch code marker."""
        
        # ✅ Determine the micro-event based on pitch code
        if pitch_code == '1':
            event_text = 'PICKOFF 1ST'
        elif pitch_code == '2':
            event_text = 'PICKOFF 2ND'
        elif pitch_code == 'W':
            event_text = "WILD PITCH"
        elif pitch_code == 'P':
            event_text = "PASSED BALL"
        elif pitch_code in ['T', 'U', 'V']:  # ✅ Consolidate similar cases
            event_text = "STEAL ATTEMPT"

        # ✅ Process the event only if `event_text` is valid
        if event_text:
            hits_hit, runs_scored, outs_recorded, walk_off = self.gamestate.process_micro_event(
                outcome=event_text,
                batter=self.batter,
                pitcher=self.pitcher,
                runners=self.gamestate.set_runners_on_base()
            )

            # ✅ Only update score and outs if changes occurred
            if outs_recorded > 0:
                self.gamestate.update_outs(outs_recorded)
            if hits_hit > 0 or runs_scored > 0:
                self.gamestate.update_score(hits_hit, runs_scored)

        return hits_hit, runs_scored, outs_recorded, walk_off

    def print_pitch_sequence(self, sequence, starting_pitch_number=1):
        """Print each pitch in the sequence, along with any pre-processed micro-events, starting from a specified pitch number."""
        for i, (count, detail, color) in enumerate(sequence):
            pitch_number_display = starting_pitch_number + i
            print_delay(f"{rgb_colored(f'[{pitch_number_display}]:', WHITE)} {rgb_colored(f'[{count}]', AMBER)} ~~ {rgb_colored(detail, color)}")
        return None  # Sequence completes without interruption

