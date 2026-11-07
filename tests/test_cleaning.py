"""Verify archived official source records reproduce the supplied clean snapshots."""
from pathlib import Path
import unittest

import pandas as pd

from scripts.cleaning import clean_housing, clean_transport, zip_text

ROOT = Path(__file__).resolve().parents[1]


class CleaningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.housing_raw = pd.read_csv(ROOT / "data/raw/df_housing_raw.csv", low_memory=False)
        cls.transport_raw = pd.read_csv(ROOT / "data/raw/df_transport_raw.csv", low_memory=False)

    def test_archived_housing_reproduces_every_supplied_field(self):
        actual = clean_housing(self.housing_raw)
        expected = pd.read_csv(ROOT / "df_housing_clean.csv", dtype={"zip_code": "string"},
                               low_memory=False)
        for column in ["project_start_date", "project_completion_date", "building_completion_date"]:
            expected[column] = pd.to_datetime(expected[column], errors="raise")
        pd.testing.assert_frame_equal(expected, actual, check_dtype=False, check_exact=True)
        self.assertEqual(actual.shape, (9551, 42))
        # Unknown source units and missing geography must never be invented as zero/ZIPs.
        self.assertEqual(int(actual["all_counted_units"].isna().sum()), 29)
        self.assertEqual(int(actual["zip_code"].isna().sum()), 1958)
        self.assertEqual(int(actual["year"].isna().sum()), 0)

    def test_archived_transport_reproduces_every_supplied_field(self):
        actual = clean_transport(self.transport_raw)
        expected = pd.read_csv(ROOT / "df_transport_clean.csv", dtype={"zip_code": "string"},
                               low_memory=False)
        expected["crash_date"] = pd.to_datetime(expected["crash_date"], errors="raise")
        key = "open_data_crash_id"
        pd.testing.assert_frame_equal(expected.sort_values(key).reset_index(drop=True),
            actual.sort_values(key).reset_index(drop=True), check_dtype=False, check_exact=True)
        self.assertEqual(actual.shape, (8072, 26))
        self.assertTrue(actual[key].notna().all())
        self.assertFalse(actual[key].duplicated().any())
        self.assertTrue(actual[["zip_code", "borough", "year"]].notna().all().all())

    def test_transport_exclusions_are_geographic_not_coordinate_imputation(self):
        raw = self.transport_raw
        actual = clean_transport(raw)
        self.assertEqual(len(raw), 13754)
        self.assertEqual(int(raw["zipcode"].isna().sum()), 5682)
        duplicate_rows = raw.duplicated()
        self.assertEqual(int(duplicate_rows.sum()), 3)
        self.assertTrue(raw.loc[duplicate_rows, "zipcode"].isna().all())
        # These source anomalies remain visible, rather than being silently geocoded.
        self.assertEqual(int(actual["zip_code"].eq("10000").sum()), 44)
        self.assertEqual(int(actual["latitude"].isna().sum()), 1295)
        self.assertEqual(actual["crash_date"].min(), pd.Timestamp("2022-10-01"))
        self.assertEqual(pd.to_datetime(raw["crash_date"]).min(), pd.Timestamp("2022-01-01"))

    def test_conflicting_crash_ids_and_fractional_zips_require_review(self):
        sample = self.transport_raw.loc[self.transport_raw["zipcode"].notna()].head(2).copy()
        sample.iloc[1, sample.columns.get_loc("open_data_crash_id")] = sample.iloc[0]["open_data_crash_id"]
        with self.assertRaisesRegex(ValueError, "crash IDs"):
            clean_transport(sample)
        with self.assertRaisesRegex(ValueError, "Fractional ZIP"):
            zip_text(pd.Series([10001.5]))

    def test_bad_geography_cannot_silently_become_missing_or_an_invented_zip(self):
        for value in ["bad ZIP", -10001, 1000, 100001]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                zip_text(pd.Series([value]))
        self.assertTrue(pd.isna(zip_text(pd.Series([None])).iloc[0]))
        self.assertEqual(zip_text(pd.Series([10000])).iloc[0], "10000")

    def test_transport_missing_dates_and_bad_counts_stop_cleaning(self):
        original = self.transport_raw.loc[self.transport_raw["zipcode"].notna()].head(1).copy()
        for value in [None, -1, 1.5, "unknown"]:
            sample = original.copy()
            sample["total_severe_injuries"] = pd.Series([value], index=sample.index, dtype="object")
            with self.subTest(injuries=value), self.assertRaisesRegex(ValueError, "counts"):
                clean_transport(sample)
        sample = original.copy()
        sample["crash_date"] = None
        with self.assertRaisesRegex(ValueError, "dates"):
            clean_transport(sample)

    def test_unknown_housing_units_are_preserved_but_negative_units_fail(self):
        sample = self.housing_raw.head(1).copy()
        sample["all_counted_units"] = float("nan")
        self.assertTrue(pd.isna(clean_housing(sample)["all_counted_units"].iloc[0]))
        sample["all_counted_units"] = -1
        with self.assertRaisesRegex(ValueError, "counts"):
            clean_housing(sample)
