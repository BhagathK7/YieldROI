from pathlib import Path
import pandas as pd


# ============================================================
# YIELD ROI - ROI CALCULATOR
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

# ------------------------------------------------------------
# Reference economic data
# ------------------------------------------------------------
# These are REFERENCE values.
# They should be replaced/updated when a newer official
# crop-specific cost/price dataset is added.
#
# Cost = cultivation cost per hectare (₹/ha)
# Price = reference selling price (₹/tonne)
#
# Do NOT interpret these as guaranteed market prices.
# ------------------------------------------------------------

CROP_ECONOMIC_DATA = {

    "Rice": {
        "cultivation_cost_per_ha": 93687.0,
        "reference_price_per_tonne": 22000.0,
        "source": "Tamil Nadu Agriculture Department - Cost of Cultivation",
        "price_source": "Reference market-price input; user-adjustable",
    },

    "Maize": {
        "cultivation_cost_per_ha": None,
        "reference_price_per_tonne": 22000.0,
        "source": "Tamil Nadu Agriculture Department",
        "price_source": "Reference market-price input; user-adjustable",
    },

    "Sorghum": {
        "cultivation_cost_per_ha": None,
        "reference_price_per_tonne": 30000.0,
        "source": "Tamil Nadu Agriculture Department",
        "price_source": "Reference market-price input; user-adjustable",
    },

    "Groundnut": {
        "cultivation_cost_per_ha": None,
        "reference_price_per_tonne": 60000.0,
        "source": "Tamil Nadu Agriculture Department",
        "price_source": "Reference market-price input; user-adjustable",
    },

    "Sugarcane": {
        "cultivation_cost_per_ha": None,
        "reference_price_per_tonne": 3500.0,
        "source": "Tamil Nadu Agriculture Department",
        "price_source": "Reference market-price input; user-adjustable",
    },

    "Ragi": {
        "cultivation_cost_per_ha": None,
        "reference_price_per_tonne": 35000.0,
        "source": "Tamil Nadu Agriculture Department",
        "price_source": "Reference market-price input; user-adjustable",
    },
}


# ============================================================
# VALIDATION
# ============================================================

def validate_positive_number(value, field_name):

    try:
        value = float(value)
    except (TypeError, ValueError):

        raise ValueError(
            f"{field_name} must be a valid number."
        )

    if value <= 0:

        raise ValueError(
            f"{field_name} must be greater than zero."
        )

    return value


# ============================================================
# GET CROP DATA
# ============================================================

def get_crop_economic_data(crop):

    crop = str(crop).strip()

    # Exact match
    if crop in CROP_ECONOMIC_DATA:
        return CROP_ECONOMIC_DATA[crop]

    # Case-insensitive match
    for crop_name, data in CROP_ECONOMIC_DATA.items():

        if crop_name.lower() == crop.lower():
            return data

    return None


# ============================================================
# CALCULATE EXPECTED PRODUCTION
# ============================================================

def calculate_production(
    area_hectares,
    predicted_yield,
):
    """
    predicted_yield is assumed to be in kg/ha.

    Production:
        hectares × kg/ha

    Converted to tonnes.
    """

    area_hectares = validate_positive_number(
        area_hectares,
        "Area"
    )

    predicted_yield = validate_positive_number(
        predicted_yield,
        "Predicted yield"
    )

    production_kg = (
        area_hectares
        * predicted_yield
    )

    production_tonnes = (
        production_kg / 1000
    )

    return production_tonnes


# ============================================================
# CALCULATE ROI
# ============================================================

def calculate_roi(
    crop,
    area_hectares,
    predicted_yield,
    selling_price_per_tonne=None,
    cultivation_cost_per_ha=None,
    additional_cost=0,
):
    """
    Calculate scenario-based agricultural ROI.

    Inputs:
        crop
        area_hectares
        predicted_yield       -> kg/ha
        selling_price         -> ₹/tonne
        cultivation_cost      -> ₹/ha
        additional_cost       -> total ₹

    Outputs:
        production
        revenue
        cultivation cost
        additional cost
        total cost
        net return
        ROI percentage

    IMPORTANT:
        This is a scenario-based economic estimate.
        It does NOT claim that the ML model caused the
        predicted yield or profit.
    """

    # --------------------------------------------------------
    # Validate crop
    # --------------------------------------------------------

    crop_data = get_crop_economic_data(
        crop
    )

    if crop_data is None:

        raise ValueError(
            f"No economic reference data is "
            f"available for crop: {crop}"
        )

    # --------------------------------------------------------
    # Validate area
    # --------------------------------------------------------

    area_hectares = validate_positive_number(
        area_hectares,
        "Area"
    )

    # --------------------------------------------------------
    # Validate predicted yield
    # --------------------------------------------------------

    predicted_yield = validate_positive_number(
        predicted_yield,
        "Predicted yield"
    )

    # --------------------------------------------------------
    # Price
    # --------------------------------------------------------

    if selling_price_per_tonne is None:

        selling_price_per_tonne = (
            crop_data[
                "reference_price_per_tonne"
            ]
        )

    selling_price_per_tonne = (
        validate_positive_number(
            selling_price_per_tonne,
            "Selling price"
        )
    )

    # --------------------------------------------------------
    # Cultivation cost
    # --------------------------------------------------------

    if cultivation_cost_per_ha is None:

        cultivation_cost_per_ha = (
            crop_data[
                "cultivation_cost_per_ha"
            ]
        )

    if cultivation_cost_per_ha is None:

        raise ValueError(
            f"No verified cultivation cost is "
            f"currently configured for {crop}. "
            f"Please provide the cost per hectare."
        )

    cultivation_cost_per_ha = (
        validate_positive_number(
            cultivation_cost_per_ha,
            "Cultivation cost per hectare"
        )
    )

    # --------------------------------------------------------
    # Additional cost
    # --------------------------------------------------------

    additional_cost = float(
        additional_cost
    )

    if additional_cost < 0:

        raise ValueError(
            "Additional cost cannot be negative."
        )

    # --------------------------------------------------------
    # Production
    # --------------------------------------------------------

    production_tonnes = calculate_production(
        area_hectares,
        predicted_yield,
    )

    # --------------------------------------------------------
    # Revenue
    # --------------------------------------------------------

    gross_revenue = (
        production_tonnes
        * selling_price_per_tonne
    )

    # --------------------------------------------------------
    # Cultivation cost
    # --------------------------------------------------------

    cultivation_cost = (
        area_hectares
        * cultivation_cost_per_ha
    )

    # --------------------------------------------------------
    # Total cost
    # --------------------------------------------------------

    total_cost = (
        cultivation_cost
        + additional_cost
    )

    # --------------------------------------------------------
    # Net return
    # --------------------------------------------------------

    net_return = (
        gross_revenue
        - total_cost
    )

    # --------------------------------------------------------
    # ROI
    # --------------------------------------------------------

    if total_cost > 0:

        roi_percentage = (
            net_return
            / total_cost
        ) * 100

    else:

        roi_percentage = 0

    # --------------------------------------------------------
    # Break-even yield
    # --------------------------------------------------------

    break_even_production_tonnes = (
        total_cost
        / selling_price_per_tonne
    )

    break_even_yield_kg_per_ha = (
        break_even_production_tonnes
        * 1000
        / area_hectares
    )

    # --------------------------------------------------------
    # Return result
    # --------------------------------------------------------

    return {

        "success": True,

        "crop": crop,

        "area_hectares":
            round(
                area_hectares,
                4
            ),

        "predicted_yield_kg_per_ha":
            round(
                predicted_yield,
                2
            ),

        "expected_production_tonnes":
            round(
                production_tonnes,
                3
            ),

        "selling_price_per_tonne":
            round(
                selling_price_per_tonne,
                2
            ),

        "gross_revenue":
            round(
                gross_revenue,
                2
            ),

        "cultivation_cost_per_ha":
            round(
                cultivation_cost_per_ha,
                2
            ),

        "cultivation_cost":
            round(
                cultivation_cost,
                2
            ),

        "additional_cost":
            round(
                additional_cost,
                2
            ),

        "total_cost":
            round(
                total_cost,
                2
            ),

        "net_return":
            round(
                net_return,
                2
            ),

        "roi_percentage":
            round(
                roi_percentage,
                2
            ),

        "break_even_yield_kg_per_ha":
            round(
                break_even_yield_kg_per_ha,
                2
            ),

        "economic_data_source":
            crop_data["source"],

        "price_source":
            crop_data["price_source"],

        "interpretation":
            (
                "Positive ROI indicates that the estimated "
                "gross revenue exceeds the modeled costs. "
                "Negative ROI indicates that the modeled "
                "costs exceed the estimated gross revenue."
            ),

        "disclaimer":
            (
                "ROI is a scenario-based economic estimate. "
                "Actual returns vary with market price, "
                "cultivation expenses, input costs, "
                "quality, losses and farm conditions."
            ),
    }


# ============================================================
# DISPLAY RESULT
# ============================================================

def display_result(result):

    print("\n" + "=" * 70)
    print("YIELD ROI - ECONOMIC ANALYSIS")
    print("=" * 70)

    print(
        f"\nCrop: {result['crop']}"
    )

    print(
        f"Area: "
        f"{result['area_hectares']} ha"
    )

    print(
        f"Predicted yield: "
        f"{result['predicted_yield_kg_per_ha']} kg/ha"
    )

    print(
        f"\nExpected production: "
        f"{result['expected_production_tonnes']} tonnes"
    )

    print(
        f"Selling price: "
        f"₹{result['selling_price_per_tonne']:,.2f}/tonne"
    )

    print(
        f"\nGross revenue: "
        f"₹{result['gross_revenue']:,.2f}"
    )

    print(
        f"Cultivation cost: "
        f"₹{result['cultivation_cost']:,.2f}"
    )

    print(
        f"Additional cost: "
        f"₹{result['additional_cost']:,.2f}"
    )

    print(
        f"Total cost: "
        f"₹{result['total_cost']:,.2f}"
    )

    print(
        f"\nNet return: "
        f"₹{result['net_return']:,.2f}"
    )

    print(
        f"ROI: "
        f"{result['roi_percentage']:.2f}%"
    )

    print(
        f"\nBreak-even yield: "
        f"{result['break_even_yield_kg_per_ha']:.2f} kg/ha"
    )

    print(
        "\nEconomic source:"
    )

    print(
        f"  {result['economic_data_source']}"
    )

    print(
        "\nNOTE:"
    )

    print(
        result["disclaimer"]
    )

    print("\n" + "=" * 70)


# ============================================================
# TEST
# ============================================================

def main():

    print("=" * 70)
    print("YIELD ROI - ROI CALCULATOR")
    print("=" * 70)

    crop = input(
        "\nCrop: "
    ).strip()

    area = input(
        "Area (hectares): "
    ).strip()

    predicted_yield = input(
        "Predicted yield (kg/ha): "
    ).strip()

    selling_price = input(
        "Selling price (₹/tonne, "
        "press Enter for reference value): "
    ).strip()

    additional_cost = input(
        "Additional cost (₹, "
        "press Enter for 0): "
    ).strip()

    # --------------------------------------------------------
    # Optional values
    # --------------------------------------------------------

    if selling_price == "":
        selling_price = None
    else:
        selling_price = float(
            selling_price
        )

    if additional_cost == "":
        additional_cost = 0
    else:
        additional_cost = float(
            additional_cost
        )

    # --------------------------------------------------------
    # Calculate
    # --------------------------------------------------------

    try:

        result = calculate_roi(
            crop=crop,
            area_hectares=float(area),
            predicted_yield=float(
                predicted_yield
            ),
            selling_price_per_tonne=
                selling_price,
            additional_cost=
                additional_cost,
        )

        display_result(
            result
        )

    except ValueError as error:

        print(
            f"\nERROR: {error}"
        )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()