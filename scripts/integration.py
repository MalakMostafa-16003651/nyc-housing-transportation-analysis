"""Reproduce the team's ZIP-year integration from the supplied clean snapshots.

python scripts/integration.py          # compare outputs, without rewriting them
python scripts/integration.py --write  # regenerate outputs and audit evidence
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
KEYS = ["zip_code", "year"]
BOROUGHS = {"Bronx", "Brooklyn", "Manhattan", "Queens", "Staten Island"}
METRICS = ["housing_building_count", "housing_project_count", "affordable_units",
           "total_housing_units", "serious_crash_count", "severe_injuries",
           "non_severe_injuries", "fatalities"]


@dataclass
class IntegrationResult:
    df_integrated: pd.DataFrame
    df_housing_agg: pd.DataFrame
    df_transport_agg: pd.DataFrame
    merge_audit: pd.DataFrame
    borough_disagreements: pd.DataFrame
    summary: dict


def _standardize(frame: pd.DataFrame, label: str) -> pd.DataFrame:
    """Keep missing keys missing and reject malformed nonmissing key values."""
    result = frame.copy()
    for key in KEYS:
        numeric = pd.to_numeric(result[key], errors="coerce")
        invalid = result[key].notna() & (numeric.isna() | numeric.mod(1).ne(0))
        if invalid.any():
            raise ValueError(f"{label}: {int(invalid.sum())} malformed {key} values")
        result[key] = numeric.astype("Int64")
    result["zip_code"] = result["zip_code"].astype("string").str.zfill(5)
    valid_zip = result["zip_code"].isna() | result["zip_code"].str.fullmatch(r"\d{5}")
    if not valid_zip.all():
        raise ValueError(f"{label}: ZIP codes must contain exactly five digits")
    result["borough"] = result["borough"].astype("string").str.strip().str.title()
    if result["borough"].isna().any() or not result["borough"].isin(BOROUGHS).all():
        raise ValueError(f"{label}: missing or unrecognized borough")
    if result.duplicated().any():
        raise ValueError(f"{label}: exact duplicate source rows must be reviewed")
    return result


def _validate_metrics(frame: pd.DataFrame, columns: list[str], label: str) -> None:
    for column in columns:
        numeric = pd.to_numeric(frame[column], errors="coerce")
        invalid = frame[column].notna() & (numeric.isna() | numeric.lt(0)
                                                   | numeric.mod(1).ne(0))
        if invalid.any():
            raise ValueError(f"{label}: invalid nonnegative count in {column}")
        frame[column] = numeric


def _validate_year(frame: pd.DataFrame, date_column: str, label: str) -> None:
    if date_column not in frame:
        return
    dates = pd.to_datetime(frame[date_column], errors="coerce")
    invalid = frame[date_column].notna() & dates.isna()
    inconsistent = dates.notna() & frame["year"].notna() & dates.dt.year.ne(frame["year"])
    if invalid.any() or inconsistent.any():
        raise ValueError(f"{label}: date parsing or year derivation is inconsistent")


def integrate(df_housing_clean: pd.DataFrame,
              df_transport_clean: pd.DataFrame) -> IntegrationResult:
    """Aggregate BOTH sources independently, audit outer match, retain matches.

    Unknown housing units are not imputed: sum(min_count=1) preserves an entirely
    unknown group's value. A partially known group remains an observed subtotal.
    """
    h = _standardize(df_housing_clean, "housing")
    t = _standardize(df_transport_clean, "transportation")
    _validate_year(h, "project_start_date", "housing")
    _validate_year(t, "crash_date", "transportation")
    _validate_metrics(h, ["all_counted_units", "total_units"], "housing")
    _validate_metrics(t, ["total_severe_injuries", "total_non_severe_injuries",
                          "total_fatalities"], "transportation")
    if t["open_data_crash_id"].isna().any() or t["open_data_crash_id"].duplicated().any():
        raise ValueError("transportation: crash IDs must be present and unique before summing injuries")
    if t[["total_severe_injuries", "total_non_severe_injuries", "total_fatalities"]].isna().any().any():
        raise ValueError("transportation: missing injury/fatality counts require source review")
    housing = h.dropna(subset=KEYS).copy()
    transport = t.dropna(subset=KEYS).copy()
    if housing[["building_id", "project_id"]].isna().any().any():
        raise ValueError("housing: missing building/project IDs in eligible ZIP-years require source review")
    borough_summary = lambda x: " / ".join(sorted(x.dropna().unique()))
    observed_sum = lambda x: x.sum(min_count=1)
    df_housing_agg = housing.groupby(KEYS, as_index=False).agg(
        housing_borough=("borough", borough_summary),
        housing_building_count=("building_id", "nunique"),
        housing_project_count=("project_id", "nunique"),
        affordable_units=("all_counted_units", observed_sum),
        total_housing_units=("total_units", observed_sum),
    )
    df_transport_agg = transport.groupby(KEYS, as_index=False).agg(
        transport_borough=("borough", borough_summary),
        serious_crash_count=("open_data_crash_id", "nunique"),
        severe_injuries=("total_severe_injuries", observed_sum),
        non_severe_injuries=("total_non_severe_injuries", observed_sum),
        fatalities=("total_fatalities", observed_sum),
    )
    merge_audit = df_housing_agg.merge(df_transport_agg, on=KEYS, how="outer",
                                     validate="one_to_one", indicator=True)
    matched = merge_audit.loc[merge_audit["_merge"] == "both"].drop(columns="_merge").copy()
    disagreements = matched.loc[
        matched["housing_borough"] != matched["transport_borough"],
        KEYS + ["housing_borough", "transport_borough"],
    ].copy()
    # Preserve Malak's documented convention; this does not correct source geography.
    borough_map = housing.groupby("zip_code")["borough"].agg(lambda x: x.mode().iloc[0])
    matched["borough"] = matched["zip_code"].map(borough_map)
    df_integrated = (matched.drop(columns=["housing_borough", "transport_borough"])
                     .sort_values(["year", "zip_code"]).reset_index(drop=True))
    df_integrated["year"] = df_integrated["year"].astype(int)
    if df_integrated[KEYS + ["borough"]].isna().any().any():
        raise ValueError("integration produced missing keys or boroughs")
    if df_integrated.duplicated(KEYS).any():
        raise ValueError("integration produced duplicate ZIP-year keys")
    _validate_metrics(df_integrated, METRICS, "integrated")
    matched_source = housing.merge(df_integrated[KEYS], on=KEYS, how="inner",
                                   validate="many_to_one")
    total_units = h["all_counted_units"].sum(min_count=1)
    missing_zip_units = h.loc[h["zip_code"].isna(), "all_counted_units"].sum(min_count=1)
    summary = {
        "integration_rule": "aggregate both datasets by zip_code + year, then inner match",
        "housing_source_rows": len(h), "transportation_source_rows": len(t),
        "housing_rows_missing_keys": int(h[KEYS].isna().any(axis=1).sum()),
        "transportation_rows_missing_keys": int(t[KEYS].isna().any(axis=1).sum()),
        "housing_zip_year_groups": len(df_housing_agg),
        "transportation_zip_year_groups": len(df_transport_agg),
        "matched_zip_year_groups": len(df_integrated),
        "housing_only_zip_year_groups": int(merge_audit["_merge"].eq("left_only").sum()),
        "transportation_only_zip_year_groups": int(merge_audit["_merge"].eq("right_only").sum()),
        "borough_disagreements": len(disagreements),
        "borough_policy": "most frequent housing borough per ZIP across the source snapshot; alphabetical tie break",
        "unknown_affordable_unit_source_rows": int(h["all_counted_units"].isna().sum()),
        "unknown_affordable_unit_rows_in_matched_groups": int(matched_source["all_counted_units"].isna().sum()),
        "housing_units_missing_zip_share": float(missing_zip_units / total_units) if total_units else None,
        "source_transportation_zip_10000_rows": int(t["zip_code"].eq("10000").sum()),
        "integrated_zip_10000_rows": int(df_integrated["zip_code"].eq("10000").sum()),
        "transportation_date_min": str(t["crash_date"].min()) if "crash_date" in t else None,
        "transportation_date_max": str(t["crash_date"].max()) if "crash_date" in t else None,
        "integrated_null_counts": {c: int(v) for c, v in df_integrated.isna().sum().items()},
        "integrated_metric_totals": {
            c: (float(total) if pd.notna(total) else None)
            for c in METRICS for total in [df_integrated[c].sum(min_count=1)]},
    }
    return IntegrationResult(df_integrated, df_housing_agg, df_transport_agg,
                             merge_audit, disagreements, summary)


def load_and_integrate(root: Path = ROOT) -> IntegrationResult:
    frames = [pd.read_csv(root / name, dtype={"zip_code": "string"}) for name in
              ["df_housing_clean.csv", "df_transport_clean.csv"]]
    result = integrate(*frames)
    # Normalize newlines so the provenance digest is portable across Git autocrlf.
    result.summary["source_sha256_lf"] = {
        name: hashlib.sha256((root / name).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        for name in ["df_housing_clean.csv", "df_transport_clean.csv"]}
    return result


def write_outputs(result: IntegrationResult, root: Path = ROOT) -> None:
    (root / "data").mkdir(exist_ok=True)
    result.df_integrated.to_csv(root / "df_integrated.csv", index=False)
    result.df_housing_agg.rename(columns={"housing_borough": "borough"}).to_csv(root / "df_housing_agg.csv", index=False)
    result.df_transport_agg.rename(columns={"transport_borough": "borough"}).to_csv(root / "df_transport_agg.csv", index=False)
    result.merge_audit.loc[result.merge_audit["_merge"] != "both"].to_csv(root / "data" / "unmatched_zip_years.csv", index=False)
    result.borough_disagreements.to_csv(root / "data" / "borough_disagreements.csv", index=False)
    (root / "data" / "integration_audit.json").write_text(json.dumps(result.summary, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = load_and_integrate()
    if args.write:
        write_outputs(result)
        print("Wrote integrated snapshot, source aggregates and audit evidence.")
    else:
        expected = pd.read_csv(ROOT / "df_integrated.csv", dtype={"zip_code": "string"})
        pd.testing.assert_frame_equal(expected, result.df_integrated, check_dtype=False)
        print("PASS: committed df_integrated.csv exactly reproduces from the two cleaned snapshots.")
    print(json.dumps(result.summary, indent=2))


if __name__ == "__main__":
    main()
