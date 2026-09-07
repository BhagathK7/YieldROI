"""
YieldROI - Official Yield Benchmark Builder

Source:
Tamil Nadu Department of Economics and Statistics
TABLE - V A
DISTRICTWISE AVERAGE YIELD RATES OF THE CROPS FOR THE YEAR 2024-25

Input:
    data/averageyieldrateofcrops.pdf

Output:
    data/official_yield_benchmarks.csv

NOTE:
The PDF is a structured government table. This script extracts the
table using pdfplumber and keeps only clearly identified crop columns.
"""

from pathlib import Path
import re
import pandas as pd
import pdfplumber


# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

PDF_PATH = PROJECT_ROOT / "data" / "averageyieldrateofcrops.pdf"
OUTPUT_PATH = PROJECT_ROOT / "data" / "official_yield_benchmarks.csv"


# ---------------------------------------------------------
# DISTRICTS
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# TEXT NORMALIZATION
# ---------------------------------------------------------

def normalize_text(value):
    if value is None:
        return ""

    value = str(value)
    value = value.replace("\n", " ")
    value = re.sub(r"\s+", " ", value)

    return value.strip()


# ---------------------------------------------------------
# EXTRACT PDF TEXT
# ---------------------------------------------------------

def extract_pdf_text():

    if not PDF_PATH.exists():
        raise FileNotFoundError(
            f"PDF not found:\n{PDF_PATH}\n\n"
            "Place averageyieldrateofcrops.pdf inside the data folder."
        )

    print("Reading official yield benchmark PDF...")
    print(PDF_PATH)

    all_text = []

    with pdfplumber.open(PDF_PATH) as pdf:

        print(f"Pages found: {len(pdf.pages)}")

        for page_number, page in enumerate(pdf.pages, start=1):

            text = page.extract_text()

            if text:
                all_text.append(
                    f"\n--- PAGE {page_number} ---\n{text}"
                )

    return "\n".join(all_text)


# ---------------------------------------------------------
# SAVE RAW EXTRACTED TEXT
# ---------------------------------------------------------

def save_raw_text(text):

    output = PROJECT_ROOT / "results" / "yield_benchmark_raw_text.txt"

    output.parent.mkdir(parents=True, exist_ok=True)

    output.write_text(
        text,
        encoding="utf-8"
    )

    print(f"\nRaw extracted text saved:")
    print(output)


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    print("=" * 70)
    print("YieldROI - Official Yield Benchmark Extraction")
    print("=" * 70)

    text = extract_pdf_text()

    save_raw_text(text)

    print("\nExtraction completed.")
    print("\nIMPORTANT:")
    print(
        "The first stage only extracts and preserves the official PDF text."
    )

    print(
        "\nWe are NOT automatically assigning numerical values to crops yet."
    )

    print(
        "This prevents incorrect crop-column mapping from entering the "
        "research dataset."
    )

    print("\nDistricts expected:", len(DISTRICTS))

    found_districts = []

    for district in DISTRICTS:

        if re.search(
            rf"\b{re.escape(district)}\b",
            text,
            flags=re.IGNORECASE
        ):
            found_districts.append(district)

    print("Districts detected:", len(found_districts))

    missing = [
        district
        for district in DISTRICTS
        if district not in found_districts
    ]

    if missing:

        print("\nWARNING - Districts not detected:")

        for district in missing:
            print(" -", district)

    else:

        print(
            "\nSUCCESS - All 38 Tamil Nadu districts were detected."
        )

    print("\nNext step:")
    print(
        "We will inspect the extracted table structure and then create "
        "official_yield_benchmarks.csv."
    )


if __name__ == "__main__":
    main()