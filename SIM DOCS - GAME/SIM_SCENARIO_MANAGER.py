from SIM_CORE import *
from SIM_SETTINGS import *
from SIM_UTILS import *
from FILE_PATHS import *
import os, sys, time, string, pandas as pd, numpy as np

class ScenarioManager:
    def __init__(self, scenario_folder=SCENARIO_DATA):
        """Loads scenario data dynamically based on outcome types."""
        self.scenario_folder = scenario_folder
        self.scenario_data = {}

    def load_scenario_data(self, outcome):
        """
        Loads the scenario CSV file corresponding to the given outcome and stores it in a DataFrame.
        """
        filename = os.path.join(self.scenario_folder, f"{outcome}.csv")

        if os.path.exists(filename):
            try:
                df = pd.read_csv(filename, encoding="utf-8-sig")
                self.scenario_data[outcome] = df
                return df
            except Exception as e:
                print(f"❌ ERROR: Failed to load {outcome}.csv - {e}")
                return None
        else:
            print(f"❌ ERROR: Scenario file not found for outcome: {outcome}")
            return None

    def get_probabilities(self, outcome, base_state, batter_side, batted_ball_type, hit_direction, hit_location):
        """
        Retrieves probability values based on the scenario (hit type, location, base state, and batter handedness).
        """
        if outcome not in self.scenario_data:
            df = self.load_scenario_data(outcome)
            if df is None:
                return {}

        df = self.scenario_data[outcome]

        # Filter based on provided criteria
        filtered_df = df[
            (df["base_state"] == base_state) &
            (df["batter_side"] == batter_side) &
            (df["batted_ball_type"] == batted_ball_type) &
            (df["hit_direction"] == hit_direction)
        ]

        # Ensure hit_location exists within the possible hit locations
        filtered_df = filtered_df[filtered_df["hit_location"].apply(lambda loc_list: hit_location in str(loc_list).split(","))]

        # If no matching records are found, return an empty dictionary
        if filtered_df.empty:
            return {}

        # Dynamically extract columns related to runner probabilities
        runner_columns = [col for col in df.columns if col.startswith(("R1", "R2", "R3"))]

        # Drop any columns that contain only NULL values
        filtered_df = filtered_df[runner_columns].dropna(axis=1, how='all')

        # Ensure there's data before accessing index 0
        if filtered_df.empty:
            return {}

        # Convert to dictionary safely
        probabilities = filtered_df.to_dict("records")[0]
        return probabilities




