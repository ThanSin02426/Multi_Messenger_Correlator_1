import logging
import pandas as pd
from collections import defaultdict
from typing import List, Dict
from astropy.coordinates import SkyCoord

import healpy as hp
import numpy as np
from astropy import units as u

from config import Config
from utils import calculate_correlation_probability
from analysis.contextual import get_context_from_catalogs

class Correlator:
    """Finds spatio-temporal correlations in a combined event DataFrame."""

    def __init__(self, all_events_df: pd.DataFrame, config: Config):
        self.config = config
        self.events_df = self._prepare_data(all_events_df)
        
    def _prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adds HEALPix index and sorts by time for efficient processing."""
        logging.info("Preparing data: sorting by time and calculating HEALPix indices...")

        original_count = len(df)
        df = df[df['astropy_coord'].apply(lambda x: isinstance(x, SkyCoord))]
        
        if len(df) < original_count:
            logging.warning(f"Filtered out {original_count - len(df)} rows with invalid coordinate data.")
            
        if df.empty:
            logging.warning("No valid events remained after filtering coordinates. Returning empty DataFrame.")
            return df
        
        df['hpx_idx'] = hp.ang2pix(
            self.config.HEALPIX_NSIDE,
            0.5 * np.pi - df['astropy_coord'].apply(lambda c: c.dec.rad),
            df['astropy_coord'].apply(lambda c: c.ra.rad)
            
        )
        return df.sort_values('astropy_time').reset_index(drop=True)

    def find_correlations(self) -> List[Dict]:
        """Finds correlations using a spatially-indexed (HEALPix) approach."""
        # ... (The find_correlations_optimized method from the previous version goes here) ...
        # ... (It is unchanged, so I'm omitting it for brevity) ...
        # The logic is exactly the same as `find_correlations_optimized` before.
        correlated_pairs = []
        pixel_to_events = defaultdict(list)
        for idx, event in self.events_df.iterrows():
            pixel_to_events[event['hpx_idx']].append(idx)
            
        for hpx_idx, event_indices in pixel_to_events.items():
            search_pixel_indices = [hpx_idx] + hp.get_all_neighbours(
                self.config.HEALPIX_NSIDE, hpx_idx
            ).tolist()
            
            candidate_indices = []
            for pix_idx in search_pixel_indices:
                candidate_indices.extend(pixel_to_events.get(pix_idx, []))
            candidate_indices.sort() # Ensure candidates are time-sorted

            for idx1 in event_indices:
                event1 = self.events_df.iloc[idx1]
                for idx2 in candidate_indices:
                    if idx1 >= idx2: continue
                    event2 = self.events_df.iloc[idx2]
                    if event1['source'] == event2['source']: continue
                    time_sep = (event2['astropy_time'] - event1['astropy_time']).to(u.day)
                    if time_sep > self.config.TIME_WINDOW: break 
                    ang_sep = event1['astropy_coord'].separation(event2['astropy_coord'])
                    if ang_sep > self.config.ANGULAR_SEPARATION: continue
                    
                    prob = calculate_correlation_probability(time_sep, ang_sep, self.config)
                    correlated_pairs.append({
                        'event1_idx': idx1, 'event2_idx': idx2, 'probability': prob,
                        'time_sep_days': time_sep.value, 'ang_sep_deg': ang_sep.to(u.degree).value
                    })
        return correlated_pairs

    def report_results(self, correlated_pairs: List[Dict]):
        """Prints a detailed report of the findings."""
        logging.info("3. Correlation Analysis Results:")
        if not correlated_pairs:
            logging.info("-> No correlated events found.")
            return

        logging.info(f"-> Found {len(correlated_pairs)} potential correlations (pairs)!")
        logging.info("NOTE: 'Clusters' of >2 events can be found by analyzing the graph of correlated pairs.")
        
        sorted_pairs = sorted(correlated_pairs, key=lambda x: x['probability'], reverse=True)
        
        for i, corr in enumerate(sorted_pairs):
            event1 = self.events_df.loc[corr['event1_idx']]
            event2 = self.events_df.loc[corr['event2_idx']]
            
            is_real = ""
            if 'is_true_source' in self.events_df.columns and event1['is_true_source'] and event2['is_true_source']:
                is_real = "✅ (Correctly Identified Injected Pair!)"
            
            # Get contextual info for the approximate midpoint
            avg_coord = SkyCoord(
                ra=np.mean([event1['astropy_coord'].ra.deg, event2['astropy_coord'].ra.deg]) * u.deg,
                dec=np.mean([event1['astropy_coord'].dec.deg, event2['astropy_coord'].dec.deg]) * u.deg
            )
            context = get_context_from_catalogs(avg_coord)

            print("-" * 75)
            print(f"  Correlation #{i+1} | Confidence Score: {corr['probability']:.2%} {is_real}")
            print(f"  - Event A: {event1['event_id']} ({event1['source']}) at {event1['astropy_time'].iso}")
            print(f"  - Event B: {event2['event_id']} ({event2['source']}) at {event2['astropy_time'].iso}")
            print(f"  - Details: Time Sep = {corr['time_sep_days'] * 24:.2f} hrs, Angular Sep = {corr['ang_sep_deg']:.3f}°")
            print(f"  - Context: {context}")