import pandas as pd
from pathlib import Path

DATA_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "district-season-and-crop-wise-area-production-and-yield-statistics-for-tamil-nadu.xlsx"
)

df = pd.read_excel(DATA_PATH)

# Calculate yield independently
df["calculated_yield"] = df["production"] / df["area"]

# Difference between dataset yield and calculated yield
df["difference"] = (
    df["crop_yield"] - df["calculated_yield"]
).abs()

valid = df["production"].notna() & (df["area"] > 0)

checked = df[valid]

print("=" * 60)
print("YIELD CONSISTENCY CHECK")
print("=" * 60)

print(f"\nRows checked: {len(checked):,}")

print("\nMaximum difference:")
print(f"{checked['difference'].max():.6f}")

print("\nMean difference:")
print(f"{checked['difference'].mean():.6f}")

print("\nRows with difference > 0.01:")
print((checked["difference"] > 0.01).sum())

print("\nRows with difference > 0.1:")
print((checked["difference"] > 0.1).sum())

print("\nLargest differences:")
print(
    checked[
        [
            "fiscal_year",
            "district",
            "crop",
            "season",
            "area",
            "production",
            "crop_yield",
            "calculated_yield",
            "difference",
        ]
    ]
    .sort_values("difference", ascending=False)
    .head(10)
    .to_string(index=False)
)

print("\n" + "=" * 60)
print("CHECK COMPLETE")
print("=" * 60)