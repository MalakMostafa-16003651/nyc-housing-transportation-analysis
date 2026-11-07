"""
Loads df_integrated for the website.

Looks for the integrated dataset in this order:
    1. df_integrated.csv in the repository root (canonical)
    2. data/df_integrated.csv (deployment fallback)
Missing or invalid data raises an actionable error; production results must never
silently be replaced with simulated records.

df_integrated columns (one row per zip_code + year):
    zip_code, borough, year
    housing:   housing_building_count, housing_project_count,
               affordable_units, total_housing_units
    transport: serious_crash_count, severe_injuries,
               non_severe_injuries, fatalities
"""

from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_FILES = [REPO_ROOT / "df_integrated.csv", REPO_ROOT / "data" / "df_integrated.csv"]

# Dropdown label -> df_integrated column.
HOUSING_CATEGORIES = {
    "Affordable units": "affordable_units",
    "Total housing units": "total_housing_units",
    "Housing buildings": "housing_building_count",
    "Housing projects": "housing_project_count",
}
TRANSPORT_CATEGORIES = {
    "Serious crashes": "serious_crash_count",
    "Severe injuries": "severe_injuries",
    "Non-severe injuries": "non_severe_injuries",
    "Fatalities": "fatalities",
}


def load_data():
    """Return validated (df_integrated, False), preserving the dashboard interface."""
    for path in DATA_FILES:
        if path.exists():
            df = pd.read_csv(path, dtype={"zip_code": "string"})
            break
    else:
        raise FileNotFoundError("df_integrated.csv is missing. Add the validated integration "
                                "output to the repository root or data/ before starting Dash.")

    measures = list(HOUSING_CATEGORIES.values()) + list(TRANSPORT_CATEGORIES.values())
    required = ["zip_code", "borough", "year", *measures]
    missing = sorted(set(required) - set(df.columns))
    if missing:
        raise ValueError(f"Integrated dataset is missing columns: {', '.join(missing)}")
    if df.empty or df[required].isna().any().any():
        raise ValueError("Integrated dataset must contain rows with no missing required values.")
    df["zip_code"] = df["zip_code"].str.strip()
    if not df["zip_code"].str.fullmatch(r"\d{5}").all():
        raise ValueError("Integrated zip_code values must be five-digit strings.")
    df["borough"] = df["borough"].astype(str).str.strip().str.title()
    valid_boroughs = {"Bronx", "Brooklyn", "Manhattan", "Queens", "Staten Island"}
    if not df["borough"].isin(valid_boroughs).all():
        raise ValueError("Integrated borough values must use the five standardized NYC names.")
    for column in ["year", *measures]:
        values = pd.to_numeric(df[column], errors="raise")
        if not ((values >= 0) & (values < float("inf")) & (values % 1 == 0)).all():
            raise ValueError(f"Integrated {column} must contain finite nonnegative integers.")
        df[column] = values.astype("int64")
    if not df["year"].between(1900, 2100).all():
        raise ValueError("Integrated year values must be calendar years between 1900 and 2100.")
    if df.duplicated(["zip_code", "year"]).any():
        raise ValueError("Integrated dataset has duplicate zip_code + year keys.")
    return df, False
