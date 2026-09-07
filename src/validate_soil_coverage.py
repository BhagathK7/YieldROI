from pathlib import Path
import pandas as pd


# ============================================================
# YIELD ROI - SOIL COVERAGE VALIDATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_FILE = BASE_DIR / "data" / "Main_Fertilizer.csv"
OUTPUT_FILE = BASE_DIR / "results" / "soil_coverage_report.csv"


def main():

    print("=" * 70)
    print("YIELD ROI - SOIL COVERAGE VALIDATION")
    print("=" * 70)

    # --------------------------------------------------------
    # Load data
    # --------------------------------------------------------
    print("\nLoading dataset...")

    df = pd.read_csv(RAW_FILE)

    print(f"Rows loaded: {len(df):,}")

    # --------------------------------------------------------
    # Location columns
    # --------------------------------------------------------
    location_cols = [
        "year",
        "district_name",
        "block_name",
        "village_name",
    ]

    # --------------------------------------------------------
    # Calculate sample coverage for every
    # location + nutrient combination
    # --------------------------------------------------------
    coverage = (
        df.groupby(
            location_cols + ["nutrient_name"],
            dropna=False
        )["value"]
        .sum()
        .reset_index(name="sample_count")
    )

    # --------------------------------------------------------
    # Calculate number of non-zero categories
    # --------------------------------------------------------
    non_zero = (
        df.assign(non_zero=df["value"] > 0)
        .groupby(
            location_cols + ["nutrient_name"],
            dropna=False
        )["non_zero"]
        .sum()
        .reset_index(name="non_zero_categories")
    )

    coverage = coverage.merge(
        non_zero,
        on=location_cols + ["nutrient_name"],
        how="left"
    )

    # --------------------------------------------------------
    # Determine coverage level
    # --------------------------------------------------------
    def coverage_level(count):

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

    coverage["coverage_level"] = (
        coverage["sample_count"]
        .apply(coverage_level)
    )

    # --------------------------------------------------------
    # Print overall statistics
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("OVERALL COVERAGE")
    print("=" * 70)

    print(
        f"\nLocation-nutrient combinations: "
        f"{len(coverage):,}"
    )

    print(
        f"Minimum samples: "
        f"{coverage['sample_count'].min():,}"
    )

    print(
        f"Maximum samples: "
        f"{coverage['sample_count'].max():,}"
    )

    print(
        f"Median samples: "
        f"{coverage['sample_count'].median():.0f}"
    )

    # --------------------------------------------------------
    # Coverage distribution
    # --------------------------------------------------------
    print("\nCoverage distribution:")

    distribution = (
        coverage["coverage_level"]
        .value_counts()
    )

    print(distribution.to_string())

    # --------------------------------------------------------
    # Nutrient-wise statistics
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("NUTRIENT-WISE COVERAGE")
    print("=" * 70)

    nutrient_summary = (
        coverage
        .groupby("nutrient_name")
        .agg(
            locations=("sample_count", "count"),
            min_samples=("sample_count", "min"),
            median_samples=("sample_count", "median"),
            max_samples=("sample_count", "max"),
            mean_samples=("sample_count", "mean"),
        )
        .reset_index()
    )

    nutrient_summary = nutrient_summary.sort_values(
        "median_samples"
    )

    print(
        nutrient_summary.to_string(
            index=False,
            formatters={
                "mean_samples": "{:.2f}".format,
                "median_samples": "{:.0f}".format,
            }
        )
    )

    # --------------------------------------------------------
    # Nutrient coverage percentages
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("NUTRIENT COVERAGE QUALITY")
    print("=" * 70)

    quality_rows = []

    for nutrient, group in coverage.groupby(
        "nutrient_name"
    ):

        total = len(group)

        very_low = (
            group["coverage_level"] == "Very Low"
        ).sum()

        low = (
            group["coverage_level"] == "Low"
        ).sum()

        moderate = (
            group["coverage_level"] == "Moderate"
        ).sum()

        good = (
            group["coverage_level"] == "Good"
        ).sum()

        high = (
            group["coverage_level"] == "High"
        ).sum()

        quality_rows.append(
            {
                "nutrient_name": nutrient,
                "total_locations": total,
                "very_low_pct": very_low / total * 100,
                "low_pct": low / total * 100,
                "moderate_pct": moderate / total * 100,
                "good_pct": good / total * 100,
                "high_pct": high / total * 100,
            }
        )

    quality = pd.DataFrame(quality_rows)

    print(
        quality.to_string(
            index=False,
            formatters={
                "very_low_pct": "{:.2f}%".format,
                "low_pct": "{:.2f}%".format,
                "moderate_pct": "{:.2f}%".format,
                "good_pct": "{:.2f}%".format,
                "high_pct": "{:.2f}%".format,
            }
        )
    )

    # --------------------------------------------------------
    # Find locations with unusually low coverage
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("LOW-COVERAGE EXAMPLES")
    print("=" * 70)

    low_coverage = coverage[
        coverage["sample_count"] <= 2
    ].sort_values(
        ["sample_count", "nutrient_name"]
    )

    if len(low_coverage) > 0:

        print(
            low_coverage.head(30).to_string(
                index=False
            )
        )

    else:
        print("\nNo locations with <= 2 samples.")

    # --------------------------------------------------------
    # Create pivoted coverage report
    # --------------------------------------------------------
    report = coverage.pivot_table(
        index=location_cols,
        columns="nutrient_name",
        values="sample_count",
        aggfunc="sum",
        fill_value=0,
    ).reset_index()

    # --------------------------------------------------------
    # Overall coverage score
    #
    # This is NOT a soil quality score.
    # It only represents how much sample-count information
    # exists for the location.
    # --------------------------------------------------------
    nutrient_columns = [
        column
        for column in report.columns
        if column not in location_cols
    ]

    report["nutrients_available"] = (
        report[nutrient_columns] > 0
    ).sum(axis=1)

    report["coverage_percentage"] = (
        report["nutrients_available"]
        / len(nutrient_columns)
        * 100
    )

    # --------------------------------------------------------
    # Save report
    # --------------------------------------------------------
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    report.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\n" + "=" * 70)
    print("REPORT SAVED")
    print("=" * 70)

    print(f"\nFile: {OUTPUT_FILE}")

    print(
        f"Rows in report: "
        f"{len(report):,}"
    )

    # --------------------------------------------------------
    # Final message
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("VALIDATION COMPLETED")
    print("=" * 70)

    print(
        "\nIMPORTANT:"
        "\nThe coverage percentage measures the availability "
        "of nutrient-category information."
        "\nIt is NOT a measure of soil fertility or soil quality."
    )

    print(
        "\nWe will use this information later to determine "
        "how confidently a soil-status recommendation can "
        "be presented."
    )


if __name__ == "__main__":
    main()