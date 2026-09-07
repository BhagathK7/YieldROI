import pandas as pd
from pathlib import Path

# --------------------------------------------------
# PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "district-season-and-crop-wise-area-production-and-yield-statistics-for-tamil-nadu.xlsx"
)

OUTPUT_FILE = BASE_DIR / "data" / "tamil_nadu_yield_cleaned.csv"


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

df = pd.read_excel(INPUT_FILE)

print("Original rows:", len(df))


# --------------------------------------------------
# REMOVE UNNECESSARY COLUMNS
# --------------------------------------------------

df = df.drop(columns=["note", "unit"], errors="ignore")


# --------------------------------------------------
# REMOVE STATE TOTAL
# --------------------------------------------------

df = df[df["district"].str.strip() != "State Total"].copy()


# --------------------------------------------------
# STANDARDIZE TEXT
# --------------------------------------------------

text_columns = ["fiscal_year", "state", "district", "crop", "season"]

for column in text_columns:
    df[column] = df[column].astype(str).str.strip()


# --------------------------------------------------
# CONVERT NUMERIC COLUMNS
# --------------------------------------------------

numeric_columns = ["area", "production", "crop_yield"]

for column in numeric_columns:
    df[column] = pd.to_numeric(df[column], errors="coerce")


# --------------------------------------------------
# REMOVE INVALID AREA
# --------------------------------------------------

df = df[df["area"] > 0].copy()


# --------------------------------------------------
# HANDLE MISSING PRODUCTION
# --------------------------------------------------

# Production is not an input feature.
# Since yield already exists, missing production does
# not make the yield target invalid.

# Therefore, we DO NOT delete these rows only because
# production is missing.


# --------------------------------------------------
# REMOVE INVALID YIELD
# --------------------------------------------------

df = df[df["crop_yield"].notna()].copy()
df = df[df["crop_yield"] > 0].copy()


# --------------------------------------------------
# EXTRACT YEAR
# --------------------------------------------------

df["year"] = (
    df["fiscal_year"]
    .str.extract(r"(\d{4})")[0]
    .astype(int)
)


# --------------------------------------------------
# CHECK YIELD CONSISTENCY
# --------------------------------------------------

calculated_yield = df["production"] / df["area"]

valid_production = df["production"].notna()

difference = (
    df.loc[valid_production, "crop_yield"]
    - calculated_yield[valid_production]
).abs()

print("\nYield consistency check:")
print("Rows checked:", len(difference))
print("Maximum difference:", difference.max())


# --------------------------------------------------
# REMOVE DUPLICATES
# --------------------------------------------------

before_duplicates = len(df)

df = df.drop_duplicates()

duplicates_removed = before_duplicates - len(df)


# --------------------------------------------------
# SORT DATA
# --------------------------------------------------

df = df.sort_values(
    ["year", "district", "crop", "season"]
).reset_index(drop=True)


# --------------------------------------------------
# SAVE
# --------------------------------------------------

df.to_csv(OUTPUT_FILE, index=False)


# --------------------------------------------------
# FINAL REPORT
# --------------------------------------------------

print("\n" + "=" * 60)
print("CLEANING COMPLETE")
print("=" * 60)

print("Original rows:", 24707)
print("Final rows:", len(df))
print("State Total removed:", 24707 - 1038 - len(df) if False else "Excluded")
print("Duplicates removed:", duplicates_removed)

print("\nMissing values:")
print(df.isnull().sum())

print("\nFinal columns:")
print(df.columns.tolist())

print("\nSaved to:")
print(OUTPUT_FILE)

print("=" * 60)