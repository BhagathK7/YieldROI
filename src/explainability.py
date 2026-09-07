"""
Yield ROI - Explainable AI (SHAP)
---------------------------------

Uses SHAP KernelExplainer on the complete trained prediction
pipeline.

Original project features:
    district
    crop
    season
    year
    area

The explanation therefore remains at the project-feature level.

Outputs:
    shap_feature_importance.csv
    shap_feature_importance.png
    shap_summary.png
    individual_shap_explanations.csv
    crop_shap_importance.csv
    shap_values.csv
"""

from pathlib import Path
import warnings

import numpy as np
import pandas as pd
import joblib
import shap
import matplotlib.pyplot as plt


warnings.filterwarnings("ignore")


# ============================================================
# 1. PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"
RESULTS_DIR = BASE_DIR / "results"

MODEL_FILE = MODEL_DIR / "best_yield_model.joblib"
TRAIN_FILE = DATA_DIR / "train.csv"
TEST_FILE = DATA_DIR / "test.csv"

RESULTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 2. FEATURES
# ============================================================

FEATURES = [
    "district",
    "crop",
    "season",
    "year",
    "area"
]

TARGET = "crop_yield"


# ============================================================
# 3. LOAD MODEL AND DATA
# ============================================================

print("=" * 70)
print("YIELD ROI - SHAP EXPLAINABILITY")
print("=" * 70)

print("\nLoading model...")

model = joblib.load(
    MODEL_FILE
)

train_df = pd.read_csv(
    TRAIN_FILE
)

test_df = pd.read_csv(
    TEST_FILE
)

X_train = train_df[
    FEATURES
].copy()

X_test = test_df[
    FEATURES
].copy()

print(
    f"Test samples: {len(X_test):,}"
)

print(
    f"Original features: {len(FEATURES)}"
)


# ============================================================
# 4. SHAP SAMPLE
# ============================================================

"""
KernelExplainer is computationally expensive.

We therefore use:
    - 40 background samples
    - 100 explanation samples

The seed makes the experiment reproducible.
"""

BACKGROUND_SIZE = 40
EXPLANATION_SIZE = 100

rng = np.random.default_rng(
    42
)


if len(X_train) > BACKGROUND_SIZE:

    background_indices = rng.choice(
        len(X_train),
        size=BACKGROUND_SIZE,
        replace=False
    )

    background = X_train.iloc[
        background_indices
    ].copy()

else:

    background = X_train.copy()


if len(X_test) > EXPLANATION_SIZE:

    explanation_indices = rng.choice(
        len(X_test),
        size=EXPLANATION_SIZE,
        replace=False
    )

    explanation_indices = np.sort(
        explanation_indices
    )

    X_explain = X_test.iloc[
        explanation_indices
    ].copy()

else:

    explanation_indices = np.arange(
        len(X_test)
    )

    X_explain = X_test.copy()


print(
    f"Background samples: "
    f"{len(background):,}"
)

print(
    f"Explanation samples: "
    f"{len(X_explain):,}"
)


# ============================================================
# 5. CONVERT CATEGORICAL FEATURES TO NUMERIC CODES
# ============================================================

"""
KernelExplainer requires numerical input.

We create a fixed numerical representation of the original
five features.

Categorical values are converted into integer codes.

The prediction wrapper converts the codes back to the exact
original strings before passing them to the trained model.
"""

category_maps = {}

X_combined = pd.concat(
    [
        X_train[FEATURES],
        X_test[FEATURES]
    ],
    ignore_index=True
)


for feature in [
    "district",
    "crop",
    "season"
]:

    categories = sorted(
        X_combined[
            feature
        ].astype(str).unique()
    )

    category_maps[
        feature
    ] = {
        value: index
        for index, value in enumerate(
            categories
        )
    }


inverse_category_maps = {}

for feature, mapping in category_maps.items():

    inverse_category_maps[
        feature
    ] = {
        index: value
        for value, index in mapping.items()
    }


def encode_dataframe(
    dataframe
):

    result = dataframe[
        FEATURES
    ].copy()

    for feature in [
        "district",
        "crop",
        "season"
    ]:

        result[feature] = (
            result[feature]
            .astype(str)
            .map(
                category_maps[
                    feature
                ]
            )
        )

    result["year"] = pd.to_numeric(
        result["year"]
    )

    result["area"] = pd.to_numeric(
        result["area"]
    )

    return result[
        FEATURES
    ].astype(float)


def decode_array(
    array
):

    decoded = pd.DataFrame(
        array,
        columns=FEATURES
    )

    for feature in [
        "district",
        "crop",
        "season"
    ]:

        decoded[feature] = (
            decoded[feature]
            .round()
            .astype(int)
            .map(
                inverse_category_maps[
                    feature
                ]
            )
        )

    decoded["year"] = (
        decoded["year"]
        .round()
        .astype(int)
    )

    decoded["area"] = (
        decoded["area"]
        .astype(float)
    )

    return decoded[
        FEATURES
    ]


background_numeric = encode_dataframe(
    background
)

explain_numeric = encode_dataframe(
    X_explain
)


# ============================================================
# 6. MODEL PREDICTION WRAPPER
# ============================================================

def predict_from_numeric(
    numeric_data
):

    numeric_data = np.asarray(
        numeric_data
    )

    decoded_data = decode_array(
        numeric_data
    )

    predictions = model.predict(
        decoded_data
    )

    return np.asarray(
        predictions,
        dtype=float
    )


# ============================================================
# 7. CREATE KERNEL EXPLAINER
# ============================================================

print(
    "\nCreating SHAP KernelExplainer..."
)

explainer = shap.KernelExplainer(
    predict_from_numeric,
    background_numeric.values
)


# ============================================================
# 8. CALCULATE SHAP VALUES
# ============================================================

print(
    "\nCalculating SHAP values..."
)

print(
    "This can take several minutes."
)

shap_values = explainer.shap_values(
    explain_numeric.values,
    nsamples=50
)

shap_values = np.asarray(
    shap_values
)

print(
    f"\nSHAP values shape: "
    f"{shap_values.shape}"
)


# ============================================================
# 9. HANDLE SHAP OUTPUT SHAPE
# ============================================================

if shap_values.ndim == 3:

    shap_values = shap_values[:, :, 0]


# ============================================================
# 10. GLOBAL FEATURE IMPORTANCE
# ============================================================

mean_abs_shap = np.abs(
    shap_values
).mean(
    axis=0
)


importance_df = pd.DataFrame(
    {
        "feature": FEATURES,

        "mean_absolute_shap":
            mean_abs_shap
    }
)


importance_df = (
    importance_df
    .sort_values(
        "mean_absolute_shap",
        ascending=False
    )
    .reset_index(
        drop=True
    )
)


total_importance = (
    importance_df[
        "mean_absolute_shap"
    ].sum()
)


importance_df[
    "importance_percentage"
] = (
    importance_df[
        "mean_absolute_shap"
    ]
    / total_importance
    * 100
)


importance_df.to_csv(
    RESULTS_DIR
    / "shap_feature_importance.csv",
    index=False
)


# ============================================================
# 11. PRINT GLOBAL IMPORTANCE
# ============================================================

print("\n" + "=" * 70)
print("GLOBAL SHAP FEATURE IMPORTANCE")
print("=" * 70)

print(
    importance_df.to_string(
        index=False,
        float_format=lambda x: f"{x:.6f}"
    )
)


# ============================================================
# 12. FEATURE IMPORTANCE PLOT
# ============================================================

print(
    "\nCreating SHAP feature importance plot..."
)

plot_df = importance_df.sort_values(
    "mean_absolute_shap"
)


plt.figure(
    figsize=(10, 6)
)

plt.barh(
    plot_df["feature"],
    plot_df["mean_absolute_shap"]
)

plt.xlabel(
    "Mean Absolute SHAP Value"
)

plt.ylabel(
    "Feature"
)

plt.title(
    "Global SHAP Feature Importance - Yield Prediction"
)

plt.tight_layout()

plt.savefig(
    RESULTS_DIR
    / "shap_feature_importance.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# 13. SHAP SUMMARY PLOT
# ============================================================

print(
    "Creating SHAP summary plot..."
)

shap.summary_plot(
    shap_values,
    explain_numeric.values,
    feature_names=FEATURES,
    show=False
)

plt.title(
    "SHAP Summary - Yield Prediction"
)

plt.tight_layout()

plt.savefig(
    RESULTS_DIR
    / "shap_summary.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# 14. INDIVIDUAL EXPLANATIONS
# ============================================================

print(
    "Creating individual explanations..."
)

individual_results = []

INDIVIDUAL_COUNT = min(
    10,
    len(X_explain)
)


for i in range(
    INDIVIDUAL_COUNT
):

    original_index = int(
        explanation_indices[i]
    )

    row = test_df.iloc[
        original_index
    ]

    shap_row = shap_values[i]

    predicted_value = model.predict(
        pd.DataFrame(
            [
                {
                    feature:
                        row[feature]
                    for feature in FEATURES
                }
            ]
        )
    )[0]


    sorted_indices = np.argsort(
        np.abs(shap_row)
    )[::-1]


    for rank, feature_index in enumerate(
        sorted_indices,
        start=1
    ):

        contribution = (
            shap_row[
                feature_index
            ]
        )

        individual_results.append(
            {
                "sample_index":
                    original_index,

                "year":
                    int(row["year"]),

                "district":
                    row["district"],

                "crop":
                    row["crop"],

                "season":
                    row["season"],

                "area":
                    float(row["area"]),

                "actual_yield":
                    float(
                        row[TARGET]
                    ),

                "predicted_yield":
                    float(
                        predicted_value
                    ),

                "feature":
                    FEATURES[
                        feature_index
                    ],

                "shap_value":
                    float(
                        contribution
                    ),

                "absolute_shap":
                    float(
                        abs(
                            contribution
                        )
                    ),

                "impact":
                    (
                        "increases prediction"
                        if contribution > 0
                        else
                        "decreases prediction"
                    ),

                "rank":
                    rank
            }
        )


individual_df = pd.DataFrame(
    individual_results
)


individual_df.to_csv(
    RESULTS_DIR
    / "individual_shap_explanations.csv",
    index=False
)


# ============================================================
# 15. CROP-LEVEL SHAP SUMMARY
# ============================================================

print(
    "Calculating crop-level SHAP importance..."
)

crop_records = []


for i, original_index in enumerate(
    explanation_indices
):

    crop_records.append(
        {
            "crop":
                test_df.iloc[
                    original_index
                ]["crop"],

            "shap_importance":
                np.abs(
                    shap_values[i]
                ).mean()
        }
    )


crop_shap_df = pd.DataFrame(
    crop_records
)


crop_shap_summary = (
    crop_shap_df
    .groupby("crop")
    .agg(
        mean_shap_importance=(
            "shap_importance",
            "mean"
        ),

        samples=(
            "shap_importance",
            "count"
        )
    )
    .reset_index()
    .sort_values(
        "mean_shap_importance",
        ascending=False
    )
)


crop_shap_summary.to_csv(
    RESULTS_DIR
    / "crop_shap_importance.csv",
    index=False
)


# ============================================================
# 16. SAVE RAW SHAP VALUES
# ============================================================

shap_values_df = pd.DataFrame(
    shap_values,
    columns=FEATURES
)


shap_values_df.to_csv(
    RESULTS_DIR
    / "shap_values.csv",
    index=False
)


# ============================================================
# 17. COMPLETION
# ============================================================

print("\n" + "=" * 70)
print("SHAP ANALYSIS COMPLETED")
print("=" * 70)

print("\nFiles created:")

print(
    " - results/shap_feature_importance.csv"
)

print(
    " - results/shap_feature_importance.png"
)

print(
    " - results/shap_summary.png"
)

print(
    " - results/individual_shap_explanations.csv"
)

print(
    " - results/crop_shap_importance.csv"
)

print(
    " - results/shap_values.csv"
)

print(
    "\nThe trained model was NOT modified."
)

print("=" * 70)