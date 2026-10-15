# G2CRM Annual Exceedance Probability (AEP) Hazard Curve Generator

## Overview

This script processes G2CRM storm detail output data to calculate empirical Annual Exceedance Probability (AEP) and return period hazard curves for:

1.  Total Water Level (with tides)
2.  Storm Surge Contribution (without tides)

It generates a CSV file containing the computed hazard curves and saves a semi-log plot for visualization.

## Prerequisites

- Python 3.x
- h5py>=3.16.0
- matplotlib>=3.10.9
- pandas>=2.3.3

## Installation

1.  Clone or download the source files.
2.  Install the required Python packages using the provided `requirements.txt` file:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Place Input Data**: Ensure your G2CRM output CSV file (e.g., `ProtectiveSystemElementStormDetail_NoSLC_run1.csv`) is in the same directory as the script.

2.  **Configure Script (Optional)**: Open the `create_aep_from_g2crm.py` script and modify the parameters in the "USER CONFIGURATION" section as needed:
    - `INPUT_CSV`: Update the path if your data file is in a different location.
    - `PSE_FILTER_ID`: Set a specific Protective System Element ID (e.g., 'BH04') to filter the data.
    - `LIFECYCLE_YEARS`: Adjust the number of simulated years per lifecycle iteration (default: 100).

3.  **Execute**: Run the script from your command line:
    ```bash
    python create_aep_from_g2crm.py
    ```

## Outputs

The script will create an `output/` directory containing the following files:

- `output.csv`: A CSV file containing the calculated AEP, return periods, peak water levels with tides, and peak water levels without tides.
- `aep_hazard_curve.png`: A semi-log plot visualizing the AEP hazard curves for both scenarios (with and without tides).

## Dependencies

This script relies on the following Python packages:

- h5py>=3.16.0
- matplotlib>=3.10.9
- pandas>=2.3.3
