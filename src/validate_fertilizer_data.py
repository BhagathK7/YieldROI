from pathlib import Path
import pandas as pd


# ============================================================
# YIELD ROI - FERTILIZER DATA VALIDATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_FILE = BASE_DIR / "data" / "Main_Fertilizer.csv"
CLEAN_FILE = BASE_DIR / "fertilizer" / "cleaned_soil_profiles.csv"


def main():

    print("=" * 70)
    print("YIELD ROI - FERTILIZER DATA VALIDATION")
    print("=" * 70)

    # --------------------------------------------------------
    # Load datasets
    # --------------------------------------------------------
    print("\nLoading datasets...")

    raw = pd.read_csv(RAW_FILE)
    clean = pd.read_csv(CLEAN_FILE)

    print(f"Raw dataset    : {len(raw):,} rows")
    print(f"Clean dataset  : {len(clean):,} profiles")

    # --------------------------------------------------------
    # Raw dataset validation
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("RAW DATASET VALIDATION")
    print("=" * 70)

    print("\nStates:")
    print(raw["state_name"].value_counts().to_string())

    print("\nYears:")
    print(raw["year"].value_counts().sort_index().to_string())

    print("\nDistricts:")
    print(f"Unique districts: {raw['district_name'].nunique()}")

    print("\nBlocks:")
    print(f"Unique blocks: {raw['block_name'].nunique()}")

    print("\nVillages:")
    print(f"Unique villages: {raw['village_name'].nunique()}")

    # --------------------------------------------------------
    # Check nutrient categories
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("NUTRIENT CATEGORY CHECK")
    print("=" * 70)

    nutrient_levels = (
        raw.groupby("nutrient_name")["nutrient_level"]
        .unique()
    )

    for nutrient, levels in nutrient_levels.items():
        print(f"\n{nutrient}:")
        print(", ".join(sorted(map(str, levels))))

    # --------------------------------------------------------
    # Count consistency
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("CATEGORY COUNT CONSISTENCY")
    print("=" * 70)

    # For every nutrient/location/year combination,
    # calculate the total number of observations represented
    grouped = (
        raw.groupby(
            [
                "year",
                "district_name",
                "block_name",
                "village_name",
                "nutrient_name",
            ],
            dropna=False
        )["value"]
        .sum()
        .reset_index(name="total_count")
    )

    print("\nTotal-count statistics:")
    print(
        grouped["total_count"]
        .describe()
        .to_string()
    )

    print("\nMost common total counts:")
    print(
        grouped["total_count"]
        .value_counts()
        .head(15)
        .to_string()
    )

    # --------------------------------------------------------
    # Check whether different nutrient categories
    # represent the same sample population
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("SAMPLE COUNT COMPARISON")
    print("=" * 70)

    count_table = raw.pivot_table(
        index=[
            "year",
            "district_name",
            "block_name",
            "village_name",
        ],
        columns="nutrient_name",
        values="value",
        aggfunc="sum",
        fill_value=0,
    )

    nutrient_totals = count_table.sum(axis=1)

    print(
        f"\nLocation-year combinations: "
        f"{len(count_table):,}"
    )

    print("\nNumber of locations where nutrient totals differ:")

    nutrients = list(count_table.columns)

    if len(nutrients) > 1:

        reference = count_table[nutrients[0]]

        for nutrient in nutrients[1:]:

            different = (
                count_table[nutrient] != reference
            ).sum()

            print(
                f"{nutrients[0]} vs {nutrient}: "
                f"{different:,}"
            )

    # --------------------------------------------------------
    # Validate cleaned profiles
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("CLEANED PROFILE VALIDATION")
    print("=" * 70)

    location_columns = [
        "year",
        "district_name",
        "district_code",
        "block_name",
        "block_code",
        "village_name",
        "village_code",
    ]

    duplicates = clean.duplicated(
        subset=location_columns
    ).sum()

    print(f"\nDuplicate profiles: {duplicates:,}")

    missing = clean.isnull().sum().sum()

    print(f"Missing values: {missing:,}")

    print(
        f"Districts: "
        f"{clean['district_name'].nunique():,}"
    )

    print(
        f"Blocks: "
        f"{clean['block_name'].nunique():,}"
    )

    print(
        f"Villages: "
        f"{clean['village_name'].nunique():,}"
    )

    # --------------------------------------------------------
    # Check status columns
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("DOMINANT STATUS VALIDATION")
    print("=" * 70)

    status_columns = [
        column
        for column in clean.columns
        if column.endswith("_status")
    ]

    for column in status_columns:

        unknown = (
            clean[column]
            .astype(str)
            .str.lower()
            == "unknown"
        ).sum()

        print(
            f"{column:40} "
            f"Unknown: {unknown:,}"
        )

    # --------------------------------------------------------
    # Nitrogen investigation
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("NITROGEN INVESTIGATION")
    print("=" * 70)

    nitrogen = clean["nitrogen_status"].value_counts()

    print(nitrogen.to_string())

    nitrogen_percentage = (
        nitrogen
        / len(clean)
        * 100
    )

    print("\nPercentages:")

    for status, percentage in nitrogen_percentage.items():
        print(
            f"{status:10}: "
            f"{percentage:.2f}%"
        )

    # --------------------------------------------------------
    # Check original count representation
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("EXAMPLE VILLAGE ANALYSIS")
    print("=" * 70)

    sample = raw[
        (raw["district_name"] == "Ariyalur")
    ].head(30)

    if len(sample) > 0:
        print(
            sample[
                [
                    "year",
                    "district_name",
                    "block_name",
                    "village_name",
                    "nutrient_name",
                    "nutrient_level",
                    "value",
                ]
            ].to_string(index=False)
        )

    # --------------------------------------------------------
    # Final conclusion
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("VALIDATION COMPLETED")
    print("=" * 70)

    print(
        "\nIMPORTANT:"
        "\nThe 'value' column is being treated as a category count."
        "\nIt is NOT being interpreted as a direct nutrient concentration."
    )

    print(
        "\nThe cleaned dataset is therefore a "
        "village-level soil-status dataset."
    )

    print(
        "\nWe will NOT train a fertilizer model until "
        "the relationship between soil status and fertilizer "
        "recommendations is established correctly."
    )

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()