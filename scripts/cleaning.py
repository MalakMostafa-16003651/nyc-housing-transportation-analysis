"""Reproduce the team's cleaned snapshots from the archived NYC source CSVs.

The transportation recipe was recovered by comparing every source field on
2026-11-07; it is not a record of the original contributor's process.
"""
import pandas as pd

BOROUGHS = {"Bronx", "Brooklyn", "Manhattan", "Queens", "Staten Island"}


def _dates(values, *, required=False):
    dates = pd.to_datetime(values, errors="coerce")
    if (values.notna() & dates.isna()).any() or (required and dates.isna().any()):
        raise ValueError(f"Missing or malformed dates in {values.name}")
    return dates


def _boroughs(values):
    normalized = values.astype("string").str.strip().str.title()
    if normalized.isna().any() or (~normalized.isin(BOROUGHS)).any():
        raise ValueError("Missing or unrecognized borough")
    return normalized


def _counts(values, *, allow_missing=False):
    numeric = pd.to_numeric(values, errors="coerce")
    if ((values.notna() & numeric.isna()).any() or
            (not allow_missing and numeric.isna().any()) or
            (numeric.dropna().lt(0) | numeric.dropna().mod(1).ne(0)).any()):
        raise ValueError(f"Missing, malformed, fractional or negative counts in {values.name}")
    return numeric


def zip_text(values):
    numeric = pd.to_numeric(values, errors="coerce")
    if (values.notna() & numeric.isna()).any():
        raise ValueError("Malformed nonmissing ZIP code")
    fractional = numeric.notna() & numeric.mod(1).ne(0)
    if fractional.any():
        raise ValueError("Fractional ZIP codes require review")
    # ZIPs are five digits in these NYC sources; do not invent missing leading digits.
    if (numeric.notna() & ~numeric.between(10000, 99999)).any():
        raise ValueError("ZIP code must have five digits")
    return numeric.astype("Int64").astype("string")


def clean_housing(df_housing_raw):
    clean = df_housing_raw.copy().rename(columns={"postcode": "zip_code"})
    clean["zip_code"] = zip_text(clean["zip_code"])
    clean["borough"] = _boroughs(clean["borough"])
    for column in ["project_start_date", "project_completion_date", "building_completion_date"]:
        clean[column] = _dates(clean[column], required=column == "project_start_date")
    for column in [c for c in clean if c.endswith("_units")]:
        clean[column] = _counts(clean[column], allow_missing=True)
    clean["year"] = clean["project_start_date"].dt.year.astype("Int64")
    return clean


def clean_transport(df_transport_raw):
    # Missing ZIPs cannot be assigned to a ZIP-year without external geography.
    # Retain source ZIP 10000 as supplied, but flag it for geography review.
    clean = df_transport_raw.drop_duplicates().dropna(subset=["zipcode"]).copy()
    clean["crash_date"] = _dates(clean["crash_date"], required=True)
    clean["year"] = clean["crash_date"].dt.year.astype("Int64")
    clean["zip_code"] = zip_text(clean["zipcode"])
    clean["borough"] = _boroughs(clean["crash_borough"])
    for column in ["total_non_severe_injuries", "total_severe_injuries", "total_fatalities"]:
        clean[column] = _counts(clean[column])
    clean["open_data_crash_id"] = _counts(clean["open_data_crash_id"])
    if clean["open_data_crash_id"].isna().any() or clean["open_data_crash_id"].duplicated().any():
        raise ValueError("Retained crash IDs are missing or duplicated; review source")
    return clean
