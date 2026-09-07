"""
Final Yield Prediction Model Training
--------------------------------------

This script:
1. Loads the prepared train/validation/test datasets.
2. Uses the following features:
   - district
   - crop
   - season
   - year
   - area
3. Excludes production to avoid target leakage.
4. Trains raw-target and log-target versions of:
   - Ridge Regression
   - Random Forest
   - XGBoost
5. Compares models using the validation set.
6. Selects the best model based on validation RMSE.
7. Evaluates the selected model on the untouched test set.
8. Saves the final model, metrics, and predictions.

Target:
    crop_yield

Train:
    1997-2018

Validation:
    2019-2020

Test:
    2021-2022
"""

from pathlib import Path
import json

import numpy as np
import pandas as pd
import joblib

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.dummy import DummyRegressor
from sklearn.compose import TransformedTargetRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from xgboost import XGBRegressor


# ============================================================
# 1. PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"

MODEL_DIR.mkdir(parents=True, exist_ok=True)


TRAIN_FILE = DATA_DIR / "train.csv"
VALIDATION_FILE = DATA_DIR / "validation.csv"
TEST_FILE = DATA_DIR / "test.csv"

BEST_MODEL_FILE = MODEL_DIR / "best_yield_model.joblib"
METRICS_FILE = MODEL_DIR / "model_metrics.json"

TEST_PREDICTIONS_FILE = DATA_DIR / "test_predictions.csv"


# ============================================================
# 2. LOAD DATA
# ============================================================

print("=" * 70)
print("YIELD ROI - FINAL YIELD MODEL TRAINING")
print("=" * 70)

print("\nLoading datasets...")

train_df = pd.read_csv(TRAIN_FILE)
validation_df = pd.read_csv(VALIDATION_FILE)
test_df = pd.read_csv(TEST_FILE)

print(f"Train rows      : {len(train_df):,}")
print(f"Validation rows : {len(validation_df):,}")
print(f"Test rows       : {len(test_df):,}")


# ============================================================
# 3. FEATURES AND TARGET
# ============================================================

FEATURES = [
    "district",
    "crop",
    "season",
    "year",
    "area"
]

TARGET = "crop_yield"


# Check required columns
required_columns = FEATURES + [TARGET]

for column in required_columns:
    if column not in train_df.columns:
        raise ValueError(f"Missing column in train.csv: {column}")

    if column not in validation_df.columns:
        raise ValueError(f"Missing column in validation.csv: {column}")

    if column not in test_df.columns:
        raise ValueError(f"Missing column in test.csv: {column}")


X_train = train_df[FEATURES].copy()
y_train = train_df[TARGET].copy()

X_validation = validation_df[FEATURES].copy()
y_validation = validation_df[TARGET].copy()

X_test = test_df[FEATURES].copy()
y_test = test_df[TARGET].copy()


# ============================================================
# 4. FEATURE TYPES
# ============================================================

CATEGORICAL_FEATURES = [
    "district",
    "crop",
    "season"
]

NUMERICAL_FEATURES = [
    "year",
    "area"
]


# ============================================================
# 5. PREPROCESSING PIPELINE
# ============================================================

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


preprocessor = ColumnTransformer(
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
# 6. MODEL FACTORIES
# ============================================================

def create_ridge():

    model = Ridge(
        alpha=10.0
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model)
        ]
    )


def create_random_forest():

    model = RandomForestRegressor(
        n_estimators=500,
        max_depth=None,
        min_samples_leaf=2,
        max_features="sqrt",
        random_state=42,
        n_jobs=-1
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model)
        ]
    )


def create_xgboost():

    model = XGBRegressor(
        n_estimators=600,
        max_depth=8,
        learning_rate=0.05,
        subsample=0.85,
        colsample_bytree=0.85,
        objective="reg:squarederror",
        eval_metric="rmse",
        random_state=42,
        n_jobs=-1
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model)
        ]
    )


def create_dummy():

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "model",
                DummyRegressor(strategy="mean")
            )
        ]
    )


# ============================================================
# 7. LOG-TARGET MODEL WRAPPER
# ============================================================

def create_log_target_model(model_pipeline):

    """
    Transforms the target using log1p during training
    and converts predictions back using expm1.

    This is useful because crop yield is strongly skewed,
    with some crops having much larger yield values.
    """

    return TransformedTargetRegressor(
        regressor=model_pipeline,
        func=np.log1p,
        inverse_func=np.expm1,
        check_inverse=True
    )


# ============================================================
# 8. MODEL COLLECTION
# ============================================================

models = {

    "Dummy Mean": create_dummy(),

    "Ridge Raw": create_ridge(),

    "Ridge Log": create_log_target_model(
        create_ridge()
    ),

    "Random Forest Raw": create_random_forest(),

    "Random Forest Log": create_log_target_model(
        create_random_forest()
    ),

    "XGBoost Raw": create_xgboost(),

    "XGBoost Log": create_log_target_model(
        create_xgboost()
    )
}


# ============================================================
# 9. METRIC FUNCTION
# ============================================================

def calculate_metrics(actual, predicted):

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

    return {
        "MAE": float(mae),
        "RMSE": float(rmse),
        "R2": float(r2)
    }


# ============================================================
# 10. TRAIN AND VALIDATE MODELS
# ============================================================

results = []

trained_models = {}

print("\n" + "=" * 70)
print("MODEL TRAINING")
print("=" * 70)


for model_name, model in models.items():

    print(f"\nTraining: {model_name}")

    model.fit(
        X_train,
        y_train
    )

    validation_predictions = model.predict(
        X_validation
    )

    metrics = calculate_metrics(
        y_validation,
        validation_predictions
    )

    results.append(
        {
            "model": model_name,
            "MAE": metrics["MAE"],
            "RMSE": metrics["RMSE"],
            "R2": metrics["R2"]
        }
    )

    trained_models[model_name] = model

    print(
        f"Validation MAE  : {metrics['MAE']:.4f}"
    )

    print(
        f"Validation RMSE : {metrics['RMSE']:.4f}"
    )

    print(
        f"Validation R²   : {metrics['R2']:.4f}"
    )


# ============================================================
# 11. MODEL COMPARISON
# ============================================================

results_df = pd.DataFrame(results)

results_df = results_df.sort_values(
    by="RMSE",
    ascending=True
).reset_index(drop=True)


print("\n" + "=" * 70)
print("VALIDATION MODEL COMPARISON")
print("=" * 70)

print(
    results_df.to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}"
    )
)


# ============================================================
# 12. SELECT BEST MODEL
# ============================================================

best_model_name = results_df.iloc[0]["model"]

best_model = trained_models[
    best_model_name
]

best_validation_rmse = float(
    results_df.iloc[0]["RMSE"]
)

print("\n" + "=" * 70)
print("BEST MODEL")
print("=" * 70)

print(f"Selected model : {best_model_name}")
print(
    f"Validation RMSE: {best_validation_rmse:.4f}"
)


# ============================================================
# 13. FINAL TEST EVALUATION
# ============================================================

print("\n" + "=" * 70)
print("FINAL TEST EVALUATION")
print("=" * 70)

test_predictions = best_model.predict(
    X_test
)

test_metrics = calculate_metrics(
    y_test,
    test_predictions
)

print(
    f"Test MAE  : {test_metrics['MAE']:.4f}"
)

print(
    f"Test RMSE : {test_metrics['RMSE']:.4f}"
)

print(
    f"Test R²   : {test_metrics['R2']:.4f}"
)


# ============================================================
# 14. SAVE TEST PREDICTIONS
# ============================================================

prediction_output = test_df.copy()

prediction_output["predicted_yield"] = test_predictions

prediction_output["absolute_error"] = (
    prediction_output[TARGET]
    - prediction_output["predicted_yield"]
).abs()

prediction_output["percentage_error"] = (
    prediction_output["absolute_error"]
    / prediction_output[TARGET]
    * 100
)

prediction_output.to_csv(
    TEST_PREDICTIONS_FILE,
    index=False
)


# ============================================================
# 15. SAVE FINAL MODEL
# ============================================================

joblib.dump(
    best_model,
    BEST_MODEL_FILE
)


# ============================================================
# 16. SAVE METRICS
# ============================================================

metrics_output = {

    "project": "Yield ROI",

    "target": TARGET,

    "features": FEATURES,

    "data_split": {
        "train": "1997-2018",
        "validation": "2019-2020",
        "test": "2021-2022"
    },

    "best_model": best_model_name,

    "validation": {
        "MAE": float(
            results_df.iloc[0]["MAE"]
        ),
        "RMSE": float(
            results_df.iloc[0]["RMSE"]
        ),
        "R2": float(
            results_df.iloc[0]["R2"]
        )
    },

    "test": test_metrics,

    "all_validation_results": results
}


with open(
    METRICS_FILE,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        metrics_output,
        file,
        indent=4
    )


# ============================================================
# 17. FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("TRAINING COMPLETED SUCCESSFULLY")
print("=" * 70)

print(
    f"\nBest Model      : {best_model_name}"
)

print(
    f"Validation RMSE : {best_validation_rmse:.4f}"
)

print(
    f"Test MAE        : {test_metrics['MAE']:.4f}"
)

print(
    f"Test RMSE       : {test_metrics['RMSE']:.4f}"
)

print(
    f"Test R²         : {test_metrics['R2']:.4f}"
)

print("\nSaved files:")

print(
    f"Model      : {BEST_MODEL_FILE}"
)

print(
    f"Metrics    : {METRICS_FILE}"
)

print(
    f"Predictions: {TEST_PREDICTIONS_FILE}"
)

print("\n" + "=" * 70)
print("NEXT STEP: SEND ME THIS TERMINAL OUTPUT")
print("=" * 70)