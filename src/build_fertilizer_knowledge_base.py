from pathlib import Path
import pandas as pd


# ============================================================
# YIELD ROI - FERTILIZER KNOWLEDGE BASE
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

OUTPUT_FILE = (
    BASE_DIR
    / "fertilizer"
    / "fertilizer_knowledge_base.csv"
)


# ============================================================
# SOURCE REFERENCES
# ============================================================

TNAU_RICE_SOURCE = (
    "TNAU Rice Nutrient Management"
)

TNAU_SUGARCANE_SOURCE = (
    "TNAU Sugarcane Nutrient Management"
)

TNAU_RAGI_SOURCE = (
    "TNAU Ragi Nutrient Management"
)


# ============================================================
# CAUVERY DELTA BLOCKS
#
# These are specifically identified in the Tamil Nadu
# Agriculture dashboard.
#
# We intentionally use BLOCK-level applicability instead
# of assuming the entire district belongs to the delta.
# ============================================================

CAUVERY_DELTA_BLOCKS = {
    "Cuddalore": [
        "Kattumannarkoil",
        "Melbhuvanagiri",
        "Keerapalayam",
        "Parangipettai",
        "Kumaratchi",
    ],

    "Trichy": [
        "Lalgudi",
        "Manachanallur",
        "Pullambadi",
        "Andanallur",
        "Thiruverambur",
        "Musiri",
    ],

    "Karur": [
        "Kulithalai",
        "Krishnarayapuram",
        "Karur",
        "Thogamalai",
    ],

    "Ariyalur": [
        "Tirumanur",
        "T.Palur",
        "Jeyamkondam",
    ],

    "Pudukottai": [
        "Aranthangi",
        "Avudaiyarkoil",
        "Manamelkudi",
        "Tiruvvarangulam",
        "Gandarvakottai",
        "Karambakudi",
    ],

    "Thanjavur": [
        "Thanjavur",
        "Tiruvaiyaru",
        "Papanasam",
        "Kumbakonam",
        "Orathanadu",
        "Madukkur",
        "Pattukkottai",
        "Peravurani",
        "Tiruvidamaruthur",
        "Budalur",
        "Ammapettai",
        "Sethubavachatram",
        "Thirupanandal",
    ],

    "Nagapattinam": [
        "Nagapattinam",
        "Tirumangai",
        "Kilvelur",
        "Keelaiyur",
        "Vedaranayam",
        "Thalainyiru",
    ],

    "Mayiladuthurai": [
        "Mayiladuthurai",
        "Kuthalam",
        "Sirkali",
        "Kollidam",
        "Sembanarkoil",
    ],

    "Thiruvarur": [
        "Thiruvarur",
        "Thiruthuraipoondi",
        "Muthupettai",
        "Mannarkudi",
        "Kothur",
        "Nanilam",
        "Needamangalam",
        "Kodavasal",
        "Koradacheri",
        "Valangaiman",
    ],
}


# ============================================================
# HELPER
# ============================================================

def make_blocks(districts):

    return ";".join(
        [
            block
            for district in districts
            for block in CAUVERY_DELTA_BLOCKS.get(
                district,
                []
            )
        ]
    )


# ============================================================
# RECOMMENDATIONS
# ============================================================

RECOMMENDATIONS = [

    # ========================================================
    # RICE - SHORT DURATION / DRY SEASON
    # ========================================================

    {
        "crop": "Rice",
        "crop_group": "Cereal",
        "season_condition": "Short Duration / Dry Season",
        "recommendation_type": "Blanket",
        "applicability_type": "Cauvery Delta / Coimbatore",
        "applicable_districts": (
            "Cauvery Delta blocks + Coimbatore"
        ),
        "applicable_blocks": make_blocks(
            list(CAUVERY_DELTA_BLOCKS.keys())
        ),
        "n_rate_kg_ha": 150,
        "p2o5_rate_kg_ha": 50,
        "k2o_rate_kg_ha": 50,
        "soil_test_required": True,
        "source_organization": (
            "Tamil Nadu Agricultural University"
        ),
        "source_reference": TNAU_RICE_SOURCE,
    },

    {
        "crop": "Rice",
        "crop_group": "Cereal",
        "season_condition": "Short Duration / Dry Season",
        "recommendation_type": "Blanket",
        "applicability_type": "Other Tracts",
        "applicable_districts": "Other Tamil Nadu areas",
        "applicable_blocks": "",
        "n_rate_kg_ha": 120,
        "p2o5_rate_kg_ha": 40,
        "k2o_rate_kg_ha": 40,
        "soil_test_required": True,
        "source_organization": (
            "Tamil Nadu Agricultural University"
        ),
        "source_reference": TNAU_RICE_SOURCE,
    },


    # ========================================================
    # RICE - WET SEASON
    # ========================================================

    {
        "crop": "Rice",
        "crop_group": "Cereal",
        "season_condition": "Medium / Long Duration / Wet Season",
        "recommendation_type": "Blanket",
        "applicability_type": "Tamil Nadu",
        "applicable_districts": "Tamil Nadu",
        "applicable_blocks": "",
        "n_rate_kg_ha": 150,
        "p2o5_rate_kg_ha": 50,
        "k2o_rate_kg_ha": 50,
        "soil_test_required": True,
        "source_organization": (
            "Tamil Nadu Agricultural University"
        ),
        "source_reference": TNAU_RICE_SOURCE,
    },


    # ========================================================
    # RICE - HYBRID
    # ========================================================

    {
        "crop": "Rice",
        "crop_group": "Cereal",
        "season_condition": "Hybrid Rice",
        "recommendation_type": "Blanket",
        "applicability_type": "Tamil Nadu",
        "applicable_districts": "Tamil Nadu",
        "applicable_blocks": "",
        "n_rate_kg_ha": 175,
        "p2o5_rate_kg_ha": 60,
        "k2o_rate_kg_ha": 60,
        "soil_test_required": True,
        "source_organization": (
            "Tamil Nadu Agricultural University"
        ),
        "source_reference": TNAU_RICE_SOURCE,
    },


    # ========================================================
    # RICE - IMPROVED WHITE PONNI
    # ========================================================

    {
        "crop": "Rice",
        "crop_group": "Cereal",
        "season_condition": "Improved White Ponni",
        "recommendation_type": "Blanket",
        "applicability_type": "Tamil Nadu",
        "applicable_districts": "Tamil Nadu",
        "applicable_blocks": "",
        "n_rate_kg_ha": 75,
        "p2o5_rate_kg_ha": 50,
        "k2o_rate_kg_ha": 50,
        "soil_test_required": True,
        "source_organization": (
            "Tamil Nadu Agricultural University"
        ),
        "source_reference": TNAU_RICE_SOURCE,
    },


    # ========================================================
    # SUGARCANE
    # ========================================================

    {
        "crop": "Sugarcane",
        "crop_group": "Commercial Crop",
        "season_condition": "Plant Crop",
        "recommendation_type": "General",
        "applicability_type": "Tamil Nadu",
        "applicable_districts": "Tamil Nadu",
        "applicable_blocks": "",
        "n_rate_kg_ha": 275,
        "p2o5_rate_kg_ha": 62.5,
        "k2o_rate_kg_ha": 112.5,
        "soil_test_required": True,
        "source_organization": (
            "Tamil Nadu Agricultural University"
        ),
        "source_reference": TNAU_SUGARCANE_SOURCE,
    },

    {
        "crop": "Sugarcane",
        "crop_group": "Commercial Crop",
        "season_condition": "Ratoon Crop",
        "recommendation_type": "General",
        "applicability_type": "Tamil Nadu",
        "applicable_districts": "Tamil Nadu",
        "applicable_blocks": "",
        "n_rate_kg_ha": 343.5,
        "p2o5_rate_kg_ha": 62.5,
        "k2o_rate_kg_ha": 112.5,
        "soil_test_required": True,
        "source_organization": (
            "Tamil Nadu Agricultural University"
        ),
        "source_reference": TNAU_SUGARCANE_SOURCE,
    },

    {
        "crop": "Sugarcane",
        "crop_group": "Commercial Crop",
        "season_condition": "Jaggery",
        "recommendation_type": "General",
        "applicability_type": "Tamil Nadu",
        "applicable_districts": "Tamil Nadu",
        "applicable_blocks": "",
        "n_rate_kg_ha": 225,
        "p2o5_rate_kg_ha": 62.5,
        "k2o_rate_kg_ha": 112.5,
        "soil_test_required": True,
        "source_organization": (
            "Tamil Nadu Agricultural University"
        ),
        "source_reference": TNAU_SUGARCANE_SOURCE,
    },


    # ========================================================
    # RAGI
    # ========================================================

    {
        "crop": "Ragi",
        "crop_group": "Millet",
        "season_condition": "Rainfed Early Direct Sown",
        "recommendation_type": "General",
        "applicability_type": "Tamil Nadu",
        "applicable_districts": "Tamil Nadu",
        "applicable_blocks": "",
        "n_rate_kg_ha": 40,
        "p2o5_rate_kg_ha": 30,
        "k2o_rate_kg_ha": 20,
        "soil_test_required": True,
        "source_organization": (
            "Tamil Nadu Agricultural University"
        ),
        "source_reference": TNAU_RAGI_SOURCE,
    },

    {
        "crop": "Ragi",
        "crop_group": "Millet",
        "season_condition": "Rainfed Early Transplanted",
        "recommendation_type": "General",
        "applicability_type": "Tamil Nadu",
        "applicable_districts": "Tamil Nadu",
        "applicable_blocks": "",
        "n_rate_kg_ha": 50,
        "p2o5_rate_kg_ha": 40,
        "k2o_rate_kg_ha": 25,
        "soil_test_required": True,
        "source_organization": (
            "Tamil Nadu Agricultural University"
        ),
        "source_reference": TNAU_RAGI_SOURCE,
    },

    {
        "crop": "Ragi",
        "crop_group": "Millet",
        "season_condition": "Rainfed Medium",
        "recommendation_type": "General",
        "applicability_type": "Tamil Nadu",
        "applicable_districts": "Tamil Nadu",
        "applicable_blocks": "",
        "n_rate_kg_ha": 50,
        "p2o5_rate_kg_ha": 40,
        "k2o_rate_kg_ha": 25,
        "soil_test_required": True,
        "source_organization": (
            "Tamil Nadu Agricultural University"
        ),
        "source_reference": TNAU_RAGI_SOURCE,
    },

    {
        "crop": "Ragi",
        "crop_group": "Millet",
        "season_condition": (
            "Irrigated Early / Medium Transplanted"
        ),
        "recommendation_type": "General",
        "applicability_type": "Tamil Nadu",
        "applicable_districts": "Tamil Nadu",
        "applicable_blocks": "",
        "n_rate_kg_ha": 60,
        "p2o5_rate_kg_ha": 40,
        "k2o_rate_kg_ha": 30,
        "soil_test_required": True,
        "source_organization": (
            "Tamil Nadu Agricultural University"
        ),
        "source_reference": TNAU_RAGI_SOURCE,
    },
]


# ============================================================
# VALIDATION
# ============================================================

def validate_knowledge_base(df):

    required_columns = [
        "crop",
        "crop_group",
        "season_condition",
        "recommendation_type",
        "applicability_type",
        "applicable_districts",
        "applicable_blocks",
        "n_rate_kg_ha",
        "p2o5_rate_kg_ha",
        "k2o_rate_kg_ha",
        "soil_test_required",
        "source_organization",
        "source_reference",
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing columns: {missing}"
        )

    nutrient_columns = [
        "n_rate_kg_ha",
        "p2o5_rate_kg_ha",
        "k2o_rate_kg_ha",
    ]

    for column in nutrient_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        if df[column].isna().any():
            raise ValueError(
                f"Invalid numeric values in {column}"
            )

        if (df[column] < 0).any():
            raise ValueError(
                f"Negative values in {column}"
            )

    # Check source fields
    for column in [
        "source_organization",
        "source_reference",
    ]:

        if (
            df[column]
            .astype(str)
            .str.strip()
            .eq("")
            .any()
        ):
            raise ValueError(
                f"Empty source information in {column}"
            )

    return df


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("YIELD ROI - FERTILIZER KNOWLEDGE BASE")
    print("=" * 70)

    df = pd.DataFrame(
        RECOMMENDATIONS
    )

    print(
        f"\nRecommendations created: "
        f"{len(df)}"
    )

    df = validate_knowledge_base(df)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\n" + "=" * 70)
    print("KNOWLEDGE BASE SUMMARY")
    print("=" * 70)

    print(
        f"\nUnique crops: "
        f"{df['crop'].nunique()}"
    )

    print(
        f"Total recommendations: "
        f"{len(df)}"
    )

    print("\nCrops:")

    for crop in sorted(
        df["crop"].unique()
    ):
        print(f"  - {crop}")

    print("\nApplicability types:")

    print(
        df["applicability_type"]
        .value_counts()
        .to_string()
    )

    print("\nNutrient units:")

    print("  N    : kg N/ha")
    print("  P2O5 : kg P2O5/ha")
    print("  K2O  : kg K2O/ha")

    print("\nSource organization:")

    print(
        df["source_organization"]
        .value_counts()
        .to_string()
    )

    print("\nSaved to:")

    print(OUTPUT_FILE)

    print("\n" + "=" * 70)
    print("KNOWLEDGE BASE CREATED SUCCESSFULLY")
    print("=" * 70)

    print(
        "\nImportant:"
        "\nDistrict/block applicability is now stored "
        "explicitly."
        "\nThe system will no longer assume that an "
        "entire district belongs to the Cauvery Delta."
    )


if __name__ == "__main__":
    main()