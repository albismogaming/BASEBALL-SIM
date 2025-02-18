import traceback
from SIM_GAMEDAY import *
from SIM_LGDATA import *
from SIM_SCOREBOARD import *

class SimulationTester:
    def __init__(self, num_simulations, league, predefined_teams=None, use_predefined=True):
        self.num_simulations = num_simulations
        self.league = league
        self.predefined_teams = predefined_teams
        self.use_predefined = use_predefined
        self.errors = []
        self.outcome_counts = {}
        
    def run_simulations(self):
        """Run a specified number of simulations and log results."""
        for i in range(self.num_simulations):
            try:
                self.run_single_simulation(i + 1)
            except Exception as e:
                error_msg = f"Simulation {i + 1}: {str(e)}"
                self.errors.append(error_msg)
                traceback.print_exc()
        
        self.display_results()
    
    def run_single_simulation(self, simulation_number):
        """Run a single game simulation, log outcomes, and detect issues."""
        # Initialize the game with optional predefined teams
        game = SimulateGame(
            league=self.league,
            predefined_teams=self.predefined_teams if self.use_predefined else None,
            use_predefined=self.use_predefined
        )
        game.play_ball()  # Run a full game simulation
        
        # Log the outcomes for statistical analysis
        self.log_final_score(game.gamestate)
    
    def log_final_score(self, gamestate):
        """Record the final score after each game."""
        away_team_score = gamestate.stats['away_team']['score']
        home_team_score = gamestate.stats['home_team']['score']
        
        # Store each game's final score in a list
        game_result = f"{gamestate.away_team} - {away_team_score} | {gamestate.home_team} - {home_team_score}"
        if game_result not in self.outcome_counts:
            self.outcome_counts[game_result] = 0
        self.outcome_counts[game_result] += 1
    
    def display_results(self):
        """Display final scores of simulations and any errors encountered."""
        print("\nSIMULATION RESULTS: FINAL SCORES")
        for game_result, count in self.outcome_counts.items():
            print(f"GAME {count}: {game_result}")
        
        print("\nErrors Encountered:")
        for error in self.errors:
            print(error)


# Example usage:
if __name__ == "__main__":
    league = LeagueAverages()  # Replace with your actual league instance
    predefined_teams = ('NYY', 'LAD')  # Set predefined teams for testing
    num_simulations = 11  # Set the number of simulations
    
    tester = SimulationTester(num_simulations, league, predefined_teams=predefined_teams, use_predefined=True)
    tester.run_simulations()
    exit_button()
