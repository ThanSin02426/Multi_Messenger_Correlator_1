from dataclasses import dataclass
from astropy import units as u

@dataclass
class Config:
    """Holds all configuration parameters for the correlator."""
    # Search parameters
    TIME_WINDOW: u.Quantity = 1.0 * u.day
    ANGULAR_SEPARATION: u.Quantity = 1.0 * u.deg
    
    # Data simulation parameters
    NUM_NOISE_EVENTS: int = 500
    NUM_TRUE_CORRELATIONS: int = 3  # How many true source-pairs to inject
    
    # HEALPix parameters for spatial indexing
    # Nside determines the resolution. 2^5 = 32 -> ~1.8 deg/pixel
    # This should be comparable to the search radius for efficiency.
    HEALPIX_NSIDE: int = 32
    
    # Output parameters
    OUTPUT_PLOT_FILENAME: str = "correlation_sky_map.png"