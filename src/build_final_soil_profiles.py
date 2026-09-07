from pathlib import Path
import pandas as pd


# ============================================================
# YIELD ROI - BUILD FINAL SOIL PROFILES
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_FILE = BASE_DIR / "data" / "Main_Fertilizer.csv"
OUTPUT_FILE = BASE_DIR / "fertilizer" / "final_soil_profiles.csv"


# ------------------------------------------------------------
# Nutrient category definitions
# ------------------------------------------------------------

CATEGORY_MAP = {
    "Nitrogen": ["Low", "Medium", "High"],
    "Phosphorus": ["Low", "Medium", "High"],
    "Potassium": ["Low", "Medium", "High"],
    "Organic Carbon": ["Low", "Medium", "High"],
    "Soil Ph": ["Acidic", "Neutral", "Alkaline"],
    "Electrical Conductivity": ["Non Saline", "Saline"],
    "Zinc": ["Deficient", "Sufficient"],
    "Boron": ["Deficient", "Sufficient"],
    "Manganese": ["Deficient", "Sufficient"],
    "Sulphur": ["Deficient", "Sufficient"],
    "Copper": ["Deficient", "Sufficient"],
    "Iron": ["Deficient", "Sufficient"],
}


LOCATION_COLUMNS = [
    "year",
    "district_name",
    "district_code",
    "block_name",
    "block_code",
    "village_name",
    "village_code",
]


def get_dominant_status(row, categories):
    """
    Return the category with the highest sample count.

    If every category has zero samples, return Unknown.
    If there is a tie, return the tied categories joined by '|'.
    """

    values = {
        category: row.get(
            f"{row['nutrient_name']}_{category}",
            0
        )
        for category in categories
    }

    maximum = max(values.values())

    if maximum == 0:
        return "Unknown"

    winners = [
        category
        for category, value in values.items()
        if value == maximum
    ]

    return "|".join(winners)


def coverage_level(count):
    """
    Describe the amount of sample information available.

    This is NOT a soil fertility score.
    """

    if count == 0:
        return "No Data"

    if count <= 2:
        return "Very Low"

    if count <= 5:
        return "Low"

    if count <= 10:
        return "Moderate"

    if count <= 25:
        return "Good"

    return "High"


def main():

    print("=" * 70)
    print("YIELD ROI - BUILD FINAL SOIL PROFILES")
    print("=" * 70)

    # --------------------------------------------------------
    # Load raw dataset
    # --------------------------------------------------------

    print("\nLoading raw soil-health dataset...")

    df = pd.read_csv(RAW_FILE)

    print(f"Rows loaded: {len(df):,}")

    # --------------------------------------------------------
    # Clean text fields
    # --------------------------------------------------------

    text_columns = [
        "state_name",
        "district_name",
        "block_name",
        "village_name",
        "nutrient_type",
        "nutrient_name",
        "nutrient_level",
    ]

    for column in text_columns:
        df[column] = (
            df[column]
            .astype(str)
            .str.strip()
        )

    # --------------------------------------------------------
    # Keep Tamil Nadu
    # --------------------------------------------------------

    df = df[
        df["state_name"].str.lower() == "tamil nadu"
    ].copy()

    # --------------------------------------------------------
    # Ensure numeric values
    # --------------------------------------------------------

    df["value"] = pd.to_numeric(
        df["value"],
        errors="coerce"
    ).fillna(0)

    # --------------------------------------------------------
    # Create profile
    # --------------------------------------------------------

    print("\nCreating village-year soil profiles...")

    profiles = (
        df[LOCATION_COLUMNS]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    print(
        f"Unique village-year profiles: "
        f"{len(profiles):,}"
    )

    # --------------------------------------------------------
    # Process every nutrient separately
    # --------------------------------------------------------

    for nutrient, categories in CATEGORY_MAP.items():

        print(f"\nProcessing: {nutrient}")

        nutrient_df = df[
            df["nutrient_name"] == nutrient
        ].copy()

        if nutrient_df.empty:
            print("  WARNING: No records found.")
            continue

        # Pivot category counts
        pivot = nutrient_df.pivot_table(
            index=LOCATION_COLUMNS,
            columns="nutrient_level",
            values="value",
            aggfunc="sum",
            fill_value=0,
        ).reset_index()

        # Rename category columns
        rename_columns = {}

        for category in categories:

            if category in pivot.columns:
                rename_columns[
                    category
                ] = f"{nutrient}_{category}"

            else:
                pivot[
                    f"{nutrient}_{category}"
                ] = 0

        pivot = pivot.rename(
            columns=rename_columns
        )

        # Keep only required columns
        required_columns = (
            LOCATION_COLUMNS
            + [
                f"{nutrient}_{category}"
                for category in categories
            ]
        )

        pivot = pivot[required_columns]

        # Merge into master profile
        profiles = profiles.merge(
            pivot,
            on=LOCATION_COLUMNS,
            how="left",
        )

    # --------------------------------------------------------
    # Replace missing category counts with zero
    # --------------------------------------------------------

    count_columns = [
        column
        for column in profiles.columns
        if any(
            column == f"{nutrient}_{category}"
            for nutrient, categories
            in CATEGORY_MAP.items()
            for category in categories
        )
    ]

    profiles[count_columns] = (
        profiles[count_columns]
        .fillna(0)
        .astype(int)
    )

    # --------------------------------------------------------
    # Add status, sample count and coverage
    # --------------------------------------------------------

    print("\nCalculating soil status and evidence...")

    for nutrient, categories in CATEGORY_MAP.items():

        category_columns = [
            f"{nutrient}_{category}"
            for category in categories
        ]

        # Total number of samples represented
        profiles[
            f"{nutrient}_sample_count"
        ] = profiles[
            category_columns
        ].sum(axis=1)

        # Dominant category
        def determine_status(row):
            values = row[category_columns]

            maximum = values.max()

            if maximum == 0:
                return "Unknown"

            winners = [
                categories[index]
                for index, value in enumerate(values)
                if value == maximum
            ]

            return "|".join(winners)

        profiles[
            f"{nutrient}_status"
        ] = profiles.apply(
            determine_status,
            axis=1
        )

        # Coverage level
        profiles[
            f"{nutrient}_coverage"
        ] = profiles[
            f"{nutrient}_sample_count"
        ].apply(coverage_level)

        # Percentage of samples supporting dominant status
        def calculate_confidence(row):

            total = row[
                f"{nutrient}_sample_count"
            ]

            if total == 0:
                return 0.0

            maximum = row[
                category_columns
            ].max()

            return (
                maximum
                / total
                * 100
            )

        profiles[
            f"{nutrient}_status_support_pct"
        ] = profiles.apply(
            calculate_confidence,
            axis=1
        ).round(2)

    # --------------------------------------------------------
    # Overall profile coverage
    # --------------------------------------------------------

    status_columns = [
        f"{nutrient}_status"
        for nutrient in CATEGORY_MAP
    ]

    profiles["nutrients_available"] = (
        profiles[status_columns]
        .apply(
            lambda row: sum(
                value != "Unknown"
                for value in row
            ),
            axis=1
        )
    )

    profiles["overall_coverage_pct"] = (
        profiles["nutrients_available"]
        / len(CATEGORY_MAP)
        * 100
    ).round(2)

    # --------------------------------------------------------
    # Overall evidence level
    # --------------------------------------------------------

    def overall_evidence(row):

        percentage = row[
            "overall_coverage_pct"
        ]

        if percentage >= 90:
            return "High"

        if percentage >= 75:
            return "Good"

        if percentage >= 50:
            return "Moderate"

        if percentage > 0:
            return "Low"

        return "No Data"

    profiles["overall_evidence_level"] = (
        profiles.apply(
            overall_evidence,
            axis=1
        )
    )

    # --------------------------------------------------------
    # Reorder columns
    # --------------------------------------------------------

    ordered_columns = LOCATION_COLUMNS

    for nutrient, categories in CATEGORY_MAP.items():

        ordered_columns += [
            f"{nutrient}_{category}"
            for category in categories
        ]

        ordered_columns += [
            f"{nutrient}_sample_count",
            f"{nutrient}_status",
            f"{nutrient}_coverage",
            f"{nutrient}_status_support_pct",
        ]

    ordered_columns += [
        "nutrients_available",
        "overall_coverage_pct",
        "overall_evidence_level",
    ]

    profiles = profiles[
        ordered_columns
    ]

    # --------------------------------------------------------
    # Final validation
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("FINAL PROFILE VALIDATION")
    print("=" * 70)

    print(
        f"\nProfiles: "
        f"{len(profiles):,}"
    )

    print(
        f"Columns: "
        f"{len(profiles.columns):,}"
    )

    print(
        f"Districts: "
        f"{profiles['district_name'].nunique():,}"
    )

    print(
        f"Blocks: "
        f"{profiles['block_name'].nunique():,}"
    )

    print(
        f"Villages: "
        f"{profiles['village_name'].nunique():,}"
    )

    print("\nOverall evidence level:")

    print(
        profiles[
            "overall_evidence_level"
        ]
        .value_counts()
        .to_string()
    )

    # --------------------------------------------------------
    # Show important soil status distributions
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("SOIL STATUS DISTRIBUTIONS")
    print("=" * 70)

    for nutrient in [
        "Nitrogen",
        "Phosphorus",
        "Potassium",
        "Organic Carbon",
        "Soil Ph",
        "Electrical Conductivity",
        "Zinc",
        "Boron",
        "Iron",
    ]:

        column = f"{nutrient}_status"

        print(f"\n{nutrient}:")

        print(
            profiles[column]
            .value_counts()
            .to_string()
        )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    profiles.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\n" + "=" * 70)
    print("FINAL SOIL PROFILE CREATED")
    print("=" * 70)

    print(
        f"\nSaved to:\n{OUTPUT_FILE}"
    )

    print(
        "\nThe original Main_Fertilizer.csv "
        "has NOT been modified."
    )

    print(
        "\nThe new dataset preserves:"
        "\n- Soil category counts"
        "\n- Dominant soil status"
        "\n- Sample count"
        "\n- Status support percentage"
        "\n- Coverage level"
        "\n- Overall evidence level"
    )

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()