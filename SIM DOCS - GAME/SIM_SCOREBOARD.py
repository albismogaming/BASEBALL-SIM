from SIM_CORE import *
from SIM_SETTINGS import *
from SIM_UTILS import *
from FILE_PATHS import *
from tabulate import tabulate
import os, sys, time, string, pandas as pd, numpy as np

class Scoreboard:
    def __init__(self, gamestate):
        self.gamestate = gamestate

    def display_bar(self):
        print(rgb_colored("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■", JET))
        short_wait()

    def display_batter_pitcher(self, batter, pitcher, advantage):
        """Display batter, pitcher, and advantage information."""
        if advantage == "BATTER":
            print(rgb_colored(f"BAT: [{batter.bats.upper()}] {batter.last_name.upper():14}        (ADV)  AVG: {batter.average:.3f}", MINT))
            print(rgb_colored(f"PIT: [{pitcher.throws.upper()}] {pitcher.last_name.upper():14} P:{pitcher.stats['pitches_thrown']:3}         AVG: {pitcher.average:.3f}", PASTEL_GRAY))
            self.display_bar()
        elif advantage == "PITCHER":
            print(rgb_colored(f"BAT: [{batter.bats.upper()}] {batter.last_name.upper():14}               AVG: {batter.average:.3f}", PASTEL_GRAY))
            print(rgb_colored(f"PIT: [{pitcher.throws.upper()}] {pitcher.last_name.upper():14} P:{pitcher.stats['pitches_thrown']:3}  (ADV)  AVG: {pitcher.average:.3f}", MINT))
            self.display_bar()
        else:
            print(rgb_colored(f"BAT: [{batter.bats.upper()}] {batter.last_name.upper():14} AVG: {batter.average:.3f}", PASTEL_GRAY))
            print(rgb_colored(f"PIT: [{pitcher.throws.upper()}] {pitcher.last_name.upper():14} P:{pitcher.stats['pitches_thrown']:3}  AVG: {pitcher.average:.3f}", PASTEL_GRAY))
            self.display_bar()


    def display_pitching_change(self, outgoing_pitcher, incoming_pitcher):
        print_delay("THE MANAGER IS COMING OUT AND APPEARS TO WANT TO MAKE A PITCHING CHANGE...")
        print_delay(f"OUT:{outgoing_pitcher.upper()}") 
        print_delay(f"IN :{incoming_pitcher.upper()}")

    def base_display(self, base, max_length=7, width=12):
        """Formats the base display with consistent width, including base name inside the colored string."""
        player = self.gamestate.bases.get(base)  # Get the player on base

        if player:
            # Truncate if name is too long, otherwise pad with spaces
            formatted_name = player.last_name[:max_length].upper().ljust(max_length)

            # Format runner display with speed, including base name inside the color formatting
            runner = rgb_colored(f"[{base}]: {formatted_name}[{player.speed}]", GOLDEN_YELLOW)
        else:
            runner = rgb_colored(f"[{base}]: " + "-" * width, JET)  # Keep width fixed for empty bases

        return runner

    def scoreboard(self):
        network = rgb_colored(f"= MLB =", WHITE, DARK_GRAY)
        inn_tb = rgb_colored(" ▲ ", YELLOW, DARK_GRAY) if self.gamestate.top_or_bottom == "TOP" else rgb_colored(" ▼ ", YELLOW, DARK_GRAY)
        inn = rgb_colored(f" {ordinal(self.gamestate.current_inning):4} ", YELLOW, DARK_GRAY)
        outs = rgb_colored(f" {(self.gamestate.outs)} OUTS ", YELLOW, DARK_GRAY)

        a_t = rgb_colored(f"⚾️{self.gamestate.away_team}  ", WHITE, DODGER_BLUE)
        a_s = rgb_colored(f" {(self.gamestate.stats['away_team']['score']):2} ", BLACK, WHITE)
        
        h_t = rgb_colored(f"⚾️{self.gamestate.home_team}  ", WHITE, NAVY_BLUE)
        h_s = rgb_colored(f" {(self.gamestate.stats['home_team']['score']):2} ", BLACK, WHITE)
        
        div1 = rgb_colored(f"┃┃", WHITE)
        div2 = rgb_colored(f"┃", WHITE)
        first = rgb_colored("▄▄", GOLDEN_YELLOW) if self.gamestate.bases['1ST'] else rgb_colored("▄▄", WHITE)
        second = rgb_colored("▀▀", GOLDEN_YELLOW) if self.gamestate.bases['2ND'] else rgb_colored("▀▀", WHITE)
        third = rgb_colored("▄▄", GOLDEN_YELLOW) if self.gamestate.bases['3RD'] else rgb_colored("▄▄", WHITE)

        on_first = self.base_display('1ST')
        on_second = self.base_display('2ND')
        on_third = self.base_display('3RD')

        scoreboard = f"""
{rgb_colored(f"┏┳━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳┓", WHITE)}
{div1}{network}{div2}{a_t}{a_s}{div2}{h_t}{h_s}{div2}{inn_tb}{inn}{div2}{outs}{div2} {third}{second}{first} {div1}
{rgb_colored(f"┣┣━━━━━━━┻━━━━━━━━━━━━┻━━━━━━━━━━━━┻━━━━━━━━━┻━━━━━━━━┻━━━━━━━━┫┫", WHITE)}
{div1} {(f"{on_first:14}")} {(f"{on_second:14}")} {(f"{on_third:14}")} {div1}
{rgb_colored(f"┗┻━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┻┛", WHITE)}
"""
        long_wait()
        print(scoreboard)
        long_wait()


    def playball_intro(self):
        message = rgb_colored(f"┃┃   PLAY BALL!   ┃┃", WHITE)
        playball_intro = f"""
{rgb_colored(f"┏┳━━━━━━━━━━━━━━━━┳┓", WHITE)}
{message}
{rgb_colored(f"┗┻━━━━━━━━━━━━━━━━┻┛", WHITE)}
"""
        long_wait()
        print(playball_intro)
        long_wait()


    def start_inning(self):
        message = rgb_colored(f"┃┃ START OF THE {ordinal(self.gamestate.current_inning):4} INN ┃┃", WHITE)
        start_inning = f"""
{rgb_colored(f"┏┳━━━━━━━━━━━━━━━━━━━━━━━┳┓", WHITE)}
{message}
{rgb_colored(f"┗┻━━━━━━━━━━━━━━━━━━━━━━━┻┛", WHITE)}
"""
        long_wait()
        print(start_inning)
        long_wait()


    def display_inning(self, inning_stage):
        top = rgb_colored(f"┃       ┃ Rs ┃ Hs ┃ Es ┃", WHITE)
        if inning_stage == "MID":
            bottom = rgb_colored(f" -  MID OF THE {ordinal(self.gamestate.current_inning):4} - ", WHITE)
        elif inning_stage == "END":
            bottom = rgb_colored(f" -  END OF THE {ordinal(self.gamestate.current_inning):4} - ", WHITE)
        else:
            raise ValueError("Invalid inning stage")

        away_team = rgb_colored(f"⚾️{self.gamestate.away_team} ", WHITE, RED)
        away_score = rgb_colored(f" {self.gamestate.stats['away_team']['score']:2} ", BLACK, WHITE)
        away_hits = rgb_colored(f" {self.gamestate.stats['away_team']['hits']:2} ", BLACK, WHITE)
        away_errors = rgb_colored(f" {self.gamestate.stats['away_team']['errors']:2} ", BLACK, WHITE)
        home_team = rgb_colored(f"⚾️{self.gamestate.home_team} ", WHITE, BLUE)
        home_score = rgb_colored(f" {self.gamestate.stats['home_team']['score']:2} ", BLACK, WHITE)
        home_hits = rgb_colored(f" {self.gamestate.stats['home_team']['hits']:2} ", BLACK, WHITE)
        home_errors = rgb_colored(f" {self.gamestate.stats['home_team']['errors']:2} ", BLACK, WHITE)

        inning_display = f"""
{rgb_colored(f"┏━━━━━━━┳━━━━┳━━━━┳━━━━┓", WHITE)}
{rgb_colored(f"{top}", WHITE)}
{rgb_colored(f"┣━━━━━━━╋━━━━╋━━━━╋━━━━┫", WHITE)}
{rgb_colored(f"┃{away_team}┃{away_score}┃{away_hits}┃{away_errors}┃", WHITE)}
{rgb_colored(f"┣━━━━━━━╋━━━━╋━━━━╋━━━━┫", WHITE)}
{rgb_colored(f"┃{home_team}┃{home_score}┃{home_hits}┃{home_errors}┃", WHITE)}
{rgb_colored(f"┣━━━━━━━┻━━━━┻━━━━┻━━━━┫", WHITE)}
{rgb_colored(f"┃{bottom}┃", WHITE)}
{rgb_colored(f"┗━━━━━━━━━━━━━━━━━━━━━━┛", WHITE)}
"""
        long_wait()
        print(inning_display)
        long_wait()

    def middle_inning(self):
        self.display_inning("MID")

    def end_inning(self):
        self.display_inning("END")

    def final(self):
        message = rgb_colored(f"      FINAL SCORE     ", WHITE)
        away_team = rgb_colored(f"⚾️{self.gamestate.away_team} ", WHITE, RED)
        away_score = rgb_colored(f" {self.gamestate.stats['away_team']['score']:2} ", BLACK, WHITE)
        home_team = rgb_colored(f"⚾️{self.gamestate.home_team} ", WHITE, BLUE)
        home_score = rgb_colored(f" {self.gamestate.stats['home_team']['score']:2} ", BLACK, WHITE)

        final_score = f"""
{rgb_colored(f"┏┳━━━━━━━━━━━━━━━━━━━━━━━┳┓", WHITE)}
{rgb_colored(f"┃┃{message} ┃┃", WHITE)}
{rgb_colored(f"┣╋━━━━━━━━━━━┳━━━━━━━━━━━╋┫", WHITE)}
{rgb_colored(f"┃┃{away_team}{away_score}┃{home_team}{home_score}┃┃", WHITE)}
{rgb_colored(f"┗┻━━━━━━━━━━━┻━━━━━━━━━━━┻┛", WHITE)}
"""
        long_wait()
        print(final_score)
        long_wait()


    def boxscore(self):
        max_innings = max(len(self.gamestate.stats['away_team']['score_by_inning']), len(self.gamestate.stats['home_team']['score_by_inning']))

        # Append 'X' if the game ends and the home team does not bat in what would be their half of the inning
        if self.gamestate.current_inning >= INNINGS and self.gamestate.stats['home_team']['score'] > self.gamestate.stats['away_team']['score'] and self.gamestate.top_or_bottom == "TOP":
            while len(self.gamestate.stats['home_team']['score_by_inning']) < self.gamestate.current_inning:  # Ensure there's space for 'X'
                self.gamestate.stats['home_team']['score_by_inning'].append(0)  # Pad innings if needed before appending 'X'
            self.gamestate.stats['home_team']['score_by_inning'][-1] = 'X'  # Replace the last 0 or append 'X'

        # Coloring and preparing headers
        headers = [rgb_colored("FINAL", YELLOW)] + \
                  [rgb_colored(f"{(i)}", YELLOW) for i in range(1, max_innings + 1)] + \
                  [rgb_colored("R", YELLOW), 
                   rgb_colored("H", YELLOW), 
                   rgb_colored("E", YELLOW)]

        away_row = [rgb_colored(f"{self.gamestate.away_team}", RED)] + \
                   [rgb_colored(str(score), WHITE) for score in self.gamestate.stats['away_team']['score_by_inning']] + \
                   [rgb_colored(str(self.gamestate.stats['away_team']['score']), RED), 
                    rgb_colored(str(self.gamestate.stats['away_team']['hits']), RED), 
                    rgb_colored(str(self.gamestate.stats['away_team']['errors']), RED)]

        home_row = [rgb_colored(f"{self.gamestate.home_team}", BLUE)] + \
                   [rgb_colored(str(score), WHITE) for score in self.gamestate.stats['home_team']['score_by_inning']] + \
                   [rgb_colored(str(self.gamestate.stats['home_team']['score']), BLUE), 
                    rgb_colored(str(self.gamestate.stats['home_team']['hits']), BLUE), 
                    rgb_colored(str(self.gamestate.stats['home_team']['errors']), BLUE)]

        print()
        print(tabulate([away_row, home_row], headers=headers, tablefmt="heavy_grid", numalign="center", stralign="center"))
        print()
