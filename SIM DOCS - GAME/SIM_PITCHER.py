import os
import pandas as pd
import numpy as np
from SIM_PLAYER import *
from FILE_PATHS import *

class Pitcher(Player):
    def __init__(self, player_id, team, age, first_name, last_name, position, average, clutch, bats, throws, hit_outcomes, direction_outcomes, hit_strengths):
        super().__init__(player_id, team, None, age, first_name, last_name, position, average, clutch, bats, throws)
        self.stats = {
            'innings_pitched': 0.0,
            'pitches_thrown': 0,
            'hits': 0,
            'runs_allowed': 0,
            'earned_runs': 0,
            'home_runs': 0,
            'strikeouts': 0,
            'walks': 0,
            'hit_by_pitch': 0,
            'outs_recorded': 0  # Track outs recorded
        }
        self.hit_outcomes = hit_outcomes
        self.direction_outcomes = direction_outcomes
        self.hit_strengths = hit_strengths

    def get_stats_as_dict(self):
        return self.stats

    def get_stats_as_list(self):
        # Calculate formatted innings pitched based on outs recorded
        total_outs = self.stats.get('outs_recorded', 0)
        full_innings = total_outs // 3
        additional_outs = total_outs % 3
        formatted_innings_pitched = f"{full_innings}.{additional_outs}"
        
        # Return the player stats list
        return [
            self.last_name.upper(),
            self.position,
            formatted_innings_pitched,
            self.stats.get('pitches_thrown', 0),
            self.stats.get('hits', 0),
            self.stats.get('runs_allowed', 0),
            self.stats.get('earned_runs', 0),
            self.stats.get('home_runs', 0),
            self.stats.get('strikeouts', 0),
            self.stats.get('walks', 0),
            self.stats.get('hit_by_pitch', 0), 
            self.get_era()  # Assuming get_era() computes the ERA correctly
        ]

    def update_stats(self, game_stats):
        for stat, value in game_stats.items():
            if stat == 'innings_pitched':
                self.stats[stat] += float(value)
            else:
                self.stats[stat] += int(value)

    def record_outs(self, outs):
        self.stats['outs_recorded'] += outs
        self.calculate_innings_pitched()

    def calculate_innings_pitched(self):
        # Ensure outs_recorded is accurately converted to display format but stored as raw outs
        total_outs = self.stats.get('outs_recorded', 0)
        full_innings = total_outs // 3
        additional_outs = total_outs % 3
        self.stats['innings_pitched'] = f"{full_innings}.{additional_outs}"

    def get_era(self):
        # Calculate innings pitched based on outs recorded
        outs_recorded = self.stats.get('outs_recorded', 0)
        full_innings = outs_recorded // 3
        additional_outs = outs_recorded % 3
        total_innings_pitched = full_innings + additional_outs / 3.0

        # Calculate ERA if there are innings pitched
        if total_innings_pitched > 0:
            era = (self.stats['earned_runs'] / total_innings_pitched) * 9
            return f"{era:.3f}"  # Format ERA to three decimal places as a string
        else:
            return "0.000"  # Return "0.000" when no innings pitched

    def record_outcome(self, pitches=0, hit_type=None, strikeout=False, walk=False, hit_by_pitch=False, runs=0, earned_runs=0, outs=0, sac_fly=False, fielders_choice=False, wild_pitch=False, passed_ball=False, po_first=False, po_second=False, sb_second=False):

        self.stats['pitches_thrown'] += pitches
        
        # Handle various outcomes
        if hit_type in ['groundout', 'flyout', 'lineout', 'popout']:
            self.record_outs(outs)
        elif hit_type in ['single', 'double', 'triple', 'homerun']:
            self.record_outs(outs)
            self.stats['hits'] += 1
            if hit_type == 'homerun':
                self.stats['home_runs'] += 1

        if strikeout:
            self.stats['strikeouts'] += 1
            self.record_outs(outs)

        if walk:
            self.stats['walks'] += 1

        if hit_by_pitch:
            self.stats['hit_by_pitch'] += 1

        if sac_fly or fielders_choice:
            self.record_outs(outs)

        if po_first or po_second:
            self.record_outs(outs)

        if sb_second:
            self.record_outs(outs)

        # Update runs and earned runs once at the end
        if runs > 0 or earned_runs > 0:
            self.stats['runs_allowed'] += runs
            self.stats['earned_runs'] += earned_runs
            
    @staticmethod
    def load_pitchers(filepath):
        data = pd.read_csv(filepath)
        pitchers = []
        for _, row in data.iterrows():
            hit_outcomes = {
                'SINGLE': row['SINGLE'],
                'DOUBLE': row['DOUBLE'],
                'TRIPLE': row['TRIPLE'],
                'HOMERUN': row['HOMERUN'],
                'WALK': row['WALK'],
                'STRIKEOUT': row['STRIKEOUT'],
                'HBP': row['HBP'],
                'OUT': row['OUT'],
                'GROUNDOUT': row['GROUNDOUT'],
                'FLYOUT': row['FLYOUT'],
                'LINEOUT': row['LINEOUT'],
                'POPOUT': row['POPOUT']
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

            pitcher = Pitcher(
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
                hit_outcomes=hit_outcomes,
                direction_outcomes=direction_outcomes,
                hit_strengths=hit_strengths            
            )
            pitchers.append(pitcher)
        return pitchers