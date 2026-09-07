"""
YieldROI - Official Benchmark Validation

Validates the extracted 2024-25 official yield benchmark dataset
before connecting it to the prediction pipeline.

This script DOES NOT modify either dataset.
"""

from pathlib import Path
import pandas as pd


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

BENCHMARK_FILE = (
    ROOT / "data" / "official_yield_benchmarks.csv"
)

HISTORICAL_FILE = (
    ROOT / "data" / "tamil_nadu_yield_cleaned.csv"
)


# ============================================================
# HELPERS
# ============================================================

def normalize(text):
    """Normalize text for comparison."""

    return (
        str(text)
        .strip()
        .lower()
        .replace("&", "and")
        .replace("-", " ")
        .replace("_", " ")
        .replace("(", "")
        .replace(")", "")
    )


def show_crop_values(df, district, crop):
    """Display all benchmark entries for a district/crop."""

    result = df[
        (df["district"].str.lower() == district.lower())
        &
        (df["crop"].str.lower() == crop.lower())
    ].copy()

    if result.empty:
        print(
            f"  {district} / {crop}: NOT FOUND"
        )
        return

    print(
        f"\n  {district} / {crop}:"
    )

    print(
        result[
            [
                "district",
                "crop",
                "season",
                "yield",
                "unit",
                "year",
                "source_page",
            ]
        ].to_string(index=False)
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("YieldROI - Official Benchmark Validation")
    print("=" * 70)

    # --------------------------------------------------------
    # Check files
    # --------------------------------------------------------

    if not BENCHMARK_FILE.exists():

        print()
        print("ERROR: Benchmark file not found:")
        print(BENCHMARK_FILE)
        return

    if not HISTORICAL_FILE.exists():

        print()
        print("ERROR: Historical dataset not found:")
        print(HISTORICAL_FILE)
        return

    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    benchmark = pd.read_csv(
        BENCHMARK_FILE
    )

    historical = pd.read_csv(
        HISTORICAL_FILE
    )

    print()
    print("Files loaded successfully.")

    # --------------------------------------------------------
    # Basic benchmark validation
    # --------------------------------------------------------

    print()
    print("-" * 70)
    print("1. BENCHMARK DATASET")
    print("-" * 70)

    print(
        f"Rows       : {len(benchmark):,}"
    )

    print(
        f"Districts  : {benchmark['district'].nunique()}"
    )

    print(
        f"Crops      : {benchmark['crop'].nunique()}"
    )

    print(
        f"Seasons    : {benchmark['season'].nunique()}"
    )

    print(
        f"Years      : {benchmark['year'].unique().tolist()}"
    )

    print()
    print("Units:")

    print(
        benchmark["unit"]
        .value_counts()
        .to_string()
    )

    # --------------------------------------------------------
    # Duplicate check
    # --------------------------------------------------------

    duplicates = benchmark[
        benchmark.duplicated(
            subset=[
                "district",
                "crop",
                "season",
                "year"
            ],
            keep=False
        )
    ]

    print()
    print(
        f"Duplicate district/crop/season rows: "
        f"{len(duplicates)}"
    )

    # --------------------------------------------------------
    # Missing values
    # --------------------------------------------------------

    print()
    print("Missing values:")

    print(
        benchmark.isna()
        .sum()
        .to_string()
    )

    # --------------------------------------------------------
    # Yield sanity checks
    # --------------------------------------------------------

    print()
    print("-" * 70)
    print("2. YIELD SANITY CHECK")
    print("-" * 70)

    negative = benchmark[
        benchmark["yield"] < 0
    ]

    print(
        f"Negative yields: {len(negative)}"
    )

    print()
    print(
        "Yield statistics:"
    )

    print(
        benchmark["yield"].describe()
        .to_string()
    )

    # --------------------------------------------------------
    # Known official values
    # --------------------------------------------------------

    print()
    print("-" * 70)
    print("3. KNOWN DISTRICT/CROP CHECKS")
    print("-" * 70)

    checks = [
        ("Thanjavur", "Paddy"),
        ("Ariyalur", "Paddy"),
        ("Coimbatore", "Maize"),
        ("Thanjavur", "Sugar Cane"),
        ("Thanjavur", "Cotton"),
        ("Ariyalur", "Black Gram"),
        ("Ariyalur", "Green Gram"),
        ("Thanjavur", "Coconut"),
    ]

    for district, crop in checks:

        show_crop_values(
            benchmark,
            district,
            crop
        )

    # --------------------------------------------------------
    # Crop overlap
    # --------------------------------------------------------

    print()
    print("-" * 70)
    print("4. HISTORICAL DATASET COMPATIBILITY")
    print("-" * 70)

    benchmark_crops = {
        normalize(x)
        for x in benchmark["crop"].unique()
    }

    historical_crops = {
        normalize(x)
        for x in historical["crop"].unique()
    }

    overlap = sorted(
        benchmark_crops
        &
        historical_crops
    )

    benchmark_only = sorted(
        benchmark_crops
        -
        historical_crops
    )

    historical_only = sorted(
        historical_crops
        -
        benchmark_crops
    )

    print()
    print(
        f"Historical crops : {len(historical_crops)}"
    )

    print(
        f"Benchmark crops  : {len(benchmark_crops)}"
    )

    print(
        f"Direct overlap   : {len(overlap)}"
    )

    print()
    print("Directly matching crops:")

    for crop in overlap:
        print(
            f"  - {crop}"
        )

    print()
    print("Benchmark-only crops:")

    for crop in benchmark_only:
        print(
            f"  - {crop}"
        )

    print()
    print("Historical-only crops:")

    for crop in historical_only:
        print(
            f"  - {crop}"
        )

    # --------------------------------------------------------
    # District compatibility
    # --------------------------------------------------------

    benchmark_districts = {
        normalize(x)
        for x in benchmark["district"].unique()
    }

    historical_districts = {
        normalize(x)
        for x in historical["district"].unique()
    }

    district_overlap = (
        benchmark_districts
        &
        historical_districts
    )

    print()
    print(
        f"District overlap: "
        f"{len(district_overlap)}"
    )

    print(
        f"Benchmark districts: "
        f"{len(benchmark_districts)}"
    )

    print(
        f"Historical districts: "
        f"{len(historical_districts)}"
    )

    # --------------------------------------------------------
    # Zero values
    # --------------------------------------------------------

    zero_rows = benchmark[
        benchmark["yield"] == 0
    ]

    print()
    print("-" * 70)
    print("5. ZERO-VALUE CHECK")
    print("-" * 70)

    print(
        f"Zero-yield benchmark rows: "
        f"{len(zero_rows):,}"
    )

    print(
        f"Percentage of benchmark: "
        f"{len(zero_rows) / len(benchmark) * 100:.2f}%"
    )

    print()
    print(
        "Zero values are retained because they are "
        "officially reported values in the source table."
    )

    # --------------------------------------------------------
    # Final verdict
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)

    checks_passed = True

    if len(benchmark) != 3458:
        checks_passed = False
        print(
            "FAIL - benchmark row count is not 3,458."
        )
    else:
        print(
            "PASS - 3,458 benchmark records."
        )

    if benchmark["district"].nunique() != 38:
        checks_passed = False
        print(
            "FAIL - district count is not 38."
        )
    else:
        print(
            "PASS - all 38 districts."
        )

    if len(duplicates) != 0:
        checks_passed = False
        print(
            "FAIL - duplicate benchmark rows found."
        )
    else:
        print(
            "PASS - no duplicate district/crop/season rows."
        )

    if len(negative) != 0:
        checks_passed = False
        print(
            "FAIL - negative yield values found."
        )
    else:
        print(
            "PASS - no negative yields."
        )

    if checks_passed:

        print()
        print(
            "FINAL STATUS: PASS"
        )

        print(
            "Official benchmark dataset is ready "
            "for integration."
        )

    else:

        print()
        print(
            "FINAL STATUS: CHECK REQUIRED"
        )

    print()
    print("=" * 70)


if __name__ == "__main__":
    main()