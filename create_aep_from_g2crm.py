"""
================================================================================
G2CRM Annual Exceedance Probability (AEP) Hazard Curve Generator
================================================================================

Overview:
    This script processes G2CRM storm detail output data to calculate empirical
    Annual Exceedance Probability (AEP) and return period hazard curves for:
      1. Total Water Level (with tides)
      2. Storm Surge Contribution (without tides)

    It generates an output CSV containing the computed hazard curves and saves
    a semi-log plot comparison.

Prerequisites & Dependencies:
    Install the required Python packages before running:
        $ pip install numpy pandas matplotlib
    Versions:
        matplotlib>=3.10.9
        pandas>=2.3.3

How to Run:
    1. Ensure the CSV ('ProtectiveSystemElementStormDetail') from G2CRM
       is placed in the same directory as this script, or update `INPUT_CSV` below to point
       to it.
    2. Adjust the user configuration parameters:
         - `PSE_FILTER_ID`: Filter by a specific Protective System Element ID (e.g., 'BH04').
         - `LIFECYCLE_YEARS`: Number of simulated years per lifecycle iteration (default: 100).
    3. Execute the script from the command line:
        $ python create_aep_from_g2crm.py

Outputs:
    - output/output.csv: Calculated AEP, return periods, and peak water levels.
    - output/aep_hazard_curve.png: Semi-log hazard curve plot figure.
================================================================================
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.style.use("seaborn-v0_8-paper")

# ==============================================================================
# USER CONFIGURATION
# ==============================================================================
FILE_DIR = Path(__file__).resolve().parent
INPUT_CSV = Path(FILE_DIR / "ProtectiveSystemElementStormDetail_NoSLC_run1.csv")
OUTPUT_DIR = Path(FILE_DIR / "output")

# PSE filtering and number of years settings
PSE_FILTER_ID = "BH04"  # Protective System Element (PSE) to consider.
LIFECYCLE_YEARS = 100  # Number of years per lifecycle iteration
# ==============================================================================


def load_max_water_levels(
    csv_path: Path, pse_filter_id: str | None = None
) -> pd.DataFrame:
    """Load G2CRM storm details and extract peak water levels per storm event."""
    if not csv_path.exists():
        raise FileNotFoundError(f"Input file not found: {csv_path}")

    df = pd.read_csv(csv_path)

    if pse_filter_id and "PSETextId" in df.columns:
        df = df[df["PSETextId"] == pse_filter_id]

    # Peak water level per lifecycle iteration and storm event for both scenarios
    max_wl = (
        df.groupby(["Iteration", "Event", "DaysFromStart", "Storm"])[
            ["TotalWaterLevel", "StormSurgeContribution"]
        ]
        .max()
        .reset_index()
    )
    return max_wl


def calculate_hazard_curve(
    df_peaks: pd.DataFrame, num_years_per_iter: int = 100
) -> pd.DataFrame:
    """Calculate empirical return periods and AEP hazard curves for both scenarios.

    Returns DataFrame ordered from smallest to largest return period.
    """
    num_lifecycles = df_peaks["Iteration"].nunique()
    total_years = num_lifecycles * num_years_per_iter

    # Rank storm peaks in descending order for exceedance frequencies
    peaks_tides = np.sort(df_peaks["TotalWaterLevel"].values)[::-1]
    peaks_no_tides = np.sort(df_peaks["StormSurgeContribution"].values)[::-1]

    ranks = np.arange(1, len(peaks_tides) + 1)
    exceedance_rate = ranks / total_years
    return_period = 1.0 / exceedance_rate

    hazard_df = pd.DataFrame(
        {
            "annual_exceedance_prob": exceedance_rate,
            "return_period_yrs": return_period,
            "peak_water_level_with_tides_ft": peaks_tides,
            "peak_water_level_no_tides_ft": peaks_no_tides,
        }
    )

    # Reverse order so output starts at smallest return period (highest AEP)
    hazard_df = hazard_df.iloc[::-1].reset_index(drop=True)

    return hazard_df


def plot_hazard_curve(
    hazard_df: pd.DataFrame,
    title: str = "AEP Hazard Curve",
    output_png: Path | None = None,
) -> None:
    """Plot both AEP hazard curves on a semi-log scale."""
    fig, ax = plt.subplots(figsize=(7, 5))

    # Plot both curves
    ax.plot(
        hazard_df["annual_exceedance_prob"],
        hazard_df["peak_water_level_with_tides_ft"],
        color="steelblue",
        lw=2,
        label="With Tides (Total Water Level)",
    )
    ax.plot(
        hazard_df["annual_exceedance_prob"],
        hazard_df["peak_water_level_no_tides_ft"],
        color="darkorange",
        lw=2,
        linestyle="--",
        label="Without Tides (Storm Surge Only)",
    )

    ax.set_xlabel("Annual Exceedance Probability (AEP)")
    ax.set_ylabel("Water Level (ft; msl)")
    ax.set_xscale("log")

    # Invert x-axis so low-frequency (extreme) events remain on the right
    ax.invert_xaxis()

    # Define standard AEP tick marks corresponding to 2-yr up to 5000-yr events
    ticks = [0.5, 0.2, 0.1, 0.05, 0.02, 0.01, 0.005, 0.002, 0.001, 0.0002]
    ax.set_xticks(ticks)
    ax.set_xticklabels([str(t) for t in ticks])
    ax.set_xlim([0.5, 0.0001])

    ax.grid(True, which="both", linestyle=":", alpha=0.5)
    ax.legend(loc="upper left", frameon=True)
    ax.set_title(title)

    plt.tight_layout()

    if output_png:
        output_png.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_png, dpi=300, bbox_inches="tight")
        print(f"Saved figure to: {output_png}")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Reading storm data from: {INPUT_CSV}")
    df_peaks = load_max_water_levels(
        csv_path=INPUT_CSV,
        pse_filter_id=PSE_FILTER_ID,
    )

    print("Computing hazard curves...")
    hazard_df = calculate_hazard_curve(
        df_peaks=df_peaks,
        num_years_per_iter=LIFECYCLE_YEARS,
    )

    # Export computed curves to output.csv
    csv_out = OUTPUT_DIR / "output.csv"
    hazard_df.to_csv(csv_out, index=False)
    print(f"Saved hazard curve data to: {csv_out}")

    # Plot & save figure
    fig_out = OUTPUT_DIR / "aep_hazard_curve.png"
    plot_hazard_curve(
        hazard_df=hazard_df,
        title=f"G2CRM AEP Curve ({PSE_FILTER_ID or 'All PSEs'})",
        output_png=fig_out,
    )
    plt.show()


if __name__ == "__main__":
    main()
