import time
import sys
import os
import string
import numpy as np
import colorama
from termcolor import colored
from SIM_SETTINGS import *


@staticmethod
def rgb_colored(text, rgb, bg_rgb=None):
    """
    Apply RGB color to text, with an optional background color.

    :param text: The text to color.
    :param rgb: Tuple for the text color (r, g, b).
    :param bg_rgb: Optional tuple for the background color (r, g, b).
    :return: Formatted text with RGB color.
    """
    r, g, b = rgb
    if bg_rgb:
        br, bg, bb = bg_rgb
        return f"\033[1m\033[38;2;{r};{g};{b}m\033[48;2;{br};{bg};{bb}m{text}\033[0m"  # Bold with foreground and background
    else:
        return f"\033[1m\033[38;2;{r};{g};{b}m{text}\033[0m"  # Bold with foreground only

def ordinal(n):
    return "%d%s" % (n,"TSNRHTDD"[(n//10%10!=1)*(n%10<4)*n%10::4])

def initialize_random_seed(seed=RAND_SEED):
    # If no seed is provided, generate a new one and set it
    if seed is None:
        seed = np.random.randint(0, 2**31 - 1)
    np.random.seed(seed)  # Set the seed for reproducibility
    print(f"SIMULATION SEED: {seed}")
    return seed

def time_format(secs):
    mins = int(secs // 60)
    rem_secs = int(secs % 60)
    formatted = f'{mins:02d}:{rem_secs:02d}'
    return formatted

def short_wait():
    time.sleep(SHORT_WAIT)

def long_wait():
    time.sleep(LONG_WAIT)

def print_delay(items, delay=PRINT_DELAY):
    for item in items:
        print(item, end='', flush=True)  # `flush=True` forces the output to be written immediately
        time.sleep(delay)  # Wait for 'delay' seconds before printing the next item
    print()  # Move to the next line after all items are printed

def apply_full_width_digits(text, width=2):
    """Convert all digits to full-width characters and apply padding."""
    full_width_text = ''.join(FULL_WIDTH_DIGITS.get(char, char) for char in str(text))
    # If the score is a single digit, add a leading full-width space
    if len(full_width_text) < width:
        full_width_text = FULL_WIDTH_SPACE + full_width_text
    
    # If the score has more digits than `width`, truncate it to the last two characters
    if len(full_width_text) > width:
        full_width_text = full_width_text[-width:]
    
    return full_width_text

def title_screen():
    title = """
  _______ ___        _______  ___ _______ ___ ___ _______ _______    _______  _______ _______ _______ _______  _______ ___     ___        _______ ___ ___ ___ ___ ___ ___     _______ _______ _______ _______      _______ ___ ___ 
 |   _   |   |      |   _   \|   |   _   |   Y   |   _   |   _   |  |   _   \|   _   |   _   |   _   |   _   \|   _   |   |   |   |      |   _   |   |   Y   |   Y   |   |   |   _   |       |   _   |   _   \    |       |   Y   |
 |.  1   |.  |      |.  1   /|.  |   1___|.      |.  |   |   1___|  |.  1   /|.  1   |   1___|.  1___|.  1   /|.  1   |.  |   |.  |      |   1___|.  |.      |.  |   |.  |   |.  1   |.|   | |.  |   |.  l   /    |___|   |   |   |
 |.  _   |.  |___   |.  _   \|.  |____   |. \_/  |.  |   |____   |  |.  _   \|.  _   |____   |.  __)_|.  _   \|.  _   |.  |___|.  |___   |____   |.  |. \_/  |.  |   |.  |___|.  _   `-|.  |-|.  |   |.  _   1     /  ___/|____   |
 |:  |   |:  1   |  |:  1    |:  |:  1   |:  |   |:  1   |:  1   |  |:  1    |:  |   |:  1   |:  1   |:  1    |:  |   |:  1   |:  1   |  |:  1   |:  |:  |   |:  1   |:  1   |:  |   | |:  | |:  1   |:  |   |    |:  1  \    |:  |
 |::.|:. |::.. . |  |::.. .  |::.|::.. . |::.|:. |::.. . |::.. . |  |::.. .  |::.|:. |::.. . |::.. . |::.. .  |::.|:. |::.. . |::.. . |  |::.. . |::.|::.|:. |::.. . |::.. . |::.|:. | |::.| |::.. . |::.|:. |    |::.. . |   |::.|
 `--- ---`-------'  `-------'`---`-------`--- ---`-------`-------'  `-------'`--- ---`-------`-------`-------'`--- ---`-------`-------'  `-------`---`--- ---`-------`-------`--- ---' `---' `-------`--- ---'    `-------'   `---'
"""
    print(title)


def exit_button():
    text = colored(f"""
┏┳━━━━━━━━━━━━━━━━━━━━━┳┓
┃┃ PRESS ENTER TO EXIT ┃┃
┗┻━━━━━━━━━━━━━━━━━━━━━┻┛                                    
""", 'green', attrs=['bold'])
    input(text)
    
    print()

