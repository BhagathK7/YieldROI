"""
YieldROI - ROI / Economic Analysis Module

Purpose:
    Calculate benchmark/scenario economic outcomes for a crop
    using:

    1. Predicted yield from the YieldROI ML model
    2. Official cultivation cost benchmarks
    3. Reference crop prices
    4. Optional official district yield benchmark

Important:
    This module provides a SCENARIO / BENCHMARK ROI estimate.
    It is not a claim of exact farmer profit because actual costs
    and selling prices vary by farm, location, season and market.

Units:
    Cost       -> INR / hectare
    Yield      -> tonnes / hectare
    Price      -> INR / tonne
    Revenue    -> INR / hectare
"""

from pathlib import Path
import json
import math


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RESULTS_DIR = PROJECT_ROOT / "results"

ROI_RESULT_FILE = RESULTS_DIR / "roi_result.json"


# ============================================================
# OFFICIAL COST BENCHMARKS
# ============================================================

# Values are taken from the official Tamil Nadu
# Cost of Cultivation reference table gathered for YieldROI.
#
# Cost unit:
#       INR / hectare
#
# Yield benchmark in the source is in quintal/hectare.
#
# We store the published cost here rather than creating
# artificial farmer-level costs.

COST_BENCHMARKS = {

    "rice": {
        "crop_name": "Rice",
        "cost_per_hectare": 93687.0,
        "source": "Tamil Nadu Agriculture - Cost of Cultivation"
    },

    "sorghum": {
        "crop_name": "Sorghum",
        "cost_per_hectare": 53621.0,
        "source": "Tamil Nadu Agriculture - Cost of Cultivation"
    },

    "maize": {
        "crop_name": "Maize",
        "cost_per_hectare": 95530.0,
        "source": "Tamil Nadu Agriculture - Cost of Cultivation"
    },

    "black gram": {
        "crop_name": "Black gram",
        "cost_per_hectare": 52775.0,
        "source": "Tamil Nadu Agriculture - Cost of Cultivation"
    },

    "blackgram": {
        "crop_name": "Black gram",
        "cost_per_hectare": 52775.0,
        "source": "Tamil Nadu Agriculture - Cost of Cultivation"
    },

    "groundnut": {
        "crop_name": "Groundnut",
        "cost_per_hectare": 98650.0,
        "source": "Tamil Nadu Agriculture - Cost of Cultivation"
    },

    "gingelly": {
        "crop_name": "Gingelly",
        "cost_per_hectare": 55099.0,
        "source": "Tamil Nadu Agriculture - Cost of Cultivation"
    },

    "sesamum": {
        "crop_name": "Gingelly",
        "cost_per_hectare": 55099.0,
        "source": "Tamil Nadu Agriculture - Cost of Cultivation"
    },

    "cotton": {
        "crop_name": "Cotton",
        "cost_per_hectare": 127589.0,
        "source": "Tamil Nadu Agriculture - Cost of Cultivation"
    },

    "cotton lint": {
        "crop_name": "Cotton",
        "cost_per_hectare": 127589.0,
        "source": "Tamil Nadu Agriculture - Cost of Cultivation"
    },

    "sugarcane": {
        "crop_name": "Sugarcane",
        "cost_per_hectare": 277275.0,
        "source": "Tamil Nadu Agriculture - Cost of Cultivation"
    }
}


# ============================================================
# REFERENCE PRICE BENCHMARKS
# ============================================================

# 2026-27 Tamil Nadu MSP/reference values gathered for
# YieldROI.
#
# Price is stored as INR / tonne.
#
# Original MSP values are generally reported as INR/quintal.
# 1 quintal = 100 kg
# 1 tonne = 10 quintals
#
# Therefore:
#       INR/tonne = INR/quintal * 10

PRICE_BENCHMARKS = {

    "rice": {
        "crop_name": "Rice",
        "price_per_tonne": 24410.0,
        "price_type": "MSP - Paddy Common",
        "source": "Tamil Nadu Agriculture - MSP 2026-27"
    },

    "sorghum": {
        "crop_name": "Sorghum",
        "price_per_tonne": 40230.0,
        "price_type": "MSP - Sorghum Hybrid",
        "source": "Tamil Nadu Agriculture - MSP 2026-27"
    },

    "maize": {
        "crop_name": "Maize",
        "price_per_tonne": 24100.0,
        "price_type": "MSP - Maize",
        "source": "Tamil Nadu Agriculture - MSP 2026-27"
    },

    "black gram": {
        "crop_name": "Black gram",
        "price_per_tonne": 82000.0,
        "price_type": "MSP - Blackgram",
        "source": "Tamil Nadu Agriculture - MSP 2026-27"
    },

    "blackgram": {
        "crop_name": "Black gram",
        "price_per_tonne": 82000.0,
        "price_type": "MSP - Blackgram",
        "source": "Tamil Nadu Agriculture - MSP 2026-27"
    },

    "groundnut": {
        "crop_name": "Groundnut",
        "price_per_tonne": 75170.0,
        "price_type": "MSP - Groundnut",
        "source": "Tamil Nadu Agriculture - MSP 2026-27"
    },

    "gingelly": {
        "crop_name": "Gingelly",
        "price_per_tonne": 103460.0,
        "price_type": "MSP - Sesamum",
        "source": "Tamil Nadu Agriculture - MSP 2026-27"
    },

    "sesamum": {
        "crop_name": "Gingelly",
        "price_per_tonne": 103460.0,
        "price_type": "MSP - Sesamum",
        "source": "Tamil Nadu Agriculture - MSP 2026-27"
    },

    "cotton": {
        "crop_name": "Cotton",
        "price_per_tonne": 82670.0,
        "price_type": "MSP - Cotton Medium Staple",
        "source": "Tamil Nadu Agriculture - MSP 2026-27"
    },

    "cotton lint": {
        "crop_name": "Cotton",
        "price_per_tonne": 82670.0,
        "price_type": "MSP - Cotton Medium Staple",
        "source": "Tamil Nadu Agriculture - MSP 2026-27"
    },

    "sugarcane": {
        "crop_name": "Sugarcane",
        "price_per_tonne": 3650.0,
        "price_type": "Published reference price",
        "source": "Tamil Nadu Agriculture - MSP/reference data"
    }
}


# ============================================================
# DISTRICT YIELD BENCHMARKS
# ============================================================

# These are optional.
#
# The ROI calculator does NOT require them to calculate ROI.
# They are used to compare the ML prediction against an
# official district benchmark when the value is supplied.

DISTRICT_YIELD_BENCHMARKS = {}


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def normalize_crop_name(crop):
    """Normalize crop names for dictionary lookup."""

    if crop is None:
        return ""

    crop = str(crop).strip().lower()

    crop = crop.replace("_", " ")
    crop = crop.replace("-", " ")

    crop = " ".join(
        crop.split()
    )

    return crop


def validate_number(
    value,
    name,
    minimum=None,
    maximum=None
):
    """Validate numeric input."""

    try:
        number = float(value)
    except (TypeError, ValueError):

        raise ValueError(
            f"{name} must be a valid number."
        )

    if not math.isfinite(number):

        raise ValueError(
            f"{name} must be a finite number."
        )

    if minimum is not None and number < minimum:

        raise ValueError(
            f"{name} must be at least {minimum}."
        )

    if maximum is not None and number > maximum:

        raise ValueError(
            f"{name} must not exceed {maximum}."
        )

    return number


# ============================================================
# ROI CALCULATOR
# ============================================================

class ROICalculator:

    def __init__(self):

        RESULTS_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

    # --------------------------------------------------------
    # GET COST
    # --------------------------------------------------------

    def get_cost_benchmark(self, crop):

        crop_key = normalize_crop_name(
            crop
        )

        return COST_BENCHMARKS.get(
            crop_key
        )

    # --------------------------------------------------------
    # GET PRICE
    # --------------------------------------------------------

    def get_price_benchmark(self, crop):

        crop_key = normalize_crop_name(
            crop
        )

        return PRICE_BENCHMARKS.get(
            crop_key
        )

    # --------------------------------------------------------
    # CALCULATE
    # --------------------------------------------------------

    def calculate_roi(
        self,
        crop,
        predicted_yield_tonnes_per_ha,
        price_per_tonne=None,
        cost_per_hectare=None,
        reference_yield_tonnes_per_ha=None,
        area_hectares=1.0,
        price_type=None
    ):
        """
        Calculate benchmark/scenario ROI.

        Formula:

            Production
                = predicted yield × area

            Revenue
                = production × selling price

            Total Cost
                = cost/ha × area

            Profit
                = revenue - total cost

            ROI %
                = (profit / total cost) × 100
        """

        # ----------------------------------------------------
        # Validation
        # ----------------------------------------------------

        if not crop:
            raise ValueError(
                "Crop is required."
            )

        predicted_yield = validate_number(
            predicted_yield_tonnes_per_ha,
            "Predicted yield",
            minimum=0
        )

        area = validate_number(
            area_hectares,
            "Area",
            minimum=0.01
        )

        # ----------------------------------------------------
        # Cost benchmark
        # ----------------------------------------------------

        cost_data = self.get_cost_benchmark(
            crop
        )

        if cost_per_hectare is None:

            if cost_data is None:

                raise ValueError(
                    f"No official cultivation-cost "
                    f"benchmark is currently configured "
                    f"for '{crop}'."
                )

            cost_per_hectare = (
                cost_data[
                    "cost_per_hectare"
                ]
            )

        else:

            cost_per_hectare = validate_number(
                cost_per_hectare,
                "Cost per hectare",
                minimum=0
            )

        # ----------------------------------------------------
        # Price benchmark
        # ----------------------------------------------------

        price_data = self.get_price_benchmark(
            crop
        )

        if price_per_tonne is None:

            if price_data is None:

                raise ValueError(
                    f"No reference price is currently "
                    f"configured for '{crop}'."
                )

            price_per_tonne = (
                price_data[
                    "price_per_tonne"
                ]
            )

            selected_price_type = (
                price_data[
                    "price_type"
                ]
            )

        else:

            price_per_tonne = validate_number(
                price_per_tonne,
                "Price per tonne",
                minimum=0
            )

            selected_price_type = (
                price_type
                if price_type
                else "User supplied scenario price"
            )

        # ----------------------------------------------------
        # Reference yield
        # ----------------------------------------------------

        if reference_yield_tonnes_per_ha is not None:

            reference_yield = validate_number(
                reference_yield_tonnes_per_ha,
                "Reference yield",
                minimum=0
            )

        else:

            reference_yield = None

        # ----------------------------------------------------
        # Production
        # ----------------------------------------------------

        predicted_production = (
            predicted_yield * area
        )

        # ----------------------------------------------------
        # Revenue
        # ----------------------------------------------------

        revenue = (
            predicted_production
            * price_per_tonne
        )

        # ----------------------------------------------------
        # Cost
        # ----------------------------------------------------

        total_cost = (
            cost_per_hectare
            * area
        )

        # ----------------------------------------------------
        # Profit
        # ----------------------------------------------------

        profit = (
            revenue
            - total_cost
        )

        # ----------------------------------------------------
        # ROI
        # ----------------------------------------------------

        if total_cost > 0:

            roi_percentage = (
                profit
                / total_cost
            ) * 100

        else:

            roi_percentage = None

        # ----------------------------------------------------
        # Benchmark comparison
        # ----------------------------------------------------

        yield_difference = None
        yield_difference_percentage = None

        if reference_yield is not None:

            yield_difference = (
                predicted_yield
                - reference_yield
            )

            if reference_yield > 0:

                yield_difference_percentage = (
                    yield_difference
                    / reference_yield
                ) * 100

        # ----------------------------------------------------
        # Profit status
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # Result
        # ----------------------------------------------------

        result = {

            "status": "success",

            "crop": crop,

            "area_hectares": round(
                area,
                4
            ),

            "predicted_yield_tonnes_per_ha": round(
                predicted_yield,
                4
            ),

            "predicted_production_tonnes": round(
                predicted_production,
                4
            ),

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

            "price_type": selected_price_type,

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
            ) if roi_percentage is not None else None,

            "profitability_status": (
                profitability_status
            ),

            "reference_yield_tonnes_per_ha": (
                round(
                    reference_yield,
                    4
                )
                if reference_yield is not None
                else None
            ),

            "yield_difference_tonnes_per_ha": (
                round(
                    yield_difference,
                    4
                )
                if yield_difference is not None
                else None
            ),

            "yield_difference_percentage": (
                round(
                    yield_difference_percentage,
                    2
                )
                if yield_difference_percentage is not None
                else None
            ),

            "cost_source": (
                cost_data["source"]
                if cost_data
                else "User supplied scenario cost"
            ),

            "price_source": (
                price_data["source"]
                if price_data
                else "User supplied scenario price"
            ),

            "calculation_basis": (
                "Benchmark/scenario ROI using "
                "predicted yield, cultivation cost "
                "and reference crop price."
            )
        }

        return result

    # --------------------------------------------------------
    # SAVE RESULT
    # --------------------------------------------------------

    def save_result(
        self,
        result,
        output_file=ROI_RESULT_FILE
    ):

        output_file = Path(
            output_file
        )

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                result,
                file,
                indent=4
            )

        return output_file


# ============================================================
# DISPLAY
# ============================================================

def print_roi(result):

    print("\n" + "=" * 65)

    print(
        "                  YIELDROI ROI ANALYSIS"
    )

    print("=" * 65)

    print(
        f"\nCrop                : "
        f"{result['crop']}"
    )

    print(
        f"Area                : "
        f"{result['area_hectares']:.2f} ha"
    )

    print(
        f"Predicted Yield     : "
        f"{result['predicted_yield_tonnes_per_ha']:.2f} "
        f"tonnes/ha"
    )

    print(
        f"Predicted Production: "
        f"{result['predicted_production_tonnes']:.2f} "
        f"tonnes"
    )

    print("\n" + "-" * 65)
    print("ECONOMIC ESTIMATE")
    print("-" * 65)

    print(
        f"\nCost / hectare      : "
        f"₹{result['cost_per_hectare']:,.2f}"
    )

    print(
        f"Total Cost          : "
        f"₹{result['total_cost']:,.2f}"
    )

    print(
        f"Reference Price     : "
        f"₹{result['price_per_tonne']:,.2f}/tonne"
    )

    print(
        f"Price Type          : "
        f"{result['price_type']}"
    )

    print(
        f"\nEstimated Revenue   : "
        f"₹{result['revenue']:,.2f}"
    )

    print(
        f"Estimated Profit    : "
        f"₹{result['profit']:,.2f}"
    )

    print(
        f"ROI                 : "
        f"{result['roi_percentage']:.2f}%"
    )

    print(
        f"Status              : "
        f"{result['profitability_status']}"
    )

    # --------------------------------------------------------
    # Benchmark
    # --------------------------------------------------------

    if (
        result.get(
            "reference_yield_tonnes_per_ha"
        )
        is not None
    ):

        print("\n" + "-" * 65)
        print("YIELD BENCHMARK")
        print("-" * 65)

        print(
            f"\nReference Yield     : "
            f"{result['reference_yield_tonnes_per_ha']:.2f} "
            f"tonnes/ha"
        )

        print(
            f"Difference          : "
            f"{result['yield_difference_tonnes_per_ha']:.2f} "
            f"tonnes/ha"
        )

        print(
            f"Difference %        : "
            f"{result['yield_difference_percentage']:.2f}%"
        )

    # --------------------------------------------------------
    # Sources
    # --------------------------------------------------------

    print("\n" + "-" * 65)
    print("DATA SOURCES")
    print("-" * 65)

    print(
        f"\nCost Source : "
        f"{result['cost_source']}"
    )

    print(
        f"Price Source: "
        f"{result['price_source']}"
    )

    print("\n" + "-" * 65)

    print(
        "NOTE: This is a benchmark/scenario ROI estimate."
    )

    print(
        "Actual farm profit may vary based on "
        "farm-specific costs and selling price."
    )

    print("=" * 65)


# ============================================================
# COMMAND-LINE TEST
# ============================================================

def main():

    print(
        "\nYieldROI ROI Calculator"
    )

    calculator = ROICalculator()

    # --------------------------------------------------------
    # Input
    # --------------------------------------------------------

    crop = input(
        "\nEnter crop: "
    ).strip()

    predicted_yield = input(
        "Enter predicted yield (tonnes/ha): "
    ).strip()

    area = input(
        "Enter area (hectares): "
    ).strip()

    # --------------------------------------------------------
    # Calculate
    # --------------------------------------------------------

    try:

        result = calculator.calculate_roi(

            crop=crop,

            predicted_yield_tonnes_per_ha=(
                predicted_yield
            ),

            area_hectares=area
        )

        print_roi(
            result
        )

        output_file = calculator.save_result(
            result
        )

        print(
            f"\nResult saved to:"
        )

        print(
            output_file
        )

    except Exception as error:

        print(
            "\nERROR:"
        )

        print(error)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()