"""Verify the actual integration notebook against its committed CSV snapshot."""
import contextlib
import io
import json
from pathlib import Path
import unittest
import pandas as pd

from scripts.integration import integrate, load_and_integrate

ROOT = Path(__file__).resolve().parents[1]


class IntegrationTests(unittest.TestCase):
    def test_canonical_pipeline_reproduces_snapshot_and_audit(self):
        result = load_and_integrate(ROOT)
        expected = pd.read_csv(ROOT / "df_integrated.csv", dtype={"zip_code": "string"})
        pd.testing.assert_frame_equal(expected, result.df_integrated, check_dtype=False)
        self.assertEqual(result.summary["matched_zip_year_groups"], 484)
        self.assertEqual(result.summary["housing_only_zip_year_groups"], 671)
        self.assertEqual(result.summary["transportation_only_zip_year_groups"], 345)
        self.assertEqual(result.summary["borough_disagreements"], 6)
        self.assertEqual(result.summary["unknown_affordable_unit_rows_in_matched_groups"], 3)

    def test_notebook_reproduces_integrated_snapshot(self):
        notebook = json.loads((ROOT / "dataEngP3.ipynb").read_text())
        scope = {"display": lambda *args: None}
        with contextlib.redirect_stdout(io.StringIO()):
            for cell in notebook["cells"]:
                if cell["cell_type"] != "code":
                    continue
                source = "".join(cell["source"])
                if "import plotly" in source:
                    break
                # Validate the real transformation without rewriting the fixture.
                source = source.split("df_integrated.to_csv(")[0]
                exec(compile(source, "dataEngP3.ipynb", "exec"), scope)
        expected = pd.read_csv(ROOT / "df_integrated.csv", dtype={"zip_code": "string"})
        actual = scope["df_integrated"]
        pd.testing.assert_frame_equal(expected, actual, check_dtype=False)
        audit = scope["merge_audit"]
        self.assertEqual(int((audit._merge == "both").sum()), len(expected))
        self.assertTrue((expected.year.between(2022, 2026)).all())
        self.assertFalse(expected.duplicated(["zip_code", "year"]).any())

    @staticmethod
    def _example_sources():
        housing = pd.DataFrame({
            "zip_code": ["10001", "10001"], "year": [2024, 2024],
            "borough": ["Manhattan", "Manhattan"], "building_id": [11, 12],
            "project_id": [1, 1], "all_counted_units": [10., 20.],
            "total_units": [15, 25],
        })
        transport = pd.DataFrame({
            "zip_code": ["10001", "10001", "10002"], "year": [2024, 2024, 2024],
            "borough": ["Manhattan"] * 3, "open_data_crash_id": [101, 102, 103],
            "total_severe_injuries": [1, 2, 1],
            "total_non_severe_injuries": [0, 1, 0], "total_fatalities": [0, 0, 0],
        })
        return housing, transport

    def test_aggregation_prevents_many_to_many_inflation(self):
        result = integrate(*self._example_sources())
        row = result.df_integrated.iloc[0]
        self.assertEqual(len(result.df_integrated), 1)
        self.assertEqual(row["affordable_units"], 30)
        self.assertEqual(row["housing_project_count"], 1)
        self.assertEqual(row["housing_building_count"], 2)
        self.assertEqual(row["serious_crash_count"], 2)
        self.assertEqual(row["severe_injuries"], 3)
        self.assertEqual(result.summary["transportation_only_zip_year_groups"], 1)

    def test_unknown_units_are_not_manufactured_as_zero(self):
        housing, transport = self._example_sources()
        housing["all_counted_units"] = float("nan")
        result = integrate(housing, transport)
        self.assertTrue(pd.isna(result.df_integrated.loc[0, "affordable_units"]))

    def test_duplicate_crash_id_cannot_double_count_injuries(self):
        housing, transport = self._example_sources()
        transport.loc[1, "open_data_crash_id"] = 101
        with self.assertRaisesRegex(ValueError, "crash IDs"):
            integrate(housing, transport)

    def test_malformed_keys_and_negative_metrics_fail_validation(self):
        housing, transport = self._example_sources()
        housing.loc[0, "zip_code"] = "not a ZIP"
        with self.assertRaisesRegex(ValueError, "malformed zip_code"):
            integrate(housing, transport)
        housing, transport = self._example_sources()
        transport.loc[0, "total_severe_injuries"] = -1
        with self.assertRaisesRegex(ValueError, "nonnegative count"):
            integrate(housing, transport)

    def test_year_must_match_the_source_date(self):
        housing, transport = self._example_sources()
        transport["crash_date"] = ["2024-01-01", "2025-01-01", "2024-01-02"]
        with self.assertRaisesRegex(ValueError, "year derivation"):
            integrate(housing, transport)
