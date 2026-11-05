"""
Loads df_integrated for the website.

- If data/df_integrated.csv exists (Person 3's real file), it is used.
- Otherwise a DUMMY dataset with the same columns is generated so the
  website can be built and tested before the real data is ready.

AGREED COLUMNS (confirm with Person 3 - charts depend on these names):
    zip_code                  str, 5 characters, e.g. "11201"
    borough                   str, title case, e.g. "Brooklyn"
    year                      int, e.g. 2022
    -- housing (aggregated per zip_code + year) --
    n_buildings               number of housing buildings
    n_projects                number of distinct housing projects
    total_units               all affordable units
    units_new_construction    units from new construction
    units_preservation        units from preservation
    -- transportation (aggregated per zip_code + year) --
    serious_injuries              all serious injuries
    serious_injuries_pedestrian   pedestrian serious injuries
    serious_injuries_cyclist      cyclist serious injuries
    serious_injuries_motorist     motorist serious injuries
"""

from pathlib import Path

import numpy as np
import pandas as pd

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "df_integrated.csv"

# Dropdown label -> column name. Change the right-hand side if Person 3
# uses different column names.
HOUSING_CATEGORIES = {
    "All affordable units": "total_units",
    "New construction": "units_new_construction",
    "Preservation": "units_preservation",
}
TRANSPORT_CATEGORIES = {
    "All serious injuries": "serious_injuries",
    "Pedestrian": "serious_injuries_pedestrian",
    "Cyclist": "serious_injuries_cyclist",
    "Motorist": "serious_injuries_motorist",
}


def _make_dummy_data():
    """Random data with the agreed columns. Numbers mean nothing."""
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
            size = rng.uniform(0.3, 2.0)  # some ZIPs are "bigger" than others
            for year in range(2014, 2025):
                new = int(rng.poisson(40 * size))
                pres = int(rng.poisson(60 * size))
                ped = int(rng.poisson(3 * size))
                cyc = int(rng.poisson(1 * size))
                mot = int(rng.poisson(4 * size))
                rows.append({
                    "zip_code": z, "borough": borough, "year": year,
                    "n_buildings": int(rng.poisson(6 * size)),
                    "n_projects": int(rng.poisson(3 * size)),
                    "total_units": new + pres,
                    "units_new_construction": new,
                    "units_preservation": pres,
                    "serious_injuries": ped + cyc + mot,
                    "serious_injuries_pedestrian": ped,
                    "serious_injuries_cyclist": cyc,
                    "serious_injuries_motorist": mot,
                })
    return pd.DataFrame(rows)


def load_data():
    """Return (df_integrated, is_dummy)."""
    if DATA_FILE.exists():
        df = pd.read_csv(DATA_FILE, dtype={"zip_code": str})
        is_dummy = False
    else:
        df = _make_dummy_data()
        is_dummy = True

    # Light safety formatting so filters and search always work
    df["zip_code"] = df["zip_code"].astype(str).str.zfill(5)
    df["borough"] = df["borough"].astype(str).str.strip().str.title()
    df["year"] = df["year"].astype(int)
    return df, is_dummy
