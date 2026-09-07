"""
Yield ROI - Model Error Analysis
--------------------------------

Analyzes the predictions produced by the final yield model.

Outputs:
1. Overall test metrics
2. Crop-wise performance
3. District-wise performance
4. Season-wise performance
5. Largest prediction errors
6. Best and worst performing crops
7. Prediction error statistics
"""

from pathlib import Path
import json

import numpy as np
import pandas as pd

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)


# ============================================================
# 1. PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
RESULTS_DIR = BASE_DIR / "results"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)

PREDICTIONS_FILE = DATA_DIR / "test_predictions.csv"


# ============================================================
# 2. LOAD PREDICTIONS
# ============================================================

print("=" * 70)
print("YIELD ROI - MODEL ERROR ANALYSIS")
print("=" * 70)

print("\nLoading test predictions...")

df = pd.read_csv(PREDICTIONS_FILE)

print(f"Rows loaded: {len(df):,}")


# ============================================================
# 3. CHECK REQUIRED COLUMNS
# ============================================================

required_columns = [
    "crop_yield",
    "predicted_yield",
    "crop",
    "district",
    "season",
    "year"
]

for column in required_columns:

    if column not in df.columns:
        raise ValueError(
            f"Required column missing: {column}"
        )


# ============================================================
# 4. CREATE ERROR COLUMNS
# ============================================================

df["error"] = (
    df["predicted_yield"]
    - df["crop_yield"]
)

df["absolute_error"] = (
    df["error"].abs()
)

df["squared_error"] = (
    df["error"] ** 2
)

df["percentage_error"] = (
    df["absolute_error"]
    / df["crop_yield"]
    * 100
)


# ============================================================
# 5. OVERALL PERFORMANCE
# ============================================================

actual = df["crop_yield"]
predicted = df["predicted_yield"]

mae = mean_absolute_error(
    actual,
    predicted
)

rmse = np.sqrt(
    mean_squared_error(
        actual,
        predicted
    )
)

r2 = r2_score(
    actual,
    predicted
)

print("\n" + "=" * 70)
print("OVERALL TEST PERFORMANCE")
print("=" * 70)

print(f"MAE  : {mae:.4f}")
print(f"RMSE : {rmse:.4f}")
print(f"R²   : {r2:.4f}")


# ============================================================
# 6. CROP-WISE PERFORMANCE
# ============================================================

def crop_metrics(group):

    actual_values = group["crop_yield"]
    predicted_values = group["predicted_yield"]

    return pd.Series(
        {
            "samples": len(group),

            "MAE": mean_absolute_error(
                actual_values,
                predicted_values
            ),

            "RMSE": np.sqrt(
                mean_squared_error(
                    actual_values,
                    predicted_values
                )
            ),

            "R2": (
                r2_score(
                    actual_values,
                    predicted_values
                )
                if len(group) >= 2
                and actual_values.nunique() > 1
                else np.nan
            ),

            "mean_actual_yield": actual_values.mean(),

            "mean_predicted_yield": predicted_values.mean(),

            "mean_percentage_error":
                group["percentage_error"].mean()
        }
    )


crop_performance = (
    df
    .groupby("crop", group_keys=False)
    .apply(
        crop_metrics,
        include_groups=False
    )
    .reset_index()
)

crop_performance = crop_performance.sort_values(
    "MAE",
    ascending=False
)

crop_performance.to_csv(
    RESULTS_DIR / "crop_performance.csv",
    index=False
)


# ============================================================
# 7. DISTRICT-WISE PERFORMANCE
# ============================================================

def district_metrics(group):

    actual_values = group["crop_yield"]
    predicted_values = group["predicted_yield"]

    return pd.Series(
        {
            "samples": len(group),

            "MAE": mean_absolute_error(
                actual_values,
                predicted_values
            ),

            "RMSE": np.sqrt(
                mean_squared_error(
                    actual_values,
                    predicted_values
                )
            ),

            "R2": (
                r2_score(
                    actual_values,
                    predicted_values
                )
                if len(group) >= 2
                and actual_values.nunique() > 1
                else np.nan
            )
        }
    )


district_performance = (
    df
    .groupby("district", group_keys=False)
    .apply(
        district_metrics,
        include_groups=False
    )
    .reset_index()
)

district_performance = district_performance.sort_values(
    "MAE",
    ascending=False
)

district_performance.to_csv(
    RESULTS_DIR / "district_performance.csv",
    index=False
)


# ============================================================
# 8. SEASON-WISE PERFORMANCE
# ============================================================

def season_metrics(group):

    actual_values = group["crop_yield"]
    predicted_values = group["predicted_yield"]

    return pd.Series(
        {
            "samples": len(group),

            "MAE": mean_absolute_error(
                actual_values,
                predicted_values
            ),

            "RMSE": np.sqrt(
                mean_squared_error(
                    actual_values,
                    predicted_values
                )
            ),

            "R2": (
                r2_score(
                    actual_values,
                    predicted_values
                )
                if len(group) >= 2
                and actual_values.nunique() > 1
                else np.nan
            )
        }
    )


season_performance = (
    df
    .groupby("season", group_keys=False)
    .apply(
        season_metrics,
        include_groups=False
    )
    .reset_index()
)

season_performance = season_performance.sort_values(
    "MAE",
    ascending=False
)

season_performance.to_csv(
    RESULTS_DIR / "season_performance.csv",
    index=False
)


# ============================================================
# 9. LARGEST PREDICTION ERRORS
# ============================================================

largest_errors = (
    df
    .sort_values(
        "absolute_error",
        ascending=False
    )
    .head(50)
)

largest_errors.to_csv(
    RESULTS_DIR / "largest_prediction_errors.csv",
    index=False
)


# ============================================================
# 10. WORST CROPS
# ============================================================

worst_crops = (
    crop_performance
    .head(10)
)

best_crops = (
    crop_performance
    .sort_values("MAE")
    .head(10)
)


print("\n" + "=" * 70)
print("10 CROPS WITH HIGHEST MAE")
print("=" * 70)

print(
    worst_crops[
        [
            "crop",
            "samples",
            "MAE",
            "RMSE",
            "R2"
        ]
    ].to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}"
    )
)


print("\n" + "=" * 70)
print("10 BEST PERFORMING CROPS")
print("=" * 70)

print(
    best_crops[
        [
            "crop",
            "samples",
            "MAE",
            "RMSE",
            "R2"
        ]
    ].to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}"
    )
)


# ============================================================
# 11. LARGEST INDIVIDUAL ERRORS
# ============================================================

print("\n" + "=" * 70)
print("10 LARGEST INDIVIDUAL ERRORS")
print("=" * 70)

print(
    largest_errors[
        [
            "year",
            "district",
            "crop",
            "season",
            "crop_yield",
            "predicted_yield",
            "absolute_error",
            "percentage_error"
        ]
    ].head(10).to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}"
    )
)


# ============================================================
# 12. ERROR SUMMARY
# ============================================================

error_summary = {

    "overall": {
        "MAE": float(mae),
        "RMSE": float(rmse),
        "R2": float(r2)
    },

    "prediction_error": {
        "mean_error": float(df["error"].mean()),
        "median_error": float(df["error"].median()),
        "mean_absolute_error": float(
            df["absolute_error"].mean()
        ),
        "maximum_absolute_error": float(
            df["absolute_error"].max()
        )
    },

    "dataset": {
        "samples": int(len(df)),
        "crops": int(df["crop"].nunique()),
        "districts": int(df["district"].nunique()),
        "seasons": int(df["season"].nunique()),
        "years": int(df["year"].nunique())
    }
}


with open(
    RESULTS_DIR / "error_analysis_summary.json",
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        error_summary,
        file,
        indent=4
    )


# ============================================================
# 13. COMPLETION
# ============================================================

print("\n" + "=" * 70)
print("ERROR ANALYSIS COMPLETED")
print("=" * 70)

print("\nFiles created:")

print(
    " - results/crop_performance.csv"
)

print(
    " - results/district_performance.csv"
)

print(
    " - results/season_performance.csv"
)

print(
    " - results/largest_prediction_errors.csv"
)

print(
    " - results/error_analysis_summary.json"
)

print("\nNext step: send me the complete terminal output.")
print("=" * 70)