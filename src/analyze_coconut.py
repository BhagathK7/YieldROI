"""
Yield ROI - Coconut Error Investigation
---------------------------------------

Investigates why Coconut has unusually large prediction errors.

This script does NOT modify the dataset or model.
It only performs analysis.
"""

from pathlib import Path

import pandas as pd
import numpy as np


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
RESULTS_DIR = BASE_DIR / "results"

TEST_FILE = DATA_DIR / "test_predictions.csv"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("YIELD ROI - COCONUT ERROR INVESTIGATION")
print("=" * 70)

df = pd.read_csv(TEST_FILE)

coconut = df[
    df["crop"].str.strip().str.lower() == "coconut"
].copy()

print(f"\nCoconut test rows: {len(coconut)}")


# ============================================================
# BASIC STATISTICS
# ============================================================

print("\n" + "=" * 70)
print("COCONUT YIELD STATISTICS")
print("=" * 70)

print(
    coconut[
        [
            "crop_yield",
            "predicted_yield",
            "area",
            "year"
        ]
    ].describe().to_string()
)


# ============================================================
# YEAR-WISE ANALYSIS
# ============================================================

year_analysis = (
    coconut
    .groupby("year")
    .agg(
        samples=("crop_yield", "count"),
        actual_mean=("crop_yield", "mean"),
        actual_min=("crop_yield", "min"),
        actual_max=("crop_yield", "max"),
        predicted_mean=("predicted_yield", "mean"),
        absolute_error_mean=("absolute_error", "mean")
    )
    .reset_index()
)

print("\n" + "=" * 70)
print("COCONUT YEAR-WISE PERFORMANCE")
print("=" * 70)

print(
    year_analysis.to_string(
        index=False,
        float_format=lambda x: f"{x:.2f}"
    )
)


# ============================================================
# DISTRICT-WISE ANALYSIS
# ============================================================

district_analysis = (
    coconut
    .groupby("district")
    .agg(
        samples=("crop_yield", "count"),
        actual_mean=("crop_yield", "mean"),
        actual_min=("crop_yield", "min"),
        actual_max=("crop_yield", "max"),
        predicted_mean=("predicted_yield", "mean"),
        MAE=("absolute_error", "mean")
    )
    .reset_index()
)

district_analysis["bias"] = (
    district_analysis["predicted_mean"]
    - district_analysis["actual_mean"]
)

district_analysis = district_analysis.sort_values(
    "MAE",
    ascending=False
)


print("\n" + "=" * 70)
print("COCONUT DISTRICT-WISE PERFORMANCE")
print("=" * 70)

print(
    district_analysis.head(20).to_string(
        index=False,
        float_format=lambda x: f"{x:.2f}"
    )
)


# ============================================================
# ACTUAL VS PREDICTED
# ============================================================

coconut["prediction_ratio"] = (
    coconut["predicted_yield"]
    / coconut["crop_yield"]
)

coconut["under_prediction"] = (
    coconut["predicted_yield"]
    < coconut["crop_yield"]
)


print("\n" + "=" * 70)
print("COCONUT PREDICTION BIAS")
print("=" * 70)

print(
    f"Mean actual yield     : "
    f"{coconut['crop_yield'].mean():.2f}"
)

print(
    f"Mean predicted yield  : "
    f"{coconut['predicted_yield'].mean():.2f}"
)

print(
    f"Mean prediction ratio : "
    f"{coconut['prediction_ratio'].mean():.4f}"
)

print(
    f"Under-predictions     : "
    f"{coconut['under_prediction'].sum()}"
    f" / {len(coconut)}"
)


# ============================================================
# EXTREME COCONUT VALUES
# ============================================================

print("\n" + "=" * 70)
print("HIGHEST ACTUAL COCONUT YIELDS")
print("=" * 70)

highest = (
    coconut
    .sort_values(
        "crop_yield",
        ascending=False
    )
    .head(20)
)

print(
    highest[
        [
            "year",
            "district",
            "area",
            "crop_yield",
            "predicted_yield",
            "absolute_error",
            "percentage_error"
        ]
    ].to_string(
        index=False,
        float_format=lambda x: f"{x:.2f}"
    )
)


# ============================================================
# SAVE RESULTS
# ============================================================

year_analysis.to_csv(
    RESULTS_DIR / "coconut_year_analysis.csv",
    index=False
)

district_analysis.to_csv(
    RESULTS_DIR / "coconut_district_analysis.csv",
    index=False
)

coconut.to_csv(
    RESULTS_DIR / "coconut_test_analysis.csv",
    index=False
)


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 70)
print("COCONUT ANALYSIS COMPLETED")
print("=" * 70)

print("\nFiles created:")

print(" - results/coconut_year_analysis.csv")
print(" - results/coconut_district_analysis.csv")
print(" - results/coconut_test_analysis.csv")

print("\nNo dataset or model was modified.")
print("=" * 70)