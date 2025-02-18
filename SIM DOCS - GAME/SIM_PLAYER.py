import os
import json
import numpy as np
import pandas as pd
from FILE_PATHS import *

class Player:
    def __init__(self, player_id, team, base_path, age, first_name, last_name, position, average, clutch, bats, throws, field=None, speed=None, obp=None, babip=None, slg=None, ops=None, iso=None):
        self.player_id = player_id
        self.team = team  # Assuming team is a Team object
        self.base_path = base_path
        self.age = age
        self.first_name = first_name
        self.last_name = last_name
        self.position = position
        self.average = average
        self.clutch = clutch
        self.bats = bats
        self.throws = throws
        self.field = field
        self.speed = speed

        # New offensive statistics
        self.obp = obp
        self.slg = slg
        self.ops = ops
        self.babip = babip
        self.iso = iso

        self.hit_outcomes = {}
        self.direction_outcomes = {}
        self.hit_strengths = {}

    def __repr__(self):
        return f"{self.team}, {self.first_name} {self.last_name}, {self.position}"

    @staticmethod
    def load_players(filepath):
        data = pd.read_csv(filepath)
        players = []
        for _, row in data.iterrows():
            player = Player(
                player_id=row['id'],
                team=row['TM'],
                base_path='base_path',  # Update this if base_path is required
                age=row['AGE'],
                first_name=row['FIRST'],
                last_name=row['LAST'],
                position=row['POS'],
                bats=row['B'],
                throws=row['T'],
                average=row['AVG'],
                clutch=row['CLU'],
                field=row.get('FLD'),
                speed=row.get('SPD'),  # Use .get() to handle missing speed for pitchers
                obp=row.get('OBP'),   # New statistics
                babip=row.get('BABIP'),
                slg=row.get('SLG'),
                ops=row.get('OPS'),
                iso=row.get('ISO')
            )
            players.append(player)
        return players