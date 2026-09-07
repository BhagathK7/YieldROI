from pathlib import Path
import pandas as pd


# ============================================================
# YIELD ROI - FERTILIZER DATA PREPARATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "Main_Fertilizer.csv"
OUTPUT_FILE = BASE_DIR / "fertilizer" / "cleaned_soil_profiles.csv"


def main():

    print("=" * 70)
    print("YIELD ROI - FERTILIZER DATA PREPARATION")
    print("=" * 70)

    # --------------------------------------------------------
    # Load dataset
    # --------------------------------------------------------
    print("\nLoading original dataset...")

    df = pd.read_csv(INPUT_FILE)

    print(f"Original rows: {len(df):,}")

    # --------------------------------------------------------
    # Keep only Tamil Nadu
    # --------------------------------------------------------
    df = df[
        df["state_name"]
        .astype(str)
        .str.strip()
        .str.lower()
        == "tamil nadu"
    ].copy()

    print(f"Tamil Nadu rows: {len(df):,}")

    # --------------------------------------------------------
    # Clean text columns
    # --------------------------------------------------------
    text_columns = [
        "year",
        "state_name",
        "district_name",
        "block_name",
        "village_name",
        "nutrient_type",
        "nutrient_name",
        "nutrient_level",
    ]

    for column in text_columns:
        df[column] = df[column].astype(str).str.strip()

    # --------------------------------------------------------
    # Convert value to numeric
    # --------------------------------------------------------
    df["value"] = pd.to_numeric(
        df["value"],
        errors="coerce"
    )

    # Remove invalid values
    df = df.dropna(subset=["value"]).copy()

    # --------------------------------------------------------
    # Create a unique location identifier
    # --------------------------------------------------------
    location_columns = [
        "year",
        "district_name",
        "district_code",
        "block_name",
        "block_code",
        "village_name",
        "village_code",
    ]

    print("\nCreating village-level soil profiles...")

    # --------------------------------------------------------
    # Convert nutrient + level into columns
    #
    # Example:
    #
    # Nitrogen + Low    -> nitrogen_low
    # Nitrogen + Medium -> nitrogen_medium
    # Nitrogen + High   -> nitrogen_high
    #
    # Soil Ph + Acidic  -> soil_ph_acidic
    # --------------------------------------------------------

    df["nutrient_column"] = (
        df["nutrient_name"]
        .str.lower()
        .str.replace(" ", "_", regex=False)
    )

    df["level_column"] = (
        df["nutrient_level"]
        .str.lower()
        .str.replace(" ", "_", regex=False)
    )

    df["profile_column"] = (
        df["nutrient_column"]
        + "_"
        + df["level_column"]
    )

    # --------------------------------------------------------
    # Pivot
    # --------------------------------------------------------
    profiles = df.pivot_table(
        index=location_columns,
        columns="profile_column",
        values="value",
        aggfunc="sum",
        fill_value=0,
    ).reset_index()

    # Remove pivot index name
    profiles.columns.name = None

    # --------------------------------------------------------
    # Add useful total/sample count columns
    # --------------------------------------------------------
    nutrient_names = [
        "nitrogen",
        "phosphorus",
        "potassium",
        "organic_carbon",
        "electrical_conductivity",
        "soil_ph",
        "zinc",
        "boron",
        "manganese",
        "sulphur",
        "copper",
        "iron",
    ]

    # --------------------------------------------------------
    # Create dominant soil status
    # --------------------------------------------------------
    status_groups = {
        "nitrogen": ["low", "medium", "high"],
        "phosphorus": ["low", "medium", "high"],
        "potassium": ["low", "medium", "high"],
        "organic_carbon": ["low", "medium", "high"],
        "electrical_conductivity": ["non_saline", "saline"],
        "soil_ph": ["acidic", "neutral", "alkaline"],
        "zinc": ["deficient", "sufficient"],
        "boron": ["deficient", "sufficient"],
        "manganese": ["deficient", "sufficient"],
        "sulphur": ["deficient", "sufficient"],
        "copper": ["deficient", "sufficient"],
        "iron": ["deficient", "sufficient"],
    }

    print("\nCalculating dominant nutrient status...")

    for nutrient, levels in status_groups.items():

        available_columns = [
            f"{nutrient}_{level}"
            for level in levels
            if f"{nutrient}_{level}" in profiles.columns
        ]

        if not available_columns:
            continue

        status_column = f"{nutrient}_status"

        def get_status(row):
            values = {
                column: row[column]
                for column in available_columns
            }

            # If every category is zero, status is unknown
            if sum(values.values()) == 0:
                return "Unknown"

            best_column = max(
                values,
                key=values.get
            )

            return best_column.replace(
                f"{nutrient}_",
                ""
            ).replace("_", " ").title()

        profiles[status_column] = profiles.apply(
            get_status,
            axis=1
        )

    # --------------------------------------------------------
    # Order columns
    # --------------------------------------------------------
    first_columns = [
        "year",
        "district_name",
        "district_code",
        "block_name",
        "block_code",
        "village_name",
        "village_code",
    ]

    status_columns = [
        column
        for column in profiles.columns
        if column.endswith("_status")
    ]

    profile_columns = [
        column
        for column in profiles.columns
        if column not in first_columns
        and column not in status_columns
    ]

    profiles = profiles[
        first_columns
        + status_columns
        + profile_columns
    ]

    # --------------------------------------------------------
    # Sort data
    # --------------------------------------------------------
    profiles = profiles.sort_values(
        by=[
            "year",
            "district_name",
            "block_name",
            "village_name",
        ]
    ).reset_index(drop=True)

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("VALIDATION")
    print("=" * 70)

    print(f"Profiles created : {len(profiles):,}")
    print(f"Columns created  : {len(profiles.columns)}")

    print(
        f"Districts        : "
        f"{profiles['district_name'].nunique():,}"
    )

    print(
        f"Blocks           : "
        f"{profiles['block_name'].nunique():,}"
    )

    print(
        f"Villages         : "
        f"{profiles['village_name'].nunique():,}"
    )

    print(
        f"Years            : "
        f"{profiles['year'].nunique():,}"
    )

    print("\nYears:")
    print(
        sorted(
            profiles["year"].unique()
        )
    )

    # --------------------------------------------------------
    # Missing values
    # --------------------------------------------------------
    print("\nMissing values:")

    missing = profiles.isnull().sum()
    missing = missing[missing > 0]

    if len(missing) == 0:
        print("No missing values.")
    else:
        print(missing.to_string())

    # --------------------------------------------------------
    # Duplicate profiles
    # --------------------------------------------------------
    duplicate_profiles = profiles.duplicated(
        subset=location_columns
    ).sum()

    print(
        f"\nDuplicate location profiles: "
        f"{duplicate_profiles:,}"
    )

    # --------------------------------------------------------
    # Show status distribution
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("SOIL STATUS SUMMARY")
    print("=" * 70)

    for column in status_columns:

        print(f"\n{column}:")

        print(
            profiles[column]
            .value_counts(dropna=False)
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
    print("FILE CREATED")
    print("=" * 70)

    print(f"\nOutput:")
    print(OUTPUT_FILE)

    print("\nFirst 5 profiles:")
    print(
        profiles.head(5).to_string(
            index=False
        )
    )

    print("\n" + "=" * 70)
    print("FERTILIZER DATA PREPARATION COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()