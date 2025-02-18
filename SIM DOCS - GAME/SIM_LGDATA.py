import numpy as np
import pandas as pd
import os
import sys
from SIM_SETTINGS import *
from FILE_PATHS import *

class LeagueAverages:
    def __init__(self):
        self.hit_outcomes = {}
        self.park_factors = {}
        self.load_hit_outcomes()
        self.load_park_factors()      

    def load_hit_outcomes(self):
        df = pd.read_csv(LEAGUE_HIT)
        if not df.empty:
            # Assuming you want to load the first row or a specific row that contains the data
            self.hit_outcomes = df.iloc[0].drop('ID', errors='ignore').to_dict()  # safely ignore ID if it exists
        else:
            raise ValueError("The CSV file is empty or the data is not available")        

    def load_park_factors(self):
        df = pd.read_csv(LEAGUE_PFR)
        if not df.empty:
            self.park_factors = df.set_index('TEAM').to_dict('index')
        else:
            raise ValueError("The CSV file is empty or the data is not available")