import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
FILE = BASE_DIR / "data" / "tamil_nadu_yield_cleaned.csv"

df = pd.read_csv(FILE)

zero = df[df["crop_yield"] == 0].copy()

print("=" * 60)
print("ZERO-YIELD ANALYSIS")
print("=" * 60)

print("\nTotal zero-yield rows:", len(zero))

print("\nZero yield by crop:")
print(zero["crop"].value_counts().to_string())

print("\nZero yield by year:")
print(zero["year"].value_counts().sort_index().to_string())

print("\nZero yield by season:")
print(zero["season"].value_counts().to_string())

print("\nZero yield by district:")
print(zero["district"].value_counts().to_string())

print("\nSample zero-yield records:")
print(
    zero[
        [
            "fiscal_year",
            "district",
            "crop",
            "season",
            "area",
            "production",
            "crop_yield",
        ]
    ]
    .head(30)
    .to_string(index=False)
)

print("\n" + "=" * 60)
print("ANALYSIS COMPLETE")
print("=" * 60)