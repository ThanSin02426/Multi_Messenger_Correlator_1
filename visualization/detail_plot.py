# visualization/detail_plot.py
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import multivariate_normal
from matplotlib.colors import LogNorm

def plot_correlation_heatmap(event1, event2, pair_info, filename):
    c1 = event1['astropy_coord']
    c2 = event2['astropy_coord']
    
    ra_center = np.mean([c1.ra.deg, c2.ra.deg])
    dec_center = np.mean([c1.dec.deg, c2.dec.deg])

    separation = pair_info['ang_sep_deg']
    max_error = max(event1['error_radius_deg'], event2['error_radius_deg'])
    
    span = (separation + 6 * max_error) * 1.2 
    span = max(span, 10 * event1['error_radius_deg'], 10 * event2['error_radius_deg'], 0.1)

    ra_grid = np.linspace(ra_center - span / 2, ra_center + span / 2, 200)
    dec_grid = np.linspace(dec_center - span / 2, dec_center + span / 2, 200)
    RA, DEC = np.meshgrid(ra_grid, dec_grid)
    pos = np.dstack((RA, DEC))

    rv1 = multivariate_normal(
        [c1.ra.deg, c1.dec.deg],
        [[event1['error_radius_deg']**2, 0], [0, event1['error_radius_deg']**2]]
    )
    rv2 = multivariate_normal(
        [c2.ra.deg, c2.dec.deg],
        [[event2['error_radius_deg']**2, 0], [0, event2['error_radius_deg']**2]]
    )

    pdf1 = rv1.pdf(pos)
    pdf2 = rv2.pdf(pos)
    overlap_product = pdf1 * pdf2

    fig, ax = plt.subplots(figsize=(8, 7))
    plt.style.use('dark_background')

    if np.any(overlap_product > 0):
        vmax = np.max(overlap_product)
        vmin = vmax / 1e5
        ax.imshow(overlap_product, cmap='viridis', origin='lower',
                  extent=[ra_grid.min(), ra_grid.max(), dec_grid.min(), dec_grid.max()],
                  aspect='auto', norm=LogNorm(vmin=vmin, vmax=vmax))

    contour1 = ax.contour(RA, DEC, pdf1, levels=5, colors='cyan', alpha=0.9, linestyles='solid')
    ax.clabel(contour1, inline=True, fontsize=8, fmt='%.1e')
    contour2 = ax.contour(RA, DEC, pdf2, levels=5, colors='magenta', alpha=0.9, linestyles='dashed')
    ax.clabel(contour2, inline=True, fontsize=8, fmt='%.1e')
    
    ax.plot(c1.ra.deg, c1.dec.deg, '+', color='cyan', markersize=10, label=f"{event1['source']} Center")
    ax.plot(c2.ra.deg, c2.dec.deg, 'x', color='magenta', markersize=10, label=f"{event2['source']} Center")
    ax.legend(fontsize='small')

    ax.set_xlabel('RA (deg)', fontsize=12)
    ax.set_ylabel('Dec (deg)', fontsize=12)
    ax.set_title('Correlation Candidate: Localization Overlap', fontsize=14)
    ax.grid(True, linestyle='--', alpha=0.4)

    text_str = (
        f"Confidence Score: {pair_info['probability']:.2%}\n"
        f"Ang. Sep: {pair_info['ang_sep_deg']:.3f}°\n"
        f"Time Sep: {pair_info['time_sep_days']*24:.2f} hrs\n"
        f"Event A: {event1['event_id']} ({event1['source']})\n"
        f"Event B: {event2['event_id']} ({event2['source']})"
    )
    props = dict(boxstyle='round', facecolor='maroon', alpha=0.7)
    ax.text(0.97, 0.97, text_str, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', horizontalalignment='right', bbox=props)
            
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close(fig)

    return filename