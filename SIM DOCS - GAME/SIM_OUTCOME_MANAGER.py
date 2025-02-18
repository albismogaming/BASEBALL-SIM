from SIM_SINGLE import *
from SIM_DOUBLE import *
from SIM_TRIPLE import *
from SIM_HOMERUN import *
from SIM_HBP_BB import *
from SIM_STRIKEOUTS import *
from SIM_POPOUTS import *
from SIM_GROUNDOUTS import *
from SIM_FLYOUTS import *
from SIM_LINEOUTS import *
from SIM_PICKOFFS import *
from SIM_WP_PB import *
from SIM_STEALS import *
from SIM_LGDATA import *

class OutcomeManager:
    def __init__(self, gamestate, league):
        self.gamestate = gamestate
        self.league = league

    def handle_macro_event(self, outcome, pitcher, batter, runners, fielding_team=None):
        """
        Handles macro events by instantiating and executing the appropriate outcome class.

        Parameters:
        - outcome (str): The result of the at-bat (e.g., "SINGLE", "DOUBLE", "HOMERUN", etc.).
        - pitcher (Pitcher): The pitcher instance.
        - batter (Batter): The batter instance.
        - runners (dict): Dictionary of runners on base.
        - fielding_team (Team, optional): The fielding team instance.

        Returns:
        None
        """
        outcome_classes = {
            "SINGLE": Single,
            "DOUBLE": Double,
            "TRIPLE": Triple,
            "HOMERUN": Homerun,
            "GROUNDOUT": Groundout,
            "FLYOUT": Flyout,
            "LINEOUT": Lineout,
            "POPOUT": Popout,
            "CALLED STRIKEOUT": CalledStrikeout,
            "SWINGING STRIKEOUT": SwingingStrikeout,
            "WALK": Walk,
            "HBP": HitByPitch
        }

        if outcome in outcome_classes:
            outcome_instance = outcome_classes[outcome](
                self.gamestate, self.league, batter, pitcher, runners, fielding_team
            )
            hits_hit, runs_scored, outs_recorded, walk_off = outcome_instance.execute()
            return hits_hit, runs_scored, outs_recorded, walk_off
        
        return 0, 0, 0, False

    def handle_micro_event(self, outcome, pitcher, batter, runners, fielding_team=None):
        """
        Handles micro-events by creating and executing the appropriate Outcome object.

        Parameters:
        - outcome (str): The micro-event type (e.g., "WILD PITCH", "STEAL ATTEMPT").
        - pitcher (Pitcher): The pitcher instance.
        - batter (Batter): The batter instance.
        - runners (dict): Dictionary of runners on base.
        - hit_direction (str, optional): The direction of the hit (for consistency, but not used in micro-events).
        - batted_ball_type (str, optional): The type of hit (for consistency, but not used in micro-events).
        - hit_location (str, optional): The hit location (for consistency, but not used in micro-events).
        - fielding_team (Team, optional): The fielding team instance.

        Returns:
        None
        """

        # Dictionary to map micro-event outcomes to their respective classes
        outcome_classes = {
            "WILD PITCH": WildPitch,
            "PASSED BALL": PassedBall,
            "STEAL ATTEMPT": BaseStealing,
            "PICKOFF 1ST": Pickoff1st,
            "PICKOFF 2ND": Pickoff2nd
        }

        # Get the outcome class based on the outcome type
        outcome_class = outcome_classes.get(outcome)

        if outcome_class:
            # Instantiate the outcome and apply its effect
            outcome_instance = outcome_class(
                self.gamestate, batter, pitcher, runners, fielding_team
            )
            hits_hit, runs_scored, outs_recorded, walk_off = outcome_instance.execute()
            return hits_hit, runs_scored, outs_recorded, walk_off
        
        return 0, 0, 0, False

