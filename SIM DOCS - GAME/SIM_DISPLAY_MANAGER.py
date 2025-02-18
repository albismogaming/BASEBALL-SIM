from SIM_SETTINGS import *
from SIM_SCOREBOARD import *
from SIM_FUNCTIONS import *


class DisplayManager:
    def __init__(self, scoreboard, display_enabled=DISPLAY_TOGGLE):
        self.scoreboard = scoreboard
        self.display_enabled = display_enabled

    @staticmethod
    def display_outcome_text(outcomes, display_enabled=DISPLAY_TEXT):
        if display_enabled:
            print_delay(rgb_colored(" ".join(outcomes), WHITE))

    @staticmethod
    def display_pitch_sequence(sequence, starting_pitch_number=1, display_enabled=DISPLAY_PITCH):
        """
        Display each pitch in the sequence with formatted details if display is enabled.
        """
        if display_enabled:
            for i, (count, detail, color) in enumerate(sequence):
                pitch_number_display = starting_pitch_number + i
                print_delay(f"{rgb_colored(f'[{pitch_number_display}]:', WHITE)} {rgb_colored(f'[{count}]', AMBER)} ~~ {rgb_colored(detail, color)}")
            return None  # Sequence completes without interruption


    def display_scoreboard(self):
        """Display the scoreboard if display is enabled."""
        if self.display_enabled:
            self.scoreboard.scoreboard()


    def display_scoreboard_bar(self):
        if self.display_enabled:
            self.scoreboard.display_bar()


    def display_matchup(self, batter, pitcher, advantage):
        """Display the scoreboard if display is enabled."""
        if self.display_enabled:
            self.scoreboard.display_batter_pitcher(batter, pitcher, advantage)


    def display_start_inning(self):
        if self.display_enabled:
            self.scoreboard.start_inning()


    def display_middle_inning(self):
        if self.display_enabled:
            self.scoreboard.middle_inning()
        

    def display_end_inning(self):
        if self.display_enabled:
            self.scoreboard.end_inning()


    def toggle_display(self, enabled):
        """Enable or disable display output."""
        self.display_enabled = enabled
