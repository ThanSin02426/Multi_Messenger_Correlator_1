# Multi-Messenger Event Correlator

This project provides a high-performance tool to find spatio-temporal correlations in simulated multi-messenger astrophysics event data.

It uses a HEALPix-based spatial index to dramatically speed up the search for correlated pairs, avoiding a slow O(n²) comparison.

## Features

- **High-Performance:** Uses a HEALPix spatial index for efficient correlation searching.
- **Realistic Simulation:** Injects known correlated pairs into a random background of noise events for robust testing.
- **Rich Visualization:** Generates a HEALPix sky map that clearly highlights all events and connects the correlated pairs.
- **Configurable:** All key parameters can be easily adjusted via command-line arguments.
- **Professional Structure:** The code is modular, well-documented, and uses modern Python practices.

## Project Structure

- `correlator.py`: The main application logic and command-line interface.
- `config.py`: Centralized dataclass for all configuration parameters.
- `data_handler.py`: Module for generating mock event data.
- `visualization.py`: Module for creating the HEALPix sky map plot.
- `utils.py`: Contains shared helper functions.
- `requirements.txt`: A list of all necessary Python packages.

## Setup

1.  **Clone the repository (or save the files):**
    Ensure all the Python files (`.py`) are in the same directory.

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## How to Run

You can run the correlator from your terminal. The script accepts several command-line arguments to customize the simulation and search.

**Basic Usage (with default settings):**

```bash
python correlator.py
```

**Customized Run:**
This example runs the simulation with 1000 noise events and a wider search window of 2 days and 3 degrees.

```bash
python correlator.py --noise-events 1000 --time-window 2.0 --angle-sep 3.0
```

### Command-Line Options

-   `--noise-events`: Number of background noise events to simulate (default: 500).
-   `--true-pairs`: Number of true correlated pairs to inject (default: 3).
-   `--time-window`: Time window for correlation search in days (default: 1.0).
-   `--angle-sep`: Angular separation for correlation search in degrees (default: 1.0).

## Output

The script will:
1.  Print its progress and the results of the correlation search to the console. Correctly identified pairs (those that were intentionally injected) will be marked.
2.  Generate a sky map image named `correlation_sky_map.png` in the same directory. This plot will show all events and draw a red dashed line between any pair found to be correlated.