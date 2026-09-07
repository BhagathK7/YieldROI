import pandas as pd
from pathlib import Path

DATA_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "district-season-and-crop-wise-area-production-and-yield-statistics-for-tamil-nadu.xlsx"
)

df = pd.read_excel(DATA_PATH)

print("=" * 70)
print("DETAILED DATASET ANALYSIS")
print("=" * 70)

# 1. State Total
print("\n1. DISTRICT COUNTS")
print(df["district"].value_counts().to_string())

# 2. Zero values
print("\n2. ZERO VALUES")
print("Area = 0:", (df["area"] == 0).sum())
print("Production = 0:", (df["production"] == 0).sum())
print("Yield = 0:", (df["crop_yield"] == 0).sum())

# 3. Missing production
print("\n3. MISSING PRODUCTION")
print("Missing production:", df["production"].isna().sum())

# 4. Crop frequency
print("\n4. CROP FREQUENCY")
print(df["crop"].value_counts().to_string())

# 5. Crop-wise yield statistics
print("\n5. CROP-WISE YIELD STATISTICS")

crop_stats = (
    df.groupby("crop")["crop_yield"]
    .agg(["count", "min", "median", "mean", "max"])
    .sort_values("count", ascending=False)
)

print(crop_stats.to_string())

# 6. Season frequency
print("\n6. SEASON FREQUENCY")
print(df["season"].value_counts().to_string())

# 7. Year frequency
print("\n7. YEAR FREQUENCY")
print(df["fiscal_year"].value_counts().sort_index().to_string())

# 8. State Total records
print("\n8. STATE TOTAL")
state_total = df[df["district"] == "State Total"]
print("State Total rows:", len(state_total))

# 9. Potential problematic rows
print("\n9. POTENTIAL PROBLEMATIC ROWS")

problematic = df[
    (df["area"] <= 0)
    | (df["crop_yield"] < 0)
]

print("Area <= 0:", (df["area"] <= 0).sum())
print("Yield < 0:", (df["crop_yield"] < 0).sum())

# 10. Yield extremes
print("\n10. TOP 20 HIGHEST YIELD VALUES")

print(
    df[
        ["fiscal_year", "district", "crop", "season",
         "area", "production", "crop_yield"]
    ]
    .sort_values("crop_yield", ascending=False)
    .head(20)
    .to_string(index=False)
)

print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)