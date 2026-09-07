"""
YieldROI - Official Benchmark Comparator

Compares an ML-predicted yield with the official
Tamil Nadu 2024-25 district-wise average yield benchmark.

Important:
    - Benchmark data is NOT used for model training.
    - Benchmark values are independent reference values.
    - Official benchmark kg/ha values are converted to tonnes/ha
      before comparison.
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


# ============================================================
# CROP NAME MAPPING
# ============================================================

# Historical ML dataset -> Official benchmark PDF

CROP_MAPPING = {

    "rice": "Paddy",
    "jowar": "Jowar (Cholam)",
    "bajra": "Bajra (Cumbu)",
    "ragi": "Ragi",

    "maize": "Maize",
    "korra": "Korra",
    "varagu": "Varagu",
    "small millets": "Samai",

    "gram": "Bengal Gram",
    "arhartur": "Red Gram",

    "moonggreen gram": "Green Gram",
    "urad": "Black Gram",

    "horse gram": "Horse Gram",
    "cowpealobia": "Cowpea",

    "other kharif pulses": "Other Pulses",
    "other rabi pulses": "Other Pulses",

    "sugarcane": "Sugar Cane",

    "arecanut": "Arecanut",
    "dry chillies": "Chillies",
    "black pepper": "Pepper",

    "cashewnut": "Cashew Nut",
    "cottonlint": "Cotton",

    "sesamum": "Gingelly",
    "sunflower": "Sun Flower",

    "castor seed": "Castor",

    "rapeseed & mustard": "Rapeseed & Mustard",

    "cardamom": "Cardamom",
    "coriander": "Coriander",
    "garlic": "Garlic",
    "ginger": "Ginger",
    "turmeric": "Turmeric",

    "tapioca": "Tapioca",
    "sweet potato": "Sweet Potato",
    "potato": "Potato",

    "onion": "Onion",

    "banana": "Banana",
    "mango": "Mango",
    "lemon": "Lemon",
    "orange": "Orange",
    "guava": "Guava",
    "grapes": "Grapes",
    "jack fruit": "Jack Fruit",
    "pine apple": "Pine Apple",

    "coconut": "Coconut",

    "tobacco": "Tobacco",

    "brinjal": "Brinjal",
    "cabbage": "Cabbage",
    "tomato": "Tomato",
    "lady's finger": "Lady's Finger",
}


# ============================================================
# DISTRICT NAME MAPPING
# ============================================================

DISTRICT_MAPPING = {

    # Common spelling/name variations.
    "tiruchirapalli": "Tiruchirapalli",
    "trichy": "Tiruchirapalli",

    "tirunelveli": "Tirunelveli",

    "tiruvallur": "Tiruvallur",

    "thoothukudi": "Thoothukudi",

    "the nilgiris": "The Nilgiris",

    "kanniyakumari": "Kanniyakumari",

    "pudukkottai": "Pudukkottai",

    "nagapattinam": "Nagapattinam",

    "tiruppur": "Tiruppur",

    "tiruvarur": "Tiruvarur",

    "mayiladuthurai": "Mayiladuthurai",
}


# ============================================================
# NORMALIZATION
# ============================================================

def normalize(value):
    """Normalize text for comparison."""

    return (
        str(value)
        .strip()
        .lower()
        .replace("_", " ")
        .replace("-", " ")
        .replace("&", "and")
        .replace("(", "")
        .replace(")", "")
        .replace("  ", " ")
    )


def normalize_crop(crop):
    """
    Convert historical crop name into official
    benchmark crop name.
    """

    key = normalize(crop)

    return CROP_MAPPING.get(
        key,
        crop
    )


def normalize_district(district):
    """
    Convert district name into official benchmark name.
    """

    key = normalize(district)

    return DISTRICT_MAPPING.get(
        key,
        district
    )


# ============================================================
# LOAD
# ============================================================

def load_benchmarks():

    if not BENCHMARK_FILE.exists():

        raise FileNotFoundError(
            f"Benchmark file not found:\n"
            f"{BENCHMARK_FILE}"
        )

    df = pd.read_csv(
        BENCHMARK_FILE
    )

    return df


# ============================================================
# FIND BENCHMARK
# ============================================================

def find_benchmark(
    district,
    crop,
    season="Combined"
):
    """
    Find the most appropriate official benchmark.

    Priority:
        1. Exact season
        2. Combined season

    Returns:
        dictionary
        or None
    """

    df = load_benchmarks()

    official_district = normalize_district(
        district
    )

    official_crop = normalize_crop(
        crop
    )

    subset = df[
        (
            df["district"].str.lower()
            ==
            official_district.lower()
        )
        &
        (
            df["crop"].str.lower()
            ==
            official_crop.lower()
        )
    ].copy()

    if subset.empty:

        return None

    # --------------------------------------------------------
    # Try exact season
    # --------------------------------------------------------

    if season:

        exact = subset[
            subset["season"].str.lower()
            ==
            str(season).lower()
        ]

        if not exact.empty:

            return exact.iloc[0].to_dict()

    # --------------------------------------------------------
    # Fall back to Combined
    # --------------------------------------------------------

    combined = subset[
        subset["season"].str.lower()
        ==
        "combined"
    ]

    if not combined.empty:

        return combined.iloc[0].to_dict()

    return None


# ============================================================
# CONVERT UNITS
# ============================================================

def benchmark_to_tonnes(
    benchmark_yield,
    unit
):
    """
    Convert official benchmark into tonnes/ha
    when appropriate.
    """

    if unit == "kg/ha":

        return float(
            benchmark_yield
        ) / 1000.0

    # Coconut is nuts/ha and cannot be directly
    # compared with tonnes/ha.
    if unit == "nuts/ha":

        return None

    # Sugarcane is already tonnes/ha.
    if unit == "tonnes/ha":

        return float(
            benchmark_yield
        )

    return None


# ============================================================
# COMPARE
# ============================================================

def compare_prediction(
    district,
    crop,
    season,
    predicted_yield
):
    """
    Compare predicted yield with official benchmark.

    predicted_yield must be tonnes/ha.
    """

    benchmark = find_benchmark(
        district=district,
        crop=crop,
        season=season
    )

    if benchmark is None:

        return {
            "status": "Benchmark unavailable",
            "district": district,
            "crop": crop,
            "season": season,
            "predicted_yield_tonnes_per_ha": (
                float(predicted_yield)
            ),
        }

    benchmark_tonnes = benchmark_to_tonnes(
        benchmark["yield"],
        benchmark["unit"]
    )

    # Cannot compare coconut nuts/ha
    # against model tonnes/ha.
    if benchmark_tonnes is None:

        return {
            "status": "Unit mismatch",
            "district": district,
            "crop": crop,
            "season": season,
            "official_crop": benchmark["crop"],
            "official_unit": benchmark["unit"],
            "predicted_yield_tonnes_per_ha": (
                float(predicted_yield)
            ),
            "official_yield": benchmark["yield"],
        }

    predicted = float(
        predicted_yield
    )

    difference = (
        predicted
        -
        benchmark_tonnes
    )

    if benchmark_tonnes != 0:

        difference_percent = (
            difference
            /
            benchmark_tonnes
        ) * 100

    else:

        difference_percent = None

    # --------------------------------------------------------
    # Performance classification
    # --------------------------------------------------------

    if benchmark_tonnes == 0:

        performance = (
            "No official production benchmark"
        )

    elif difference_percent >= 5:

        performance = "Above benchmark"

    elif difference_percent <= -5:

        performance = "Below benchmark"

    else:

        performance = "Near benchmark"

    return {

        "status": "Compared",

        "district": district,

        "crop": crop,

        "season": season,

        "official_crop": benchmark["crop"],

        "official_season": benchmark["season"],

        "predicted_yield_tonnes_per_ha": predicted,

        "official_yield_original": (
            benchmark["yield"]
        ),

        "official_unit": benchmark["unit"],

        "official_yield_tonnes_per_ha": (
            benchmark_tonnes
        ),

        "difference_tonnes_per_ha": (
            difference
        ),

        "difference_percent": (
            difference_percent
        ),

        "performance": performance,

        "benchmark_year": benchmark["year"],

        "source_page": benchmark["source_page"],
    }


# ============================================================
# DISPLAY
# ============================================================

def display_comparison(result):

    print()
    print("=" * 70)
    print("OFFICIAL BENCHMARK COMPARISON")
    print("=" * 70)

    print()

    print(
        f"District             : "
        f"{result.get('district')}"
    )

    print(
        f"Crop                 : "
        f"{result.get('crop')}"
    )

    print(
        f"Season               : "
        f"{result.get('season')}"
    )

    print()

    print(
        f"Predicted Yield      : "
        f"{result.get('predicted_yield_tonnes_per_ha', 0):.3f} "
        f"tonnes/ha"
    )

    if result.get(
        "official_yield_tonnes_per_ha"
    ) is not None:

        print(
            f"Official Benchmark   : "
            f"{result['official_yield_tonnes_per_ha']:.3f} "
            f"tonnes/ha"
        )

        print(
            f"Difference           : "
            f"{result['difference_tonnes_per_ha']:.3f} "
            f"tonnes/ha"
        )

        if result["difference_percent"] is not None:

            print(
                f"Difference %         : "
                f"{result['difference_percent']:.2f}%"
            )

        print()

        print(
            f"Performance          : "
            f"{result['performance']}"
        )

    else:

        print(
            "Official Benchmark   : "
            "Not directly comparable"
        )

    print()

    print(
        f"Status               : "
        f"{result['status']}"
    )

    print()

    if result.get("source_page"):

        print(
            f"Official Source Page : "
            f"{result['source_page']}"
        )

    print()
    print("=" * 70)


# ============================================================
# TEST
# ============================================================

def main():

    print("=" * 70)
    print("YieldROI - Benchmark Comparator Test")
    print("=" * 70)

    print()

    # Test 1
    result = compare_prediction(
        district="Thanjavur",
        crop="Rice",
        season="Kharif",
        predicted_yield=3.28
    )

    display_comparison(
        result
    )

    print()

    # Test 2
    result = compare_prediction(
        district="Ariyalur",
        crop="Rice",
        season="Kharif",
        predicted_yield=3.50
    )

    display_comparison(
        result
    )

    print()

    # Test 3 - Maize
    result = compare_prediction(
        district="Coimbatore",
        crop="Maize",
        season="Kharif",
        predicted_yield=5.80
    )

    display_comparison(
        result
    )

    print()

    # Test 4 - Coconut
    result = compare_prediction(
        district="Thanjavur",
        crop="Coconut",
        season="Combined",
        predicted_yield=3.00
    )

    display_comparison(
        result
    )


if __name__ == "__main__":
    main()