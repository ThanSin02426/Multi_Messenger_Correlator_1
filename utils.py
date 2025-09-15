import numpy as np
from astropy import units as u
from config import Config

def calculate_correlation_probability(time_sep: u.Quantity, ang_sep: u.Quantity, config: Config) -> float:
    """
    Calculates a simple confidence score for a potential correlation based on
    temporal and spatial proximity.

    The score is normalized by the search window sizes. A value of 1.0 would
    mean a perfect overlap in time and space, while 0 means the separation
    is at or beyond the search window.
    """
    time_score = 1 - (time_sep / config.TIME_WINDOW)
    space_score = 1 - (ang_sep / config.ANGULAR_SEPARATION)
    
    # Ensure scores are non-negative before multiplication
    time_score = max(0, time_score.value)
    space_score = max(0, space_score.value)
    
    return np.sqrt(time_score * space_score)