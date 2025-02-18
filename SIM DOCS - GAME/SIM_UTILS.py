from SIM_SETTINGS import *
import numpy as np

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
