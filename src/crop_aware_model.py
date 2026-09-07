"""
Yield ROI - Crop-Aware Model Experiment
----------------------------------------

Purpose:
Compare the current global Random Forest Log model with a
crop-aware calibration approach.

The experiment does NOT modify the original dataset.

Approach:
1. Train the existing global Random Forest Log model.
2. Generate validation predictions.
3. Calculate crop-level residual bias from validation data.
4. Apply those learned crop biases to validation/test predictions.
5. Compare global vs crop-aware performance.
6. Select the approach only if it improves overall validation RMSE.
7. Evaluate the selected approach on the untouched test set.

Important:
The crop bias is learned ONLY from the training data through
cross-validation-style out-of-fold predictions. This prevents
using validation/test targets to construct the correction.
"""

from pathlib import Path
import json

import numpy as np
import pandas as pd
import joblib

from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import KFold
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
MODEL_DIR = BASE_DIR / "models"
RESULTS_DIR = BASE_DIR / "results"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


TRAIN_FILE = DATA_DIR / "train.csv"
VALIDATION_FILE = DATA_DIR / "validation.csv"
TEST_FILE = DATA_DIR / "test.csv"

GLOBAL_MODEL_FILE = MODEL_DIR / "best_yield_model.joblib"

RESULTS_FILE = RESULTS_DIR / "crop_aware_comparison.json"


# ============================================================
# 2. LOAD DATA
# ============================================================

print("=" * 70)
print("YIELD ROI - CROP-AWARE MODEL EXPERIMENT")
print("=" * 70)

print("\nLoading datasets...")

train_df = pd.read_csv(TRAIN_FILE)
validation_df = pd.read_csv(VALIDATION_FILE)
test_df = pd.read_csv(TEST_FILE)

print(f"Train rows      : {len(train_df):,}")
print(f"Validation rows : {len(validation_df):,}")
print(f"Test rows       : {len(test_df):,}")


# ============================================================
# 3. FEATURES
# ============================================================

FEATURES = [
    "district",
    "crop",
    "season",
    "year",
    "area"
]

TARGET = "crop_yield"

CATEGORICAL_FEATURES = [
    "district",
    "crop",
    "season"
]

NUMERICAL_FEATURES = [
    "year",
    "area"
]


X_train = train_df[FEATURES].copy()
y_train = train_df[TARGET].copy()

X_validation = validation_df[FEATURES].copy()
y_validation = validation_df[TARGET].copy()

X_test = test_df[FEATURES].copy()
y_test = test_df[TARGET].copy()


# ============================================================
# 4. PREPROCESSOR
# ============================================================

def create_preprocessor():

    categorical_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(strategy="most_frequent")
            ),
            (
                "onehot",
                OneHotEncoder(
                    handle_unknown="ignore",
                    sparse_output=True
                )
            )
        ]
    )

    numerical_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(strategy="median")
            ),
            (
                "scaler",
                StandardScaler()
            )
        ]
    )

    return ColumnTransformer(
        transformers=[
            (
                "categorical",
                categorical_pipeline,
                CATEGORICAL_FEATURES
            ),
            (
                "numerical",
                numerical_pipeline,
                NUMERICAL_FEATURES
            )
        ]
    )


# ============================================================
# 5. CREATE GLOBAL RANDOM FOREST LOG MODEL
# ============================================================

def create_global_model():

    rf = RandomForestRegressor(
        n_estimators=500,
        max_depth=None,
        min_samples_leaf=2,
        max_features="sqrt",
        random_state=42,
        n_jobs=-1
    )

    pipeline = Pipeline(
        steps=[
            (
                "preprocessor",
                create_preprocessor()
            ),
            (
                "model",
                rf
            )
        ]
    )

    model = TransformedTargetRegressor(
        regressor=pipeline,
        func=np.log1p,
        inverse_func=np.expm1,
        check_inverse=True
    )

    return model


# ============================================================
# 6. METRIC FUNCTION
# ============================================================

def calculate_metrics(actual, predicted):

    return {
        "MAE": float(
            mean_absolute_error(
                actual,
                predicted
            )
        ),

        "RMSE": float(
            np.sqrt(
                mean_squared_error(
                    actual,
                    predicted
                )
            )
        ),

        "R2": float(
            r2_score(
                actual,
                predicted
            )
        )
    }


# ============================================================
# 7. CROP-WISE METRICS
# ============================================================

def calculate_crop_metrics(
    actual_df,
    predictions,
    label
):

    temp = actual_df.copy()

    temp["prediction"] = predictions

    rows = []

    for crop, group in temp.groupby("crop"):

        actual = group[TARGET]
        predicted = group["prediction"]

        rows.append(
            {
                "crop": crop,
                "samples": len(group),

                f"{label}_MAE":
                    mean_absolute_error(
                        actual,
                        predicted
                    ),

                f"{label}_RMSE":
                    np.sqrt(
                        mean_squared_error(
                            actual,
                            predicted
                        )
                    ),

                f"{label}_R2":
                    (
                        r2_score(
                            actual,
                            predicted
                        )
                        if len(group) >= 2
                        and actual.nunique() > 1
                        else np.nan
                    )
            }
        )

    return pd.DataFrame(rows)


# ============================================================
# 8. TRAIN GLOBAL MODEL
# ============================================================

print("\n" + "=" * 70)
print("STEP 1 - TRAINING GLOBAL RANDOM FOREST LOG")
print("=" * 70)

global_model = create_global_model()

global_model.fit(
    X_train,
    y_train
)

validation_global_predictions = (
    global_model.predict(
        X_validation
    )
)

test_global_predictions = (
    global_model.predict(
        X_test
    )
)

validation_global_metrics = calculate_metrics(
    y_validation,
    validation_global_predictions
)

test_global_metrics = calculate_metrics(
    y_test,
    test_global_predictions
)

print("\nGlobal Validation:")
print(
    f"MAE  : {validation_global_metrics['MAE']:.4f}"
)
print(
    f"RMSE : {validation_global_metrics['RMSE']:.4f}"
)
print(
    f"R²   : {validation_global_metrics['R2']:.4f}"
)

print("\nGlobal Test:")
print(
    f"MAE  : {test_global_metrics['MAE']:.4f}"
)
print(
    f"RMSE : {test_global_metrics['RMSE']:.4f}"
)
print(
    f"R²   : {test_global_metrics['R2']:.4f}"
)


# ============================================================
# 9. LEARN CROP BIAS FROM TRAINING DATA ONLY
# ============================================================

print("\n" + "=" * 70)
print("STEP 2 - LEARNING CROP BIAS")
print("=" * 70)

print(
    "\nGenerating out-of-fold training predictions..."
)

kf = KFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

oof_predictions = np.zeros(
    len(train_df)
)

for fold, (train_idx, valid_idx) in enumerate(
    kf.split(X_train),
    start=1
):

    print(f"Training fold {fold}/5...")

    fold_model = create_global_model()

    fold_model.fit(
        X_train.iloc[train_idx],
        y_train.iloc[train_idx]
    )

    oof_predictions[valid_idx] = (
        fold_model.predict(
            X_train.iloc[valid_idx]
        )
    )


oof_df = train_df[
    [
        "crop",
        TARGET
    ]
].copy()

oof_df["prediction"] = oof_predictions

oof_df["residual"] = (
    oof_df[TARGET]
    - oof_df["prediction"]
)


# ============================================================
# 10. CALCULATE CROP BIAS
# ============================================================

crop_bias = (
    oof_df
    .groupby("crop")
    .agg(
        mean_residual=("residual", "mean"),
        sample_count=("residual", "count")
    )
    .reset_index()
)


# ============================================================
# 11. SHRINK SMALL-CROP BIASES
# ============================================================

"""
Small crops can have unreliable bias estimates.

We shrink crop bias toward zero using:

    adjusted_bias =
        bias * n / (n + smoothing)

This prevents a crop with very few observations from
receiving an excessively large correction.
"""

SMOOTHING = 50

crop_bias["adjusted_bias"] = (
    crop_bias["mean_residual"]
    * crop_bias["sample_count"]
    / (
        crop_bias["sample_count"]
        + SMOOTHING
    )
)


print("\nCrop bias examples:")

print(
    crop_bias
    .sort_values(
        "adjusted_bias",
        ascending=False
    )
    .head(10)
    .to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}"
    )
)


# ============================================================
# 12. APPLY CROP BIAS
# ============================================================

bias_map = dict(
    zip(
        crop_bias["crop"],
        crop_bias["adjusted_bias"]
    )
)


def apply_crop_bias(
    dataframe,
    predictions
):

    result = np.asarray(
        predictions,
        dtype=float
    ).copy()

    crops = dataframe["crop"].values

    for i, crop in enumerate(crops):

        result[i] += bias_map.get(
            crop,
            0.0
        )

    # Yield cannot be negative
    result = np.maximum(
        result,
        0
    )

    return result


validation_crop_aware_predictions = (
    apply_crop_bias(
        X_validation,
        validation_global_predictions
    )
)

test_crop_aware_predictions = (
    apply_crop_bias(
        X_test,
        test_global_predictions
    )
)


# ============================================================
# 13. CROP-AWARE METRICS
# ============================================================

validation_crop_aware_metrics = calculate_metrics(
    y_validation,
    validation_crop_aware_predictions
)

test_crop_aware_metrics = calculate_metrics(
    y_test,
    test_crop_aware_predictions
)


print("\n" + "=" * 70)
print("CROP-AWARE RESULTS")
print("=" * 70)

print("\nCrop-Aware Validation:")
print(
    f"MAE  : {validation_crop_aware_metrics['MAE']:.4f}"
)
print(
    f"RMSE : {validation_crop_aware_metrics['RMSE']:.4f}"
)
print(
    f"R²   : {validation_crop_aware_metrics['R2']:.4f}"
)

print("\nCrop-Aware Test:")
print(
    f"MAE  : {test_crop_aware_metrics['MAE']:.4f}"
)
print(
    f"RMSE : {test_crop_aware_metrics['RMSE']:.4f}"
)
print(
    f"R²   : {test_crop_aware_metrics['R2']:.4f}"
)


# ============================================================
# 14. CROP-WISE COMPARISON
# ============================================================

global_crop_metrics = calculate_crop_metrics(
    test_df,
    test_global_predictions,
    "global"
)

crop_aware_crop_metrics = calculate_crop_metrics(
    test_df,
    test_crop_aware_predictions,
    "crop_aware"
)

crop_comparison = global_crop_metrics.merge(
    crop_aware_crop_metrics,
    on=["crop", "samples"],
    how="outer"
)

crop_comparison["MAE_change"] = (
    crop_comparison["crop_aware_MAE"]
    - crop_comparison["global_MAE"]
)

crop_comparison["RMSE_change"] = (
    crop_comparison["crop_aware_RMSE"]
    - crop_comparison["global_RMSE"]
)

crop_comparison = crop_comparison.sort_values(
    "MAE_change"
)

crop_comparison.to_csv(
    RESULTS_DIR / "crop_aware_comparison.csv",
    index=False
)


# ============================================================
# 15. COCONUT COMPARISON
# ============================================================

print("\n" + "=" * 70)
print("COCONUT COMPARISON")
print("=" * 70)

coconut_result = crop_comparison[
    crop_comparison["crop"].str.lower() == "coconut"
]

if not coconut_result.empty:

    print(
        coconut_result.to_string(
            index=False,
            float_format=lambda x: f"{x:.4f}"
        )
    )


# ============================================================
# 16. VALIDATION-BASED MODEL DECISION
# ============================================================

if (
    validation_crop_aware_metrics["RMSE"]
    < validation_global_metrics["RMSE"]
):

    selected_approach = "Crop-Aware Random Forest Log"

    selected_test_predictions = (
        test_crop_aware_predictions
    )

    selected_test_metrics = (
        test_crop_aware_metrics
    )

    print("\nCrop-aware approach improved validation RMSE.")

else:

    selected_approach = "Global Random Forest Log"

    selected_test_predictions = (
        test_global_predictions
    )

    selected_test_metrics = (
        test_global_metrics
    )

    print(
        "\nCrop-aware approach did NOT improve "
        "validation RMSE."
    )

    print(
        "Keeping the simpler global model."
    )


# ============================================================
# 17. SAVE PREDICTIONS
# ============================================================

final_predictions_df = test_df.copy()

final_predictions_df["global_prediction"] = (
    test_global_predictions
)

final_predictions_df["crop_aware_prediction"] = (
    test_crop_aware_predictions
)

final_predictions_df["selected_prediction"] = (
    selected_test_predictions
)

final_predictions_df["selected_absolute_error"] = (
    final_predictions_df[TARGET]
    - final_predictions_df["selected_prediction"]
).abs()

final_predictions_df.to_csv(
    RESULTS_DIR / "crop_aware_test_predictions.csv",
    index=False
)


# ============================================================
# 18. SAVE RESULTS
# ============================================================

experiment_results = {

    "experiment": "Crop-aware Random Forest Log",

    "global_model": {
        "validation": validation_global_metrics,
        "test": test_global_metrics
    },

    "crop_aware_model": {
        "validation": validation_crop_aware_metrics,
        "test": test_crop_aware_metrics
    },

    "selected_approach": selected_approach,

    "selected_test_metrics": selected_test_metrics,

    "bias_smoothing": SMOOTHING
}


with open(
    RESULTS_FILE,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        experiment_results,
        file,
        indent=4
    )


# ============================================================
# 19. DO NOT REPLACE FINAL MODEL YET
# ============================================================

"""
Important:
We intentionally do NOT overwrite:

    models/best_yield_model.joblib

because this is an experiment.

We will only replace the final model after reviewing the
validation/test results.
"""


# ============================================================
# 20. COMPLETION
# ============================================================

print("\n" + "=" * 70)
print("CROP-AWARE EXPERIMENT COMPLETED")
print("=" * 70)

print(
    f"\nSelected approach: {selected_approach}"
)

print(
    f"Selected Test MAE  : "
    f"{selected_test_metrics['MAE']:.4f}"
)

print(
    f"Selected Test RMSE : "
    f"{selected_test_metrics['RMSE']:.4f}"
)

print(
    f"Selected Test R²   : "
    f"{selected_test_metrics['R2']:.4f}"
)

print("\nFiles created:")

print(
    " - results/crop_aware_comparison.csv"
)

print(
    " - results/crop_aware_test_predictions.csv"
)

print(
    " - results/crop_aware_comparison.json"
)

print(
    "\nFinal model file was NOT modified."
)

print("=" * 70)