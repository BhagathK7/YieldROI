from pathlib import Path
import sys

import joblib
import pandas as pd
from flask import Flask, render_template, request


# =========================================================
# PROJECT PATH
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))


from benchmark_comparator import compare_prediction


# =========================================================
# FLASK
# =========================================================

app = Flask(__name__)


# =========================================================
# PATHS
# =========================================================

MODEL_PATH = PROJECT_ROOT / "models" / "best_yield_model.joblib"

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "tamil_nadu_yield_cleaned.csv"
)


# =========================================================
# LOAD MODEL ONCE
# =========================================================

MODEL = None


def load_model():
    """
    Load the trained model once when the application starts.
    """

    global MODEL

    if MODEL is None:

        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                "Model not found: "
                "models/best_yield_model.joblib"
            )

        MODEL = joblib.load(MODEL_PATH)

    return MODEL


# =========================================================
# LOAD MODEL-SUPPORTED INPUT VALUES
# =========================================================

def load_supported_values():

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            "Cleaned dataset not found: "
            "data/tamil_nadu_yield_cleaned.csv"
        )

    data = pd.read_csv(DATA_PATH)

    required_columns = [
        "district",
        "crop",
        "season",
        "year",
        "area",
    ]

    missing = [
        column
        for column in required_columns
        if column not in data.columns
    ]

    if missing:
        raise ValueError(
            "Required dataset columns are missing: "
            + ", ".join(missing)
        )

    districts = sorted(
        data["district"]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )

    crops = sorted(
        data["crop"]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )

    seasons = sorted(
        data["season"]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )

    years = sorted(
        pd.to_numeric(
            data["year"],
            errors="coerce"
        )
        .dropna()
        .astype(int)
        .unique()
        .tolist()
    )

    return districts, crops, seasons, years


# =========================================================
# UI OPTIONS
# =========================================================

try:

    DISTRICTS, CROPS, SEASONS, YEARS = (
        load_supported_values()
    )

except Exception:

    # Safe fallback only if the dataset cannot be loaded.
    DISTRICTS = [
        "Ariyalur",
        "Chengalpattu",
        "Chennai",
        "Coimbatore",
        "Cuddalore",
        "Dharmapuri",
        "Dindigul",
        "Erode",
        "Kallakurichi",
        "Kancheepuram",
        "Karur",
        "Krishnagiri",
        "Madurai",
        "Mayiladuthurai",
        "Nagapattinam",
        "Namakkal",
        "Perambalur",
        "Pudukkottai",
        "Ramanathapuram",
        "Ranipet",
        "Salem",
        "Sivaganga",
        "Tenkasi",
        "Thanjavur",
        "The Nilgiris",
        "Theni",
        "Thoothukudi",
        "Tiruchirappalli",
        "Tirunelveli",
        "Tirupathur",
        "Tiruppur",
        "Tiruvallur",
        "Tiruvarur",
        "Vellore",
        "Viluppuram",
        "Virudhunagar",
        "Tiruvannamalai",
        "Kanyakumari",
    ]

    CROPS = [
        "Rice",
        "Sorghum",
        "Maize",
        "Black Gram",
        "Groundnut",
        "Gingelly",
        "Cotton",
        "Sugarcane",
        "Ragi",
        "Banana",
        "Coconut",
        "Onion",
        "Potato",
        "Tapioca",
        "Turmeric",
    ]

    SEASONS = [
        "Kharif",
        "Rabi",
        "Summer",
        "Whole Year",
        "Autumn",
        "Winter",
    ]

    YEARS = list(range(1997, 2023))


# =========================================================
# ROI REFERENCE DATA
# =========================================================

COSTS = {
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


PRICES = {
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


# =========================================================
# ROI CALCULATION
# =========================================================

def calculate_roi(crop, predicted_yield, area):

    crop_key = crop.strip().lower()

    if (
        crop_key not in COSTS
        or crop_key not in PRICES
    ):

        return {
            "available": False,
            "message": (
                "ROI reference data is not currently "
                "available for this crop."
            ),
        }

    cost_per_ha = float(COSTS[crop_key])

    price_per_tonne = float(PRICES[crop_key])

    total_cost = cost_per_ha * area

    production_tonnes = predicted_yield * area

    revenue = production_tonnes * price_per_tonne

    profit = revenue - total_cost

    roi = (
        (profit / total_cost) * 100
        if total_cost > 0
        else 0
    )

    return {
        "available": True,
        "cost_per_ha": cost_per_ha,
        "total_cost": total_cost,
        "price_per_tonne": price_per_tonne,
        "production_tonnes": production_tonnes,
        "revenue": revenue,
        "profit": profit,
        "roi": roi,
        "status": (
            "Profitable"
            if profit >= 0
            else "Loss"
        ),
    }


# =========================================================
# MODEL PREDICTION
# =========================================================

def predict_yield(
    district,
    crop,
    season,
    year,
    area,
):

    model = load_model()

    input_data = pd.DataFrame(
        [
            {
                "district": district,
                "crop": crop,
                "season": season,
                "year": year,
                "area": area,
            }
        ]
    )

    prediction = float(
        model.predict(input_data)[0]
    )

    # Yield is already in tonnes/hectare.
    return max(0.0, prediction)


# =========================================================
# COMMON TEMPLATE DATA
# =========================================================

def template_data():

    return {
        "districts": DISTRICTS,
        "crops": CROPS,
        "seasons": SEASONS,
        "years": YEARS,
    }


# =========================================================
# HOME
# =========================================================

@app.route("/")
def index():

    defaults = {
        "district": (
            "Thanjavur"
            if "Thanjavur" in DISTRICTS
            else DISTRICTS[0]
        ),
        "crop": (
            "Rice"
            if "Rice" in CROPS
            else CROPS[0]
        ),
        "season": (
            "Kharif"
            if "Kharif" in SEASONS
            else SEASONS[0]
        ),
        "year": (
            2022
            if 2022 in YEARS
            else YEARS[-1]
        ),
        "area": 100,
    }

    return render_template(
        "index.html",
        **template_data(),
        defaults=defaults,
    )


# =========================================================
# PREDICTION
# =========================================================

@app.route("/predict", methods=["POST"])
def predict():

    try:

        district = request.form.get(
            "district",
            "",
        ).strip()

        crop = request.form.get(
            "crop",
            "",
        ).strip()

        season = request.form.get(
            "season",
            "",
        ).strip()

        year_raw = request.form.get(
            "year",
            "",
        ).strip()

        area_raw = request.form.get(
            "area",
            "",
        ).strip()


        # -------------------------------------------------
        # BASIC VALIDATION
        # -------------------------------------------------

        if not district:
            raise ValueError(
                "Please select a district."
            )

        if not crop:
            raise ValueError(
                "Please select a crop."
            )

        if not season:
            raise ValueError(
                "Please select a season."
            )

        if district not in DISTRICTS:
            raise ValueError(
                "The selected district is not supported "
                "by the trained model."
            )

        if crop not in CROPS:
            raise ValueError(
                "The selected crop is not supported "
                "by the trained model."
            )

        if season not in SEASONS:
            raise ValueError(
                "The selected season is not supported "
                "by the trained model."
            )


        # -------------------------------------------------
        # YEAR
        # -------------------------------------------------

        try:
            year = int(year_raw)
        except (TypeError, ValueError):
            raise ValueError(
                "Please select a valid year."
            )

        if year not in YEARS:
            raise ValueError(
                "Please select a year supported "
                "by the trained model."
            )


        # -------------------------------------------------
        # AREA
        # -------------------------------------------------

        try:
            area = float(area_raw)
        except (TypeError, ValueError):
            raise ValueError(
                "Please enter a valid area."
            )

        if area <= 0:
            raise ValueError(
                "Area must be greater than 0."
            )

        if area > 100000:
            raise ValueError(
                "Please enter an area below 100,000 hectares."
            )


        # -------------------------------------------------
        # ML PREDICTION
        # -------------------------------------------------

        predicted_yield = predict_yield(
            district=district,
            crop=crop,
            season=season,
            year=year,
            area=area,
        )


        # -------------------------------------------------
        # OFFICIAL BENCHMARK
        # -------------------------------------------------

        benchmark = compare_prediction(
            district=district,
            crop=crop,
            season=season,
            predicted_yield=predicted_yield,
        )


        # -------------------------------------------------
        # ROI
        # -------------------------------------------------

        roi = calculate_roi(
            crop=crop,
            predicted_yield=predicted_yield,
            area=area,
        )


        # -------------------------------------------------
        # FINAL RESULT
        # -------------------------------------------------

        result = {
            "district": district,
            "crop": crop,
            "season": season,
            "year": year,
            "area": area,
            "predicted_yield": predicted_yield,
            "benchmark": benchmark,
            "roi": roi,
        }


        return render_template(
            "result.html",
            result=result,
        )


    except Exception as exc:

        defaults = {
            "district": request.form.get(
                "district",
                "Thanjavur",
            ),
            "crop": request.form.get(
                "crop",
                "Rice",
            ),
            "season": request.form.get(
                "season",
                "Kharif",
            ),
            "year": request.form.get(
                "year",
                2022,
            ),
            "area": request.form.get(
                "area",
                100,
            ),
        }

        return render_template(
            "index.html",
            **template_data(),
            defaults=defaults,
            error=str(exc),
        )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
    )