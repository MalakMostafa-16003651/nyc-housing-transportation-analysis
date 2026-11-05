"""Verify the actual integration notebook against its committed CSV snapshot."""
import contextlib
import io
import json
from pathlib import Path
import unittest
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


class IntegrationTests(unittest.TestCase):
    def test_notebook_reproduces_integrated_snapshot(self):
        notebook = json.loads((ROOT / "dataEngP3.ipynb").read_text())
        scope = {}
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
