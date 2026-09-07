"""
YieldROI - Integrated Yield Prediction + ROI

Pipeline:

User Input
    ↓
Existing trained Yield Model
    ↓
Predicted Yield (tonnes/ha)
    ↓
Production
    ↓
Revenue
    ↓
Cost
    ↓
Profit
    ↓
ROI %

IMPORTANT:
    The trained model is loaded directly from:
        models/best_yield_model.joblib

    The model output is used directly as tonnes/hectare.
    No additional /1000 conversion is applied.
"""

from pathlib import Path
import json
import math

import joblib
import pandas as pd


# ============================================================
# 1. PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_DIR = BASE_DIR / "models"
RESULTS_DIR = BASE_DIR / "results"

MODEL_FILE = MODEL_DIR / "best_yield_model.joblib"

OUTPUT_FILE = (
    RESULTS_DIR
    / "integrated_prediction_roi.json"
)

RESULTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 2. ROI BENCHMARK DATA
# ============================================================

# Cost:
#     INR / hectare
#
# Price:
#     INR / tonne

COST_BENCHMARKS = {

    "rice": 93687.0,

    "sorghum": 53621.0,

    "maize": 95530.0,

    "black gram": 52775.0,

    "blackgram": 52775.0,

    "groundnut": 98650.0,

    "gingelly": 55099.0,

    "sesamum": 55099.0,

    "cotton": 127589.0,

    "cotton lint": 127589.0,

    "sugarcane": 277275.0
}


PRICE_BENCHMARKS = {

    "rice": {
        "price": 24410.0,
        "type": "MSP - Paddy Common"
    },

    "sorghum": {
        "price": 40230.0,
        "type": "MSP - Sorghum Hybrid"
    },

    "maize": {
        "price": 24100.0,
        "type": "MSP - Maize"
    },

    "black gram": {
        "price": 82000.0,
        "type": "MSP - Blackgram"
    },

    "blackgram": {
        "price": 82000.0,
        "type": "MSP - Blackgram"
    },

    "groundnut": {
        "price": 75170.0,
        "type": "MSP - Groundnut"
    },

    "gingelly": {
        "price": 103460.0,
        "type": "MSP - Sesamum"
    },

    "sesamum": {
        "price": 103460.0,
        "type": "MSP - Sesamum"
    },

    "cotton": {
        "price": 82670.0,
        "type": "MSP - Cotton Medium Staple"
    },

    "cotton lint": {
        "price": 82670.0,
        "type": "MSP - Cotton Medium Staple"
    },

    "sugarcane": {
        "price": 3650.0,
        "type": "Published reference price"
    }
}


# ============================================================
# 3. UTILITY FUNCTIONS
# ============================================================

def normalize_crop(crop):

    return (
        str(crop)
        .strip()
        .lower()
        .replace("_", " ")
        .replace("-", " ")
    )


def validate_text(
    value,
    field_name
):

    value = str(value).strip()

    if not value:

        raise ValueError(
            f"{field_name} cannot be empty."
        )

    return value


def validate_number(
    value,
    field_name,
    minimum=None
):

    try:

        number = float(value)

    except (TypeError, ValueError):

        raise ValueError(
            f"{field_name} must be a valid number."
        )

    if not math.isfinite(number):

        raise ValueError(
            f"{field_name} must be a finite number."
        )

    if (
        minimum is not None
        and number < minimum
    ):

        raise ValueError(
            f"{field_name} must be at least "
            f"{minimum}."
        )

    return number


# ============================================================
# 4. LOAD MODEL
# ============================================================

def load_model():

    if not MODEL_FILE.exists():

        raise FileNotFoundError(
            "\nTrained model not found:\n"
            f"{MODEL_FILE}\n\n"
            "Please run:\n"
            "python src/train_models.py"
        )

    print(
        "\nLoading trained YieldROI model..."
    )

    model = joblib.load(
        MODEL_FILE
    )

    print(
        "Model loaded successfully:"
    )

    print(
        f"  {MODEL_FILE}"
    )

    return model


# ============================================================
# 5. PREDICT YIELD
# ============================================================

def predict_yield(
    model,
    district,
    crop,
    season,
    year,
    area
):

    # The training script uses exactly these
    # five features.
    #
    # district
    # crop
    # season
    # year
    # area

    input_data = pd.DataFrame(
        [
            {
                "district": district,
                "crop": crop,
                "season": season,
                "year": year,
                "area": area
            }
        ]
    )

    prediction = model.predict(
        input_data
    )

    predicted_yield = float(
        prediction[0]
    )

    if not math.isfinite(
        predicted_yield
    ):

        raise ValueError(
            "The ML model returned an invalid "
            "yield prediction."
        )

    # A yield prediction cannot be negative.

    predicted_yield = max(
        0.0,
        predicted_yield
    )

    return predicted_yield


# ============================================================
# 6. CALCULATE ROI
# ============================================================

def calculate_roi(
    crop,
    predicted_yield_tonnes_per_ha,
    area_hectares
):

    crop_key = normalize_crop(
        crop
    )

    # --------------------------------------------------------
    # Check crop
    # --------------------------------------------------------

    if crop_key not in COST_BENCHMARKS:

        available = ", ".join(
            sorted(
                COST_BENCHMARKS.keys()
            )
        )

        raise ValueError(
            f"\nNo cultivation-cost benchmark "
            f"is configured for '{crop}'.\n\n"
            f"Currently supported crops:\n"
            f"{available}"
        )

    if crop_key not in PRICE_BENCHMARKS:

        raise ValueError(
            f"No reference price configured "
            f"for '{crop}'."
        )

    # --------------------------------------------------------
    # Production
    # --------------------------------------------------------

    predicted_production_tonnes = (
        predicted_yield_tonnes_per_ha
        * area_hectares
    )

    # --------------------------------------------------------
    # Cost
    # --------------------------------------------------------

    cost_per_hectare = (
        COST_BENCHMARKS[crop_key]
    )

    total_cost = (
        cost_per_hectare
        * area_hectares
    )

    # --------------------------------------------------------
    # Price
    # --------------------------------------------------------

    price_data = PRICE_BENCHMARKS[
        crop_key
    ]

    price_per_tonne = (
        price_data["price"]
    )

    price_type = (
        price_data["type"]
    )

    # --------------------------------------------------------
    # Revenue
    # --------------------------------------------------------

    revenue = (
        predicted_production_tonnes
        * price_per_tonne
    )

    # --------------------------------------------------------
    # Profit
    # --------------------------------------------------------

    profit = (
        revenue
        - total_cost
    )

    # --------------------------------------------------------
    # ROI
    # --------------------------------------------------------

    if total_cost > 0:

        roi_percentage = (
            profit
            / total_cost
        ) * 100

    else:

        roi_percentage = None

    # --------------------------------------------------------
    # Profitability
    # --------------------------------------------------------

    if profit > 0:

        profitability_status = (
            "Profitable"
        )

    elif profit < 0:

        profitability_status = (
            "Loss"
        )

    else:

        profitability_status = (
            "Break-even"
        )

    return {

        "predicted_yield_tonnes_per_ha":
            round(
                predicted_yield_tonnes_per_ha,
                4
            ),

        "predicted_production_tonnes":
            round(
                predicted_production_tonnes,
                4
            ),

        "cost_per_hectare":
            round(
                cost_per_hectare,
                2
            ),

        "total_cost":
            round(
                total_cost,
                2
            ),

        "price_per_tonne":
            round(
                price_per_tonne,
                2
            ),

        "price_type":
            price_type,

        "revenue":
            round(
                revenue,
                2
            ),

        "profit":
            round(
                profit,
                2
            ),

        "roi_percentage":
            round(
                roi_percentage,
                2
            )
            if roi_percentage is not None
            else None,

        "profitability_status":
            profitability_status
    }


# ============================================================
# 7. COMPLETE PIPELINE
# ============================================================

def run_pipeline(
    district,
    crop,
    season,
    year,
    area
):

    # --------------------------------------------------------
    # Validate input
    # --------------------------------------------------------

    district = validate_text(
        district,
        "District"
    )

    crop = validate_text(
        crop,
        "Crop"
    )

    season = validate_text(
        season,
        "Season"
    )

    year = validate_number(
        year,
        "Year"
    )

    area = validate_number(
        area,
        "Area",
        minimum=0.01
    )

    # --------------------------------------------------------
    # Load model
    # --------------------------------------------------------

    model = load_model()

    # --------------------------------------------------------
    # Predict yield
    # --------------------------------------------------------

    print(
        "\nGenerating yield prediction..."
    )

    predicted_yield = predict_yield(
        model=model,
        district=district,
        crop=crop,
        season=season,
        year=year,
        area=area
    )

    # --------------------------------------------------------
    # IMPORTANT
    #
    # The prediction is used directly as
    # tonnes/hectare.
    #
    # No /1000 conversion.
    # --------------------------------------------------------

    print(
        "Calculating ROI..."
    )

    roi = calculate_roi(
        crop=crop,
        predicted_yield_tonnes_per_ha=(
            predicted_yield
        ),
        area_hectares=area
    )

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    result = {

        "project":
            "YieldROI",

        "input": {

            "district":
                district,

            "crop":
                crop,

            "season":
                season,

            "year":
                int(year)
                if year.is_integer()
                else year,

            "area_hectares":
                round(
                    area,
                    4
                )
        },

        "yield_prediction": {

            "predicted_yield_tonnes_per_ha":
                roi[
                    "predicted_yield_tonnes_per_ha"
                ],

            "predicted_production_tonnes":
                roi[
                    "predicted_production_tonnes"
                ]
        },

        "economic_analysis":
            roi,

        "calculation_basis":
            (
                "Benchmark/scenario ROI using "
                "the YieldROI ML yield prediction, "
                "official cultivation-cost benchmark "
                "and reference crop price."
            ),

        "model_file":
            str(
                MODEL_FILE
            )
    }

    return result


# ============================================================
# 8. DISPLAY RESULT
# ============================================================

def display_result(result):

    print("\n")

    print(
        "=" * 70
    )

    print(
        "              YIELDROI - PREDICTION + ROI"
    )

    print(
        "=" * 70
    )

    input_data = result[
        "input"
    ]

    prediction = result[
        "yield_prediction"
    ]

    economics = result[
        "economic_analysis"
    ]

    # --------------------------------------------------------
    # Input
    # --------------------------------------------------------

    print("\nINPUT")

    print(
        f"District            : "
        f"{input_data['district']}"
    )

    print(
        f"Crop                : "
        f"{input_data['crop']}"
    )

    print(
        f"Season              : "
        f"{input_data['season']}"
    )

    print(
        f"Year                : "
        f"{input_data['year']}"
    )

    print(
        f"Area                : "
        f"{input_data['area_hectares']:.2f} ha"
    )

    # --------------------------------------------------------
    # Yield
    # --------------------------------------------------------

    print(
        "\n" + "-" * 70
    )

    print(
        "ML YIELD PREDICTION"
    )

    print(
        "-" * 70
    )

    print(
        f"\nPredicted Yield     : "
        f"{prediction['predicted_yield_tonnes_per_ha']:,.2f} "
        f"tonnes/ha"
    )

    print(
        f"Total Production    : "
        f"{prediction['predicted_production_tonnes']:,.2f} "
        f"tonnes"
    )

    # --------------------------------------------------------
    # ROI
    # --------------------------------------------------------

    print(
        "\n" + "-" * 70
    )

    print(
        "ROI / ECONOMIC ANALYSIS"
    )

    print(
        "-" * 70
    )

    print(
        f"\nCost / hectare      : "
        f"₹{economics['cost_per_hectare']:,.2f}"
    )

    print(
        f"Total Cost          : "
        f"₹{economics['total_cost']:,.2f}"
    )

    print(
        f"Reference Price     : "
        f"₹{economics['price_per_tonne']:,.2f}/tonne"
    )

    print(
        f"Price Type          : "
        f"{economics['price_type']}"
    )

    print(
        f"\nEstimated Revenue   : "
        f"₹{economics['revenue']:,.2f}"
    )

    print(
        f"Estimated Profit    : "
        f"₹{economics['profit']:,.2f}"
    )

    print(
        f"ROI                 : "
        f"{economics['roi_percentage']:.2f}%"
    )

    print(
        f"Status              : "
        f"{economics['profitability_status']}"
    )

    # --------------------------------------------------------
    # Note
    # --------------------------------------------------------

    print(
        "\n" + "-" * 70
    )

    print(
        "NOTE: ROI is a benchmark/scenario estimate."
    )

    print(
        "Actual farm economics may vary with "
        "farm-specific costs and selling prices."
    )

    print(
        "=" * 70
    )


# ============================================================
# 9. SAVE RESULT
# ============================================================

def save_result(result):

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            result,
            file,
            indent=4
        )

    return OUTPUT_FILE


# ============================================================
# 10. COMMAND-LINE INTERFACE
# ============================================================

def main():

    print(
        "\nYieldROI - Integrated Yield + ROI"
    )

    print(
        "------------------------------------"
    )

    try:

        district = input(
            "\nEnter district: "
        ).strip()

        crop = input(
            "Enter crop: "
        ).strip()

        season = input(
            "Enter season: "
        ).strip()

        year = input(
            "Enter year: "
        ).strip()

        area = input(
            "Enter area (hectares): "
        ).strip()

        # ----------------------------------------------------
        # Run
        # ----------------------------------------------------

        result = run_pipeline(
            district=district,
            crop=crop,
            season=season,
            year=year,
            area=area
        )

        # ----------------------------------------------------
        # Display
        # ----------------------------------------------------

        display_result(
            result
        )

        # ----------------------------------------------------
        # Save
        # ----------------------------------------------------

        output_path = save_result(
            result
        )

        print(
            "\nIntegrated result saved to:"
        )

        print(
            output_path
        )

    except Exception as error:

        print(
            "\nERROR"
        )

        print(
            "-" * 70
        )

        print(
            error
        )

        print(
            "-" * 70
        )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()