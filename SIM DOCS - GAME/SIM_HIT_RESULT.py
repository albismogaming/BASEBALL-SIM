from SIM_CORE import *
from SIM_SETTINGS import *
from SIM_UTILS import *
from FILE_PATHS import *
import os, sys, time, string, pandas as pd, numpy as np

class HitInformation:
    def __init__(self, gamestate, league, pitcher, batter, home_team):
        self.gamestate = gamestate
        self.league = league
        self.pitcher = pitcher
        self.batter = batter
        self.home_team = home_team
        self.probability_adjuster = ProbabilityAdjuster(batter, pitcher, league, gamestate, home_team)
        self.hit_data = {}
        self.load_all_hit_location_files(HIT_LOCS)

    def determine_hit_direction(self, outcome):
        """Determine the hit direction based on the outcome type."""
        if outcome not in ['SINGLE', 'DOUBLE', 'TRIPLE', 'HOMERUN', 'GROUNDOUT', 'FLYOUT', 'LINEOUT', 'POPOUT']:
            return None

        batter_direction = self.batter.direction_outcomes
        pitcher_direction = self.pitcher.direction_outcomes
        league_direction = self.league.hit_outcomes

        directions = ['PULL', 'CENT']
        direction_probabilities = {}

        # Calculate probabilities for PULL and CENT
        for direction in directions:
            direction_prob = self.probability_adjuster.calculated_base_probability(
                batter_direction.get(direction, 0),
                pitcher_direction.get(direction, 0),
                league_direction.get(direction, 0)
            )
            direction_probabilities[direction] = direction_prob

        # Ensure non-negative probabilities
        direction_probabilities = {direction: max(0, prob) for direction, prob in direction_probabilities.items()}

        # Calculate OPPO probability dynamically
        sum_other_probs = sum(direction_probabilities.values())
        direction_probabilities['OPPO'] = max(0, 1 - sum_other_probs)

        # Normalize to ensure sum = 1
        total_prob = sum(direction_probabilities.values())
        normalized_probabilities = {direction: prob / total_prob for direction, prob in direction_probabilities.items()}

        # Select direction based on probability
        return np.random.choice(list(normalized_probabilities.keys()), p=list(normalized_probabilities.values()))

    def determine_batted_ball_type(self, outcome, hit_direction):
        """Determine the type of batted ball based on the outcome and hit direction."""
        
        hit_types = ['GROUNDBALL', 'FLYBALL', 'LINEDRIVE', 'POPUP']
        
        outcome_probabilities = {
            'SINGLE': [0.470, 0.045, 0.480, 0.005],
            'DOUBLE': [0.140, 0.170, 0.690, 0.000],
            'TRIPLE': [0.080, 0.360, 0.560, 0.000],
            'HOMERUN': [0.000, 0.830, 0.170, 0.000],
            'FLYOUT': [0.000, 0.900, 0.100, 0.000],
            'GROUNDOUT': [0.950, 0.000, 0.050, 0.000],
            'LINEOUT': [0.000, 0.000, 1.000, 0.000],
            'POPOUT': [0.000, 0.000, 0.000, 1.000]
        }
        
        # Restrict hit types based on hit direction
        restricted_types = set()
        
        if outcome in ['DOUBLE', 'TRIPLE']:
            if hit_direction == 'CENTER':
                restricted_types.add('GROUNDBALL')  # Doubles/triples to center are never groundballs
        
        if outcome in ['HOMERUN', 'FLYOUT', 'LINEOUT']:
            restricted_types.update(['GROUNDBALL', 'POPUP'])  # These outcomes cannot be grounders or popups

        if outcome == 'POPOUT':
            restricted_types.update(['GROUNDBALL', 'FLYBALL', 'LINEDRIVE'])  # Only popups allowed
        
        # Filter valid hit types
        valid_hit_types = [h for h in hit_types if h not in restricted_types]
        
        # Get probability distribution for the given outcome
        if outcome not in outcome_probabilities:
            return 'UNKNOWN'

        # Adjust probabilities to only include valid hit types
        probs = [outcome_probabilities[outcome][hit_types.index(h)] for h in valid_hit_types]
        
        # Normalize probabilities to sum to 1
        total_prob = sum(probs)
        if total_prob > 0:
            probs = [p / total_prob for p in probs]
        else:
            return 'UNKNOWN'  # Fallback if no valid probabilities exist
        
        return np.random.choice(valid_hit_types, p=probs)

    def load_all_hit_location_files(self, folder):
        """
        Loads all hit location CSV files into a dictionary.
        """
        for filename in os.listdir(folder):
            if filename.endswith(".csv"):
                outcome = filename.replace(".csv", "").upper()  # Extract the outcome name
                filepath = os.path.join(folder, filename)

                df = pd.read_csv(filepath, encoding="utf-8-sig")

                # Convert hit_location and probability columns into lists
                df["hit_location"] = df["hit_location"].apply(lambda x: x.split(",") if isinstance(x, str) else [])
                df["probability"] = df["probability"].apply(lambda x: [float(p) for p in x.split(",")] if isinstance(x, str) else [])

                self.hit_data[outcome] = df
    
    def get_hit_location(self, outcome, batter_side, hit_direction, batted_ball_type):
        """
        Retrieves a hit location based on hit outcome, direction, batted ball type, and batter side.
        """
        outcome = outcome.upper()  # Ensure case consistency

        if outcome not in self.hit_data:
            return "unknown_location"

        df = self.hit_data[outcome]

        # Filter the dataframe for matching hit parameters
        filtered_df = df[
            (df["batter_side"] == batter_side) &
            (df["hit_direction"] == hit_direction) &
            (df["batted_ball_type"] == batted_ball_type)
        ]

        if filtered_df.empty:
            return "unknown_location"

        # Select a random row (there should only be one per category)
        row = filtered_df.iloc[0]

        # Choose a hit location based on probabilities
        selected_location = np.random.choice(row["hit_location"], p=row["probability"])
        return selected_location

    def determine_hit_information(self, outcome, batter_side):
        """Returns hit direction, batted ball type, and hit location in a single call."""
        hit_direction = self.determine_hit_direction(outcome)  # Determine hit direction
        batted_ball_type = self.determine_batted_ball_type(outcome, hit_direction)  # Determine batted ball type
        hit_location = self.get_hit_location(outcome, batter_side, hit_direction, batted_ball_type)  # Determine hit location
        
        return hit_direction, batted_ball_type, hit_location  # ✅ Now returns all three