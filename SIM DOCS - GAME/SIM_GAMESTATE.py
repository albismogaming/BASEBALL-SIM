from SIM_SETTINGS import *
from SIM_SINGLE import *
from SIM_DOUBLE import *
from SIM_TRIPLE import *
from SIM_HOMERUN import *
from SIM_GROUNDOUTS import *
from SIM_FLYOUTS import *
from SIM_STRIKEOUTS import *
from SIM_POPOUTS import *
from SIM_HBP_BB import *
from SIM_WP_PB import *
from SIM_STEALS import *
from SIM_BATTER import *
from SIM_SCENARIO_MANAGER import *
from SIM_OUTCOME_MANAGER import *
from SIM_STATS_MANAGER import *

class GameState:
    def __init__(self, away_team, home_team, league):
        self.current_inning = 1
        self.top_or_bottom = "TOP"
        self.balls = 0
        self.strikes = 0
        self.outs = 0
        self.bases = {'1ST': None, '2ND': None, '3RD': None}
        self.away_team = away_team
        self.home_team = home_team
        self.hits_hit = 0
        self.runs_scored = 0
        self.pickoffs = 0
        self.is_walk_off = False
        self.is_inning_over = False
        self.is_game_over = False
        self.outcome_manager = OutcomeManager(self, league)

        self.stats = {
            'away_team': {'score': 0, 'hits': 0, 'errors': 0, 'score_by_inning': []},
            'home_team': {'score': 0, 'hits': 0, 'errors': 0, 'score_by_inning': []}
        }

    @property
    def score_difference(self):
        return abs(self.stats['home_team']['score'] - self.stats['away_team']['score'])

    @property
    def current_count(self):
        """Return the current count as a formatted string, e.g., '2-1' for 2 balls, 1 strike."""
        return f"{self.balls}-{self.strikes}"

    def reset_count(self):
        """Reset the ball and strike count for a new at-bat."""
        self.balls = 0
        self.strikes = 0

    def update_count(self, pitch_code, count_balls, count_strikes):
        if pitch_code in ['S', 'C', 'F', 'U', 'V'] and count_strikes < 2:
            count_strikes += 1
        elif pitch_code in ['B','W', 'P', 'T'] and count_balls < 3:
            count_balls += 1
        return count_balls, count_strikes

    def update_score(self, hits_hit, runs_scored):
        """Update team hits and call increment_run for scoring."""
        current_team = 'away_team' if self.top_or_bottom == "TOP" else 'home_team'

        self.stats[current_team]['hits'] += hits_hit
        self.increment_run(runs_scored)
        self.hits_hit = 0
        self.runs_scored = 0

    def update_outs(self, outs_recorded):
        """Updates the number of outs and checks if the inning should end."""
        self.outs += outs_recorded

    def increment_run(self, runs):
        """Increment the score for the current team and update inning score."""
        current_team = 'away_team' if self.top_or_bottom == "TOP" else 'home_team'

        # ✅ If this is a walk-off scenario, limit the runs to only what is needed to win
        if self.is_walk_off_scenario() and current_team == "home_team":
            runs = self.get_walk_off_runs_needed(runs)  # ✅ Limit to required runs

        self.stats[current_team]['score'] += runs

        # Ensure score_by_inning list is long enough for the current inning
        while len(self.stats[current_team]['score_by_inning']) < self.current_inning:
            self.stats[current_team]['score_by_inning'].append(0)

        # Add runs to the current inning's score
        self.stats[current_team]['score_by_inning'][self.current_inning - 1] += runs

        # ✅ If a walk-off occurred, trigger the end of the game
        if self.is_walk_off_scenario() and current_team == "home_team":
            self.set_walk_off()

    def clear_base(self, base):
        """Clear a specific base."""
        self.bases[base] = None

    def set_runners_on_base(self):
        """Retrieve runners currently on base."""
        return {
            '1ST': self.bases['1ST'],
            '2ND': self.bases['2ND'],
            '3RD': self.bases['3RD']
        }

    def move_runner(self, from_base, to_base, runner=None):
        """
        Move a runner (or batter) from one base to another.

        - If `from_base` is "HOME", the runner is the batter.
        - If `to_base` is "OUT", the runner is out (outs are handled separately).
        - This function ONLY moves runners and does NOT update runs or outs.
        """
        if from_base == "HOME" and runner:  # Batter movement
            if to_base != "OUT":  # Only move if not out
                if not self.bases.get(to_base):  # Ensure base isn't occupied
                    self.bases[to_base] = runner  # Place batter on base
        else:
            if not self.bases.get(to_base):  # Ensure destination is empty
                self.bases[to_base] = self.bases[from_base]  # Move runner

        self.clear_base(from_base)  # Always clear the original base

    def get_base_state(self):
        """Returns a string representing the current base state."""
        base_tuple = (self.bases["1ST"] is not None, 
                    self.bases["2ND"] is not None, 
                    self.bases["3RD"] is not None)

        base_states = {
            (True, True, True): "BASES_LOADED",
            (True, False, False): "RUNNER_ON_FIRST",
            (False, True, False): "RUNNER_ON_SECOND",
            (False, False, True): "RUNNER_ON_THIRD",
            (True, True, False): "FIRST_AND_SECOND",
            (True, False, True): "FIRST_AND_THIRD",
            (False, True, True): "SECOND_AND_THIRD",
            (False, False, False): "BASES_EMPTY"
        }

        return base_states.get(base_tuple, "BASES_EMPTY")  # Default to "BASES_EMPTY"

    def is_team_trailing_by_two(self):
        """Check if either team is trailing by two or more runs."""
        home_score = self.stats['home_team']['score']
        away_score = self.stats['away_team']['score']
        return abs(home_score - away_score) >= 2
        
    def toggle_inning(self):
        # Switch between top and bottom or increment the inning
        if self.top_or_bottom == "TOP":
            self.top_or_bottom = "BOT"
        else:
            self.top_or_bottom = "TOP"
            self.current_inning += 1

    def end_inning(self):
        """Checks if the inning should end and marks it as over."""
        if self.outs >= 3:
            self.is_inning_over = True
            return True
        return False

    def end_of_game(self):
        """Checks if the game should end due to a walk-off or completed innings."""

        # ✅ If a walk-off occurs, end the game immediately
        if self.is_walk_off:
            self.is_game_over = True
            return True  

        # ✅ If it's the top of the 9th or later, the game should NOT end unless the home team is leading.
        if self.current_inning >= INNINGS and self.top_or_bottom == "TOP":
            if self.stats['home_team']['score'] > self.stats['away_team']['score']:
                self.is_game_over = True  # ✅ Home team is ahead after the top half, game over.
                return True
            return False  # ✅ If the away team is ahead, the bottom half must be played.

        # ✅ If it's the bottom of the 9th or later, and the away team is leading, end the game.
        if self.current_inning >= INNINGS and self.top_or_bottom == "BOT":
            if self.stats['away_team']['score'] > self.stats['home_team']['score']:
                self.is_game_over = True  # ✅ Away team wins after the full inning.
                return True
        return False  # ✅ If none of these conditions are met, the game continues.

    def reset_inning(self):
        self.is_inning_over = False
        self.outs = 0
        self.hits_hit = 0
        self.runs_scored = 0
        self.bases = {'1ST': None, '2ND': None, '3RD': None}

    def is_walk_off_scenario(self):
        """Returns True if the home team is batting and can end the game with this run."""
        return (
            self.top_or_bottom == "BOT" and 
            self.current_inning >= INNINGS and 
            self.stats["home_team"]["score"] > self.stats["away_team"]["score"]
        )

    def get_walk_off_runs_needed(self, runs_scored):
        """Returns the number of runs needed for a walk-off."""
        if not self.is_walk_off_scenario():
            return runs_scored  # ✅ If it's not a walk-off, return normal runs scored

        runs_needed = (self.stats["away_team"]["score"] + 1) - self.stats["home_team"]["score"]
        return min(runs_scored, runs_needed)  # ✅ Limit to the necessary runs to win

    def set_walk_off(self):
        """Sets the walk-off toggle to True and ends the game."""
        self.is_walk_off = True
        self.is_inning_over = True
        self.is_game_over = True  # ✅ Ensures no further plays process

    def check_for_wild_pitch_or_passed_ball(self):
        rand_value = np.random.random()
        if rand_value < WILDPITCH:
            return 'W'
        elif rand_value < PASSBALL:
            return 'P'
        return None

    def check_for_pickoff(self):
        """Determine if a pickoff attempt occurs based on runner presence, outs, and runner speed."""
        
        base_state = self.get_base_state()  # ✅ Get current base situation
        runner_on_first = self.bases.get('1ST')
        runner_on_second = self.bases.get('2ND')

        # ✅ If there are no runners on first or second, no pickoff is possible
        if base_state not in ['RUNNER_ON_FIRST', 'RUNNER_ON_SECOND', 'FIRST_AND_SECOND']:
            return None  # No pickoff attempt

        # Initialize pickoff probabilities
        pickoff_prob_first = PICKOFF_1ST if runner_on_first else 0
        pickoff_prob_second = PICKOFF_2ND if runner_on_second else 0

        # ✅ Only apply speed adjustment if a runner is present
        if runner_on_first:
            pickoff_prob_first += runner_on_first.speed * 0.004
        if runner_on_second:
            pickoff_prob_second += runner_on_second.speed * 0.002

        # ✅ Adjust probability based on outs
        outs_adjustment = {0: 0.03, 1: 0.02, 2: 0.01}[self.outs]
        if runner_on_first:
            pickoff_prob_first += outs_adjustment
        if runner_on_second:
            pickoff_prob_second += outs_adjustment

        # ✅ Determine pickoff attempt using final probabilities
        pickoff_attempt = None
        if runner_on_first and runner_on_first.speed > 5 and np.random.random() < pickoff_prob_first:
            pickoff_attempt = '1'  # Pickoff attempt at first
        elif runner_on_second and runner_on_second.speed > 5 and np.random.random() < pickoff_prob_second:
            pickoff_attempt = '2'  # Pickoff attempt at second

        return pickoff_attempt

    def check_for_stealing(self, pitch_type):
        """Check if a steal attempt should occur and return the specific marker based on pitch type."""

        base_state = self.get_base_state()
        # Check if there's a runner on first but no runner on second
        runner_on_first = self.bases.get('1ST')
        runner_on_second = self.bases.get('2ND')
        
        # Only consider a steal if conditions allow
        if runner_on_first and not runner_on_second and runner_on_first.speed >= 5:
            steal_prob = STEALING_PROB

            # Late-game, close score situation adjustment
            if self.current_inning > 6 and abs(self.score_difference) <= 2:
                steal_prob += 0.05

            # Adjust probability based on the number of outs
            if self.outs == 0:
                steal_prob += 0.03
            elif self.outs == 1:
                steal_prob += 0.04
            elif self.outs == 2:
                steal_prob += 0.05

            # Attempt the steal if within probability threshold
            if np.random.random() < steal_prob:
                # Return the specific marker for the type of pitch the steal occurs on
                if pitch_type == 'B':
                    return 'T'  # Steal on a ball
                elif pitch_type == 'S':
                    return 'U'  # Steal on a swinging strike
                elif pitch_type == 'C':
                    return 'V'  # Steal on a called strike

        # No conditions met for steal attempt
        return None

    def process_macro_event(self, outcome, batter, pitcher, runners, fielding_team=None):
        hits_hit, runs_scored, outs_recorded, walk_off = self.outcome_manager.handle_macro_event(outcome, batter, pitcher, runners, fielding_team)
        return hits_hit, runs_scored, outs_recorded, walk_off

    def process_micro_event(self, outcome, batter, pitcher, runners, fielding_team=None):
        hits_hit, runs_scored, outs_recorded, walk_off = self.outcome_manager.handle_micro_event(outcome, batter, pitcher, runners, fielding_team)
        return hits_hit, runs_scored, outs_recorded, walk_off