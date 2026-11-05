"""
Loads df_integrated for the website.

Looks for the integrated dataset in this order:
    1. data/df_integrated.csv
    2. df_integrated.csv in the repository root
If neither exists, a DUMMY dataset with the same columns is generated so the
website still runs.

df_integrated columns (one row per zip_code + year):
    zip_code, borough, year
    housing:   housing_building_count, housing_project_count,
               affordable_units, total_housing_units
    transport: serious_crash_count, severe_injuries,
               non_severe_injuries, fatalities
"""

from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_FILES = [REPO_ROOT / "data" / "df_integrated.csv", REPO_ROOT / "df_integrated.csv"]

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


def _make_dummy_data():
    """Random data with the real column names. Numbers mean nothing."""
    rng = np.random.default_rng(42)
    zips_by_borough = {
        "Manhattan": [f"100{n:02d}" for n in range(1, 41)],
        "Bronx": [f"104{n:02d}" for n in range(51, 76)],
        "Brooklyn": [f"112{n:02d}" for n in range(1, 40)],
        "Queens": [f"11{n}" for n in range(354, 380)],
        "Staten Island": [f"103{n:02d}" for n in range(1, 15)],
    }
    rows = []
    for borough, zips in zips_by_borough.items():
        for z in zips:
            size = rng.uniform(0.3, 2.0)
            for year in range(2022, 2027):
                affordable = int(rng.poisson(200 * size))
                severe = int(rng.poisson(12 * size))
                rows.append({
                    "zip_code": z, "borough": borough, "year": year,
                    "housing_building_count": int(rng.poisson(6 * size)) + 1,
                    "housing_project_count": int(rng.poisson(4 * size)) + 1,
                    "affordable_units": affordable,
                    "total_housing_units": affordable + int(rng.poisson(120 * size)),
                    "serious_crash_count": severe,
                    "severe_injuries": severe,
                    "non_severe_injuries": int(rng.poisson(3 * size)),
                    "fatalities": int(rng.poisson(0.8 * size)),
                })
    return pd.DataFrame(rows)


def load_data():
    """Return (df_integrated, is_dummy)."""
    for path in DATA_FILES:
        if path.exists():
            df = pd.read_csv(path)
            is_dummy = False
            break
    else:
        df = _make_dummy_data()
        is_dummy = True

    # Consistent formats for the filters and search:
    # zip_code is stored as a number in the CSV, so turn it back into 5-character text
    df["zip_code"] = df["zip_code"].astype(int).astype(str).str.zfill(5)
    df["borough"] = df["borough"].astype(str).str.strip().str.title()
    df["year"] = df["year"].astype(int)
    return df, is_dummy
