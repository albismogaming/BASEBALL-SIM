from SIM_CORE import *
from SIM_SETTINGS import *
from SIM_UTILS import *
from FILE_PATHS import *
from SIM_PLAYER import *
import re, os, sys, time, string, pandas as pd, numpy as np

class Batter(Player):
    def __init__(self, player_id, team, age, first_name, last_name, position, average, clutch, bats, throws, field, speed, obp, babip, slg, ops, iso, hit_outcomes, direction_outcomes, hit_strengths):
        super().__init__(player_id, team, None, age, first_name, last_name, position, average, clutch, bats, throws, field, speed, obp, babip, slg, ops, iso)
        self.stats = {
            "at_bats": 0, "hits": 0, "singles": 0, "doubles": 0, "triples": 0, "home_runs": 0,
            "strikeouts": 0, "walks": 0, "hit_by_pitch": 0, "runs": 0, "rbi": 0
        }
        self.hit_outcomes = hit_outcomes
        self.direction_outcomes = direction_outcomes
        self.hit_strengths = hit_strengths
        self.reset_at_bat_outcomes()

    def reset_at_bat_outcomes(self):
        self.had_hit = False
        self.hit_type = None
        self.had_strikeout = False
        self.had_walk = False
        self.had_hit_by_pitch = False

    def get_stats_as_dict(self):
        return self.stats

    def get_stats_as_list(self):
        return [
            self.last_name.upper(), self.position, self.stats['at_bats'], self.stats['hits'], self.stats['singles'],
            self.stats['doubles'], self.stats['triples'], self.stats['home_runs'], self.stats['strikeouts'],
            self.stats['walks'], self.stats['hit_by_pitch'], self.calculate_batting_average()
        ]

    def record_at_bat(self, hit_type=None, strikeout=False, walk=False, hit_by_pitch=False):
        """Records an at-bat outcome, updating the batter's stats."""
        
        # ✅ Walks and hit-by-pitches do NOT count as an at-bat
        if not walk and not hit_by_pitch:
            self.stats["at_bats"] += 1  

        # ✅ Handling hits
        if hit_type:
            self.stats["hits"] += 1
            hit_mapping = {
                "single": "singles",
                "double": "doubles",
                "triple": "triples",
                "homerun": "home_runs"
            }
            if hit_type in hit_mapping:
                self.stats[hit_mapping[hit_type]] += 1

        # ✅ Handling other outcomes
        if strikeout:
            self.stats["strikeouts"] += 1
        if walk:
            self.stats["walks"] += 1
        if hit_by_pitch:
            self.stats["hit_by_pitch"] += 1

        # ✅ Reset temporary tracking for at-bat outcomes
        self.reset_at_bat_outcomes()

    def calculate_batting_average(self):
        if self.stats['at_bats'] > 0:
            return f"{(self.stats['hits'] / self.stats['at_bats']):.3f}"
        else:
            return 0.0

    def get_batting_average(self):
        return self.average  # Assuming average is already a float value
    
    @staticmethod
    def load_batters(df):
        batters = []
        for _, row in df.iterrows():
            hit_outcomes = {
                'SINGLE': float(row['SINGLE']),
                'DOUBLE': float(row['DOUBLE']),
                'TRIPLE': float(row['TRIPLE']),
                'HOMERUN': float(row['HOMERUN']),
                'WALK': float(row['WALK']),
                'STRIKEOUT': float(row['STRIKEOUT']),
                'HBP': float(row['HBP']),
                'OUT': float(row['OUT']),
                'GROUNDOUT': float(row['GROUNDOUT']),
                'FLYOUT': float(row['FLYOUT']),
                'LINEOUT': float(row['LINEOUT']),
                'POPOUT': float(row['POPOUT']),
            }
            direction_outcomes = {
                'PULL': row['Pull%'],
                'CENT': row['Cent%'],
                'OPPO': row['Oppo%']              
            }
            hit_strengths = {
                'SOFT': row['Soft%'],
                'MEDM': row['Med%'],
                'HARD': row['Hard%']
            }

            batter = Batter(
                player_id=row['id'],
                team=row['TM'],
                position=row['POS'],
                age=row['AGE'],
                first_name=row['FIRST'],
                last_name=row['LAST'],
                bats=row['B'],
                throws=row['T'],
                average=row['AVG'],
                clutch=row['CLU'],
                speed=row['SPD'],
                field=row['FLD'],
                obp=row['OBP'],   # New statistics
                babip=row['BABIP'],
                slg=row['SLG'],
                ops=row['OPS'],
                iso=row['ISO'],
                hit_outcomes=hit_outcomes,
                direction_outcomes=direction_outcomes,
                hit_strengths=hit_strengths
            )
            batters.append(batter)
        return batters
