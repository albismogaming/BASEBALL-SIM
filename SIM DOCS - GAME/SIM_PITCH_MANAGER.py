from SIM_CORE import *
from SIM_SETTINGS import *
from SIM_UTILS import *
from FILE_PATHS import *
import os, sys, time, string, pandas as pd, numpy as np

class PitchingManager:
    def __init__(self, starting_pitchers, relief_pitchers):
        self.starting_pitchers = starting_pitchers
        self.relief_pitchers = relief_pitchers
        self.pitchers_used = []
        self.current_pitcher = None

    def select_starting_pitcher(self, manual_selection=None):
        """Select a starting pitcher, either manually or randomly."""
        if not self.starting_pitchers:
            raise ValueError("No pitchers available in the rotation.")

        if manual_selection:
            # Manual selection
            print(rgb_colored("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■", WHITE))
            for idx, pitcher in enumerate(self.starting_pitchers):
                print(rgb_colored(f"[{idx + 1}]: {pitcher.last_name.upper():14}   AVG: {pitcher.average:.3f}", PLATINUM))
            print(rgb_colored("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■", WHITE))

            # Handle input safely
            while True:
                try:
                    choice = int(input(rgb_colored("SELECT STARTING PITCHER: ", PLATINUM)))
                    if 1 <= choice <= len(self.starting_pitchers):
                        self.current_pitcher = self.starting_pitchers[choice - 1]
                        break
                    print(rgb_colored("INVALID CHOICE! PLEASE CHOOSE A VALID PITCHER.", RED))
                except ValueError:
                    print(rgb_colored("INVALID INPUT! ENTER A NUMBER.", RED))
        else:
            # Random selection
            index = np.random.randint(0, len(self.starting_pitchers))
            self.current_pitcher = self.starting_pitchers[index]
            print(rgb_colored(f"RANDOMLY SELECTED STARTING PITCHER: {self.current_pitcher.last_name.upper()}", GREEN))

        self.pitchers_used.append(self.current_pitcher)
        return self.current_pitcher

    def get_relief_pitcher(self):
        available_relievers = [p for p in self.relief_pitchers if p not in self.pitchers_used]
        if available_relievers:
            self.current_pitcher = available_relievers[0]  # You can adjust the selection strategy
            self.pitchers_used.append(self.current_pitcher)
        else:
            raise ValueError("No more relief pitchers available")

    def get_unused_starting_pitcher(self):
        available_starters = [p for p in self.starting_pitchers if p not in self.pitchers_used]
        if available_starters:
            self.current_pitcher = available_starters[0]  # You can adjust the selection strategy
            self.pitchers_used.append(self.current_pitcher)
        else:
            raise ValueError("No more starting pitchers available")

    def make_pitching_change(self, current_inning):
        """Selects and announces a new pitcher based on the inning and available pitchers."""

        # Get the current (outgoing) pitcher’s name and stats
        outgoing_pitcher = self.get_current_pitcher()
        outgoing_name = outgoing_pitcher.last_name.upper()

        # Logic to select a new pitcher
        if current_inning <= 3:
            try:
                self.get_unused_starting_pitcher()
            except ValueError:
                pass  # Handle no available starting pitchers if needed
        else:
            try:
                self.get_relief_pitcher()
            except ValueError:
                self.get_unused_starting_pitcher()  # Fall back to a starting pitcher if no relievers are available

        # Get the new (incoming) pitcher’s name and details
        incoming_pitcher = self.get_current_pitcher()
        incoming_name = incoming_pitcher.last_name.upper()

    def get_current_pitcher(self):
        if self.current_pitcher:
            return self.current_pitcher
        else:
            raise ValueError("No current pitcher selected")

    def reset_pitchers_used(self):
        """Reset the list of used pitchers after a game or series."""
        self.pitchers_used = []

    def check_for_pitching_change(self, current_inning, gamestate, scoreboard):
        current_inning = gamestate.current_inning
        pitcher = self.get_current_pitcher()
        outs_recorded = pitcher.stats.get('outs_recorded', 0)
        full_innings = outs_recorded // 3
        additional_outs = outs_recorded % 3
        innings_pitched = full_innings + additional_outs / 3.0

        pitches_thrown = pitcher.stats.get('pitches_thrown', 0)
        runs_allowed = pitcher.stats.get('runs_allowed', 0)
        hits_allowed = pitcher.stats.get('hits', 0)
        walks_issued = pitcher.stats.get('walks', 0)
        struggle_index = (0.5 * runs_allowed) + (0.2 * hits_allowed) + (0.1 * walks_issued)

        # Calculate score differential and determine if the team is leading or trailing
        home_score = gamestate.stats['home_team']['score']
        away_score = gamestate.stats['away_team']['score']
        score_differential = abs(home_score - away_score)
        team_trailing = home_score < away_score if pitcher.team == 'home' else away_score < home_score


        # Skip pitching change logic if it's the last out of the inning or game
        if gamestate.outs % 3 == 2:
            return  # Exit early as no change is needed for the last out

        # Define a helper function to trigger pitching change
        def trigger_pitching_change():
            self.make_pitching_change(current_inning)

        # Define blowout threshold with slightly relaxed criteria after the 7th inning
        blowout = (score_differential >= 6 if current_inning >= 7 else score_differential >= 8)
        high_leverage = (current_inning >= 8 and score_differential <= 3)

        # Starter pitcher logic
        if pitcher.position == 'SP':
            # Relaxed criteria for blowout or low-leverage situations
            if blowout or team_trailing and score_differential > 5:
                if (
                    pitches_thrown >= EXTENDED_STARTER_PITCHES_LIMIT or
                    innings_pitched >= EXTENDED_STARTER_INNINGS_LIMIT or
                    runs_allowed >= EXTENDED_STARTER_RUNS_LIMIT
                ):
                    trigger_pitching_change()
            
            # Stricter criteria in normal or high-leverage situations
            else:
                if (
                    (pitches_thrown >= STARTER_PITCHES_LIMIT and innings_pitched >= STARTER_INNINGS_LIMIT) or
                    struggle_index >= STARTER_STRUGGLE_LIMIT or
                    runs_allowed >= STARTER_RUNS_LIMIT or
                    hits_allowed >= STARTER_HITS_LIMIT
                ):
                    trigger_pitching_change()
                elif pitches_thrown >= STARTER_PITCHES_LIMIT * 0.9 and gamestate.outs % 3 == 2:
                    # Allow the starter to finish the inning if close to pitch limit and only one out left
                    return
                elif high_leverage and (pitches_thrown >= STARTER_PITCHES_LIMIT * 0.8 or runs_allowed >= STARTER_RUNS_LIMIT * 0.8):
                    # In high-leverage situations, reduce tolerance for pitch counts or runs allowed
                    trigger_pitching_change()

        # Reliever pitcher logic
        elif pitcher.position == 'RP':
            # Use relaxed criteria in blowout or non-high-leverage situations
            if blowout or team_trailing and score_differential >= 5:
                if (
                    pitches_thrown >= EXTENDED_RELIEVER_PITCHES_LIMIT or
                    innings_pitched >= EXTENDED_RELIEVER_INNINGS_LIMIT or
                    runs_allowed >= EXTENDED_RELIEVER_RUNS_LIMIT
                ):
                    trigger_pitching_change()
            else:
                # Stricter criteria in high-leverage or normal situations
                if (
                    (pitches_thrown >= RELIEVER_PITCHES_LIMIT and innings_pitched >= RELIEVER_INNINGS_LIMIT) or
                    runs_allowed >= RELIEVER_RUNS_LIMIT or
                    hits_allowed >= RELIEVER_HITS_LIMIT
                ):
                    trigger_pitching_change()
                elif pitches_thrown >= RELIEVER_PITCHES_LIMIT * 0.9 and gamestate.outs % 3 == 2:
                    # Allow reliever to finish inning if close to pitch limit with only one out left
                    print("Allowing reliever to finish inning with limited pitches remaining and one out left.")
                    return
                elif high_leverage and (pitches_thrown >= RELIEVER_PITCHES_LIMIT * 0.8 or runs_allowed >= RELIEVER_RUNS_LIMIT * 0.8):
                    # In high-leverage situations, prioritize change sooner
                    trigger_pitching_change()
