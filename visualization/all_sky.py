import numpy as np
import pandas as pd
import healpy as hp
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
from typing import List, Dict


def plot_on_healpix(events_df: pd.DataFrame, correlated_pairs: List[Dict], filename: str):
    """
    Generates and saves a HEALPix mollweide projection of the events.
    All events are plotted, and correlated pairs are connected by lines.
    """
    nside = 64
    npix = hp.nside2npix(nside)
    hpx_map = np.zeros(npix, dtype=np.float64)

    fig = plt.figure(figsize=(12, 8))
    plt.style.use('dark_background')
    hp.mollview(hpx_map, title="Multi-Messenger Event Sky Map", fig=fig, cbar=False, notext=True)
    hp.graticule(color='gray', alpha=0.5)

    styles = {
        'Neutrino': {'marker': 'o', 'c': '#3498db', 's': 50, 'label': 'Neutrino'}, # Blue
        'Gamma-ray': {'marker': 's', 'c': '#e74c3c', 's': 50, 'label': 'Gamma-ray'}, # Red
        'Grav-Wave': {'marker': '^', 'c': '#2ecc71', 's': 70, 'label': 'Grav-Wave'}, # Green
        'Optical-Transient': {'marker': 'x', 'c': '#f1c40f', 's': 60, 'label': 'Optical'}, # Yellow
    }
    
    plotted_labels = set()
    for _, event in events_df.iterrows():
        coord = event['astropy_coord']
        style = styles.get(event['source'], {'marker': '.', 'c': 'gray', 's': 30})
        label = style.get('label') if style.get('label') not in plotted_labels else None
        if label: plotted_labels.add(label)
        
        hp.projplot(coord.ra.deg, coord.dec.deg, marker=style['marker'], color=style['c'], markersize=style['s']/10, lonlat=True, label=label)
        
    for pair in correlated_pairs:
        ev1 = events_df.loc[pair['event1_idx']]
        ev2 = events_df.loc[pair['event2_idx']]
        hp.projplot(
            [ev1['astropy_coord'].ra.deg, ev2['astropy_coord'].ra.deg],
            [ev1['astropy_coord'].dec.deg, ev2['astropy_coord'].dec.deg],
            '#e94560', # Use accent color from CSS
            linestyle='--', lonlat=True, linewidth=1.5, alpha=0.9
        )
        
    plt.legend(loc='upper right', bbox_to_anchor=(1.1, 0.9))
    plt.savefig(filename, dpi=150, bbox_inches='tight') 
    plt.close(fig)