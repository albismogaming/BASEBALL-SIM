from SIM_CORE import *
from SIM_SETTINGS import *
from FILE_PATHS import *
import re, os, sys, time, string, pandas as pd, numpy as np

@staticmethod
def rand_val():
    return np.random.random()

@staticmethod
def get_batter_side(batter, pitcher):
    if batter.bats == 'B':  # Switch hitter
        return 'R' if pitcher.throws == 'L' else 'L'
    return batter.bats  # Right or left handed as usual

@staticmethod
def normalize_probabilities(probabilities):
    total_prob = sum(probabilities.values())
    return {outcome: prob / total_prob for outcome, prob in probabilities.items()} if total_prob > 0 else {}

@staticmethod
def adjust_probability(base_prob, speed):
    """
    Adjusts base probability based on speed using a weighted combination of speed scaling and predefined speed tiers.
    """

    # Determine speed-based adjustment from predefined tiers
    speed_adjustment = next(
        (np.random.uniform(low, high) for (low_bound, high_bound), (low, high) in SPEED_TIERS.items() if low_bound <= speed <= high_bound),
        0.0
    )

    # Blended scaling: Mixes linear scaling with tier-based adjustments
    weighted_adjustment = ((speed - AVG_SPEED) / 100) * base_prob * 0.3  

    # Random variation factor
    random_adj = np.random.uniform(-0.03, 0.03) * (speed / 10)

    # Final adjusted probability
    adjusted_prob = base_prob + weighted_adjustment + speed_adjustment + random_adj

    # Ensure probability stays within 0-1 range
    return min(max(adjusted_prob, 0), 1)

@staticmethod
def rev_adjust_probability(base_prob, speed):
    """
    Adjusts a base probability in reverse, making it lower for faster runners and higher for slower ones.
    This is useful for negative outcomes like double plays or getting thrown out on the bases.
    """

    # Determine speed-based adjustment from predefined tiers
    speed_adjustment = next(
        (np.random.uniform(low, high) for (low_bound, high_bound), (low, high) in SPEED_TIERS.items() if low_bound <= speed <= high_bound),
        0.0  # Default to 0 if no matching tier found
    )

    # Weighted Scaling: Blend of linear and tier-based adjustments
    speed_factor = (AVG_SPEED - speed) / 100  # Normalized between -1 and 1 (inverted for reverse effect)
    weighted_adjustment = speed_factor * base_prob * 0.3  # Controls impact strength

    # Random adjustment factor to introduce natural variation (slower runners more affected)
    random_adj = np.random.uniform(-0.03, 0.03) * ((10 - speed) / 10)  

    # Final adjusted probability (subtract speed adjustment for reverse effect)
    adjusted_prob = base_prob + weighted_adjustment - speed_adjustment + random_adj

    # Ensure probability stays within 0-1 range
    return min(max(adjusted_prob, 0), 1)

def strip_ansi(text):
    """Remove ANSI color codes from text."""
    return re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', text)

@staticmethod
def rgb_colored(text, rgb, bg_rgb=None, align=None, width=40):
    """
    Apply RGB color to text, with optional background color and alignment.
    
    :param text: The text to color.
    :param rgb: Tuple for text color (r, g, b).
    :param bg_rgb: Optional tuple for background color (r, g, b).
    :param align: Alignment ('left', 'center', 'right'), default None.
    :param width: Width for alignment (default 40).
    :return: Formatted text with RGB color.
    """
    # Strip ANSI codes to get actual visible text width
    stripped_text = strip_ansi(text)
    
    # Apply alignment before adding color
    if align == "center":
        formatted_text = stripped_text.center(width)
    elif align == "right":
        formatted_text = stripped_text.rjust(width)
    elif align == "left":
        formatted_text = stripped_text.ljust(width)
    else:
        formatted_text = stripped_text  # No alignment

    # Apply color formatting
    r, g, b = rgb
    if bg_rgb:
        br, bg, bb = bg_rgb
        return f"\033[1m\033[38;2;{r};{g};{b}m\033[48;2;{br};{bg};{bb}m{formatted_text}\033[0m"
    else:
        return f"\033[1m\033[38;2;{r};{g};{b}m{formatted_text}\033[0m"

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
    text = rgb_colored(f"""
┏┳━━━━━━━━━━━━━━━━━━━━━┳┓
┃┃ PRESS ENTER TO EXIT ┃┃
┗┻━━━━━━━━━━━━━━━━━━━━━┻┛                                    
""", GREEN)
    input(text)
    
    print()