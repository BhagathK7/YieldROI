"""
YieldROI - Fertilizer Product Optimizer

Purpose
-------
Converts the recommended nutrient requirement:

    N
    P2O5
    K2O

into practical fertilizer product quantities.

Products currently supported
----------------------------
Urea     : 46% N
DAP      : 18% N + 46% P2O5
SSP      : 16% P2O5
MOP      : 60% K2O

Method
------
The optimizer first satisfies the P2O5 requirement using DAP.

The nitrogen supplied by DAP is then subtracted from the
total N requirement.

The remaining N is supplied using Urea.

Potassium is supplied using MOP.

This is a deterministic nutrient-balancing calculation.
It is NOT a machine-learning prediction.

Important
---------
The final recommendation should still be interpreted along
with the applicable TNAU recommendation, soil test results,
crop, variety, season and local agricultural guidance.
"""


from typing import Optional


# ============================================================
# FERTILIZER PRODUCT COMPOSITIONS
# ============================================================

FERTILIZER_PRODUCTS = {

    "DAP": {
        "name": "DAP",
        "full_name": "Diammonium Phosphate",
        "n_percent": 18.0,
        "p2o5_percent": 46.0,
        "k2o_percent": 0.0,
        "unit": "kg"
    },

    "Urea": {
        "name": "Urea",
        "full_name": "Urea",
        "n_percent": 46.0,
        "p2o5_percent": 0.0,
        "k2o_percent": 0.0,
        "unit": "kg"
    },

    "SSP": {
        "name": "SSP",
        "full_name": "Single Super Phosphate",
        "n_percent": 0.0,
        "p2o5_percent": 16.0,
        "k2o_percent": 0.0,
        "unit": "kg"
    },

    "MOP": {
        "name": "MOP",
        "full_name": "Muriate of Potash",
        "n_percent": 0.0,
        "p2o5_percent": 0.0,
        "k2o_percent": 60.0,
        "unit": "kg"
    }
}


# ============================================================
# HELPERS
# ============================================================

def _number(
    value,
    default=0.0
):
    """
    Safely convert a value to float.
    """

    if value is None:
        return default

    try:
        result = float(value)

    except (
        ValueError,
        TypeError
    ):
        return default

    if result < 0:
        return default

    return result


def _round(
    value,
    digits=2
):
    """
    Safe rounding helper.
    """

    return round(
        float(value),
        digits
    )


def _product_amount(
    nutrient_required,
    percentage
):
    """
    Calculate fertilizer quantity required to supply
    a nutrient requirement.

    Example:

        40 kg P2O5
        SSP = 16% P2O5

        40 / 0.16 = 250 kg SSP
    """

    if percentage <= 0:
        return 0.0

    return (
        nutrient_required
        /
        (percentage / 100.0)
    )


def _nutrient_from_product(
    product_amount,
    percentage
):
    """
    Calculate nutrient supplied by a fertilizer product.
    """

    return (
        product_amount
        *
        percentage
        /
        100.0
    )


# ============================================================
# MAIN OPTIMIZER
# ============================================================

def optimize_fertilizer(
    n: Optional[float],
    p2o5: Optional[float],
    k2o: Optional[float],
    area: float = 1.0
):
    """
    Convert nutrient requirements into fertilizer products.

    Parameters
    ----------
    n:
        Required nitrogen in kg/ha.

    p2o5:
        Required phosphorus as P2O5 in kg/ha.

    k2o:
        Required potassium as K2O in kg/ha.

    area:
        Field area in hectares.

    Returns
    -------
    dict
        Complete fertilizer product plan.

    Example
    -------
    For:

        N    = 120 kg/ha
        P2O5 = 40 kg/ha
        K2O  = 40 kg/ha

    approximately:

        DAP  = 86.96 kg/ha
        Urea = 226.84 kg/ha
        MOP  = 66.67 kg/ha
    """

    # --------------------------------------------------------
    # Validate inputs
    # --------------------------------------------------------

    n_required = _number(n)

    p_required = _number(p2o5)

    k_required = _number(k2o)

    field_area = _number(
        area,
        default=1.0
    )

    if field_area <= 0:
        field_area = 1.0

    # --------------------------------------------------------
    # Product compositions
    # --------------------------------------------------------

    dap = FERTILIZER_PRODUCTS["DAP"]

    urea = FERTILIZER_PRODUCTS["Urea"]

    mop = FERTILIZER_PRODUCTS["MOP"]

    # --------------------------------------------------------
    # STEP 1
    #
    # Supply P2O5 using DAP.
    #
    # DAP contains 46% P2O5.
    # --------------------------------------------------------

    dap_per_ha = _product_amount(
        p_required,
        dap["p2o5_percent"]
    )

    # Nitrogen contributed by DAP.
    dap_n_per_ha = _nutrient_from_product(
        dap_per_ha,
        dap["n_percent"]
    )

    # --------------------------------------------------------
    # STEP 2
    #
    # Remaining nitrogen is supplied using Urea.
    #
    # Urea contains 46% N.
    # --------------------------------------------------------

    remaining_n_per_ha = max(
        n_required - dap_n_per_ha,
        0.0
    )

    urea_per_ha = _product_amount(
        remaining_n_per_ha,
        urea["n_percent"]
    )

    # --------------------------------------------------------
    # STEP 3
    #
    # Supply K2O using MOP.
    #
    # MOP contains 60% K2O.
    # --------------------------------------------------------

    mop_per_ha = _product_amount(
        k_required,
        mop["k2o_percent"]
    )

    # --------------------------------------------------------
    # Supplied nutrients
    # --------------------------------------------------------

    urea_n_per_ha = _nutrient_from_product(
        urea_per_ha,
        urea["n_percent"]
    )

    total_n_supplied = (
        dap_n_per_ha
        +
        urea_n_per_ha
    )

    total_p_supplied = (
        _nutrient_from_product(
            dap_per_ha,
            dap["p2o5_percent"]
        )
    )

    total_k_supplied = (
        _nutrient_from_product(
            mop_per_ha,
            mop["k2o_percent"]
        )
    )

    # --------------------------------------------------------
    # Field quantities
    # --------------------------------------------------------

    dap_total = (
        dap_per_ha
        *
        field_area
    )

    urea_total = (
        urea_per_ha
        *
        field_area
    )

    mop_total = (
        mop_per_ha
        *
        field_area
    )

    # --------------------------------------------------------
    # Total fertilizer weight
    # --------------------------------------------------------

    total_fertilizer_per_ha = (
        dap_per_ha
        +
        urea_per_ha
        +
        mop_per_ha
    )

    total_fertilizer_field = (
        total_fertilizer_per_ha
        *
        field_area
    )

    # --------------------------------------------------------
    # Nutrient balance
    # --------------------------------------------------------

    n_balance = (
        total_n_supplied
        -
        n_required
    )

    p_balance = (
        total_p_supplied
        -
        p_required
    )

    k_balance = (
        total_k_supplied
        -
        k_required
    )

    # --------------------------------------------------------
    # Product plan
    # --------------------------------------------------------

    products = [

        {
            "product": "DAP",
            "full_name":
                dap["full_name"],

            "grade":
                "18-46-0",

            "quantity_kg_per_ha":
                _round(
                    dap_per_ha
                ),

            "quantity_kg_total":
                _round(
                    dap_total
                ),

            "purpose":
                "Supplies P2O5 and part of N."
        },

        {
            "product": "Urea",
            "full_name":
                urea["full_name"],

            "grade":
                "46-0-0",

            "quantity_kg_per_ha":
                _round(
                    urea_per_ha
                ),

            "quantity_kg_total":
                _round(
                    urea_total
                ),

            "purpose":
                "Supplies the remaining N requirement."
        },

        {
            "product": "MOP",
            "full_name":
                mop["full_name"],

            "grade":
                "0-0-60",

            "quantity_kg_per_ha":
                _round(
                    mop_per_ha
                ),

            "quantity_kg_total":
                _round(
                    mop_total
                ),

            "purpose":
                "Supplies K2O."
        }
    ]

    # --------------------------------------------------------
    # Return
    # --------------------------------------------------------

    return {

        "available": True,

        "method":
            "Deterministic nutrient-to-product optimization",

        "area_hectares":
            _round(
                field_area,
                3
            ),

        "target_nutrients": {

            "n_kg_per_ha":
                _round(
                    n_required
                ),

            "p2o5_kg_per_ha":
                _round(
                    p_required
                ),

            "k2o_kg_per_ha":
                _round(
                    k_required
                )
        },

        "supplied_nutrients": {

            "n_kg_per_ha":
                _round(
                    total_n_supplied
                ),

            "p2o5_kg_per_ha":
                _round(
                    total_p_supplied
                ),

            "k2o_kg_per_ha":
                _round(
                    total_k_supplied
                )
        },

        "balance": {

            "n_kg_per_ha":
                _round(
                    n_balance
                ),

            "p2o5_kg_per_ha":
                _round(
                    p_balance
                ),

            "k2o_kg_per_ha":
                _round(
                    k_balance
                )
        },

        "products":
            products,

        "total_fertilizer": {

            "kg_per_ha":
                _round(
                    total_fertilizer_per_ha
                ),

            "kg_total":
                _round(
                    total_fertilizer_field
                )
        },

        "product_grades": {

            "DAP":
                "18-46-0",

            "Urea":
                "46-0-0",

            "MOP":
                "0-0-60"
        },

        "note":
            (
                "Product quantities are calculated from "
                "the selected nutrient recommendation "
                "and standard fertilizer grades. "
                "Actual field application should follow "
                "soil-test and TNAU agricultural guidance."
            )
    }


# ============================================================
# CONVENIENCE FUNCTION
# ============================================================

def optimize_from_recommendation(
    recommendation,
    area=1.0
):
    """
    Accept an existing YieldROI fertilizer recommendation
    dictionary and convert its N/P/K requirement into
    product quantities.

    This makes integration with the existing
    FertilizerRecommender easier.
    """

    if not isinstance(
        recommendation,
        dict
    ):

        return {
            "available": False,
            "message":
                "Invalid fertilizer recommendation."
        }

    n = (
        recommendation.get(
            "nitrogen_kg_per_ha"
        )
    )

    if n is None:
        n = recommendation.get(
            "n"
        )

    if n is None:
        n = recommendation.get(
            "nitrogen"
        )

    p = (
        recommendation.get(
            "phosphorus_kg_per_ha"
        )
    )

    if p is None:
        p = recommendation.get(
            "p2o5"
        )

    if p is None:
        p = recommendation.get(
            "phosphorus"
        )

    k = (
        recommendation.get(
            "potassium_kg_per_ha"
        )
    )

    if k is None:
        k = recommendation.get(
            "k2o"
        )

    if k is None:
        k = recommendation.get(
            "potassium"
        )

    if (
        n is None
        or p is None
        or k is None
    ):

        return {

            "available": False,

            "message":
                (
                    "Complete N, P2O5 and K2O "
                    "requirements are required "
                    "before fertilizer products "
                    "can be calculated."
                )
        }

    return optimize_fertilizer(
        n=n,
        p2o5=p,
        k2o=k,
        area=area
    )


# ============================================================
# COMMAND-LINE TEST
# ============================================================

def main():

    print()
    print("=" * 70)
    print("YIELDROI - FERTILIZER PRODUCT OPTIMIZER")
    print("=" * 70)

    # Example:
    # N = 120
    # P2O5 = 40
    # K2O = 40
    # Area = 1 hectare

    result = optimize_fertilizer(
        n=120,
        p2o5=40,
        k2o=40,
        area=1
    )

    print("\nTARGET NUTRIENTS")

    print(
        f"N     : "
        f"{result['target_nutrients']['n_kg_per_ha']} kg/ha"
    )

    print(
        f"P2O5  : "
        f"{result['target_nutrients']['p2o5_kg_per_ha']} kg/ha"
    )

    print(
        f"K2O   : "
        f"{result['target_nutrients']['k2o_kg_per_ha']} kg/ha"
    )

    print("\nPRODUCT PLAN")

    for product in result["products"]:

        print(
            f"{product['product']:8} "
            f"{product['quantity_kg_per_ha']:8.2f} kg/ha"
        )

    print(
        "\nTotal fertilizer : "
        f"{result['total_fertilizer']['kg_per_ha']:.2f} kg/ha"
    )

    print(
        "\nField area       : "
        f"{result['area_hectares']:.2f} ha"
    )

    print(
        "\nField requirement:"
    )

    for product in result["products"]:

        print(
            f"{product['product']:8} "
            f"{product['quantity_kg_total']:8.2f} kg"
        )

    print()
    print("=" * 70)


if __name__ == "__main__":
    main()