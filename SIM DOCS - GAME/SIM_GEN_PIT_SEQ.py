import pandas as pd
import numpy as np
from termcolor import colored
from SIM_WP_PB import *
from SIM_STRIKEOUTS import *
from SIM_STEALS import *
from SIM_LGDATA import *
from SIM_GAMESTATE import *
from SIM_SETTINGS import *
from SIM_FUNCTIONS import *
from FILE_PATHS import *

class PitchSequence:
    def __init__(self, league, gamestate, pitcher, batter):
        self.league = league
        self.gamestate = gamestate
        self.pitcher = pitcher
        self.batter = batter
        self.pitch_sequences = {}
        self.pitch_lengths = {}        
        self.runners = []
        self.pitch_code_mapping = PITCH_CODE_MAP

        # Load JSON Data
        self.load_pitch_lengths()
        self.load_all_pitch_sequences()

    def load_pitch_lengths(self):
        """Loads pitch length probabilities from a CSV file."""
        file_path = os.path.join(PBP_SEQUENCE, "PITCH_LENGTHS.csv")
        try:
            self.pitch_lengths = pd.read_csv(file_path, encoding="utf-8-sig")
        except FileNotFoundError:
            raise ValueError(f"❌ ERROR: {file_path} not found.")
        except pd.errors.EmptyDataError:
            raise ValueError(f"❌ ERROR: {file_path} is empty or improperly formatted.")

    def load_all_pitch_sequences(self):
        """Loads pitch sequences for all outcomes from separate CSV files."""
        outcomes = ['groundball', 'flyball', 'lineball', 'popball', 
                    'strikethree', 'walk', 'hbp', 'single', 'double', 
                    'triple', 'homerun']
        for outcome in outcomes:
            self.load_pitch_sequences(outcome)

    def load_pitch_sequences(self, outcome):
        """Loads pitch sequences from the corresponding CSV file based on outcome."""
        filename_map = {
            'groundball': 'HIP.csv',
            'flyball': 'HIP.csv',
            'lineball': 'HIP.csv',
            'popball': 'HIP.csv',
            'strikethree': 'KO.csv',
            'walk': 'BB.csv',
            'hbp': 'HBP.csv',
            'single': 'HIP.csv',
            'double': 'HIP.csv',
            'triple': 'HIP.csv',
            'homerun': 'HIP.csv'
        }
        
        if outcome in filename_map:
            file_path = os.path.join(PBP_SEQUENCE, filename_map[outcome])
            try:
                self.pitch_sequences[outcome] = pd.read_csv(file_path, encoding="utf-8-sig")
            except FileNotFoundError:
                raise ValueError(f"❌ ERROR: {file_path} not found.")
            except pd.errors.EmptyDataError:
                raise ValueError(f"❌ ERROR: {file_path} is empty or improperly formatted.")
        else:
            raise ValueError(f"❌ ERROR: No pitch sequences available for outcome {outcome}")

    def determine_first_pitch(self):
        """Selects the first pitch result using a discrete probability distribution."""
        
        first_pitch_probabilities = {
            "B": 0.45,  # Pitcher throws a ball 35% of the time
            "C": 0.40,  # Called strike 30% of the time
            "S": 0.05,  # Swinging strike 20% of the time
            "F": 0.10   # Foul ball 15% of the time
        }

        # Extract outcomes and probabilities
        outcomes = list(first_pitch_probabilities.keys())
        probabilities = list(first_pitch_probabilities.values())

        # Select first pitch based on probabilities
        return np.random.choice(outcomes, p=probabilities)

    def determine_pitch_count(self, event_type):
        """Determines the number of pitches in an at-bat based on event type probabilities from a CSV file."""

        # Ensure pitch length data is loaded
        if self.pitch_lengths is None or self.pitch_lengths.empty:
            print(f"❌ ERROR: Pitch length data not loaded. Returning default of 1 pitch.")
            return 1  

        # Filter pitch length data for the given event type
        filtered_df = self.pitch_lengths[self.pitch_lengths["outcome"] == event_type]

        if filtered_df.empty:
            print(f"⚠️ WARNING: No pitch length data found for event type '{event_type}'. Defaulting to 1 pitch.")
            return 1  

        # Extract pitch lengths and probabilities
        pitch_lengths = filtered_df["pitch_length"].tolist()
        probabilities = filtered_df["probability"].tolist()

        # Normalize probabilities to sum to 1
        total_prob = sum(probabilities)
        if total_prob > 0:
            probabilities = [p / total_prob for p in probabilities]
        else:
            print(f"❌ ERROR: Probabilities for '{event_type}' sum to 0. Defaulting to 1 pitch.")
            return 1  

        # Select a pitch count based on the probabilities
        selected_pitch_count = np.random.choice(pitch_lengths, p=probabilities)

        return selected_pitch_count

    def classify_pitch_event_type(self, event_outcome):
        """
        Classifies an event outcome into its corresponding pitch event type.
        
        Args:
            event_outcome (str): The outcome of the pitch (e.g., "SINGLE", "STRIKEOUT").

        Returns:
            str: The classified pitch event type (e.g., "single", "strikethree").
        """

        # Mapping of event outcomes to their classifications
        outcome_mapping = {
            "SINGLE": "single",
            "DOUBLE": "double",
            "TRIPLE": "triple",
            "HOMERUN": "homerun",
            "GROUNDOUT": "groundball",
            "FLYOUT": "flyball",
            "LINEOUT": "lineball",
            "POPOUT": "popball",
            "WALK": "walk",
            "STRIKEOUT": "strikethree",  # Renaming to prevent overlap
            "HBP": "hbp"
        }

        # Return the mapped classification or default to "in play"
        return outcome_mapping.get(event_outcome, "in play")


    def select_random_pitch_sequence(self, event_type, sequence_length):
        """
        Selects a pitch sequence based on event type and sequence length, ensuring realistic pitch selection.

        Args:
            event_type (str): The type of event (e.g., "strikeout", "walk", "hbp", "single").
            sequence_length (int): The total length of the pitch sequence.

        Returns:
            list: A randomly selected pitch sequence.
        """

        # Ensure pitch sequences are loaded
        if event_type not in self.pitch_sequences or self.pitch_sequences[event_type].empty:
            raise ValueError(f"❌ ERROR: No pitch sequences loaded for event type '{event_type}'.")

        event_sequences_df = self.pitch_sequences[event_type]  # Retrieve DataFrame for the event

        # 🚨 Handle Walks (4-Pitch Guaranteed) 🚨
        if event_type == "walk" and sequence_length == 4:
            return ["B", "B", "B", "B"]

        # 🚨 Handle 3-Pitch Strikeouts Without Running First-Pitch Function 🚨
        if event_type == "strikethree" and sequence_length == 3:
            valid_first_pitches = ["S", "C", "F"]  # Only strikes/fouls start a 3-pitch K
            first_pitch = np.random.choice(valid_first_pitches)

            possible_sequences = {
                "S": ["SFS", "SFC", "SCS", "SCC"],
                "C": ["CFS", "CFC", "CSC", "CSS"],
                "F": ["FFS", "FFC", "FSC", "FSS"]
            }

            # Select a varied sequence
            return list(np.random.choice(possible_sequences[first_pitch]))

        # 🚨 Handle Single-Pitch At-Bats 🚨
        if sequence_length == 1:
            return ["X"] if event_type in ["single", "double", "triple", "homerun", "groundball", "popball", "lineball", "flyball"] else ["H"] if event_type == "hbp" else ["?"]

        # 🚨 Determine the First Pitch 🚨
        first_pitch = self.determine_first_pitch()

        # Filter sequences based on length
        filtered_sequences = event_sequences_df[event_sequences_df["length"] == sequence_length]

        # If no exact match, find the closest available length
        if filtered_sequences.empty:
            closest_length = event_sequences_df["length"].sub(sequence_length).abs().idxmin()
            filtered_sequences = event_sequences_df.loc[[closest_length]]

        # Further filter sequences where the first pitch matches our determined first pitch
        filtered_sequences = filtered_sequences[filtered_sequences["sequence"].str.startswith(first_pitch)]

        # If no match is found, revert to any sequence with the correct length
        if filtered_sequences.empty:
            filtered_sequences = event_sequences_df[event_sequences_df["length"] == sequence_length]

        # Select a random sequence from the available options
        random_sequence = filtered_sequences.sample(1)["sequence"].values[0]

        return random_sequence.split(", ")  # Convert stored string back to a list


