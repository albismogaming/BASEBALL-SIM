# import random

# class BasketballSimulatorNoMaxPossessions:
#     def __init__(self, home_team, away_team):
#         self.teams = {home_team: 0, away_team: 0}  # Scores
#         self.possession = home_team  # Starting possession
#         self.opponent = away_team
#         self.quarter = 1
#         self.time_remaining = 12 * 60  # 12 minutes per quarter (in seconds)
#         self.fouls = {home_team: 0, away_team: 0}  # Team fouls per quarter
#         self.play_log = []  # Stores play-by-play events
#         self.shot_clock = 24  # Shot clock for possessions

#     def get_opponent(self):
#         return self.opponent if self.possession == list(self.teams.keys())[0] else list(self.teams.keys())[0]

#     def simulate_possession(self):
#         """Simulate a single possession with a shot attempt, turnover, or foul."""
#         if self.time_remaining <= 0:
#             return  # End quarter if time runs out

#         play_result = ""
#         event = random.choices(["2PT", "3PT", "FT", "Turnover"], weights=[45, 30, 15, 10])[0]

#         if event == "Turnover":
#             play_result = f"{self.possession} commits a turnover."
#         else:
#             shot_made = random.random() < (0.46 if event == "2PT" else 0.35)  # Shooting percentages

#             if event == "FT":
#                 self.fouls[self.get_opponent()] += 1  # Foul recorded
#                 made_free_throws = sum(random.random() < 0.75 for _ in range(2))  # Two free throws
#                 self.teams[self.possession] += made_free_throws
#                 play_result = f"{self.possession} was fouled. Made {made_free_throws} free throws."

#             elif shot_made:
#                 points = 2 if event == "2PT" else 3
#                 self.teams[self.possession] += points
#                 play_result = f"{self.possession} makes a {points}-pointer!"
#             else:
#                 # Missed shot, determine rebound
#                 if random.random() < 0.3:  # 30% chance of an offensive rebound
#                     play_result = f"{self.possession} misses a {event}. Offensive rebound!"
#                     return  # Retain possession, simulate again
#                 else:
#                     play_result = f"{self.possession} misses a {event}. {self.get_opponent()} gets the rebound."

#         self.play_log.append(play_result)
#         self.switch_possession()  # Change possession after play

#     def switch_possession(self):
#         """Switch possession to the other team."""
#         self.possession, self.opponent = self.opponent, self.possession
#         self.shot_clock = 24  # Reset shot clock
#         self.time_remaining -= random.randint(10, 24)  # Time used per possession

#     def simulate_quarter(self):
#         """Simulate a full quarter without a max possessions limit."""
#         self.play_log.append(f"--- START OF QUARTER {self.quarter} ---")
#         while self.time_remaining > 0:
#             self.simulate_possession()

#         self.play_log.append(f"--- END OF QUARTER {self.quarter} ---\n")
#         self.quarter += 1
#         self.time_remaining = 12 * 60  # Reset clock for next quarter
#         self.fouls = {team: 0 for team in self.teams}  # Reset fouls

#     def simulate_game(self):
#         """Simulate a full four-quarter game."""
#         for _ in range(4):
#             self.simulate_quarter()

#         # Display Final Score
#         self.play_log.append("=== FINAL SCORE ===")
#         for team, score in self.teams.items():
#             self.play_log.append(f"{team}: {score}")

#         return self.play_log

# # Run the simulation
# home_team = "Lakers"
# away_team = "Celtics"
# sim = BasketballSimulatorNoMaxPossessions(home_team, away_team)
# game_log = sim.simulate_game()

# # Display final score
# final_score = {team: score for team, score in sim.teams.items()}
# print(final_score)

