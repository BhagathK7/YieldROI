"""
YieldROI - Real Laboratory Soil Sample Loader

Loads the real Dharmapuri laboratory-tested soil dataset.

Source:
Physico-chemical properties of soil samples from Dharmapuri,
Tamil Nadu, India.

IMPORTANT:
- No synthetic soil values are generated.
- Only values present in the original source file are used.
- The loader supports the original extracted dataset structure.
"""

from pathlib import Path
import re
import pandas as pd


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

SOIL_ROOT = (
    PROJECT_ROOT
    / "fertilizer"
    / "soil_samples"
    / "dharmapuri"
)


# ============================================================
# HELPERS
# ============================================================

def normalize_name(value):

    if value is None:
        return ""

    text = str(value).strip().lower()

    text = (
        text
        .replace("%", " percent ")
        .replace("²", "2")
        .replace("₃", "3")
    )

    return re.sub(
        r"[^a-z0-9]+",
        "_",
        text
    ).strip("_")


def clean_sample_id(value):

    if value is None:
        return ""

    try:
        if pd.isna(value):
            return ""
    except Exception:
        pass

    text = str(value).strip()

    if text.endswith(".0"):

        try:

            number = float(text)

            if number.is_integer():
                return str(int(number))

        except Exception:
            pass

    return text


def to_number(value):

    if value is None:
        return None

    try:
        if pd.isna(value):
            return None
    except Exception:
        pass

    if isinstance(value, str):

        value = value.strip()

        # Extract the first numeric value if units
        # are included in the cell.
        match = re.search(
            r"-?\d+(?:\.\d+)?",
            value.replace(",", "")
        )

        if match:
            value = match.group(0)

    try:

        number = pd.to_numeric(
            value,
            errors="coerce"
        )

        if pd.isna(number):
            return None

        return float(number)

    except Exception:
        return None


def clean_text(value):

    if value is None:
        return None

    try:
        if pd.isna(value):
            return None
    except Exception:
        pass

    text = str(value).strip()

    return text if text else None


# ============================================================
# COLUMN ALIASES
# ============================================================

COLUMN_ALIASES = {

    "sample_id": [
        "sample_no",
        "sample",
        "sample_id",
        "sample_number",
        "sample_code",
        "sample_name"
    ],

    "latitude": [
        "latitude",
        "lat",
        "gps_latitude",
        "gps_lat"
    ],

    "longitude": [
        "longitude",
        "lon",
        "long",
        "gps_longitude",
        "gps_long"
    ],

    "ph": [
        "ph",
        "soil_ph"
    ],

    "ec": [
        "ec",
        "ec_ds_m",
        "electrical_conductivity"
    ],

    "sand": [
        "sand",
        "sand_percent",
        "sand_percentage"
    ],

    "silt": [
        "silt",
        "silt_percent",
        "silt_percentage"
    ],

    "clay": [
        "clay",
        "clay_percent",
        "clay_percentage"
    ],

    "texture": [
        "textural_class",
        "textural_classification",
        "texture",
        "soil_texture"
    ],

    "bulk_density": [
        "bd",
        "bulk_density",
        "bulk_density_mg_m3",
        "bulk_density_g_cm3"
    ],

    "whc": [
        "whc",
        "water_holding_capacity",
        "water_holding_capacity_percent"
    ],

    "organic_carbon": [
        "oc_g_kg",
        "oc",
        "organic_carbon",
        "organic_carbon_g_kg",
        "organic_carbon_percent"
    ],

    "caco3": [
        "caco3",
        "ca_co3",
        "calcium_carbonate"
    ],

    "available_n": [
        "avn",
        "available_n",
        "available_nitrogen",
        "available_n_kg_ha",
        "n_kg_ha"
    ],

    "available_p": [
        "avp",
        "available_p",
        "available_phosphorus",
        "available_p_kg_ha",
        "p_kg_ha"
    ],

    "available_k": [
        "avk",
        "available_k",
        "available_potassium",
        "available_k_kg_ha",
        "k_kg_ha"
    ],

    "firka": [
        "firka",
        "firka_name"
    ],

    "depth": [
        "depth",
        "soil_depth",
        "depth_cm"
    ]
}


NUMERIC_COLUMNS = [
    "latitude",
    "longitude",
    "ph",
    "ec",
    "sand",
    "silt",
    "clay",
    "bulk_density",
    "whc",
    "organic_carbon",
    "caco3",
    "available_n",
    "available_p",
    "available_k"
]


# ============================================================
# COLUMN FINDER
# ============================================================

def find_column(dataframe, aliases):

    columns = {
        normalize_name(column): column
        for column in dataframe.columns
    }

    for alias in aliases:

        normalized = normalize_name(alias)

        if normalized in columns:
            return columns[normalized]

    return None


# ============================================================
# SOIL SAMPLE LOADER
# ============================================================

class DharmapuriSoilSamples:

    def __init__(self, root=SOIL_ROOT):

        self.root = Path(root)

        self.data = self._load()

    # ========================================================
    # DISCOVER FILES
    # ========================================================

    def _discover_files(self):

        if not self.root.exists():

            print(
                "[Soil Loader] Soil directory not found:"
            )

            print(
                f"    {self.root}"
            )

            return []

        files = []

        for path in self.root.rglob("*"):

            if not path.is_file():
                continue

            if path.name.startswith("~$"):
                continue

            if path.suffix.lower() in {
                ".csv",
                ".xlsx",
                ".xls"
            }:

                files.append(path)

        return sorted(
            set(files),
            key=lambda x: str(x).lower()
        )

    # ========================================================
    # READ FILE
    # ========================================================

    def _read_file(self, path):

        try:

            suffix = path.suffix.lower()

            if suffix == ".csv":

                # The original Dharmapuri Tables.csv has:
                #
                # Row 0 -> table title
                # Row 1 -> actual column headers
                # Row 2 -> units
                # Row 3+ -> samples
                #
                # Therefore we use header=1 and skip row 2.

                dataframe = pd.read_csv(
                    path,
                    header=1,
                    skiprows=[2],
                    encoding="utf-8"
                )

                return dataframe

            if suffix in {
                ".xlsx",
                ".xls"
            }:

                return pd.read_excel(
                    path
                )

        except UnicodeDecodeError:

            try:

                return pd.read_csv(
                    path,
                    header=1,
                    skiprows=[2],
                    encoding="latin1"
                )

            except Exception as exc:

                print(
                    f"[Soil Loader] Could not read "
                    f"{path.name}: {exc}"
                )

        except Exception as exc:

            print(
                f"[Soil Loader] Could not read "
                f"{path.name}: {exc}"
            )

        return None

    # ========================================================
    # NORMALIZE DATAFRAME
    # ========================================================

    def _normalize_dataframe(
        self,
        dataframe,
        source_path
    ):

        if dataframe is None:
            return None

        if dataframe.empty:
            return None

        dataframe = dataframe.dropna(
            axis=0,
            how="all"
        ).copy()

        dataframe = dataframe.dropna(
            axis=1,
            how="all"
        ).copy()

        if dataframe.empty:
            return None

        print(
            f"[Soil Loader] Inspecting: "
            f"{source_path.name}"
        )

        print(
            "[Soil Loader] Columns:",
            list(dataframe.columns)
        )

        # ====================================================
        # SAMPLE ID
        # ====================================================

        sample_column = find_column(
            dataframe,
            COLUMN_ALIASES["sample_id"]
        )

        if sample_column is None:

            print(
                f"[Soil Loader] Skipping "
                f"{source_path.name}: "
                "Sample ID column not found."
            )

            return None

        # ====================================================
        # BUILD STANDARD DATAFRAME
        # ====================================================

        output = pd.DataFrame(
            index=dataframe.index
        )

        for target, aliases in COLUMN_ALIASES.items():

            source_column = find_column(
                dataframe,
                aliases
            )

            if source_column is None:

                output[target] = None

            else:

                output[target] = (
                    dataframe[source_column]
                )

        # ====================================================
        # SAMPLE IDs
        # ====================================================

        output["sample_id"] = (
            dataframe[sample_column]
            .map(clean_sample_id)
        )
        
            # ====================================================
    # KEEP ONLY REAL SAMPLE IDs
    # ====================================================
    #
    # The original Tables.csv contains multiple tables,
    # repeated headers, units and descriptive statistics.
    # Only IDs such as M1, M2, M3 ... are actual samples.
    #
    # Do NOT treat "Sample no", blank rows, or statistics
    # rows as soil samples.

        output = output[
            output["sample_id"]
            .astype(str)
            .str.fullmatch(
                r"[A-Za-z]+[0-9]+",
                na=False
            )
        ].copy()

        output = output[
            output["sample_id"]
            .astype(str)
            .str.strip()
            != ""
        ].copy()

        if output.empty:
            return None

        # ====================================================
        # NUMERIC FIELDS
        # ====================================================

        for column in NUMERIC_COLUMNS:

            output[column] = (
                output[column]
                .map(to_number)
            )

        # ====================================================
        # TEXT FIELDS
        # ====================================================

        for column in [
            "texture",
            "firka",
            "depth"
        ]:

            output[column] = (
                output[column]
                .map(clean_text)
            )

        # ====================================================
        # DISTRICT
        # ====================================================

        output["district"] = "Dharmapuri"

        # ====================================================
        # SOURCE FILE
        # ====================================================

        try:

            output["source_file"] = str(
                source_path.relative_to(
                    self.root
                )
            )

        except ValueError:

            output["source_file"] = (
                source_path.name
            )

        print(
            f"[Soil Loader] Loaded "
            f"{len(output)} samples from "
            f"{source_path.name}"
        )

        return output

    # ========================================================
    # LOAD
    # ========================================================

    def _load(self):

        files = self._discover_files()

        if not files:

            print(
                "[Soil Loader] No soil data files found."
            )

            return pd.DataFrame()

        print(
            f"[Soil Loader] Found "
            f"{len(files)} data file(s)."
        )

        frames = []

        for path in files:

            dataframe = self._read_file(
                path
            )

            normalized = (
                self._normalize_dataframe(
                    dataframe,
                    path
                )
            )

            if normalized is not None:

                frames.append(
                    normalized
                )

        if not frames:

            print(
                "[Soil Loader] No valid soil "
                "sample tables found."
            )

            return pd.DataFrame()

        result = pd.concat(
            frames,
            ignore_index=True
        )

        # ====================================================
        # REMOVE DUPLICATE SAMPLE IDs
        # ====================================================

        result = result.drop_duplicates(
            subset=["sample_id"],
            keep="first"
        )

        result = result.reset_index(
            drop=True
        )

        print(
            "[Soil Loader] FINAL SAMPLE COUNT:",
            len(result)
        )

        return result

    # ========================================================
    # REFRESH
    # ========================================================

    def refresh(self):

        self.data = self._load()

        return self.data

    # ========================================================
    # STATUS
    # ========================================================

    def is_available(self):

        return not self.data.empty

    # ========================================================
    # COUNT
    # ========================================================

    def count(self):

        return int(
            len(self.data)
        )

    # ========================================================
    # SAMPLE IDS
    # ========================================================

    def sample_ids(self):

        if self.data.empty:
            return []

        return (
            self.data["sample_id"]
            .astype(str)
            .tolist()
        )

    # ========================================================
    # LIST SAMPLES
    # ========================================================

    def list_samples(self):

        if self.data.empty:
            return []

        samples = []

        for _, row in self.data.iterrows():

            samples.append({

                "sample_id":
                    str(
                        row.get(
                            "sample_id",
                            ""
                        )
                    ),

                "district":
                    "Dharmapuri",

                "firka":
                    self._safe_text(
                        row.get("firka")
                    ),

                "latitude":
                    self._safe_number(
                        row.get("latitude")
                    ),

                "longitude":
                    self._safe_number(
                        row.get("longitude")
                    ),

                "depth":
                    self._safe_text(
                        row.get("depth")
                    )
            })

        return samples

    # ========================================================
    # GET SAMPLE
    # ========================================================

    def get(self, sample_id):

        if not sample_id:
            return None

        if self.data.empty:
            return None

        requested = (
            str(sample_id)
            .strip()
            .lower()
        )

        rows = self.data[
            self.data["sample_id"]
            .astype(str)
            .str.strip()
            .str.lower()
            == requested
        ]

        if rows.empty:
            return None

        row = rows.iloc[0]

        result = {}

        for key, value in row.items():

            if value is None:

                result[key] = None
                continue

            try:

                if pd.isna(value):

                    result[key] = None
                    continue

            except Exception:
                pass

            if hasattr(value, "item"):

                try:

                    result[key] = value.item()
                    continue

                except Exception:
                    pass

            result[key] = value

        return result

    # ========================================================
    # SAFE NUMBER
    # ========================================================

    @staticmethod
    def _safe_number(value):

        if value is None:
            return None

        try:

            if pd.isna(value):
                return None

        except Exception:
            pass

        try:

            return float(value)

        except (
            ValueError,
            TypeError
        ):

            return None

    # ========================================================
    # SAFE TEXT
    # ========================================================

    @staticmethod
    def _safe_text(value):

        if value is None:
            return None

        try:

            if pd.isna(value):
                return None

        except Exception:
            pass

        return str(value).strip()

    # ========================================================
    # NUTRIENT STATUS
    # ========================================================

    @staticmethod
    def nutrient_status(
        nutrient,
        value
    ):

        if value is None:
            return "No Data"

        try:

            value = float(value)

        except (
            ValueError,
            TypeError
        ):

            return "No Data"

        nutrient_key = normalize_name(
            nutrient
        )

        # Nitrogen
        if nutrient_key in {
            "n",
            "nitrogen",
            "available_n",
            "available_nitrogen"
        }:

            if value < 280:
                return "Low"

            if value <= 450:
                return "Medium"

            return "High"

        # Phosphorus
        if nutrient_key in {
            "p",
            "phosphorus",
            "available_p",
            "available_phosphorus",
            "p2o5"
        }:

            if value < 11:
                return "Low"

            if value <= 22:
                return "Medium"

            return "High"

        # Potassium
        if nutrient_key in {
            "k",
            "potassium",
            "available_k",
            "available_potassium"
        }:

            if value < 118:
                return "Low"

            if value <= 280:
                return "Medium"

            return "High"

        # Organic Carbon
        if nutrient_key in {
            "oc",
            "organic_carbon",
            "organic_carbon_percent",
            "soc"
        }:

            if value < 0.50:
                return "Low"

            if value <= 0.75:
                return "Medium"

            return "High"

        return "No Data"

    # ========================================================
    # SOIL SUMMARY
    # ========================================================

    def soil_summary(self, sample_id):

        sample = self.get(
            sample_id
        )

        if sample is None:
            return None

        return {

            "sample_id":
                sample.get("sample_id"),

            "district":
                sample.get("district"),

            "firka":
                sample.get("firka"),

            "latitude":
                sample.get("latitude"),

            "longitude":
                sample.get("longitude"),

            "depth":
                sample.get("depth"),

            "ph":
                sample.get("ph"),

            "ec":
                sample.get("ec"),

            "sand":
                sample.get("sand"),

            "silt":
                sample.get("silt"),

            "clay":
                sample.get("clay"),

            "texture":
                sample.get("texture"),

            "bulk_density":
                sample.get("bulk_density"),

            "whc":
                sample.get("whc"),

            "organic_carbon":
                sample.get("organic_carbon"),

            "caco3":
                sample.get("caco3"),

            "available_n":
                sample.get("available_n"),

            "available_p":
                sample.get("available_p"),

            "available_k":
                sample.get("available_k"),

            "nitrogen_status":
                self.nutrient_status(
                    "available_n",
                    sample.get("available_n")
                ),

            "phosphorus_status":
                self.nutrient_status(
                    "available_p",
                    sample.get("available_p")
                ),

            "potassium_status":
                self.nutrient_status(
                    "available_k",
                    sample.get("available_k")
                ),

            "organic_carbon_status":
                self.nutrient_status(
                    "organic_carbon",
                    sample.get("organic_carbon")
                )
        }


# ============================================================
# TEST
# ============================================================

def main():

    print()
    print("=" * 60)
    print("YieldROI - Dharmapuri Soil Sample Loader")
    print("=" * 60)
    print()

    print(
        "Soil root:",
        SOIL_ROOT
    )

    print()

    loader = DharmapuriSoilSamples()

    print()

    print(
        "Samples loaded:",
        loader.count()
    )

    print()

    for sample in loader.list_samples()[:10]:

        print(sample)

    print()

    # Show a complete real sample
    if loader.sample_ids():

        first_id = loader.sample_ids()[0]

        print(
            f"First sample ({first_id}) full data:"
        )

        print(
            loader.get(first_id)
        )

    print()

    if loader.is_available():

        print(
            "STATUS: REAL SOIL SAMPLES AVAILABLE"
        )

    else:

        print(
            "STATUS: NO SOIL SAMPLES AVAILABLE"
        )

    print()


if __name__ == "__main__":
    main()