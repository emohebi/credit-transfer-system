"""
Concordance Loader

Parses the concordance Excel file containing:
  code, code_name, qualification_code, qualification_title, anzsco_code, anzsco_title

Builds lookup maps:
  - unit_code → {unit_title, qualification_codes}
  - qualification_code → {title, unit_codes, anzsco_codes}
  - anzsco_code → {title, qualification_codes}
"""
import logging
import pandas as pd
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger(__name__)


class ConcordanceData:
    """Holds all concordance lookup maps."""

    def __init__(self):
        # unit_code → title
        self.unit_titles: Dict[str, str] = {}

        # unit_code → [qual_codes]
        self.unit_to_quals: Dict[str, List[str]] = defaultdict(list)

        # qual_code → title
        self.qual_titles: Dict[str, str] = {}

        # qual_code → [unit_codes]
        self.qual_to_units: Dict[str, List[str]] = defaultdict(list)

        # qual_code → [anzsco_codes]
        self.qual_to_occupations: Dict[str, List[str]] = defaultdict(list)

        # anzsco_code → title
        self.occupation_titles: Dict[str, str] = {}

        # anzsco_code → [qual_codes]
        self.occupation_to_quals: Dict[str, List[str]] = defaultdict(list)

    @property
    def unit_count(self) -> int:
        return len(self.unit_titles)

    @property
    def qualification_count(self) -> int:
        return len(self.qual_titles)

    @property
    def occupation_count(self) -> int:
        return len(self.occupation_titles)


def load_concordance(file_path: str) -> ConcordanceData:
    """
    Load concordance from Excel/CSV.

    Expected columns (flexible naming):
        code | code_name | qualification_code | qualification_title | anzsco_code | anzsco_title

    Returns:
        ConcordanceData with all lookup maps populated.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Concordance file not found: {file_path}")

    logger.info(f"Loading concordance from: {file_path}")

    if path.suffix == ".csv":
        df = pd.read_csv(file_path, dtype=str)
    elif path.suffix in (".xlsx", ".xls"):
        df = pd.read_excel(file_path, dtype=str)
    else:
        raise ValueError(f"Unsupported format: {path.suffix}")

    # Normalise column names
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # Map flexible column names
    col_map = _detect_columns(df)
    logger.info(f"Detected columns: {col_map}")

    df = df.rename(columns=col_map)

    # Clean
    for col in ["code", "code_name", "qualification_code", "qualification_title",
                 "anzsco_code", "anzsco_title"]:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str).str.strip()

    # Drop rows with no unit code
    df = df[df["code"] != ""]

    data = ConcordanceData()

    for _, row in df.iterrows():
        unit_code = row.get("code", "")
        unit_title = row.get("code_name", "")
        qual_code = row.get("qualification_code", "")
        qual_title = row.get("qualification_title", "")
        anzsco_code = row.get("anzsco_code", "")
        anzsco_title = row.get("anzsco_title", "")

        # Unit → title
        if unit_code and unit_title:
            data.unit_titles[unit_code] = unit_title

        # Unit ↔ Qualification
        if unit_code and qual_code:
            if qual_code not in data.unit_to_quals[unit_code]:
                data.unit_to_quals[unit_code].append(qual_code)
            if unit_code not in data.qual_to_units[qual_code]:
                data.qual_to_units[qual_code].append(unit_code)

        # Qualification → title
        if qual_code and qual_title:
            data.qual_titles[qual_code] = qual_title

        # Qualification ↔ Occupation
        if qual_code and anzsco_code:
            if anzsco_code not in data.qual_to_occupations[qual_code]:
                data.qual_to_occupations[qual_code].append(anzsco_code)
            if qual_code not in data.occupation_to_quals[anzsco_code]:
                data.occupation_to_quals[anzsco_code].append(qual_code)

        # Occupation → title
        if anzsco_code and anzsco_title:
            data.occupation_titles[anzsco_code] = anzsco_title

    logger.info(f"Concordance loaded:")
    logger.info(f"  Units with titles: {data.unit_count}")
    logger.info(f"  Qualifications: {data.qualification_count}")
    logger.info(f"  Occupations (ANZSCO): {data.occupation_count}")

    return data


def _detect_columns(df: pd.DataFrame) -> Dict[str, str]:
    """
    Flexible column detection.
    Maps whatever the user's columns are to our standard names.
    """
    mapping = {}
    col_set = set(df.columns)

    # code (unit code)
    for candidate in ["code", "unit_code", "unitcode", "unit"]:
        if candidate in col_set:
            mapping[candidate] = "code"
            break

    # code_name (unit title)
    for candidate in ["code_name", "codename", "unit_name", "unit_title", "unittitle"]:
        if candidate in col_set:
            mapping[candidate] = "code_name"
            break

    # qualification_code
    for candidate in ["qualification_code", "qual_code", "qualcode", "qualification"]:
        if candidate in col_set:
            mapping[candidate] = "qualification_code"
            break

    # qualification_title
    for candidate in ["qualification_title", "qual_title", "qualtitle", "qualification_name"]:
        if candidate in col_set:
            mapping[candidate] = "qualification_title"
            break

    # anzsco_code
    for candidate in ["anzsco_code", "anzscocode", "anzsco", "occupation_code"]:
        if candidate in col_set:
            mapping[candidate] = "anzsco_code"
            break

    # anzsco_title
    for candidate in ["anzsco_title", "anzscotitle", "occupation_title", "occupation_name"]:
        if candidate in col_set:
            mapping[candidate] = "anzsco_title"
            break

    return mapping
