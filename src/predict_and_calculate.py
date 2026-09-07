"""
YieldROI - Integrated Prediction + Benchmark + ROI Pipeline

Pipeline:

    Input
      ↓
    ML Yield Prediction
      ↓
    Official 2024-25 Benchmark Comparison
      ↓
    ROI Calculation
      ↓
    Final Result

Important:
    - Model predicts tonnes/ha.
    - Official benchmark is independent validation data.
    - ROI is a benchmark/scenario estimate, not actual farmer profit.
"""

from pathlib import Path
import json
import joblib
import pandas as pd


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

MODEL_FILE = (
    ROOT / "models" / "best_yield_model.joblib"
)

RESULT_FILE = (
    ROOT / "results" / "integrated_prediction_roi.json"
)


# ============================================================
# IMPORT BENCHMARK COMPARATOR
# ============================================================

from benchmark_comparator import compare_prediction


# ============================================================
# MODEL FEATURES
# ============================================================

FEATURES = [
    "district",
    "crop",
    "season",
    "year",
    "area",
]


# ============================================================
# ROI DATA
# ============================================================

# Cost of cultivation:
# ₹ / hectare

COST_PER_HECTARE = {

    "rice": 93687,

    "sorghum": 53621,

    "maize": 95530,

    "black gram": 52775,
    "blackgram": 52775,

    "groundnut": 98650,

    "gingelly": 55099,
    "sesamum": 55099,

    "cotton": 127589,
    "cotton lint": 127589,

    "sugarcane": 277275,
}


# Reference prices:
# ₹ / tonne

REFERENCE_PRICE = {

    "rice": 24410,

    "sorghum": 40230,

    "maize": 24100,

    "black gram": 82000,
    "blackgram": 82000,

    "groundnut": 75170,

    "gingelly": 103460,
    "sesamum": 103460,

    "cotton": 82670,
    "cotton lint": 82670,

    "sugarcane": 3650,
}


PRICE_TYPE = {

    "rice": "MSP - Paddy Common",

    "sorghum": "MSP - Sorghum Hybrid",

    "maize": "MSP - Maize",

    "black gram": "MSP - Blackgram",
    "blackgram": "MSP - Blackgram",

    "groundnut": "MSP - Groundnut",

    "gingelly": "MSP - Sesamum",
    "sesamum": "MSP - Sesamum",

    "cotton": "MSP - Cotton Medium Staple",
    "cotton lint": "MSP - Cotton Medium Staple",

    "sugarcane": "Published reference price",
}


# ============================================================
# MODEL
# ============================================================

def load_model():

    if not MODEL_FILE.exists():

        raise FileNotFoundError(
            f"Model not found:\n{MODEL_FILE}"
        )

    return joblib.load(
        MODEL_FILE
    )


# ============================================================
# VALIDATION
# ============================================================

def validate_input(
    district,
    crop,
    season,
    year,
    area
):

    if not str(district).strip():

        raise ValueError(
            "District cannot be empty."
        )

    if not str(crop).strip():

        raise ValueError(
            "Crop cannot be empty."
        )

    if not str(season).strip():

        raise ValueError(
            "Season cannot be empty."
        )

    try:

        year = int(year)

    except:

        raise ValueError(
            "Year must be an integer."
        )

    if year < 1997:

        raise ValueError(
            "Year must be 1997 or later."
        )

    try:

        area = float(area)

    except:

        raise ValueError(
            "Area must be numeric."
        )

    if area <= 0:

        raise ValueError(
            "Area must be greater than zero."
        )


# ============================================================
# PREDICT YIELD
# ============================================================

def predict_yield(
    model,
    district,
    crop,
    season,
    year,
    area
):

    input_data = pd.DataFrame(
        [{
            "district": district,
            "crop": crop,
            "season": season,
            "year": int(year),
            "area": float(area),
        }]
    )

    prediction = model.predict(
        input_data[FEATURES]
    )[0]

    # Model target is tonnes/ha.
    prediction = float(
        prediction
    )

    # Safety check.
    if prediction < 0:

        prediction = 0.0

    return prediction


# ============================================================
# ROI
# ============================================================

def calculate_roi(
    crop,
    predicted_yield,
    area
):

    crop_key = (
        str(crop)
        .strip()
        .lower()
    )

    if crop_key not in COST_PER_HECTARE:

        return {
            "status": "ROI unavailable",
            "reason": (
                "Cost/reference-price data is not "
                "available for this crop."
            ),
        }

    cost_per_ha = float(
        COST_PER_HECTARE[crop_key]
    )

    price_per_tonne = float(
        REFERENCE_PRICE[crop_key]
    )

    area = float(area)

    predicted_yield = float(
        predicted_yield
    )

    total_cost = (
        cost_per_ha
        *
        area
    )

    total_production = (
        predicted_yield
        *
        area
    )

    revenue = (
        total_production
        *
        price_per_tonne
    )

    profit = (
        revenue
        -
        total_cost
    )

    if total_cost > 0:

        roi_percent = (
            profit
            /
            total_cost
        ) * 100

    else:

        roi_percent = 0.0

    if profit > 0:

        status = "Profitable"

    elif profit < 0:

        status = "Loss"

    else:

        status = "Break-even"

    return {

        "status": status,

        "cost_per_hectare": cost_per_ha,

        "total_cost": total_cost,

        "reference_price_per_tonne": (
            price_per_tonne
        ),

        "price_type": PRICE_TYPE[
            crop_key
        ],

        "total_production_tonnes": (
            total_production
        ),

        "revenue": revenue,

        "profit": profit,

        "roi_percent": roi_percent,

        "roi_note": (
            "Benchmark/scenario estimate. "
            "Actual farmer costs, prices and returns "
            "may differ."
        ),
    }


# ============================================================
# COMPLETE PIPELINE
# ============================================================

def run_pipeline(
    district,
    crop,
    season,
    year,
    area
):

    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    validate_input(
        district,
        crop,
        season,
        year,
        area
    )

    # --------------------------------------------------------
    # Load model
    # --------------------------------------------------------

    model = load_model()

    # --------------------------------------------------------
    # ML prediction
    # --------------------------------------------------------

    predicted_yield = predict_yield(
        model=model,
        district=district,
        crop=crop,
        season=season,
        year=year,
        area=area
    )

    # --------------------------------------------------------
    # Production
    # --------------------------------------------------------

    total_production = (
        predicted_yield
        *
        float(area)
    )

    # --------------------------------------------------------
    # Official benchmark
    # --------------------------------------------------------

    benchmark = compare_prediction(
        district=district,
        crop=crop,
        season=season,
        predicted_yield=predicted_yield
    )

    # --------------------------------------------------------
    # ROI
    # --------------------------------------------------------

    roi = calculate_roi(
        crop=crop,
        predicted_yield=predicted_yield,
        area=area
    )

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    result = {

        "input": {

            "district": district,

            "crop": crop,

            "season": season,

            "year": int(year),

            "area_hectares": float(area),
        },

        "prediction": {

            "predicted_yield_tonnes_per_ha": (
                predicted_yield
            ),

            "total_production_tonnes": (
                total_production
            ),
        },

        "official_benchmark": benchmark,

        "roi": roi,

        "notes": [

            "Model prediction is expressed "
            "in tonnes per hectare.",

            "Official benchmark is an independent "
            "2024-25 Tamil Nadu reference.",

            "ROI is a benchmark/scenario estimate "
            "and should not be interpreted as "
            "actual farmer profit.",

        ],
    }

    return result


# ============================================================
# DISPLAY
# ============================================================

def display_result(result):

    data = result["input"]

    prediction = result["prediction"]

    benchmark = result[
        "official_benchmark"
    ]

    roi = result["roi"]

    print()
    print("=" * 75)
    print("                         YieldROI")
    print("       Intelligent Crop Yield + Benchmark + ROI")
    print("=" * 75)

    print()

    print("INPUT")
    print("-" * 75)

    print(
        f"District        : "
        f"{data['district']}"
    )

    print(
        f"Crop            : "
        f"{data['crop']}"
    )

    print(
        f"Season          : "
        f"{data['season']}"
    )

    print(
        f"Year            : "
        f"{data['year']}"
    )

    print(
        f"Area            : "
        f"{data['area_hectares']:.2f} ha"
    )

    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    print()
    print("ML PREDICTION")
    print("-" * 75)

    print(
        f"Predicted Yield : "
        f"{prediction['predicted_yield_tonnes_per_ha']:.3f} "
        f"tonnes/ha"
    )

    print(
        f"Total Production: "
        f"{prediction['total_production_tonnes']:.3f} "
        f"tonnes"
    )

    # --------------------------------------------------------
    # Benchmark
    # --------------------------------------------------------

    print()
    print("OFFICIAL 2024-25 BENCHMARK")
    print("-" * 75)

    status = benchmark.get(
        "status"
    )

    print(
        f"Status          : "
        f"{status}"
    )

    if (
        benchmark.get(
            "official_yield_tonnes_per_ha"
        )
        is not None
    ):

        print(
            f"Official Yield  : "
            f"{benchmark['official_yield_tonnes_per_ha']:.3f} "
            f"tonnes/ha"
        )

        print(
            f"Difference      : "
            f"{benchmark['difference_tonnes_per_ha']:.3f} "
            f"tonnes/ha"
        )

        if benchmark.get(
            "difference_percent"
        ) is not None:

            print(
                f"Difference %    : "
                f"{benchmark['difference_percent']:.2f}%"
            )

        print(
            f"Performance     : "
            f"{benchmark['performance']}"
        )

        print(
            f"Source page     : "
            f"{benchmark['source_page']}"
        )

    else:

        print(
            "Official Yield  : "
            "Not directly comparable"
        )

        if benchmark.get(
            "official_unit"
        ):

            print(
                f"Official Unit   : "
                f"{benchmark['official_unit']}"
            )

    # --------------------------------------------------------
    # ROI
    # --------------------------------------------------------

    print()
    print("ROI / ECONOMIC SCENARIO")
    print("-" * 75)

    if roi.get("status") == "ROI unavailable":

        print(
            "ROI             : "
            "Unavailable"
        )

        print(
            f"Reason          : "
            f"{roi['reason']}"
        )

    else:

        print(
            f"Cost / ha       : ₹"
            f"{roi['cost_per_hectare']:,.2f}"
        )

        print(
            f"Total Cost      : ₹"
            f"{roi['total_cost']:,.2f}"
        )

        print(
            f"Reference Price : ₹"
            f"{roi['reference_price_per_tonne']:,.2f}"
            f" / tonne"
        )

        print(
            f"Price Type      : "
            f"{roi['price_type']}"
        )

        print(
            f"Revenue         : ₹"
            f"{roi['revenue']:,.2f}"
        )

        print(
            f"Profit          : ₹"
            f"{roi['profit']:,.2f}"
        )

        print(
            f"ROI             : "
            f"{roi['roi_percent']:.2f}%"
        )

        print(
            f"Status          : "
            f"{roi['status']}"
        )

    print()

    print(
        "NOTE: Benchmark and ROI values are "
        "reference/scenario estimates."
    )

    print()

    print("=" * 75)


# ============================================================
# SAVE
# ============================================================

def save_result(result):

    RESULT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        RESULT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            result,
            f,
            indent=4
        )

    print()
    print(
        f"Result saved to:"
    )

    print(
        RESULT_FILE
    )


# ============================================================
# MAIN TEST
# ============================================================

def main():

    print()
    print("=" * 75)
    print("YieldROI - Integrated Pipeline Test")
    print("=" * 75)

    print()
    print(
        "Test case:"
    )

    print(
        "Thanjavur / Rice / Kharif / 2022 / 100 ha"
    )

    try:

        result = run_pipeline(

            district="Thanjavur",

            crop="Rice",

            season="Kharif",

            year=2022,

            area=100,

        )

        display_result(
            result
        )

        save_result(
            result
        )

    except Exception as e:

        print()
        print(
            "ERROR:"
        )

        print(
            str(e)
        )


if __name__ == "__main__":
    main()