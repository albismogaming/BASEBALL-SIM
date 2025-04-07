from SIM_CORE import *
from SIM_SETTINGS import *
from SIM_UTILS import *
from FILE_PATHS import *
import os, sys, time, string, pandas as pd, numpy as np

class ProbabilityAdjuster:
    def __init__(self, batter, pitcher, league, gamestate, home_team, matchup_manager=None):
        self.batter = batter
        self.pitcher = pitcher
        self.league = league
        self.gamestate = gamestate
        self.home_team = home_team  # Store home_team
        self.matchup_manager = matchup_manager
        
    def calculated_base_probability(self, batter_prob, pitcher_prob, league_avg):
        bc = np.sqrt(league_avg * (1 - batter_prob))
        pc = np.sqrt(league_avg * (1 - pitcher_prob))
        lc = np.sqrt(league_avg * (1 - league_avg))
        eu = np.sqrt(np.e)
        m = 1/(np.sqrt(2.3)**(1/0.07))
        n = (league_avg - m)
        p = np.sqrt(n * (np.e ** lc))

        batter = ((batter_prob - league_avg) / pc)
        pitcher = ((pitcher_prob - league_avg) / bc)
        combined = ((batter + pitcher) / eu)

        probability = ((combined * p) + league_avg)
        return np.clip(probability, 0, 1)  # Ensure probability is between 

    def calculate_split_advantage(self, batter_handedness, pitcher_handedness):
        if batter_handedness == 'R':
            if pitcher_handedness == 'L':
                return np.random.uniform(1.03, 1.08)  # Righty vs Lefty, batter advantage
            else:
                return np.random.uniform(0.94, 0.98)  # Righty vs Righty, pitcher advantage
        elif batter_handedness == 'L':
            if pitcher_handedness == 'R':
                return np.random.uniform(1.03, 1.08)  # Lefty vs Righty, batter advantage
            else:
                return np.random.uniform(0.94, 0.98)  # Lefty vs Lefty, pitcher advantage
        elif batter_handedness == 'B':
            if pitcher_handedness == 'R':
                return np.random.uniform(1.01, 1.03)  # Switch-hitter vs Righty, slight advantage
            elif pitcher_handedness == 'L':
                return np.random.uniform(1.01, 1.03)  # Switch-hitter vs Lefty, slight advantage
            else:
                return 1.00  # Neutral advantage for unknown cases
        else:
            return 1.00  # Default neutral advantage for unknown cases

    def apply_random_factor(self, average):
        return average + np.random.uniform(-0.00777, 0.00777)

    def calculate_advantage(self, inning, score_difference):
        adjusted_batter_avg = self.apply_random_factor(self.batter.average)
        adjusted_pitcher_avg = self.apply_random_factor(self.pitcher.average)

        if self.is_clutch_situation(inning, score_difference):
            clutch_difference = self.batter.clutch - self.pitcher.clutch
            adjusted_batter_avg += clutch_difference + 0.00314

        combined_deviation = (adjusted_batter_avg - LEAGUE_BA) - (LEAGUE_BA - adjusted_pitcher_avg)
        return "BATTER" if combined_deviation > 0 else "PITCHER" if combined_deviation < 0 else "NEUTRAL"

    def initialize_factors(self, advantage):
        if advantage == "BATTER":
            return {outcome: np.random.uniform(*POSITIVE_RANGES[outcome]) for outcome in POSITIVE_OUTCOMES}
        elif advantage == "PITCHER":
            return {outcome: np.random.uniform(*NEGATIVE_RANGES[outcome]) for outcome in POSITIVE_OUTCOMES}
        return {outcome: 1.00 for outcome in POSITIVE_OUTCOMES}

    def apply_factors(self, probabilities, factors):
        """Multiply each probability by its corresponding factor."""
        return {outcome: prob * factors.get(outcome, 1) for outcome, prob in probabilities.items()}

    def apply_park_factors(self, probabilities):
        """Apply park factors to probabilities if available."""
        park_factors = self.league.park_factors.get(self.home_team, {})
        return {outcome: prob * park_factors.get(outcome, 1) for outcome, prob in probabilities.items()}

    def is_clutch_situation(self, inning, score_difference):
        # Gather relevant game state data
        runners_on_base = self.gamestate.bases
        outs = self.gamestate.outs
        home_score = self.gamestate.stats['home_team']['score']
        away_score = self.gamestate.stats['away_team']['score']
        game_tied = home_score == away_score

        # Check for clutch situations based on inning, score, runners, and outs
        if inning >= 7 and (score_difference <= 4 or game_tied):
            return True

        # Runners in scoring position or two outs with any runners on base
        if runners_on_base['2ND'] or runners_on_base['3RD'] or (outs == 2 and any(runners_on_base.values())):
            return True

        # Late inning, team trailing by one run scenario
        if inning >= 7:
            if ((self.gamestate.home_team == self.home_team and home_score < away_score and score_difference == 1) or
                (self.gamestate.home_team != self.home_team and away_score < home_score and score_difference == 1)):
                return True

        return False

    def calculated_probability(self, outcomes, batter_prob, pitcher_prob, league_prob, factors):
        probabilities = {}

        # Step 1: Calculate base probability for each outcome
        for outcome in outcomes:
            batter_value = batter_prob.get(outcome, 0)
            pitcher_value = pitcher_prob.get(outcome, 0)
            league_value = league_prob.get(outcome, 0)

            # Calculate base probability for each outcome
            base_probability = self.calculated_base_probability(batter_value, pitcher_value, league_value)

            # Retrieve contextual factors
            matchup_count = self.matchup_manager.get_matchup_count()
            batter_handedness = self.batter.bats
            pitcher_handedness = self.pitcher.throws

            # Calculate split factor and adjust the base probability
            split_factor = self.calculate_split_advantage(batter_handedness, pitcher_handedness)
            split_adjusted_prob = base_probability * split_factor

            # Apply matchup adjustments for both batter and pitcher
            adjusted_batter_prob = self.matchup_manager.adjust_probability_for_matchups(split_adjusted_prob, matchup_count, is_batter=True)
            adjusted_pitcher_prob = self.matchup_manager.adjust_probability_for_matchups(split_adjusted_prob, matchup_count, is_batter=False)

            # Recalculate the final probability with adjustments
            final_probability = self.calculated_base_probability(adjusted_batter_prob, adjusted_pitcher_prob, league_value)

            probabilities[outcome] = final_probability

        # Step 2: Apply factors to each outcome probability
        probabilities = self.apply_factors(probabilities, factors)
        probabilities = self.apply_park_factors(probabilities)

        # Ensure probabilities are non-negative
        probabilities = {outcome: max(0, prob) for outcome, prob in probabilities.items()}

        return probabilities



