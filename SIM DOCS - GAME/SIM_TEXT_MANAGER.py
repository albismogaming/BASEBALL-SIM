from SIM_CORE import *
from SIM_SETTINGS import *
from SIM_UTILS import *
from FILE_PATHS import *
import os, sys, time, string, pandas as pd, numpy as np

class TextManager:
    def __init__(self, folder=TEXT_PATH):
        """
        Initializes the TextManager by loading all CSV files from the given folder.
        """
        self.text_data = {}
        self.load_all_text_files(folder)

    def load_all_text_files(self, folder):
        """
        Loads all CSV files in the specified folder into the text_data dictionary.
        """
        for filename in os.listdir(folder):
            if filename.endswith(".csv"):
                key = filename.replace(".csv", "").upper()  # Remove .csv and uppercase for consistency
                filepath = os.path.join(folder, filename)
                
                # Load CSV into a DataFrame
                self.text_data[key] = pd.read_csv(filepath, encoding="utf-8-sig")
    
    def get_event_description(self, event_type, base_state, batter_side=None, hit_location=None):
        """
        Retrieves a random event description based on the event type and game situation.
        """

        # Ensure the event type exists in loaded data
        event_type = event_type.upper()
        if event_type not in self.text_data:
            print(f"❌ ERROR: Event description file for '{event_type}' not found.")
            return "No description available."

        df = self.text_data[event_type]

        # Filtering logic
        if event_type in ["STRIKEOUT", "STEAL", "PICKOFF_1ST", "PICKOFF_2ND", "WALK", "WILDPITCH", "PASSEDBALL", "HBP"]:
            # These events use a custom "base_state" terminology instead of actual base states
            filtered_df = df[df["base_state"] == base_state]
        else:
            # Standard filtering for hit events
            filtered_df = df[
                (df["base_state"] == base_state) &
                (df["batter_side"] == batter_side) &
                (df["hit_location"] == hit_location)
            ]

        # Return a random description if available
        if not filtered_df.empty:
            return filtered_df["text_description"].sample(n=1).values[0]

        return "No description available for this scenario."