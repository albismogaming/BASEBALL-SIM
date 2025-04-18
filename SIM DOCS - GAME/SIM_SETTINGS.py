from COLOR_CODES import *

## GAME SETTINGS ##
DISPLAY_TOGGLE = True
DISPLAY_TEXT = True
DISPLAY_PITCH = True

RAND_SEED = 1002665789

STARTER_INNINGS_LIMIT = 5
STARTER_PITCHES_LIMIT = 95
STARTER_RUNS_LIMIT = 5
STARTER_HITS_LIMIT = 8
STARTER_STRUGGLE_LIMIT = 4.3

EXTENDED_STARTER_INNINGS_LIMIT = 7
EXTENDED_STARTER_PITCHES_LIMIT = 110
EXTENDED_STARTER_RUNS_LIMIT = 5
EXTENDED_STARTER_HITS_LIMIT = 10

RELIEVER_INNINGS_LIMIT = 2
RELIEVER_PITCHES_LIMIT = 25
RELIEVER_RUNS_LIMIT = 2
RELIEVER_HITS_LIMIT = 4

EXTENDED_RELIEVER_INNINGS_LIMIT = 3
EXTENDED_RELIEVER_PITCHES_LIMIT = 40
EXTENDED_RELIEVER_RUNS_LIMIT = 3
EXTENDED_RELIEVER_HITS_LIMIT = 5

# // GAME SETTINGS // #
INNINGS = 9
OUTS = 3
LEAGUE_BA = 0.248
AVG_SPEED = 4
SPEED_TIERS = {
    (0.0, 1.0): (-0.09, -0.05),  # Very slow runners
    (1.1, 2.5): (-0.05, -0.02),  
    (2.6, 4.0): (-0.02, 0.00),  
    (4.1, 5.5): (0.00, 0.02),  # Slightly below average
    (5.6, 6.5): (0.02, 0.03),   # Average speed (no major bonus or penalty)
    (6.6, 7.5): (0.03, 0.05),  
    (7.6, 8.5): (0.05, 0.06),  
    (8.6, 10.0): (0.06, 0.08)   # Elite speedsters
}
PICKOFFS = 2

SHORT_WAIT = 0
LONG_WAIT = 0
PRINT_DELAY = 0

# SHORT_WAIT = 0.25
# LONG_WAIT = 0.50
# PRINT_DELAY = 0.03

# // PICKOFF OUTCOME PROBABILITIES //
PICKOFF_1ST = 0.10
PICKOFF_2ND = 0.05
PICKOFF_PROB = 0.03

# // WILD PITCH AND PASSBALL OUTCOME PROBABILITIES //
WILDPITCH = 0.005
PASSBALL = 0.005

# // STEALING CHANCE //
STEALING_CHANCE = 0.70
STEALING_PROB = 0.35

# // AT BAT OUTCOME SETTINGS // #
POSITIVE_OUTCOMES = ['SINGLE', 'DOUBLE', 'TRIPLE', 'HOMERUN', 'WALK', 'STRIKEOUT', 'HBP']
POSITIVE_RANGES = {
    'SINGLE': (1.01, 1.05),
    'DOUBLE': (1.07, 1.13),
    'TRIPLE': (1.03, 1.07),
    'HOMERUN': (1.03, 1.07),
    'WALK': (1.01, 1.05),
    'STRIKEOUT': (0.95, 0.99),
    'HBP': (1.01, 1.03)
}

NEGATIVE_OUTCOMES = ['GROUNDOUT', 'FLYOUT', 'LINEOUT', 'POPOUT']
NEGATIVE_RANGES = {
    'SINGLE': (0.95, 0.99),
    'DOUBLE': (0.95, 0.99),
    'TRIPLE': (0.95, 0.99),
    'HOMERUN': (0.95, 0.99),
    'WALK': (0.95, 0.99),
    'STRIKEOUT': (1.01, 1.03),
    'HBP': (0.95, 0.99)
}

PITCH_CODE_MAP = {
    'B': ('BALL', PASTEL_GREEN),
    'S': ('STRIKE SWINGING', PASTEL_RED),
    'C': ('CALLED STRIKE', CHILI_RED),
    'F': ('FOUL BALL', PASTEL_YELLOW),
    'H': ('HIT BY PITCH', AQUA),
    'X': ('HIT IN PLAY', DODGER_BLUE)
}

FULL_WIDTH_SPACE = '　'  # Full-width space character
FULL_WIDTH_DIGITS = {
    '0': '０', '1': '１', '2': '２', '3': '３', '4': '４',
    '5': '５', '6': '６', '7': '７', '8': '８', '9': '９'
}