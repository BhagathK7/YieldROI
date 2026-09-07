from pathlib import Path
import pandas as pd


# ============================================================
# YIELD ROI - FERTILIZER DATASET INSPECTION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "Main_Fertilizer.csv"


def main():
    print("=" * 70)
    print("YIELD ROI - FERTILIZER DATASET INSPECTION")
    print("=" * 70)

    print("\nLoading dataset...")
    df = pd.read_csv(DATA_FILE)

    # --------------------------------------------------------
    # Basic information
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("BASIC INFORMATION")
    print("=" * 70)

    print(f"Rows    : {len(df):,}")
    print(f"Columns : {len(df.columns)}")

    print("\nColumns:")
    for i, column in enumerate(df.columns, 1):
        print(f"{i:2}. {column}")

    # --------------------------------------------------------
    # Data types
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("DATA TYPES")
    print("=" * 70)

    print(df.dtypes.to_string())

    # --------------------------------------------------------
    # Missing values
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("MISSING VALUES")
    print("=" * 70)

    missing = df.isnull().sum()
    missing = missing[missing > 0]

    if len(missing) == 0:
        print("No missing values found.")
    else:
        print(missing.to_string())

    # --------------------------------------------------------
    # Duplicate rows
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("DUPLICATES")
    print("=" * 70)

    duplicates = df.duplicated().sum()
    print(f"Duplicate rows: {duplicates:,}")

    # --------------------------------------------------------
    # Unique values
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("UNIQUE VALUE COUNTS")
    print("=" * 70)

    for column in df.columns:
        print(f"{column:20}: {df[column].nunique(dropna=True):,}")

    # --------------------------------------------------------
    # Year information
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("YEARS")
    print("=" * 70)

    if "year" in df.columns:
        print(sorted(df["year"].dropna().unique()))

    # --------------------------------------------------------
    # District information
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("DISTRICTS")
    print("=" * 70)

    if "district_name" in df.columns:
        districts = sorted(df["district_name"].dropna().unique())

        print(f"Number of districts: {len(districts)}")
        print(", ".join(map(str, districts)))

    # --------------------------------------------------------
    # Nutrient information
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("NUTRIENT TYPES")
    print("=" * 70)

    if "nutrient_type" in df.columns:
        print(df["nutrient_type"].value_counts(dropna=False).to_string())

    print("\nNutrient names:")

    if "nutrient_name" in df.columns:
        print(
            df["nutrient_name"]
            .value_counts(dropna=False)
            .to_string()
        )

    # --------------------------------------------------------
    # Nutrient levels
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("NUTRIENT LEVELS")
    print("=" * 70)

    if "nutrient_level" in df.columns:
        print(
            df["nutrient_level"]
            .value_counts(dropna=False)
            .to_string()
        )

    # --------------------------------------------------------
    # State information
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("STATE INFORMATION")
    print("=" * 70)

    if "state_name" in df.columns:
        print(df["state_name"].value_counts(dropna=False).to_string())

    # --------------------------------------------------------
    # Sample records
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("FIRST 10 RECORDS")
    print("=" * 70)

    print(df.head(10).to_string(index=False))

    # --------------------------------------------------------
    # Numerical summary
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("NUMERICAL SUMMARY")
    print("=" * 70)

    numeric_columns = df.select_dtypes(include="number").columns

    if len(numeric_columns) > 0:
        print(
            df[numeric_columns]
            .describe()
            .transpose()
            .to_string()
        )

    # --------------------------------------------------------
    # Important combinations
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("DISTRICT + NUTRIENT COVERAGE")
    print("=" * 70)

    if "district_name" in df.columns and "nutrient_name" in df.columns:
        coverage = pd.crosstab(
            df["district_name"],
            df["nutrient_name"]
        )

        print(
            f"Districts : {coverage.shape[0]:,}\n"
            f"Nutrients : {coverage.shape[1]:,}"
        )

        print("\nCoverage preview:")
        print(coverage.head(10).to_string())

    # --------------------------------------------------------
    # Dataset validation
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)

    required_columns = [
        "year",
        "state_name",
        "district_name",
        "block_name",
        "village_name",
        "nutrient_type",
        "nutrient_name",
        "nutrient_level",
        "value",
    ]

    print("\nRequired columns:")

    for column in required_columns:
        status = "OK" if column in df.columns else "MISSING"
        print(f"{status:8} {column}")

    print("\n" + "=" * 70)
    print("INSPECTION COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()