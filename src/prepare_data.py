import pandas as pd
from pathlib import Path

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "data" / "tamil_nadu_yield_cleaned.csv"

TRAIN_FILE = BASE_DIR / "data" / "train.csv"
VALIDATION_FILE = BASE_DIR / "data" / "validation.csv"
TEST_FILE = BASE_DIR / "data" / "test.csv"


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(INPUT_FILE)

print("=" * 70)
print("TAMIL NADU YIELD DATASET - FINAL ML PREPARATION")
print("=" * 70)

print(f"\nTotal records: {len(df):,}")


# ============================================================
# BASIC VALIDATION
# ============================================================

required_columns = [
    "fiscal_year",
    "state",
    "district",
    "crop",
    "season",
    "area",
    "production",
    "crop_yield",
    "year",
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )


# ============================================================
# REMOVE PRODUCTION FROM ML DATA
# ============================================================

# Production is mathematically related to yield:
#
#     Yield ≈ Production / Area
#
# Therefore production must NOT be used as a prediction feature.

model_columns = [
    "fiscal_year",
    "state",
    "district",
    "crop",
    "season",
    "area",
    "crop_yield",
    "year",
]

df = df[model_columns].copy()


# ============================================================
# FINAL DATA QUALITY CHECK
# ============================================================

if df["crop_yield"].isna().any():
    raise ValueError("Missing crop_yield values found.")

if (df["crop_yield"] <= 0).any():
    raise ValueError("Non-positive crop_yield values found.")

if df["area"].isna().any() or (df["area"] <= 0).any():
    raise ValueError("Invalid area values found.")

if df.duplicated().any():
    raise ValueError("Duplicate rows found.")


# ============================================================
# SORT CHRONOLOGICALLY
# ============================================================

df = df.sort_values(
    by=["year", "district", "crop", "season"]
).reset_index(drop=True)


# ============================================================
# TEMPORAL TRAIN / VALIDATION / TEST SPLIT
# ============================================================
#
# 1997–2018  -> Training
# 2019–2020  -> Validation
# 2021–2022  -> Final Test
#
# This prevents future information from leaking into training.

train = df[df["year"] <= 2018].copy()

validation = df[
    (df["year"] >= 2019) &
    (df["year"] <= 2020)
].copy()

test = df[df["year"] >= 2021].copy()


# ============================================================
# CHECK SPLIT SIZES
# ============================================================

print("\nSPLIT SUMMARY")
print("-" * 70)

print(f"Training   : {len(train):,} records")
print(f"Validation : {len(validation):,} records")
print(f"Test       : {len(test):,} records")

print("\nYear ranges:")
print(
    f"Training   : {train['year'].min()} - {train['year'].max()}"
)
print(
    f"Validation : {validation['year'].min()} - "
    f"{validation['year'].max()}"
)
print(
    f"Test       : {test['year'].min()} - {test['year'].max()}"
)


# ============================================================
# LEAKAGE CHECK
# ============================================================

max_train_year = train["year"].max()
min_validation_year = validation["year"].min()
min_test_year = test["year"].min()

if max_train_year >= min_validation_year:
    raise ValueError("Training/validation temporal leakage detected.")

if max_train_year >= min_test_year:
    raise ValueError("Training/test temporal leakage detected.")

if validation["year"].max() >= min_test_year:
    raise ValueError("Validation/test temporal leakage detected.")


# ============================================================
# SAVE
# ============================================================

train.to_csv(TRAIN_FILE, index=False)
validation.to_csv(VALIDATION_FILE, index=False)
test.to_csv(TEST_FILE, index=False)


# ============================================================
# FINAL REPORT
# ============================================================

print("\nFILES CREATED")
print("-" * 70)

print(f"Training   : {TRAIN_FILE}")
print(f"Validation : {VALIDATION_FILE}")
print(f"Test       : {TEST_FILE}")

print("\nFeature columns:")
print([
    "district",
    "crop",
    "season",
    "year",
    "area",
])

print("\nTarget:")
print("crop_yield")

print("\nProduction:")
print("EXCLUDED — target leakage prevention")

print("\n" + "=" * 70)
print("ML DATA PREPARATION COMPLETE")
print("=" * 70)