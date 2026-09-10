"""
YieldROI - Fertilizer Recommendation Engine

Uses:
    1. Tamil Nadu soil-status profiles
    2. TNAU fertilizer recommendation knowledge base
    3. District/block applicability rules

The fertilizer recommendation is knowledge/rule based.
"""

from pathlib import Path
import pandas as pd
import re


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

SOIL_PROFILE_FILE = (
    PROJECT_ROOT / "fertilizer" / "final_soil_profiles.csv"
)

KNOWLEDGE_BASE_FILE = (
    PROJECT_ROOT / "fertilizer" / "fertilizer_knowledge_base.csv"
)


# ============================================================
# TEXT UTILITIES
# ============================================================

def normalize_text(value):
    """Normalize text for reliable comparisons."""

    if pd.isna(value):
        return ""

    text = str(value).strip().lower()

    text = text.replace("_", " ")
    text = text.replace("-", " ")

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def normalize_column(column):
    """Normalize a dataframe column name."""

    return (
        str(column)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
    )


def find_column(df, names):
    """Find a column using possible column names."""

    columns = {
        normalize_column(col): col
        for col in df.columns
    }

    for name in names:

        key = normalize_column(name)

        if key in columns:
            return columns[key]

    return None


def split_values(value):
    """
    Split applicability fields.

    Supports:
        A|B
        A,B
        A;B
    """

    if pd.isna(value):
        return []

    text = str(value).strip()

    if not text:
        return []

    parts = re.split(r"[|;,]", text)

    return [
        normalize_text(part)
        for part in parts
        if normalize_text(part)
    ]


def contains_value(value, allowed):
    """Check whether normalized value exists in allowed values."""

    value = normalize_text(value)

    if not value:
        return False

    if "*" in allowed:
        return True

    return value in allowed


# ============================================================
# RECOMMENDER
# ============================================================

class FertilizerRecommender:

    def __init__(
        self,
        soil_profile_file=SOIL_PROFILE_FILE,
        knowledge_base_file=KNOWLEDGE_BASE_FILE
    ):

        self.soil_profile_file = Path(
            soil_profile_file
        )

        self.knowledge_base_file = Path(
            knowledge_base_file
        )

        self.soil_profiles = None
        self.knowledge_base = None

        self.load_data()

    # ========================================================
    # LOAD DATA
    # ========================================================

    def load_data(self):

        if not self.soil_profile_file.exists():
            raise FileNotFoundError(
                f"Soil profile file not found:\n"
                f"{self.soil_profile_file}"
            )

        if not self.knowledge_base_file.exists():
            raise FileNotFoundError(
                f"Knowledge base file not found:\n"
                f"{self.knowledge_base_file}"
            )

        self.soil_profiles = pd.read_csv(
            self.soil_profile_file
        )

        self.knowledge_base = pd.read_csv(
            self.knowledge_base_file
        )

        self.soil_profiles.columns = [
            normalize_column(col)
            for col in self.soil_profiles.columns
        ]

        self.knowledge_base.columns = [
            normalize_column(col)
            for col in self.knowledge_base.columns
        ]

    # ========================================================
    # SOIL PROFILE
    # ========================================================

    def find_soil_profile(
        self,
        district,
        block=None,
        village=None,
        year=None
    ):
        """Find the best available soil profile."""

        df = self.soil_profiles.copy()

        district_col = find_column(
            df,
            ["district_name", "district"]
        )

        block_col = find_column(
            df,
            ["block_name", "block"]
        )

        village_col = find_column(
            df,
            ["village_name", "village"]
        )

        year_col = find_column(
            df,
            ["year"]
        )

        if district_col is None:
            raise ValueError(
                "District column not found in soil profile dataset."
            )

        district_value = normalize_text(
            district
        )

        df = df[
            df[district_col]
            .map(normalize_text)
            == district_value
        ]

        if df.empty:
            return None

        # ----------------------------------------------------
        # Block
        # ----------------------------------------------------

        if block and block_col:

            block_value = normalize_text(
                block
            )

            block_df = df[
                df[block_col]
                .map(normalize_text)
                == block_value
            ]

            if not block_df.empty:
                df = block_df

        # ----------------------------------------------------
        # Village
        # ----------------------------------------------------

        if village and village_col:

            village_value = normalize_text(
                village
            )

            village_df = df[
                df[village_col]
                .map(normalize_text)
                == village_value
            ]

            if not village_df.empty:
                df = village_df

        # ----------------------------------------------------
        # Requested year
        # ----------------------------------------------------

        if year is not None and year_col:

            try:

                requested_year = int(year)

                year_df = df[
                    pd.to_numeric(
                        df[year_col],
                        errors="coerce"
                    )
                    == requested_year
                ]

                if not year_df.empty:
                    df = year_df

            except (ValueError, TypeError):
                pass

        # ----------------------------------------------------
        # Otherwise latest year
        # ----------------------------------------------------

        elif year_col:

            numeric_year = pd.to_numeric(
                df[year_col],
                errors="coerce"
            )

            if numeric_year.notna().any():

                latest_year = numeric_year.max()

                latest_df = df[
                    numeric_year == latest_year
                ]

                if not latest_df.empty:
                    df = latest_df

        return df.iloc[0].to_dict()

    # ========================================================
    # SOIL STATUS
    # ========================================================

    def get_soil_status(
        self,
        profile,
        nutrient
    ):
        """Extract a nutrient's status."""

        mapping = {

            "nitrogen": [
                "nitrogen_status",
                "nitrogen_level",
                "nitrogen"
            ],

            "phosphorus": [
                "phosphorus_status",
                "phosphorus_level",
                "phosphorus"
            ],

            "potassium": [
                "potassium_status",
                "potassium_level",
                "potassium"
            ],

            "ph": [
                "soil_ph_status",
                "soil_ph_level",
                "soil_ph",
                "ph_status",
                "ph"
            ],

            "organic_carbon": [
                "organic_carbon_status",
                "organic_carbon_level",
                "organic_carbon"
            ],

            "electrical_conductivity": [
                "electrical_conductivity_status",
                "electrical_conductivity_level",
                "electrical_conductivity",
                "ec_status"
            ],

            "zinc": [
                "zinc_status",
                "zinc_level",
                "zinc"
            ],

            "boron": [
                "boron_status",
                "boron_level",
                "boron"
            ],

            "iron": [
                "iron_status",
                "iron_level",
                "iron"
            ],

            "manganese": [
                "manganese_status",
                "manganese_level",
                "manganese"
            ],

            "copper": [
                "copper_status",
                "copper_level",
                "copper"
            ],

            "sulphur": [
                "sulphur_status",
                "sulphur_level",
                "sulphur"
            ]
        }

        profile_normalized = {
            normalize_column(k): v
            for k, v in profile.items()
        }

        nutrient = normalize_text(
            nutrient
        )

        for candidate in mapping.get(
            nutrient,
            []
        ):

            key = normalize_column(
                candidate
            )

            if key in profile_normalized:

                value = profile_normalized[key]

                if not pd.isna(value):
                    return str(value)

        # Fallback search

        nutrient_key = nutrient.replace(
            " ",
            "_"
        )

        for key, value in profile_normalized.items():

            if nutrient_key in key:

                if (
                    "status" in key
                    or "level" in key
                ):

                    if not pd.isna(value):
                        return str(value)

        return "No Data"

    # ========================================================
    # SOIL SUMMARY
    # ========================================================

    def get_soil_summary(self, profile):

        nutrients = [
            "nitrogen",
            "phosphorus",
            "potassium",
            "ph",
            "organic_carbon",
            "electrical_conductivity",
            "zinc",
            "boron",
            "iron",
            "manganese",
            "copper",
            "sulphur"
        ]

        return {
            nutrient: self.get_soil_status(
                profile,
                nutrient
            )
            for nutrient in nutrients
        }

    # ========================================================
    # FIND CROP RULES
    # ========================================================

    def get_crop_rules(
        self,
        crop,
        variety_or_type=None
    ):

        crop_col = find_column(
            self.knowledge_base,
            [
                "crop",
                "crop_name"
            ]
        )

        if crop_col is None:
            raise ValueError(
                "Crop column not found in knowledge base."
            )

        crop_value = normalize_text(
            crop
        )

        rules = self.knowledge_base[
            self.knowledge_base[crop_col]
            .map(normalize_text)
            == crop_value
        ].copy()

        if rules.empty:
            return rules

        # ----------------------------------------------------
        # Match crop type if available
        # ----------------------------------------------------

        if variety_or_type:

            requested = normalize_text(
                variety_or_type
            )

            type_columns = [
                "variety",
                "crop_type",
                "type",
                "duration",
                "season_type",
                "applicability_type"
            ]

            for column_name in type_columns:

                type_col = find_column(
                    rules,
                    [column_name]
                )

                if type_col is None:
                    continue

                matches = rules[
                    rules[type_col]
                    .map(normalize_text)
                    .str.contains(
                        re.escape(requested),
                        na=False
                    )
                ]

                if not matches.empty:
                    rules = matches
                    break

        return rules

    # ========================================================
    # RULE SELECTION
    # ========================================================

    def select_rule(
        self,
        crop,
        district,
        block=None,
        variety_or_type=None
    ):
        """
        Select the correct recommendation.

        Priority:

        1. Exact block
        2. Exact district
        3. Crop-type applicability
        4. Other Tracts fallback
        5. General rule
        """

        rules = self.get_crop_rules(
            crop,
            variety_or_type
        )

        if rules.empty:

            return (
                None,
                "No recommendation rule exists for this crop."
            )

        district_norm = normalize_text(
            district
        )

        block_norm = normalize_text(
            block
        )

        block_col = find_column(
            rules,
            [
                "applicable_blocks",
                "applicable_block",
                "blocks"
            ]
        )

        district_col = find_column(
            rules,
            [
                "applicable_districts",
                "applicable_district",
                "districts"
            ]
        )

        type_col = find_column(
            rules,
            [
                "applicability_type",
                "application_type"
            ]
        )

        # ----------------------------------------------------
        # STEP 1: EXACT BLOCK MATCH
        # ----------------------------------------------------

        if block and block_col:

            for _, row in rules.iterrows():

                allowed_blocks = split_values(
                    row[block_col]
                )

                if contains_value(
                    block_norm,
                    allowed_blocks
                ):

                    return (
                        row,
                        f"Block '{block}' is explicitly "
                        f"covered by this recommendation."
                    )

        # ----------------------------------------------------
        # STEP 2: EXACT DISTRICT MATCH
        # ----------------------------------------------------

        if district_col:

            for _, row in rules.iterrows():

                allowed_districts = split_values(
                    row[district_col]
                )

                if contains_value(
                    district_norm,
                    allowed_districts
                ):

                    return (
                        row,
                        f"District '{district}' is explicitly "
                        f"covered by this recommendation."
                    )

        # ----------------------------------------------------
        # STEP 3: APPLICABILITY TYPE
        # ----------------------------------------------------

        if type_col:

            requested_type = normalize_text(
                variety_or_type
            )

            # Direct type match
            if requested_type:

                for _, row in rules.iterrows():

                    applicability = normalize_text(
                        row[type_col]
                    )

                    if (
                        requested_type in applicability
                        or applicability in requested_type
                    ):

                        # Do not accept a Cauvery Delta rule
                        # unless its block actually matched.
                        if (
                            "cauvery delta"
                            in applicability
                        ):
                            continue

                        return (
                            row,
                            f"Crop type '{variety_or_type}' "
                            f"matched the applicable rule."
                        )

            # ------------------------------------------------
            # Other Tracts
            # ------------------------------------------------

            for _, row in rules.iterrows():

                applicability = normalize_text(
                    row[type_col]
                )

                if (
                    "other tract" in applicability
                    or "other tracts" in applicability
                    or "general tract" in applicability
                ):

                    return (
                        row,
                        f"{district} / {block} is not listed "
                        f"under the specified Cauvery Delta "
                        f"blocks; the Other Tracts rate was "
                        f"selected."
                    )

        # ----------------------------------------------------
        # STEP 4: GENERAL RULE
        # ----------------------------------------------------

        for _, row in rules.iterrows():

            applicability = ""

            if type_col:
                applicability = normalize_text(
                    row[type_col]
                )

            if (
                not applicability
                or applicability in {
                    "general",
                    "all",
                    "all districts",
                    "all blocks"
                }
            ):

                return (
                    row,
                    "General crop recommendation selected."
                )

        # ----------------------------------------------------
        # FINAL SAFE FALLBACK
        # ----------------------------------------------------

        row = rules.iloc[0]

        return (
            row,
            "No location-specific rule matched; "
            "the first available validated crop rule "
            "was selected."
        )

    # ========================================================
    # EXTRACT NPK
    # ========================================================

    def extract_npk(self, rule):

        if rule is None:
            return {
                "nitrogen": None,
                "phosphorus": None,
                "potassium": None
            }

        values = {
            normalize_column(k): v
            for k, v in rule.items()
        }

        result = {
            "nitrogen": None,
            "phosphorus": None,
            "potassium": None
        }

        # ----------------------------------------------------
        # Direct column matching
        # ----------------------------------------------------

        aliases = {

            "nitrogen": [
                "nitrogen",
                "nitrogen_kg_ha",
                "n",
                "n_kg_ha",
                "recommended_n",
                "recommended_nitrogen",
                "n_rate"
            ],

            "phosphorus": [
                "phosphorus",
                "phosphorus_kg_ha",
                "p",
                "p_kg_ha",
                "p2o5",
                "p2o5_kg_ha",
                "recommended_p",
                "recommended_phosphorus",
                "p_rate"
            ],

            "potassium": [
                "potassium",
                "potassium_kg_ha",
                "k",
                "k_kg_ha",
                "k2o",
                "k2o_kg_ha",
                "recommended_k",
                "recommended_potassium",
                "k_rate"
            ]
        }

        for nutrient, candidates in aliases.items():

            for candidate in candidates:

                key = normalize_column(
                    candidate
                )

                if key in values:

                    value = values[key]

                    if pd.isna(value):
                        continue

                    try:

                        result[nutrient] = float(
                            value
                        )

                        break

                    except (
                        ValueError,
                        TypeError
                    ):
                        pass

        # ----------------------------------------------------
        # Search column names intelligently
        # ----------------------------------------------------

        search_patterns = {

            "nitrogen": [
                "nitrogen",
                "n_rate",
                "n_kg",
                "recommended_n"
            ],

            "phosphorus": [
                "phosphorus",
                "p2o5",
                "p_rate",
                "p_kg",
                "recommended_p"
            ],

            "potassium": [
                "potassium",
                "k2o",
                "k_rate",
                "k_kg",
                "recommended_k"
            ]
        }

        for nutrient, patterns in search_patterns.items():

            if result[nutrient] is not None:
                continue

            for column, value in values.items():

                if any(
                    pattern in column
                    for pattern in patterns
                ):

                    try:

                        if not pd.isna(value):

                            result[nutrient] = float(
                                value
                            )

                            break

                    except (
                        ValueError,
                        TypeError
                    ):
                        pass

        # ----------------------------------------------------
        # Search all string values for N:P:K
        # ----------------------------------------------------

        if any(
            result[x] is None
            for x in result
        ):

            for value in values.values():

                if pd.isna(value):
                    continue

                text = str(value)

                # Match:
                # 150:50:50
                # 150 : 50 : 50
                # 150-50-50
                # N 150 P 50 K 50

                match = re.search(
                    r"(\d+(?:\.\d+)?)"
                    r"\s*[:/\-]\s*"
                    r"(\d+(?:\.\d+)?)"
                    r"\s*[:/\-]\s*"
                    r"(\d+(?:\.\d+)?)",
                    text
                )

                if match:

                    numbers = [
                        float(match.group(1)),
                        float(match.group(2)),
                        float(match.group(3))
                    ]

                    if result["nitrogen"] is None:
                        result["nitrogen"] = numbers[0]

                    if result["phosphorus"] is None:
                        result["phosphorus"] = numbers[1]

                    if result["potassium"] is None:
                        result["potassium"] = numbers[2]

                    break

        return result

    # ========================================================
    # FERTILIZER PRODUCT CALCULATION
    # ========================================================

    @staticmethod
    def calculate_fertilizer_products(
        nitrogen,
        phosphorus,
        potassium
    ):
        """
        Convert the recommended N-P2O5-K2O requirement
        into commercial fertilizer quantities.

        Fertilizer grades:
            DAP  = 18-46-0
            Urea = 46-0-0
            MOP  = 0-0-60

        Calculation:
            1. DAP satisfies the P2O5 requirement.
            2. Nitrogen supplied by DAP is deducted.
            3. Urea supplies the remaining nitrogen.
            4. MOP supplies the required K2O.

        This is deterministic nutrient balancing.
        It is NOT an ML prediction.
        """

        values = {
            "nitrogen": nitrogen,
            "phosphorus": phosphorus,
            "potassium": potassium
        }

        for name, value in values.items():

            if value is None:
                raise ValueError(
                    f"{name.title()} requirement is missing."
                )

            try:

                numeric = float(value)

            except (ValueError, TypeError):

                raise ValueError(
                    f"{name.title()} requirement "
                    f"is not numeric."
                )

            if numeric < 0:
                raise ValueError(
                    f"{name.title()} requirement "
                    f"cannot be negative."
                )

            values[name] = numeric

        nitrogen_required = values["nitrogen"]
        phosphorus_required = values["phosphorus"]
        potassium_required = values["potassium"]

        # ----------------------------------------------------
        # Fertilizer nutrient percentages
        # ----------------------------------------------------

        DAP_N = 0.18
        DAP_P2O5 = 0.46

        UREA_N = 0.46

        MOP_K2O = 0.60

        # ----------------------------------------------------
        # DAP
        # ----------------------------------------------------

        dap_kg = (
            phosphorus_required / DAP_P2O5
            if phosphorus_required > 0
            else 0.0
        )

        nitrogen_from_dap = dap_kg * DAP_N

        # ----------------------------------------------------
        # Urea
        # ----------------------------------------------------

        remaining_nitrogen = max(
            nitrogen_required - nitrogen_from_dap,
            0.0
        )

        urea_kg = (
            remaining_nitrogen / UREA_N
            if remaining_nitrogen > 0
            else 0.0
        )

        # ----------------------------------------------------
        # MOP
        # ----------------------------------------------------

        mop_kg = (
            potassium_required / MOP_K2O
            if potassium_required > 0
            else 0.0
        )

        # ----------------------------------------------------
        # Final nutrient balance
        # ----------------------------------------------------

        supplied_nitrogen = (
            nitrogen_from_dap
            + (urea_kg * UREA_N)
        )

        supplied_phosphorus = (
            dap_kg * DAP_P2O5
        )

        supplied_potassium = (
            mop_kg * MOP_K2O
        )

        return {

            "method": (
                "DAP first for P2O5, Urea for remaining N, "
                "and MOP for K2O."
            ),

            "fertilizer_grades": {
                "DAP": "18-46-0",
                "Urea": "46-0-0",
                "MOP": "0-0-60"
            },

            "products": [

                {
                    "name": "DAP",
                    "grade": "18-46-0",
                    "kg_per_ha": round(
                        dap_kg,
                        2
                    ),
                    "nutrient_contribution": {
                        "N_kg": round(
                            nitrogen_from_dap,
                            2
                        ),
                        "P2O5_kg": round(
                            supplied_phosphorus,
                            2
                        ),
                        "K2O_kg": 0.0
                    }
                },

                {
                    "name": "Urea",
                    "grade": "46-0-0",
                    "kg_per_ha": round(
                        urea_kg,
                        2
                    ),
                    "nutrient_contribution": {
                        "N_kg": round(
                            urea_kg * UREA_N,
                            2
                        ),
                        "P2O5_kg": 0.0,
                        "K2O_kg": 0.0
                    }
                },

                {
                    "name": "MOP",
                    "grade": "0-0-60",
                    "kg_per_ha": round(
                        mop_kg,
                        2
                    ),
                    "nutrient_contribution": {
                        "N_kg": 0.0,
                        "P2O5_kg": 0.0,
                        "K2O_kg": round(
                            supplied_potassium,
                            2
                        )
                    }
                }

            ],

            "required_npk": {
                "N_kg_per_ha": round(
                    nitrogen_required,
                    2
                ),
                "P2O5_kg_per_ha": round(
                    phosphorus_required,
                    2
                ),
                "K2O_kg_per_ha": round(
                    potassium_required,
                    2
                )
            },

            "supplied_npk": {
                "N_kg_per_ha": round(
                    supplied_nitrogen,
                    2
                ),
                "P2O5_kg_per_ha": round(
                    supplied_phosphorus,
                    2
                ),
                "K2O_kg_per_ha": round(
                    supplied_potassium,
                    2
                )
            },

            "balance_check": {
                "nitrogen_difference": round(
                    supplied_nitrogen
                    - nitrogen_required,
                    6
                ),
                "phosphorus_difference": round(
                    supplied_phosphorus
                    - phosphorus_required,
                    6
                ),
                "potassium_difference": round(
                    supplied_potassium
                    - potassium_required,
                    6
                )
            }
        }

    # ========================================================
    # MAIN RECOMMENDATION
    # ========================================================

    def recommend(
        self,
        district,
        block,
        crop,
        variety_or_type=None,
        village=None,
        year=None
    ):

        if not district:
            raise ValueError(
                "District is required."
            )

        if not crop:
            raise ValueError(
                "Crop is required."
            )

        # ----------------------------------------------------
        # Soil profile
        # ----------------------------------------------------

        profile = self.find_soil_profile(
            district=district,
            block=block,
            village=village,
            year=year
        )

        if profile is None:

            soil_summary = {}

            soil_message = (
                f"No soil profile found for "
                f"{district}"
            )

            if block:
                soil_message += (
                    f" / {block}"
                )

        else:

            soil_summary = self.get_soil_summary(
                profile
            )

            soil_message = (
                "Matching Tamil Nadu soil-status "
                "profile found."
            )

        # ----------------------------------------------------
        # Select fertilizer rule
        # ----------------------------------------------------

        rule, reason = self.select_rule(
            crop=crop,
            district=district,
            block=block,
            variety_or_type=variety_or_type
        )

        if rule is None:

            return {
                "status": "not_available",

                "district": district,
                "block": block,
                "village": village,

                "crop": crop,
                "variety_or_type": variety_or_type,

                "soil_profile_found": (
                    profile is not None
                ),

                "soil_summary": soil_summary,

                "recommendation_available": False,

                "message": (
                    f"No validated fertilizer "
                    f"recommendation is available "
                    f"for {crop}."
                ),

                "applicability_reason": reason
            }

        # ----------------------------------------------------
        # NPK
        # ----------------------------------------------------

        npk = self.extract_npk(
            rule
        )

        # ----------------------------------------------------
        # Fertilizer product quantities
        # ----------------------------------------------------

        fertilizer_products = None

        if (
            npk["nitrogen"] is not None
            and npk["phosphorus"] is not None
            and npk["potassium"] is not None
        ):

            fertilizer_products = (
                self.calculate_fertilizer_products(
                    nitrogen=npk["nitrogen"],
                    phosphorus=npk["phosphorus"],
                    potassium=npk["potassium"]
                )
            )

        # ----------------------------------------------------
        # Metadata
        # ----------------------------------------------------

        rule_dict = rule.to_dict()

        source = (
            rule_dict.get("source")
            or rule_dict.get("reference")
            or rule_dict.get("source_reference")
            or "TNAU fertilizer recommendation"
        )

        applicability_type = (
            rule_dict.get(
                "applicability_type"
            )
            or ""
        )

        # ----------------------------------------------------
        # Result
        # ----------------------------------------------------

        return {

            "status": "success",

            "district": district,
            "block": block,
            "village": village,

            "crop": crop,
            "variety_or_type": variety_or_type,

            "soil_profile_found": (
                profile is not None
            ),

            "soil_message": soil_message,

            "soil_summary": soil_summary,

            "recommendation_available": True,

            "nitrogen_kg_per_ha": npk[
                "nitrogen"
            ],

            "phosphorus_kg_per_ha": npk[
                "phosphorus"
            ],

            "potassium_kg_per_ha": npk[
                "potassium"
            ],

            # NEW:
            # Commercial fertilizer quantities
            "fertilizer_products": fertilizer_products,

            "applicability_type": (
                applicability_type
            ),

            "applicability_reason": reason,

            "source": source,

            "basis": (
                "Tamil Nadu soil-status data + "
                "TNAU fertilizer recommendation rules "
                "+ deterministic fertilizer product calculation"
            )
        }


# ============================================================
# DISPLAY
# ============================================================

def print_recommendation(result):

    print("\n" + "=" * 65)

    print(
        "             YIELDROI FERTILIZER RECOMMENDATION"
    )

    print("=" * 65)

    print(
        f"\nDistrict : "
        f"{result.get('district', '-')}"
    )

    print(
        f"Block    : "
        f"{result.get('block', '-')}"
    )

    print(
        f"Village  : "
        f"{result.get('village', '-')}"
    )

    print(
        f"Crop     : "
        f"{result.get('crop', '-')}"
    )

    print(
        f"Type     : "
        f"{result.get('variety_or_type', '-')}"
    )

    # --------------------------------------------------------
    # SOIL
    # --------------------------------------------------------

    print("\n" + "-" * 65)
    print("SOIL STATUS")
    print("-" * 65)

    soil_summary = result.get(
        "soil_summary",
        {}
    )

    display_names = {

        "nitrogen": "Nitrogen",

        "phosphorus": "Phosphorus",

        "potassium": "Potassium",

        "ph": "Soil pH",

        "organic_carbon": "Organic Carbon",

        "electrical_conductivity":
            "Electrical Conductivity",

        "zinc": "Zinc",

        "boron": "Boron",

        "iron": "Iron",

        "manganese": "Manganese",

        "copper": "Copper",

        "sulphur": "Sulphur"
    }

    if soil_summary:

        for key, value in soil_summary.items():

            print(
                f"{display_names.get(key, key):25}: "
                f"{value}"
            )

    else:

        print(
            "No matching soil profile available."
        )

    # --------------------------------------------------------
    # RECOMMENDATION
    # --------------------------------------------------------

    print("\n" + "-" * 65)
    print("FERTILIZER RECOMMENDATION")
    print("-" * 65)

    if result.get(
        "recommendation_available",
        False
    ):

        n = result.get(
            "nitrogen_kg_per_ha"
        )

        p = result.get(
            "phosphorus_kg_per_ha"
        )

        k = result.get(
            "potassium_kg_per_ha"
        )

        print(
            f"\nNitrogen (N)      : "
            f"{n if n is not None else 'N/A'} kg/ha"
        )

        print(
            f"Phosphorus (P₂O₅): "
            f"{p if p is not None else 'N/A'} kg/ha"
        )

        print(
            f"Potassium (K₂O)  : "
            f"{k if k is not None else 'N/A'} kg/ha"
        )

        if (
            n is not None
            and p is not None
            and k is not None
        ):

            print(
                f"\nN:P₂O₅:K₂O        : "
                f"{n:g}:{p:g}:{k:g}"
            )

        # ----------------------------------------------------
        # PRODUCT QUANTITIES
        # ----------------------------------------------------

        fertilizer_products = result.get(
            "fertilizer_products"
        )

        if (
            fertilizer_products
            and isinstance(
                fertilizer_products,
                dict
            )
        ):

            print("\n" + "-" * 65)
            print("COMMERCIAL FERTILIZER PRODUCTS")
            print("-" * 65)

            for product in fertilizer_products.get(
                "products",
                []
            ):

                print(
                    f"\n{product.get('name', '-')}"
                    f" ({product.get('grade', '-')})"
                )

                print(
                    f"  Quantity : "
                    f"{product.get('kg_per_ha', 0)} kg/ha"
                )

            print(
                "\nCalculation:"
            )

            print(
                fertilizer_products.get(
                    "method",
                    "-"
                )
            )

            balance = fertilizer_products.get(
                "balance_check",
                {}
            )

            print(
                "\nNutrient balance:"
            )

            print(
                f"  N difference    : "
                f"{balance.get('nitrogen_difference', '-')}"
            )

            print(
                f"  P₂O₅ difference : "
                f"{balance.get('phosphorus_difference', '-')}"
            )

            print(
                f"  K₂O difference  : "
                f"{balance.get('potassium_difference', '-')}"
            )

        print(
            "\nApplicability:"
        )

        print(
            result.get(
                "applicability_reason",
                "-"
            )
        )

        print(
            "\nSource:"
        )

        print(
            result.get(
                "source",
                "-"
            )
        )

    else:

        print(
            "\nNo validated recommendation available."
        )

        print(
            result.get(
                "message",
                "-"
            )
        )

    print("\n" + "=" * 65)


# ============================================================
# COMMAND LINE TEST
# ============================================================

def main():

    print(
        "\nYieldROI Fertilizer Recommendation Engine"
    )

    try:

        recommender = FertilizerRecommender()

    except Exception as error:

        print(
            "\nERROR while loading fertilizer data:"
        )

        print(error)

        return

    district = input(
        "\nEnter district: "
    ).strip()

    block = input(
        "Enter block: "
    ).strip()

    crop = input(
        "Enter crop: "
    ).strip()

    variety_or_type = input(
        "Enter crop type/variety "
        "(optional): "
    ).strip()

    village = input(
        "Enter village "
        "(optional): "
    ).strip()

    year = input(
        "Enter soil-data year "
        "(optional): "
    ).strip()

    if not year:
        year = None

    try:

        result = recommender.recommend(

            district=district,

            block=block or None,

            crop=crop,

            variety_or_type=(
                variety_or_type
                if variety_or_type
                else None
            ),

            village=village or None,

            year=year
        )

        print_recommendation(
            result
        )

    except Exception as error:

        print(
            "\nERROR:"
        )

        print(error)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()