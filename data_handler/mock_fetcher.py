import numpy as np
import pandas as pd
from astropy.time import Time
from astropy.coordinates import SkyCoord
from astropy import units as u

from data_handler.base_fetcher import BaseFetcher
from config import Config

class MockFetcher(BaseFetcher):
    def __init__(self, config: Config):
        super().__init__("MockData")
        self.config = config

    def fetch(self) -> pd.DataFrame:
        events = []
        sources = ['Neutrino', 'Gamma-ray', 'Grav-Wave', 'Optical-Transient']
        
        for i in range(self.config.NUM_TRUE_CORRELATIONS):
            # ... (base_time and base_coord creation is the same)
            base_time = Time('2023-01-01T00:00:00') + np.random.uniform(0, 365) * u.day
            base_coord = SkyCoord(
                ra=np.random.uniform(0, 360) * u.deg,
                dec=np.random.uniform(-90, 90) * u.deg,
                frame='icrs'
            )
            source1, source2 = np.random.choice(sources, 2, replace=False)
            
            events.append({
                'event_id': f'TRUE{i}_A', 'source': source1,
                'astropy_time': base_time, 'astropy_coord': base_coord,
                'is_true_source': True,
                'error_radius_deg': np.random.uniform(0.1, 0.5)  # <-- ADDED/VERIFY THIS LINE
            })
            
            # ... (time_offset, ang_offset, offset_coord creation is the same)
            time_offset = np.random.uniform(0, self.config.TIME_WINDOW.to(u.s).value * 0.5) * u.s
            ang_offset = np.random.uniform(0, self.config.ANGULAR_SEPARATION.to(u.deg).value * 0.5) * u.deg
            offset_coord = base_coord.directional_offset_by(
                np.random.uniform(0, 360) * u.deg, ang_offset
            )
            events.append({
                'event_id': f'TRUE{i}_B', 'source': source2,
                'astropy_time': base_time + time_offset, 'astropy_coord': offset_coord,
                'is_true_source': True,
                'error_radius_deg': np.random.uniform(0.1, 0.5) # <-- ADDED/VERIFY THIS LINE
            })

        # --- Generate Background Noise Events ---
        for i in range(self.config.NUM_NOISE_EVENTS):
            events.append({
                'event_id': f'NOISE_{i}', 'source': np.random.choice(sources),
                'astropy_time': Time('2023-01-01T00:00:00') + np.random.uniform(0, 365) * u.day,
                'astropy_coord': SkyCoord(
                    ra=np.random.uniform(0, 360) * u.deg,
                    dec=np.rad2deg(np.arcsin(np.random.uniform(-1, 1))) * u.deg, frame='icrs'
                ),
                'is_true_source': False,
                'error_radius_deg': np.random.uniform(0.2, 1.5) # <-- ADDED/VERIFY THIS LINE
            })
            
        return pd.DataFrame(events)