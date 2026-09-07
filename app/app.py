from pathlib import Path
import sys
import json

import joblib
import pandas as pd
from flask import Flask, render_template, request, jsonify


# ============================================================
# PROJECT PATHS
# ============================================================

# app.py is inside:
# YieldROI/app/app.py
#
# PROJECT_ROOT therefore becomes:
# YieldROI/

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"
MODEL_DIR = PROJECT_ROOT / "models"
FERTILIZER_DIR = PROJECT_ROOT / "fertilizer"
SRC_DIR = PROJECT_ROOT / "src"
TEMPLATES_DIR = PROJECT_ROOT / "templates"
STATIC_DIR = PROJECT_ROOT / "static"


# Allow imports from src/
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


# ============================================================
# FLASK APP
# ============================================================

app = Flask(
    __name__,
    template_folder=str(TEMPLATES_DIR),
    static_folder=str(STATIC_DIR),
)


# ============================================================
# FILE PATHS
# ============================================================

YIELD_DATA_PATH = DATA_DIR / "tamil_nadu_yield_cleaned.csv"
BENCHMARK_PATH = DATA_DIR / "official_yield_benchmarks.csv"

MODEL_PATH = MODEL_DIR / "best_yield_model.joblib"
METRICS_PATH = MODEL_DIR / "model_metrics.json"

SOIL_PROFILE_PATH = FERTILIZER_DIR / "final_soil_profiles.csv"
FERTILIZER_KB_PATH = FERTILIZER_DIR / "fertilizer_knowledge_base.csv"


# ============================================================
# LOAD DATA
# ============================================================

def load_yield_data():
    if not YIELD_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Yield dataset not found:\n{YIELD_DATA_PATH}"
        )

    df = pd.read_csv(YIELD_DATA_PATH)

    # Make sure year exists in a usable form
    if "year" not in df.columns:
        if "fiscal_year" in df.columns:
            df["year"] = (
                df["fiscal_year"]
                .astype(str)
                .str[:4]
                .astype(int)
            )
        else:
            raise ValueError(
                "Yield dataset does not contain 'year' or 'fiscal_year'."
            )

    return df


def load_benchmark_data():
    if not BENCHMARK_PATH.exists():
        print(f"WARNING: Benchmark file not found: {BENCHMARK_PATH}")
        return pd.DataFrame()

    return pd.read_csv(BENCHMARK_PATH)


def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model not found:\n{MODEL_PATH}"
        )

    return joblib.load(MODEL_PATH)


def load_metrics():
    if not METRICS_PATH.exists():
        print(f"WARNING: Model metrics not found: {METRICS_PATH}")
        return {}

    try:
        with open(METRICS_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as exc:
        print(f"WARNING: Could not read model metrics: {exc}")
        return {}


# ============================================================
# INITIAL LOAD
# ============================================================

YIELD_DF = load_yield_data()
BENCHMARK_DF = load_benchmark_data()
MODEL = load_model()
MODEL_METRICS = load_metrics()


# ============================================================
# NORMALIZATION HELPERS
# ============================================================

def normalize_text(value):
    if value is None:
        return ""

    return (
        str(value)
        .strip()
        .lower()
        .replace("_", " ")
        .replace("-", " ")
    )


def find_column(df, possible_names):
    normalized = {
        normalize_text(column): column
        for column in df.columns
    }

    for name in possible_names:
        key = normalize_text(name)

        if key in normalized:
            return normalized[key]

    return None


# ============================================================
# CROP / DISTRICT NAME MAPPINGS
# ============================================================

CROP_MAP = {
    "rice": "paddy",
    "paddy": "paddy",

    "sugarcane": "sugar cane",
    "sugar cane": "sugar cane",

    "cotton lint": "cotton",
    "cotton": "cotton",

    "sesamum": "sesamum",
    "gingelly": "sesamum",

    "blackgram": "black gram",
    "black gram": "black gram",

    "greengram": "green gram",
    "green gram": "green gram",

    "groundnut": "groundnut",

    "maize": "maize",

    "ragi": "ragi",

    "sorghum": "jowar cholam",
    "jowar": "jowar cholam",

    "bajra": "bajra cumbu",
    "cumbu": "bajra cumbu",
}


DISTRICT_MAP = {
    "tiruchirappalli": "trichy",
    "trichy": "trichy",

    "thanjavur": "thanjavur",

    "ariyalur": "ariyalur",

    "coimbatore": "coimbatore",

    "tiruppur": "tiruppur",

    "kallakurichi": "kallakurichi",

    "mayiladuthurai": "mayiladuthurai",

    "chengalpattu": "chengalpattu",

    "villupuram": "viluppuram",
}


# ============================================================
# BENCHMARK COMPARISON
# ============================================================

def compare_with_benchmark(
    district,
    crop,
    season,
    predicted_yield
):
    """
    Compare predicted yield with the official 2024-25
    Tamil Nadu district-wise benchmark.

    Historical model output:
        tonnes/ha

    Benchmark:
        Usually kg/ha
        Sugar cane -> tonnes/ha
        Coconut -> nuts/ha
    """

    if BENCHMARK_DF.empty:
        return {
            "available": False,
            "message": "Official benchmark data is not available."
        }

    district_col = find_column(
        BENCHMARK_DF,
        ["district", "district_name"]
    )

    crop_col = find_column(
        BENCHMARK_DF,
        ["crop", "crop_name"]
    )

    season_col = find_column(
        BENCHMARK_DF,
        ["season", "season_name"]
    )

    yield_col = find_column(
        BENCHMARK_DF,
        ["yield", "yield_rate", "average_yield", "value"]
    )

    unit_col = find_column(
        BENCHMARK_DF,
        ["unit", "yield_unit"]
    )

    if not district_col or not crop_col or not yield_col:
        return {
            "available": False,
            "message": "Benchmark columns could not be identified."
        }

    target_district = normalize_text(district)
    target_crop = normalize_text(crop)
    target_season = normalize_text(season)

    mapped_district = DISTRICT_MAP.get(
        target_district,
        target_district
    )

    mapped_crop = CROP_MAP.get(
        target_crop,
        target_crop
    )

    df = BENCHMARK_DF.copy()

    df["_district"] = df[district_col].apply(normalize_text)
    df["_crop"] = df[crop_col].apply(normalize_text)

    # District match
    district_matches = df[
        df["_district"] == mapped_district
    ]

    if district_matches.empty:
        # Try original district name
        district_matches = df[
            df["_district"] == target_district
        ]

    if district_matches.empty:
        return {
            "available": False,
            "message": f"No official benchmark found for {district}."
        }

    # Crop match
    crop_matches = district_matches[
        district_matches["_crop"] == mapped_crop
    ]

    if crop_matches.empty:
        crop_matches = district_matches[
            district_matches["_crop"] == target_crop
        ]

    if crop_matches.empty:
        return {
            "available": False,
            "message": (
                f"No official benchmark found for "
                f"{district} / {crop}."
            )
        }

    selected = pd.DataFrame()

    # Try exact season first
    if season_col:
        crop_matches = crop_matches.copy()
        crop_matches["_season"] = (
            crop_matches[season_col]
            .apply(normalize_text)
        )

        selected = crop_matches[
            crop_matches["_season"] == target_season
        ]

    # If exact season isn't available, use Combined
    if selected.empty and season_col:
        selected = crop_matches[
            crop_matches["_season"].isin(
                ["combined", "overall", "all seasons"]
            )
        ]

    # Last fallback
    if selected.empty:
        selected = crop_matches

    if selected.empty:
        return {
            "available": False,
            "message": "No suitable benchmark value found."
        }

    row = selected.iloc[0]

    try:
        benchmark_value = float(row[yield_col])
    except (ValueError, TypeError):
        return {
            "available": False,
            "message": "Benchmark yield is not numeric."
        }

    unit = ""
    if unit_col:
        unit = str(row[unit_col])

    normalized_unit = normalize_text(unit)

    # --------------------------------------------------------
    # Coconut cannot be compared with tonnes/ha yield
    # --------------------------------------------------------

    if "nut" in normalized_unit:
        return {
            "available": False,
            "message": (
                "Benchmark uses nuts/ha, while the model "
                "predicts tonnes/ha. Direct comparison is not valid."
            ),
            "unit": unit
        }

    # --------------------------------------------------------
    # Convert kg/ha -> tonnes/ha
    # --------------------------------------------------------

    if "kg" in normalized_unit:
        benchmark_tonnes = benchmark_value / 1000.0

    elif "tonne" in normalized_unit:
        benchmark_tonnes = benchmark_value

    else:
        # Fallback for older benchmark rows
        if benchmark_value > 100:
            benchmark_tonnes = benchmark_value / 1000.0
        else:
            benchmark_tonnes = benchmark_value

    difference = predicted_yield - benchmark_tonnes

    if benchmark_tonnes != 0:
        percentage_difference = (
            difference / benchmark_tonnes
        ) * 100
    else:
        percentage_difference = 0

    if percentage_difference >= 5:
        status = "Above benchmark"
    elif percentage_difference <= -5:
        status = "Below benchmark"
    else:
        status = "Near benchmark"

    return {
        "available": True,
        "district": district,
        "crop": crop,
        "season": season,
        "benchmark_yield": round(benchmark_tonnes, 3),
        "benchmark_original_value": benchmark_value,
        "benchmark_unit": unit,
        "predicted_yield": round(predicted_yield, 3),
        "difference": round(difference, 3),
        "percentage_difference": round(
            percentage_difference,
            2
        ),
        "status": status,
        "year": "2024-25"
    }


# ============================================================
# ROI CALCULATION
# ============================================================

COST_PER_HECTARE = {
    "rice": 93687,
    "paddy": 93687,

    "sorghum": 53621,
    "jowar": 53621,

    "maize": 95530,

    "black gram": 52775,
    "blackgram": 52775,

    "groundnut": 98650,

    "gingelly": 55099,
    "sesamum": 55099,

    "cotton": 127589,
    "cotton lint": 127589,

    "sugarcane": 277275,
    "sugar cane": 277275,
}


REFERENCE_PRICE_PER_TONNE = {
    "rice": 24410,
    "paddy": 24410,

    "sorghum": 40230,
    "jowar": 40230,

    "maize": 24100,

    "black gram": 82000,
    "blackgram": 82000,

    "groundnut": 75170,

    "gingelly": 103460,
    "sesamum": 103460,

    "cotton": 82670,
    "cotton lint": 82670,

    "sugarcane": 3650,
    "sugar cane": 3650,
}


PRICE_SOURCE_NAME = {
    "rice": "MSP Paddy Common",
    "paddy": "MSP Paddy Common",

    "sorghum": "MSP Sorghum Hybrid",
    "jowar": "MSP Sorghum Hybrid",

    "maize": "MSP Maize",

    "black gram": "MSP Blackgram",
    "blackgram": "MSP Blackgram",

    "groundnut": "MSP Groundnut",

    "gingelly": "MSP Sesamum",
    "sesamum": "MSP Sesamum",

    "cotton": "MSP Cotton Medium Staple",
    "cotton lint": "MSP Cotton Medium Staple",

    "sugarcane": "Published reference price",
    "sugar cane": "Published reference price",
}


def calculate_roi(crop, predicted_yield, area):
    crop_key = normalize_text(crop)

    cost_per_hectare = COST_PER_HECTARE.get(crop_key)
    price_per_tonne = REFERENCE_PRICE_PER_TONNE.get(crop_key)

    if cost_per_hectare is None:
        return {
            "available": False,
            "message": (
                f"ROI cost data is not currently available for "
                f"{crop}."
            )
        }

    if price_per_tonne is None:
        return {
            "available": False,
            "message": (
                f"Reference price is not currently available for "
                f"{crop}."
            )
        }

    total_cost = cost_per_hectare * area

    total_production = predicted_yield * area

    revenue = total_production * 1000 * price_per_tonne

    profit = revenue - total_cost

    if total_cost != 0:
        roi_percentage = (
            profit / total_cost
        ) * 100
    else:
        roi_percentage = 0

    status = "Profitable" if profit >= 0 else "Loss"

    return {
        "available": True,
        "crop": crop,
        "predicted_yield": round(predicted_yield, 3),
        "area": round(area, 3),

        "cost_per_hectare": round(
            cost_per_hectare,
            2
        ),

        "total_cost": round(
            total_cost,
            2
        ),

        "price_per_tonne": round(
            price_per_tonne,
            2
        ),

        "price_source": PRICE_SOURCE_NAME.get(
            crop_key,
            "Published reference price"
        ),

        "total_production_tonnes": round(
            total_production,
            3
        ),

        "revenue": round(
            revenue,
            2
        ),

        "profit": round(
            profit,
            2
        ),

        "roi_percentage": round(
            roi_percentage,
            2
        ),

        "status": status
    }


# ============================================================
# FERTILIZER RECOMMENDATION
# ============================================================

def get_fertilizer_recommendation(
    district,
    block,
    village,
    crop,
    crop_type,
    year
):
    """
    Safely connect the Flask application with the existing
    fertilizer recommender.

    The recommender itself remains in src/.
    """

    try:
        import fertilizer_recommender

    except Exception as exc:
        return {
            "available": False,
            "message": (
                "Fertilizer recommendation module could not "
                f"be loaded: {exc}"
            )
        }

    possible_functions = [
        "recommend_fertilizer",
        "get_recommendation",
        "recommend"
    ]

    function = None

    for function_name in possible_functions:
        if hasattr(
            fertilizer_recommender,
            function_name
        ):
            function = getattr(
                fertilizer_recommender,
                function_name
            )
            break

    if function is None:
        return {
            "available": False,
            "message": (
                "Fertilizer recommender function is not "
                "exposed by fertilizer_recommender.py yet."
            )
        }

    try:
        # Try keyword arguments first
        result = function(
            district=district,
            block=block,
            village=village,
            crop=crop,
            crop_type=crop_type,
            year=year
        )

        if result is None:
            return {
                "available": False,
                "message": "No fertilizer recommendation returned."
            }

        # Normalize the result into JSON-safe data
        if isinstance(result, dict):
            result = dict(result)

            if "available" not in result:
                result["available"] = True

            return result

        return {
            "available": True,
            "recommendation": str(result)
        }

    except TypeError:
        # Some existing implementations may have a different
        # function signature. Try positional arguments.

        try:
            result = function(
                district,
                block,
                village,
                crop,
                crop_type,
                year
            )

            if isinstance(result, dict):
                result = dict(result)

                if "available" not in result:
                    result["available"] = True

                return result

            return {
                "available": True,
                "recommendation": str(result)
            }

        except Exception as exc:
            return {
                "available": False,
                "message": (
                    "Fertilizer recommendation failed: "
                    f"{exc}"
                )
            }

    except Exception as exc:
        return {
            "available": False,
            "message": (
                "Fertilizer recommendation failed: "
                f"{exc}"
            )
        }


# ============================================================
# INPUT VALIDATION
# ============================================================

def validate_prediction_input(data):
    required_fields = [
        "district",
        "crop",
        "season",
        "year",
        "area"
    ]

    missing = []

    for field in required_fields:
        value = data.get(field)

        if value is None or str(value).strip() == "":
            missing.append(field)

    if missing:
        return False, (
            "Missing required fields: "
            + ", ".join(missing)
        )

    try:
        year = int(data["year"])
    except (ValueError, TypeError):
        return False, "Year must be a valid integer."

    if year < 1997 or year > 2100:
        return False, "Please enter a valid year."

    try:
        area = float(data["area"])
    except (ValueError, TypeError):
        return False, "Area must be a valid number."

    if area <= 0:
        return False, "Area must be greater than zero."

    return True, ""


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def index():

    districts = sorted(
        YIELD_DF["district"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    crops = sorted(
        YIELD_DF["crop"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    seasons = sorted(
        YIELD_DF["season"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    return render_template(
        "index.html",
        districts=districts,
        crops=crops,
        seasons=seasons
    )


# ============================================================
# PREDICTION
# ============================================================

@app.route("/predict", methods=["POST"])
def predict():

    data = request.get_json(silent=True)

    if data is None:
        data = request.form.to_dict()

    valid, error_message = validate_prediction_input(data)

    if not valid:
        return jsonify({
            "success": False,
            "error": error_message
        }), 400

    district = str(data["district"]).strip()
    crop = str(data["crop"]).strip()
    season = str(data["season"]).strip()

    year = int(data["year"])
    area = float(data["area"])

    # --------------------------------------------------------
    # Model prediction
    # --------------------------------------------------------

    prediction_input = pd.DataFrame([{
        "district": district,
        "crop": crop,
        "season": season,
        "year": year,
        "area": area
    }])

    try:
        predicted_yield = float(
            MODEL.predict(prediction_input)[0]
        )

    except Exception as exc:
        return jsonify({
            "success": False,
            "error": (
                "Model prediction failed: "
                f"{exc}"
            )
        }), 500

    # Model target is tonnes/ha.
    predicted_yield = max(
        predicted_yield,
        0
    )

    # --------------------------------------------------------
    # Benchmark
    # --------------------------------------------------------

    benchmark = compare_with_benchmark(
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
    # Fertilizer
    # --------------------------------------------------------

    block = str(
        data.get("block", "")
    ).strip()

    village = str(
        data.get("village", "")
    ).strip()

    crop_type = str(
        data.get("crop_type", "")
    ).strip()

    fertilizer = get_fertilizer_recommendation(
        district=district,
        block=block,
        village=village,
        crop=crop,
        crop_type=crop_type,
        year=year
    )

    # --------------------------------------------------------
    # Model metrics
    # IMPORTANT:
    # Accuracy remains TERMINAL ONLY.
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("YIELDROI PREDICTION")
    print("=" * 60)

    print(f"District        : {district}")
    print(f"Crop            : {crop}")
    print(f"Season          : {season}")
    print(f"Year            : {year}")
    print(f"Area            : {area} ha")

    print(
        f"Predicted Yield : "
        f"{predicted_yield:.3f} tonnes/ha"
    )

    if MODEL_METRICS:
        print("\nMODEL PERFORMANCE")

        # Try several possible metric structures
        test_metrics = MODEL_METRICS.get(
            "test",
            MODEL_METRICS.get(
                "Test",
                MODEL_METRICS
            )
        )

        if isinstance(test_metrics, dict):

            r2 = test_metrics.get(
                "r2",
                test_metrics.get(
                    "R2",
                    test_metrics.get("test_r2")
                )
            )

            mae = test_metrics.get(
                "mae",
                test_metrics.get(
                    "MAE",
                    test_metrics.get("test_mae")
                )
            )

            rmse = test_metrics.get(
                "rmse",
                test_metrics.get(
                    "RMSE",
                    test_metrics.get("test_rmse")
                )
            )

            if r2 is not None:
                try:
                    r2_value = float(r2)

                    print(
                        f"Test R²        : "
                        f"{r2_value:.4f}"
                    )

                    print(
                        f"Variance "
                        f"explained      : "
                        f"{r2_value * 100:.2f}%"
                    )

                except (ValueError, TypeError):
                    pass

            if mae is not None:
                print(f"Test MAE        : {mae}")

            if rmse is not None:
                print(f"Test RMSE       : {rmse}")

            print(
                "Note             : "
                "R² is a regression metric, "
                "not classification accuracy."
            )

    print("=" * 60 + "\n")

    # --------------------------------------------------------
    # Final response
    # --------------------------------------------------------

    result = {
        "success": True,

        "input": {
            "district": district,
            "crop": crop,
            "season": season,
            "year": year,
            "area": area,
            "block": block,
            "village": village,
            "crop_type": crop_type
        },

        "prediction": {
            "yield_tonnes_per_hectare": round(
                predicted_yield,
                3
            ),
            "total_production_tonnes": round(
                predicted_yield * area,
                3
            )
        },

        "benchmark": benchmark,

        "roi": roi,

        "fertilizer": fertilizer
    }

    return jsonify(result)


# ============================================================
# REPORT PAGE
# ============================================================

@app.route("/report")
def report():
    """
    The report page receives prediction data through
    the query string from result.html.
    """

    return render_template("report.html")


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health")
def health():

    return jsonify({
        "status": "ok",
        "project": "YieldROI",
        "yield_data": YIELD_DATA_PATH.exists(),
        "benchmark_data": BENCHMARK_PATH.exists(),
        "model": MODEL_PATH.exists(),
        "metrics": METRICS_PATH.exists(),
        "soil_profiles": SOIL_PROFILE_PATH.exists(),
        "fertilizer_kb": FERTILIZER_KB_PATH.exists()
    })


# ============================================================
# APPLICATION START
# ============================================================

if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("YieldROI")
    print("=" * 60)

    print(f"Project root : {PROJECT_ROOT}")
    print(f"Yield data   : {YIELD_DATA_PATH}")
    print(f"Benchmark    : {BENCHMARK_PATH}")
    print(f"Model        : {MODEL_PATH}")
    print(f"Templates    : {TEMPLATES_DIR}")
    print(f"Static       : {STATIC_DIR}")

    print("\nFiles:")
    print(
        f"  Yield data : "
        f"{'FOUND' if YIELD_DATA_PATH.exists() else 'MISSING'}"
    )
    print(
        f"  Benchmark  : "
        f"{'FOUND' if BENCHMARK_PATH.exists() else 'MISSING'}"
    )
    print(
        f"  Model      : "
        f"{'FOUND' if MODEL_PATH.exists() else 'MISSING'}"
    )
    print(
        f"  Templates  : "
        f"{'FOUND' if TEMPLATES_DIR.exists() else 'MISSING'}"
    )
    print(
        f"  Static     : "
        f"{'FOUND' if STATIC_DIR.exists() else 'MISSING'}"
    )

    print("\nStarting server...")
    print("Open: http://127.0.0.1:5000")
    print("=" * 60 + "\n")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )