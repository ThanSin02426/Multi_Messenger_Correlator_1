import os
import logging
from flask import Flask, render_template, request, jsonify
from astropy import units as u
import pandas as pd

from config import Config
from correlator import Correlator
from data_handler.mock_fetcher import MockFetcher
from visualization.all_sky import plot_on_healpix 
from visualization.detail_plot import plot_correlation_heatmap


app = Flask(__name__)
if not os.path.exists('static/plots'):
    os.makedirs('static/plots')
    
logging.basicConfig(level=logging.INFO)

@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')

@app.route('/run', methods=['POST'])
def run_correlation():
    """API endpoint to run the correlation pipeline."""
    try:
        # 1. Get parameters from the frontend request
        data = request.json
        noise_events = int(data.get('noiseEvents', 500))
        true_pairs = int(data.get('truePairs', 3))
        time_window = float(data.get('timeWindow', 1.0))
        angle_sep = float(data.get('angleSep', 1.0))

        # 2. Create a config object
        app_config = Config(
            NUM_NOISE_EVENTS=noise_events,
            NUM_TRUE_CORRELATIONS=true_pairs,
            TIME_WINDOW=time_window * u.day,
            ANGULAR_SEPARATION=angle_sep * u.deg
        )

        # 3. Run the pipeline (data fetching and correlation)
        logging.info("Fetching mock data...")
        fetcher = MockFetcher(app_config)
        all_events = fetcher.fetch()

        logging.info("Running correlation search...")
        correlator_instance = Correlator(all_events, app_config)
        correlated_pairs = correlator_instance.find_correlations()

        # 4. Generate visualizations and prepare results
        results = []
        
        # All-sky plot
        all_sky_plot_path = os.path.join('static/plots', 'all_sky_map.png')
        plot_on_healpix(correlator_instance.events_df, correlated_pairs, all_sky_plot_path)

        # Detail plots for each correlation
        sorted_pairs = sorted(correlated_pairs, key=lambda x: x['probability'], reverse=True)
        for i, pair in enumerate(sorted_pairs):
            event1 = correlator_instance.events_df.loc[pair['event1_idx']]
            event2 = correlator_instance.events_df.loc[pair['event2_idx']]
            
            detail_plot_filename = os.path.join('static/plots', f'correlation_detail_{i}.png')
            plot_correlation_heatmap(event1, event2, pair, detail_plot_filename)
            
            # Format result for frontend
            results.append({
                "id": i,
                "probability": f"{pair['probability']:.2%}",
                "event1_id": event1['event_id'],
                "event1_source": event1['source'],
                "event2_id": event2['event_id'],
                "event2_source": event2['source'],
                "time_sep_hrs": f"{pair['time_sep_days'] * 24:.2f}",
                "ang_sep_deg": f"{pair['ang_sep_deg']:.3f}",
                "detail_plot_url": detail_plot_filename
            })
            
        # 5. Return JSON response
        return jsonify({
            "success": True,
            "all_sky_plot_url": all_sky_plot_path,
            "correlations": results
        })

    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)