import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
FILE = BASE_DIR / "data" / "tamil_nadu_yield_cleaned.csv"

df = pd.read_csv(FILE)

print("=" * 60)
print("CLEANED DATASET VERIFICATION")
print("=" * 60)

print("\nShape:")
print(df.shape)

print("\nMissing values:")
print(df.isnull().sum())

print("\nDistricts:")
print(df["district"].nunique())

print("\nCrops:")
print(df["crop"].nunique())

print("\nSeasons:")
print(df["season"].nunique())

print("\nYears:")
print(df["year"].min(), "to", df["year"].max())

print("\nState Total present:")
print((df["district"] == "State Total").sum())

print("\nZero yield:")
print((df["crop_yield"] == 0).sum())

print("\nDuplicate rows:")
print(df.duplicated().sum())

print("\nFirst 5 rows:")
print(df.head().to_string(index=False))

print("\n" + "=" * 60)
print("VERIFICATION COMPLETE")
print("=" * 60)