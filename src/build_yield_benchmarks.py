"""
YieldROI - Official Yield Benchmark Extraction

Source:
Tamil Nadu Department of Economics and Statistics
Districtwise Average Yield Rates of the Crops for the Year 2024-25

This benchmark dataset is used ONLY for:
    - validation
    - comparison with model predictions
    - dashboard analytics

It is NOT used for model training.
"""

from pathlib import Path
import re
import pdfplumber
import pandas as pd


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

PDF_PATH = ROOT / "data" / "averageyieldrateofcrops.pdf"
OUTPUT_CSV = ROOT / "data" / "official_yield_benchmarks.csv"
RAW_TEXT = ROOT / "results" / "yield_benchmark_raw_text.txt"
REPORT = ROOT / "results" / "benchmark_extraction_report.txt"


# ============================================================
# OFFICIAL DISTRICTS
# ============================================================

DISTRICTS = [
    "Chennai",
    "Kancheepuram",
    "Chengalpattu",
    "Tiruvallur",
    "Cuddalore",
    "Villupuram",
    "Kallakurichi",
    "Vellore",
    "Ranipet",
    "Tirupathur",
    "Tiruvannamalai",
    "Salem",
    "Namakkal",
    "Dharmapuri",
    "Krishnagiri",
    "Coimbatore",
    "Tiruppur",
    "Erode",
    "Tiruchirapalli",
    "Karur",
    "Perambalur",
    "Ariyalur",
    "Pudukkottai",
    "Thanjavur",
    "Tiruvarur",
    "Nagapattinam",
    "Mayiladuthurai",
    "Madurai",
    "Theni",
    "Dindigul",
    "Ramanathapuram",
    "Virudhunagar",
    "Sivagangai",
    "Tirunelveli",
    "Tenkasi",
    "Thoothukudi",
    "The Nilgiris",
    "Kanniyakumari",
]


# ============================================================
# PDF COLUMN DEFINITIONS
# ============================================================

PAGE_COLUMNS = {

    1: [
        ("Paddy", "Kar/Kuruvai/Sornavari", "kg/ha"),
        ("Paddy", "Samba/Thaladi/Pishanam", "kg/ha"),
        ("Paddy", "Navarai/Kodai", "kg/ha"),
        ("Paddy", "Combined", "kg/ha"),
        ("Jowar (Cholam)", "Kharif", "kg/ha"),
        ("Jowar (Cholam)", "Rabi", "kg/ha"),
        ("Jowar (Cholam)", "Combined", "kg/ha"),
    ],

    2: [
        ("Bajra (Cumbu)", "Kharif", "kg/ha"),
        ("Bajra (Cumbu)", "Rabi", "kg/ha"),
        ("Bajra (Cumbu)", "Combined", "kg/ha"),
        ("Ragi", "Kharif", "kg/ha"),
        ("Ragi", "Rabi", "kg/ha"),
        ("Ragi", "Combined", "kg/ha"),
    ],

    3: [
        ("Maize", "Kharif", "kg/ha"),
        ("Maize", "Rabi", "kg/ha"),
        ("Maize", "Combined", "kg/ha"),
        ("Korra", "Combined", "kg/ha"),
        ("Varagu", "Kharif", "kg/ha"),
        ("Varagu", "Rabi", "kg/ha"),
        ("Varagu", "Combined", "kg/ha"),
    ],

    4: [
        ("Samai", "Kharif", "kg/ha"),
        ("Samai", "Rabi", "kg/ha"),
        ("Samai", "Combined", "kg/ha"),
        ("Other Cereals", "Combined", "kg/ha"),
        ("Bengal Gram", "Combined", "kg/ha"),
        ("Red Gram", "Kharif", "kg/ha"),
        ("Red Gram", "Rabi", "kg/ha"),
        ("Red Gram", "Combined", "kg/ha"),
    ],

    5: [
        ("Green Gram", "Kharif", "kg/ha"),
        ("Green Gram", "Rabi", "kg/ha"),
        ("Green Gram", "Combined", "kg/ha"),
        ("Black Gram", "Kharif", "kg/ha"),
        ("Black Gram", "Rabi", "kg/ha"),
        ("Black Gram", "Combined", "kg/ha"),
        ("Horse Gram", "Kharif", "kg/ha"),
        ("Horse Gram", "Rabi", "kg/ha"),
        ("Horse Gram", "Combined", "kg/ha"),
    ],

    6: [
        ("Cowpea", "Kharif", "kg/ha"),
        ("Cowpea", "Rabi", "kg/ha"),
        ("Cowpea", "Combined", "kg/ha"),
        ("Other Pulses", "Kharif", "kg/ha"),
        ("Other Pulses", "Rabi", "kg/ha"),
        ("Other Pulses", "Combined", "kg/ha"),
        ("Sugar Cane", "Combined", "tonnes/ha"),
    ],

    7: [
        ("Arecanut", "Combined", "kg/ha"),
        ("Chillies", "Combined", "kg/ha"),
        ("Cloves", "Combined", "kg/ha"),
        ("Garlic", "Combined", "kg/ha"),
        ("Pepper", "Combined", "kg/ha"),
        ("Turmeric", "Combined", "kg/ha"),
        ("Ginger", "Combined", "kg/ha"),
    ],

    8: [
        ("Coriander", "Combined", "kg/ha"),
        ("Cardamom", "Combined", "kg/ha"),
        ("Tamarind", "Combined", "kg/ha"),
        ("Tapioca", "Combined", "kg/ha"),
        ("Sweet Potato", "Combined", "kg/ha"),
        ("Potato", "Kharif", "kg/ha"),
        ("Potato", "Rabi", "kg/ha"),
        ("Potato", "Combined", "kg/ha"),
    ],

    9: [
        ("Onion", "Kharif", "kg/ha"),
        ("Onion", "Rabi", "kg/ha"),
        ("Onion", "Combined", "kg/ha"),
        ("Brinjal", "Combined", "kg/ha"),
        ("Lady's Finger", "Combined", "kg/ha"),
        ("Cabbage", "Combined", "kg/ha"),
        ("Tomato", "Combined", "kg/ha"),
    ],

    10: [
        ("Banana", "Combined", "kg/ha"),
        ("Mango", "Combined", "kg/ha"),
        ("Lemon", "Combined", "kg/ha"),
        ("Orange", "Combined", "kg/ha"),
        ("Cashew Nut", "Combined", "kg/ha"),
        ("Jack Fruit", "Combined", "kg/ha"),
        ("Pine Apple", "Combined", "kg/ha"),
    ],

    11: [
        ("Guava", "Combined", "kg/ha"),
        ("Grapes", "Combined", "kg/ha"),
        ("Groundnut", "Kharif", "kg/ha"),
        ("Groundnut", "Rabi", "kg/ha"),
        ("Groundnut", "Combined", "kg/ha"),
        ("Gingelly", "Kharif", "kg/ha"),
        ("Gingelly", "Rabi", "kg/ha"),
        ("Gingelly", "Combined", "kg/ha"),
    ],

    12: [
        ("Sun Flower", "Kharif", "kg/ha"),
        ("Sun Flower", "Rabi", "kg/ha"),
        ("Sun Flower", "Combined", "kg/ha"),
        ("Rapeseed & Mustard", "Combined", "kg/ha"),
        ("Castor", "Combined", "kg/ha"),
    ],

    13: [
        ("Cotton", "Kharif", "kg/ha"),
        ("Cotton", "Rabi", "kg/ha"),
        ("Cotton", "Combined", "kg/ha"),
        ("Tobacco", "Combined", "kg/ha"),
        ("Coconut", "Combined", "nuts/ha"),
    ],
}


# ============================================================
# HELPERS
# ============================================================

def extract_numbers(text):
    """
    Extract numeric values from text.
    """

    matches = re.findall(
        r"(?<![A-Za-z])\d+(?:\.\d+)?",
        text
    )

    return [
        float(x.replace(",", ""))
        for x in matches
    ]


def get_district_lines(text):
    """
    Find the official district lines.

    Handles both:

        1 Chennai

    and:

        1 Chennai 3689 3008 3874 ...
    """

    result = []

    for line in text.splitlines():

        line = line.strip()

        match = re.match(
            r"^(\d{1,2})\s+(.+)$",
            line
        )

        if not match:
            continue

        number = int(match.group(1))

        if number < 1 or number > 38:
            continue

        remainder = match.group(2).strip()

        district = None

        # Match longest district names first.
        for official in sorted(
            DISTRICTS,
            key=len,
            reverse=True
        ):

            if remainder.startswith(official):

                district = official
                break

        if district is None:
            continue

        after_district = remainder[
            len(district):
        ].strip()

        values = extract_numbers(
            after_district
        )

        result.append(
            {
                "number": number,
                "district": district,
                "values": values,
            }
        )

    # Remove duplicates.
    final = []
    seen = set()

    for item in result:

        if item["number"] in seen:
            continue

        seen.add(item["number"])
        final.append(item)

    return sorted(
        final,
        key=lambda x: x["number"]
    )


def get_numeric_only_rows(text):
    """
    Extract numeric-only rows.

    Used when district names and values
    are separated in the PDF text.
    """

    rows = []

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        if not re.fullmatch(
            r"[\d\s.,-]+",
            line
        ):
            continue

        values = extract_numbers(line)

        if values:
            rows.append(values)

    return rows


def normalize_values(values, expected):
    """
    Make the extracted row exactly match the
    expected number of columns.

    PDF extraction can sometimes omit trailing
    zero cells.

    Missing trailing cells are therefore treated
    as zero.
    """

    if len(values) == expected:
        return values

    if len(values) < expected:

        return values + [
            0.0
        ] * (
            expected - len(values)
        )

    # Too many values means this row is not safe.
    return None


def build_records(page_number, text):
    """
    Hybrid extraction.

    Strategy:

    1. Try district + values on same line.
    2. If values are missing/separated, use
       numeric-only rows.
    """

    expected_columns = PAGE_COLUMNS[
        page_number
    ]

    expected_count = len(
        expected_columns
    )

    district_lines = get_district_lines(
        text
    )

    records = []

    # --------------------------------------------------------
    # METHOD 1
    # District and values on same line
    # --------------------------------------------------------

    direct_success = 0

    for item in district_lines:

        values = normalize_values(
            item["values"],
            expected_count
        )

        if values is None:
            continue

        if len(item["values"]) > 0:

            direct_success += 1

            for i, (
                crop,
                season,
                unit
            ) in enumerate(
                expected_columns
            ):

                records.append(
                    {
                        "district": item["district"],
                        "crop": crop,
                        "season": season,
                        "yield": values[i],
                        "unit": unit,
                        "year": "2024-25",
                        "source": (
                            "Tamil Nadu Department "
                            "of Economics and Statistics "
                            "- Districtwise Average "
                            "Yield Rates of Crops 2024-25"
                        ),
                        "source_page": page_number,
                    }
                )

    # If all 38 districts were extracted directly,
    # use that result.
    if direct_success == 38:

        return records, 38, "district-line extraction"

    # --------------------------------------------------------
    # METHOD 2
    # District names separated from numeric rows
    # --------------------------------------------------------

    numeric_rows = get_numeric_only_rows(
        text
    )

    valid_rows = []

    for row in numeric_rows:

        normalized = normalize_values(
            row,
            expected_count
        )

        if normalized is None:
            continue

        valid_rows.append(
            normalized
        )

        if len(valid_rows) == 38:
            break

    # Need exactly 38 districts and 38 numeric rows.
    if (
        len(district_lines) >= 38
        and len(valid_rows) >= 38
    ):

        records = []

        for i in range(38):

            district = DISTRICTS[i]

            values = valid_rows[i]

            for j, (
                crop,
                season,
                unit
            ) in enumerate(
                expected_columns
            ):

                records.append(
                    {
                        "district": district,
                        "crop": crop,
                        "season": season,
                        "yield": values[j],
                        "unit": unit,
                        "year": "2024-25",
                        "source": (
                            "Tamil Nadu Department "
                            "of Economics and Statistics "
                            "- Districtwise Average "
                            "Yield Rates of Crops 2024-25"
                        ),
                        "source_page": page_number,
                    }
                )

        return records, 38, "numeric-row extraction"

    return [], len(district_lines), "FAILED"


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("YieldROI - Official Yield Benchmark Extraction")
    print("=" * 70)

    print()
    print("Source:")
    print(PDF_PATH)

    if not PDF_PATH.exists():

        print()
        print("ERROR: PDF not found.")
        return

    OUTPUT_CSV.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    RAW_TEXT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    all_records = []
    report = []

    with pdfplumber.open(PDF_PATH) as pdf:

        print()
        print(
            f"Pages found: {len(pdf.pages)}"
        )

        # ----------------------------------------------------
        # Save raw text
        # ----------------------------------------------------

        with open(
            RAW_TEXT,
            "w",
            encoding="utf-8"
        ) as raw:

            for page_number, page in enumerate(
                pdf.pages,
                start=1
            ):

                text = page.extract_text() or ""

                raw.write(
                    "\n"
                    + "=" * 80
                    + "\n"
                )

                raw.write(
                    f"PAGE {page_number}\n"
                )

                raw.write(
                    "=" * 80
                    + "\n"
                )

                raw.write(text)
                raw.write("\n")

        # ----------------------------------------------------
        # Extract every page
        # ----------------------------------------------------

        for page_number, page in enumerate(
            pdf.pages,
            start=1
        ):

            text = page.extract_text() or ""

            records, districts_found, method = (
                build_records(
                    page_number,
                    text
                )
            )

            all_records.extend(
                records
            )

            status = (
                "PASS"
                if (
                    districts_found == 38
                    and len(records) ==
                    len(PAGE_COLUMNS[page_number]) * 38
                )
                else "CHECK"
            )

            print(
                f"Page {page_number:2d}/13... "
                f"{len(records):4d} records, "
                f"{districts_found:2d} districts, "
                f"method={method}, "
                f"{status}"
            )

            report.append(
                f"Page {page_number}: "
                f"{len(records)} records | "
                f"{districts_found} districts | "
                f"{method} | "
                f"{status}"
            )

    # ========================================================
    # DATAFRAME
    # ========================================================

    df = pd.DataFrame(
        all_records
    )

    if df.empty:

        print()
        print(
            "ERROR: No benchmark records extracted."
        )
        return

    # Remove duplicates.
    df = df.drop_duplicates(
        subset=[
            "district",
            "crop",
            "season",
            "year"
        ]
    )

    df = df.sort_values(
        by=[
            "district",
            "crop",
            "season"
        ]
    ).reset_index(
        drop=True
    )

    # ========================================================
    # VALIDATION
    # ========================================================

    expected_records = sum(
        len(PAGE_COLUMNS[p]) * 38
        for p in PAGE_COLUMNS
    )

    actual_records = len(df)

    districts_found = sorted(
        df["district"].unique()
    )

    missing_districts = [
        d
        for d in DISTRICTS
        if d not in districts_found
    ]

    crop_count = df[
        "crop"
    ].nunique()

    season_count = df[
        "season"
    ].nunique()

    # ========================================================
    # SAVE CSV
    # ========================================================

    df.to_csv(
        OUTPUT_CSV,
        index=False,
        encoding="utf-8-sig"
    )

    # ========================================================
    # REPORT
    # ========================================================

    with open(
        REPORT,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "YieldROI - Official Yield Benchmark "
            "Extraction Report\n"
        )

        f.write(
            "=" * 70
            + "\n\n"
        )

        f.write(
            f"Source: {PDF_PATH.name}\n"
        )

        f.write(
            "Reference year: 2024-25\n\n"
        )

        f.write(
            f"Expected records: "
            f"{expected_records}\n"
        )

        f.write(
            f"Actual records: "
            f"{actual_records}\n"
        )

        f.write(
            f"Districts: "
            f"{len(districts_found)}\n"
        )

        f.write(
            f"Crops: "
            f"{crop_count}\n"
        )

        f.write(
            f"Seasons: "
            f"{season_count}\n\n"
        )

        f.write(
            "PAGE RESULTS\n"
        )

        f.write(
            "-" * 50
            + "\n"
        )

        for line in report:

            f.write(
                line + "\n"
            )

        f.write("\n")

        if missing_districts:

            f.write(
                "MISSING DISTRICTS\n"
            )

            for district in missing_districts:

                f.write(
                    f"- {district}\n"
                )

        else:

            f.write(
                "DISTRICT COVERAGE: PASS\n"
            )

        f.write("\n")

        f.write(
            "CROP COUNTS\n"
        )

        f.write(
            "-" * 50
            + "\n"
        )

        for crop, count in (
            df["crop"]
            .value_counts()
            .sort_index()
            .items()
        ):

            f.write(
                f"{crop}: {count}\n"
            )

    # ========================================================
    # FINAL DISPLAY
    # ========================================================

    print()
    print("=" * 70)
    print(
        "OFFICIAL YIELD BENCHMARK EXTRACTION COMPLETE"
    )
    print("=" * 70)

    print()
    print(
        f"Records       : {actual_records:,}"
    )

    print(
        f"Expected      : {expected_records:,}"
    )

    print(
        f"Districts     : {len(districts_found)}"
    )

    print(
        f"Crops         : {crop_count}"
    )

    print(
        f"Seasons       : {season_count}"
    )

    print()

    if not missing_districts:

        print(
            "PASS - all 38 districts detected."
        )

    else:

        print(
            "WARNING - missing districts:"
        )

        for district in missing_districts:
            print(
                f"  - {district}"
            )

    print()

    if actual_records == expected_records:

        print(
            "PASS - complete benchmark structure extracted."
        )

    else:

        print(
            "WARNING - benchmark records are still missing."
        )

    print()

    print("Output files:")
    print(
        f"  CSV    : {OUTPUT_CSV}"
    )
    print(
        f"  Raw    : {RAW_TEXT}"
    )
    print(
        f"  Report : {REPORT}"
    )

    print()

    print("First 10 records:")

    print(
        df.head(10).to_string(
            index=False
        )
    )

    print()
    print("=" * 70)


if __name__ == "__main__":
    main()