from pathlib import Path
import pandas as pd


# ============================================================
# YIELD ROI - FERTILIZER RECOMMENDER
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

SOIL_FILE = (
    BASE_DIR
    / "fertilizer"
    / "final_soil_profiles.csv"
)

KNOWLEDGE_FILE = (
    BASE_DIR
    / "fertilizer"
    / "fertilizer_knowledge_base.csv"
)


# ============================================================
# SOIL STATUS COLUMNS
# ============================================================

NUTRIENT_STATUS_COLUMNS = {
    "Nitrogen": "Nitrogen_status",
    "Phosphorus": "Phosphorus_status",
    "Potassium": "Potassium_status",
    "Organic Carbon": "Organic Carbon_status",
    "Soil pH": "Soil Ph_status",
    "Electrical Conductivity":
        "Electrical Conductivity_status",
    "Zinc": "Zinc_status",
    "Boron": "Boron_status",
    "Manganese": "Manganese_status",
    "Sulphur": "Sulphur_status",
    "Copper": "Copper_status",
    "Iron": "Iron_status",
}


# ============================================================
# LOAD DATA
# ============================================================

def load_data():

    if not SOIL_FILE.exists():
        raise FileNotFoundError(
            f"Soil profile file not found:\n{SOIL_FILE}"
        )

    if not KNOWLEDGE_FILE.exists():
        raise FileNotFoundError(
            f"Knowledge base file not found:\n{KNOWLEDGE_FILE}"
        )

    soil = pd.read_csv(SOIL_FILE)
    knowledge = pd.read_csv(KNOWLEDGE_FILE)

    return soil, knowledge


# ============================================================
# FIND SOIL PROFILE
# ============================================================

def find_soil_profile(
    soil,
    district,
    block,
    village,
    year,
):

    result = soil[
        (
            soil["district_name"]
            .astype(str)
            .str.strip()
            .str.lower()
            == district.strip().lower()
        )
        &
        (
            soil["block_name"]
            .astype(str)
            .str.strip()
            .str.lower()
            == block.strip().lower()
        )
        &
        (
            soil["village_name"]
            .astype(str)
            .str.strip()
            .str.lower()
            == village.strip().lower()
        )
        &
        (
            soil["year"]
            .astype(str)
            .str.strip()
            .str.lower()
            == year.strip().lower()
        )
    ]

    if result.empty:
        return None

    return result.iloc[0]


# ============================================================
# CHECK BLOCK APPLICABILITY
# ============================================================

def block_is_applicable(
    recommendation,
    district,
    block,
):
    """
    Determine whether a district/block matches
    the recommendation's geographic applicability.

    Rules:

    1. Tamil Nadu
       -> applicable everywhere in Tamil Nadu.

    2. Cauvery Delta / Coimbatore
       -> block must be explicitly listed.

    3. Other Tracts
       -> used when the block is not part of the
          explicitly listed special region.

    """

    applicability = str(
        recommendation["applicability_type"]
    ).strip().lower()

    district = district.strip().lower()
    block = block.strip().lower()

    # --------------------------------------------------------
    # General Tamil Nadu recommendation
    # --------------------------------------------------------

    if applicability == "tamil nadu":
        return True

    # --------------------------------------------------------
    # Special Cauvery Delta / Coimbatore recommendation
    # --------------------------------------------------------

    if applicability == "cauvery delta / coimbatore":

        applicable_blocks = str(
            recommendation.get(
                "applicable_blocks",
                ""
            )
        )

        if not applicable_blocks:
            return False

        blocks = [
            item.strip().lower()
            for item in applicable_blocks.split(";")
            if item.strip()
        ]

        return block in blocks

    # --------------------------------------------------------
    # Other tracts
    # --------------------------------------------------------

    if applicability == "other tracts":

        special_recommendation = (
            "Cauvery Delta / Coimbatore"
        )

        special_rows = KNOWLEDGE_CACHE[
            KNOWLEDGE_CACHE[
                "applicability_type"
            ]
            .astype(str)
            .str.strip()
            .str.lower()
            == special_recommendation.lower()
        ]

        special_blocks = set()

        for _, row in special_rows.iterrows():

            values = str(
                row.get(
                    "applicable_blocks",
                    ""
                )
            ).split(";")

            for value in values:

                value = value.strip().lower()

                if value:
                    special_blocks.add(value)

        return block not in special_blocks

    return False


# ============================================================
# FIND BEST RECOMMENDATION
# ============================================================

def find_recommendation(
    knowledge,
    crop,
    district,
    block,
    season_condition=None,
):
    """
    Find recommendation using:

        Crop
          ↓
        Season / condition
          ↓
        District / block applicability
    """

    crop_rows = knowledge[
        knowledge["crop"]
        .astype(str)
        .str.strip()
        .str.lower()
        == crop.strip().lower()
    ].copy()

    if crop_rows.empty:
        return None

    # --------------------------------------------------------
    # First filter by season/condition
    # --------------------------------------------------------

    if season_condition:

        condition_rows = crop_rows[
            crop_rows["season_condition"]
            .astype(str)
            .str.strip()
            .str.lower()
            == season_condition.strip().lower()
        ].copy()

        if not condition_rows.empty:
            crop_rows = condition_rows

    # --------------------------------------------------------
    # Check geographic applicability
    # --------------------------------------------------------

    applicable = []

    for _, row in crop_rows.iterrows():

        if block_is_applicable(
            row,
            district,
            block,
        ):
            applicable.append(row)

    if not applicable:
        return None

    applicable_df = pd.DataFrame(
        applicable
    )

    # --------------------------------------------------------
    # If exactly one match
    # --------------------------------------------------------

    if len(applicable_df) == 1:
        return applicable_df.iloc[0]

    # --------------------------------------------------------
    # Multiple valid recommendations
    # --------------------------------------------------------

    return applicable_df


# ============================================================
# CLEAN STATUS
# ============================================================

def clean_status(status):

    if pd.isna(status):
        return "Unknown"

    status = str(status).strip()

    if not status:
        return "Unknown"

    return status


# ============================================================
# BUILD SOIL EVIDENCE
# ============================================================

def build_soil_evidence(profile):

    evidence = []

    for nutrient, status_column in (
        NUTRIENT_STATUS_COLUMNS.items()
    ):

        if status_column not in profile.index:
            continue

        status = clean_status(
            profile[status_column]
        )

        # final_soil_profiles uses "Soil Ph"
        generated_name = nutrient

        if nutrient == "Soil pH":
            generated_name = "Soil Ph"

        sample_column = (
            f"{generated_name}_sample_count"
        )

        support_column = (
            f"{generated_name}_status_support_pct"
        )

        coverage_column = (
            f"{generated_name}_coverage"
        )

        sample_count = profile.get(
            sample_column,
            0
        )

        support = profile.get(
            support_column,
            0
        )

        coverage = profile.get(
            coverage_column,
            "No Data"
        )

        try:
            sample_count = int(
                float(sample_count)
            )
        except (ValueError, TypeError):
            sample_count = 0

        try:
            support = float(support)
        except (ValueError, TypeError):
            support = 0.0

        evidence.append(
            {
                "nutrient": nutrient,
                "status": status,
                "sample_count": sample_count,
                "support_percentage": round(
                    support,
                    2
                ),
                "coverage": str(coverage),
            }
        )

    return evidence


# ============================================================
# BUILD EXPLANATION
# ============================================================

def build_explanation(
    soil_evidence,
    recommendation,
):

    reasons = []

    important_nutrients = [
        "Nitrogen",
        "Phosphorus",
        "Potassium",
        "Organic Carbon",
        "Soil pH",
    ]

    for item in soil_evidence:

        if item["nutrient"] not in important_nutrients:
            continue

        if item["status"] == "Unknown":
            continue

        reasons.append(
            f"{item['nutrient']}: "
            f"{item['status']} "
            f"({item['sample_count']} samples, "
            f"{item['support_percentage']:.1f}% support)"
        )

    if isinstance(
        recommendation,
        pd.Series
    ):

        reasons.append(
            "Baseline nutrient recommendation "
            f"is from "
            f"{recommendation['source_organization']} "
            f"({recommendation['source_reference']})."
        )

    return reasons


# ============================================================
# GENERATE RECOMMENDATION
# ============================================================

def generate_recommendation(
    district,
    block,
    village,
    year,
    crop,
    season_condition=None,
):

    global KNOWLEDGE_CACHE

    soil, knowledge = load_data()

    KNOWLEDGE_CACHE = knowledge

    # --------------------------------------------------------
    # Find soil profile
    # --------------------------------------------------------

    profile = find_soil_profile(
        soil,
        district,
        block,
        village,
        year,
    )

    if profile is None:

        return {
            "success": False,
            "message": (
                "No soil profile was found for "
                "the selected village and year."
            ),
        }

    # --------------------------------------------------------
    # Find recommendation
    # --------------------------------------------------------

    recommendation = find_recommendation(
        knowledge=knowledge,
        crop=crop,
        district=district,
        block=block,
        season_condition=season_condition,
    )

    if recommendation is None:

        return {
            "success": False,
            "message": (
                f"No geographically applicable verified "
                f"recommendation was found for {crop} "
                f"in {district} - {block}."
            ),
        }

    # --------------------------------------------------------
    # Multiple recommendations
    # --------------------------------------------------------

    if isinstance(
        recommendation,
        pd.DataFrame
    ):

        options = []

        for _, row in recommendation.iterrows():

            options.append(
                {
                    "season_condition":
                        row["season_condition"],

                    "recommendation_type":
                        row["recommendation_type"],

                    "applicability_type":
                        row["applicability_type"],

                    "n_rate_kg_ha":
                        float(
                            row["n_rate_kg_ha"]
                        ),

                    "p2o5_rate_kg_ha":
                        float(
                            row["p2o5_rate_kg_ha"]
                        ),

                    "k2o_rate_kg_ha":
                        float(
                            row["k2o_rate_kg_ha"]
                        ),

                    "district_condition":
                        row["applicability_type"],
                }
            )

        return {
            "success": True,
            "requires_selection": True,

            "message": (
                "Multiple applicable verified "
                "recommendations were found. "
                "Please select the crop condition."
            ),

            "soil_profile":
                profile.to_dict(),

            "options":
                options,
        }

    # --------------------------------------------------------
    # Soil evidence
    # --------------------------------------------------------

    soil_evidence = build_soil_evidence(
        profile
    )

    explanation = build_explanation(
        soil_evidence,
        recommendation,
    )

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    return {

        "success": True,

        "requires_selection": False,

        "location": {
            "year": profile["year"],
            "district": profile["district_name"],
            "block": profile["block_name"],
            "village": profile["village_name"],
        },

        "crop": crop,

        "soil_evidence": soil_evidence,

        "recommendation": {

            "season_condition":
                recommendation[
                    "season_condition"
                ],

            "recommendation_type":
                recommendation[
                    "recommendation_type"
                ],

            "applicability_type":
                recommendation[
                    "applicability_type"
                ],

            "N_kg_per_ha":
                float(
                    recommendation[
                        "n_rate_kg_ha"
                    ]
                ),

            "P2O5_kg_per_ha":
                float(
                    recommendation[
                        "p2o5_rate_kg_ha"
                    ]
                ),

            "K2O_kg_per_ha":
                float(
                    recommendation[
                        "k2o_rate_kg_ha"
                    ]
                ),

            "soil_test_required":
                bool(
                    recommendation[
                        "soil_test_required"
                    ]
                ),

            "source_organization":
                recommendation[
                    "source_organization"
                ],

            "source_reference":
                recommendation[
                    "source_reference"
                ],
        },

        "explanation":
            explanation,

        "disclaimer": (
            "This recommendation combines available "
            "local soil-status evidence with published "
            "agricultural guidance. It is not a replacement "
            "for a current field soil test or advice from "
            "a qualified agricultural professional."
        ),
    }


# ============================================================
# DISPLAY RESULT
# ============================================================

def display_result(result):

    print("\n" + "=" * 70)
    print("FERTILIZER RECOMMENDATION")
    print("=" * 70)

    if not result["success"]:

        print(
            f"\nERROR: {result['message']}"
        )

        return

    # --------------------------------------------------------
    # Multiple options
    # --------------------------------------------------------

    if result.get(
        "requires_selection",
        False
    ):

        print(
            f"\n{result['message']}"
        )

        print("\nAvailable options:")

        for index, option in enumerate(
            result["options"],
            start=1
        ):

            print(
                f"\n{index}. "
                f"{option['season_condition']}"
            )

            print(
                f"   Applicability: "
                f"{option['applicability_type']}"
            )

            print(
                f"   N    : "
                f"{option['n_rate_kg_ha']} kg/ha"
            )

            print(
                f"   P2O5 : "
                f"{option['p2o5_rate_kg_ha']} kg/ha"
            )

            print(
                f"   K2O  : "
                f"{option['k2o_rate_kg_ha']} kg/ha"
            )

        return

    # --------------------------------------------------------
    # Location
    # --------------------------------------------------------

    location = result["location"]

    print(
        f"\nLocation:"
        f"\n  District : {location['district']}"
        f"\n  Block    : {location['block']}"
        f"\n  Village  : {location['village']}"
        f"\n  Year     : {location['year']}"
    )

    print(
        f"\nCrop: {result['crop']}"
    )

    # --------------------------------------------------------
    # Soil evidence
    # --------------------------------------------------------

    print("\nSOIL EVIDENCE")

    for item in result["soil_evidence"]:

        print(
            f"  {item['nutrient']}: "
            f"{item['status']} | "
            f"{item['sample_count']} samples | "
            f"{item['support_percentage']:.1f}% support | "
            f"{item['coverage']}"
        )

    # --------------------------------------------------------
    # Recommendation
    # --------------------------------------------------------

    recommendation = result[
        "recommendation"
    ]

    print(
        "\nRECOMMENDED NUTRIENT RATES"
    )

    print(
        f"  Nitrogen (N) : "
        f"{recommendation['N_kg_per_ha']} kg/ha"
    )

    print(
        f"  Phosphorus (P2O5) : "
        f"{recommendation['P2O5_kg_per_ha']} kg/ha"
    )

    print(
        f"  Potassium (K2O) : "
        f"{recommendation['K2O_kg_per_ha']} kg/ha"
    )

    print(
        f"\nCondition: "
        f"{recommendation['season_condition']}"
    )

    print(
        f"Applicability: "
        f"{recommendation['applicability_type']}"
    )

    print(
        f"Type: "
        f"{recommendation['recommendation_type']}"
    )

    print("\nSource:")

    print(
        f"  {recommendation['source_organization']}"
    )

    print(
        f"  {recommendation['source_reference']}"
    )

    # --------------------------------------------------------
    # Explanation
    # --------------------------------------------------------

    print("\nWHY?")

    for reason in result["explanation"]:

        print(f"  - {reason}")

    # --------------------------------------------------------
    # Disclaimer
    # --------------------------------------------------------

    print("\nDISCLAIMER:")

    print(
        result["disclaimer"]
    )

    print("\n" + "=" * 70)


# ============================================================
# INTERACTIVE TEST
# ============================================================

def main():

    print("=" * 70)
    print("YIELD ROI - FERTILIZER RECOMMENDER")
    print("=" * 70)

    district = input(
        "\nDistrict: "
    ).strip()

    block = input(
        "Block: "
    ).strip()

    village = input(
        "Village: "
    ).strip()

    year = input(
        "Year (example: 2024-25): "
    ).strip()

    crop = input(
        "Crop: "
    ).strip()

    season_condition = input(
        "Season/Crop condition "
        "(press Enter if unsure): "
    ).strip()

    if season_condition == "":
        season_condition = None

    result = generate_recommendation(
        district=district,
        block=block,
        village=village,
        year=year,
        crop=crop,
        season_condition=season_condition,
    )

    display_result(result)


if __name__ == "__main__":
    main()