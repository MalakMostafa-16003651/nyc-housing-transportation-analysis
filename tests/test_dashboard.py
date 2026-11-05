"""Run from the repository root: python -m unittest discover -s tests."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
import app as dashboard
from charts import ALL_CHARTS


class DashboardTests(unittest.TestCase):
    def test_real_data_contract(self):
        df = dashboard.df_integrated
        self.assertFalse(dashboard.IS_DUMMY)
        self.assertFalse(df.duplicated(["zip_code", "year"]).any())
        self.assertFalse(df.isna().any().any())

    def test_completed_charts_under_filters(self):
        for boroughs, zips, years in [([], [], [2022, 2026]),
                                      (["Brooklyn"], [], [2023, 2025]),
                                      ([], ["11212"], [2023, 2023])]:
            df = dashboard.filter_data(boroughs, zips, years, "Affordable units", "Serious crashes")
            self.assertFalse(df.empty)
            for number, chart in ALL_CHARTS[:8]:
                with self.subTest(rq=number, boroughs=boroughs, zips=zips):
                    fig = chart(df)
                    self.assertGreater(len(fig.data), 0)
                    fig.to_json()
        self.assertTrue((df.zip_code == "11212").all())
        self.assertTrue((df.year == 2023).all())

    def test_search_and_empty_report(self):
        parsed = dashboard.parse_search("Brooklyn 2023 2025 severe")
        self.assertEqual(parsed["borough"], ["Brooklyn"])
        self.assertEqual(parsed["years"], [2023, 2025])
        self.assertEqual(parsed["transport"], "Severe injuries")
        _, charts = dashboard.generate_report(1, 0, [], ["00000"], [2023, 2025],
                                              "Affordable units", "Serious crashes")
        self.assertEqual(charts, [])

    def test_http_report_callback(self):
        client = dashboard.server.test_client()
        for route in ["/", "/_dash-layout", "/_dash-dependencies"]:
            self.assertEqual(client.get(route).status_code, 200)
        key = next(k for k in dashboard.app.callback_map if "summary-row" in k)
        response = client.post("/_dash-update-component", json={
            "output": key,
            "outputs": [{"id": "summary-row", "property": "children"},
                        {"id": "charts-grid", "property": "children"}],
            "inputs": [{"id": "generate-btn", "property": "n_clicks", "value": 1},
                       {"id": "search-trigger", "property": "data", "value": 0}],
            "state": [{"id": name, "property": "value", "value": value} for name, value in [
                ("borough-filter", ["Brooklyn"]), ("zip-filter", []),
                ("year-filter", [2023, 2025]), ("housing-filter", "Affordable units"),
                ("transport-filter", "Serious crashes")]],
            "changedPropIds": ["generate-btn.n_clicks"],
        })
        self.assertEqual(response.status_code, 200)
        cards = response.get_json()["response"]["charts-grid"]["children"]
        self.assertEqual(len(cards), 12)
        for card in cards[:8]:
            self.assertEqual(card["props"]["children"][0]["type"], "Graph")

    def test_every_measure_combination_and_search(self):
        for housing in dashboard.HOUSING_CATEGORIES:
            for transport in dashboard.TRANSPORT_CATEGORIES:
                df = dashboard.filter_data(["Brooklyn"], [], [2023, 2025], housing, transport)
                self.assertEqual(df.housing_selected.sum(), df[dashboard.HOUSING_CATEGORIES[housing]].sum())
                self.assertEqual(df.injuries_selected.sum(), df[dashboard.TRANSPORT_CATEGORIES[transport]].sum())
                summary, cards = dashboard.generate_report(1, 0, ["Brooklyn"], [], [2023, 2025], housing, transport)
                self.assertEqual(len(summary), 4)
                for card in cards[:8]:
                    self.assertEqual(card.children[0].__class__.__name__, "Graph")
        result = dashboard.apply_search(1, 0, "11212 2023 affordable fatalities", 0)
        self.assertEqual(result[1], ["11212"])
        self.assertEqual(result[2], [2023, 2023])
        self.assertEqual(result[4], "Fatalities")
        self.assertEqual(result[-1], 1)

    def test_rq1_to_rq4_plot_values(self):
        df = dashboard.filter_data(["Brooklyn"], [], [2023, 2025], "Affordable units", "Serious crashes")
        figs = [fn(df) for _, fn in ALL_CHARTS[:4]]
        self.assertAlmostEqual(sum(sum(trace.x) for trace in figs[0].data), df.affordable_units.sum())
        for trace in figs[1].data:
            self.assertAlmostEqual(sum(trace.y), 100)
        self.assertEqual(list(figs[2].data[0].x), [2023, 2024, 2025])
        self.assertEqual(list(figs[2].data[0].y), list(df.groupby("year").affordable_units.sum()))
        self.assertAlmostEqual(sum(sum(trace.y) for trace in figs[3].data), df.severe_injuries.sum())
