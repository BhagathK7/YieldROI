import pandas as pd
from pathlib import Path

# Dataset path
DATA_PATH = Path(__file__).resolve().parent.parent / "data" / \
    "district-season-and-crop-wise-area-production-and-yield-statistics-for-tamil-nadu.xlsx"

print("=" * 60)
print("TAMIL NADU CROP YIELD DATASET INSPECTION")
print("=" * 60)

# Load Excel
df = pd.read_excel(DATA_PATH)

print("\n1. DATASET SHAPE")
print(f"Rows    : {df.shape[0]:,}")
print(f"Columns : {df.shape[1]}")

print("\n2. COLUMNS")
for column in df.columns:
    print(f" - {column}")

print("\n3. DATA TYPES")
print(df.dtypes)

print("\n4. MISSING VALUES")
print(df.isnull().sum())

print("\n5. DUPLICATE ROWS")
print(f"Duplicates: {df.duplicated().sum():,}")

print("\n6. FIRST 5 ROWS")
print(df.head().to_string())

print("\n7. UNIQUE VALUES")
for column in ["state", "district", "crop", "season", "unit"]:
    if column in df.columns:
        print(f"\n{column.upper()} ({df[column].nunique()} unique):")
        print(df[column].dropna().unique())

print("\n8. YEAR RANGE")
print(df["fiscal_year"].min(), "to", df["fiscal_year"].max())

print("\n9. NUMERIC SUMMARY")
print(df.describe().to_string())

print("\n" + "=" * 60)
print("INSPECTION COMPLETE")
print("=" * 60)