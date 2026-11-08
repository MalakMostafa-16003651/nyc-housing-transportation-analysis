"""Run from the repository root: python -m unittest discover -s tests."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
import app as dashboard
from charts import ALL_CHARTS
from charts import rq7_rq8, rq9_rq10, rq11_rq12
import data_loader


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
            for number, chart in ALL_CHARTS:
                with self.subTest(rq=number, boroughs=boroughs, zips=zips):
                    fig = chart(df)
                    self.assertTrue(len(fig.data) > 0 or len(fig.layout.annotations) > 0)
                    fig.to_json()
        self.assertTrue((df.zip_code == "11212").all())
        self.assertTrue((df.year == 2023).all())

    def test_search_and_empty_report(self):
        parsed = dashboard.parse_search("Brooklyn 2023 2025 severe")
        self.assertEqual(parsed["borough"], ["Brooklyn"])
        self.assertEqual(parsed["years"], [2023, 2025])
        self.assertEqual(parsed["transport"], "Severe injuries")
        _, charts, exploration = dashboard.generate_report(1, 0, [], ["00000"], [2023, 2025],
                                              "Affordable units", "Serious crashes")
        self.assertEqual(charts, [])
        self.assertEqual(exploration, [])

    def test_http_report_callback(self):
        client = dashboard.server.test_client()
        for route in ["/", "/_dash-layout", "/_dash-dependencies"]:
            self.assertEqual(client.get(route).status_code, 200)
        key = next(k for k in dashboard.app.callback_map if "summary-row" in k)
        response = client.post("/_dash-update-component", json={
            "output": key,
            "outputs": [{"id": "summary-row", "property": "children"},
                        {"id": "charts-grid", "property": "children"},
                        {"id": "exploration-chart", "property": "children"}],
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
        for card in cards[:10]:
            self.assertEqual(card["props"]["children"][0]["type"], "Graph")
        self.assertEqual(response.get_json()["response"]["exploration-chart"]["children"]["type"], "Graph")

    def test_every_measure_combination_and_search(self):
        for housing in dashboard.HOUSING_CATEGORIES:
            for transport in dashboard.TRANSPORT_CATEGORIES:
                df = dashboard.filter_data(["Brooklyn"], [], [2023, 2025], housing, transport)
                self.assertEqual(df.housing_selected.sum(), df[dashboard.HOUSING_CATEGORIES[housing]].sum())
                self.assertEqual(df.injuries_selected.sum(), df[dashboard.TRANSPORT_CATEGORIES[transport]].sum())
                summary, cards, exploration = dashboard.generate_report(1, 0, ["Brooklyn"], [], [2023, 2025], housing, transport)
                self.assertEqual(len(summary), 4)
                figure = exploration.figure
                self.assertEqual(figure.layout.xaxis.title.text, housing)
                self.assertEqual(figure.layout.yaxis.title.text, transport)
                self.assertEqual(sum(sum(trace.x) for trace in figure.data), df.housing_selected.sum())
                self.assertEqual(sum(sum(trace.y) for trace in figure.data), df.injuries_selected.sum())
                for card in cards[:10]:
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

    def test_search_does_not_silently_drop_unknown_zip_or_year(self):
        for query in ["Brooklyn 99999", "11212 2020", "Brooklyn 2023 2029"]:
            with self.subTest(query=query):
                result = dashboard.apply_search(1, 0, query, 4)
                self.assertTrue(all(value is dashboard.dash.no_update for value in result[:5]))
                self.assertIn("Search not applied", result[5])
                self.assertIs(result[-1], dashboard.dash.no_update)
        self.assertEqual(dashboard.parse_search("non-severe buildings 2024")["transport"],
                         "Non-severe injuries")
        self.assertEqual(dashboard.parse_search("total units 2024")["housing"], "Total housing units")

    def test_missing_or_invalid_data_is_never_replaced_with_dummy_rows(self):
        # Keep temporary fixtures inside the checkout for restricted Windows hosts.
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1],
                                         prefix=".dashboard-test-") as folder:
            path = Path(folder) / "df_integrated.csv"
            with patch.object(data_loader, "DATA_FILES", [path]):
                with self.assertRaises(FileNotFoundError):
                    data_loader.load_data()
                df = dashboard.df_integrated.copy()
                invalid_frames = [df.drop(columns="affordable_units"),
                                  pd.concat([df, df.iloc[:1]]),
                                  df.assign(severe_injuries=-1),
                                  df.assign(zip_code="1234"),
                                  df.assign(affordable_units=float("nan"))]
                for invalid in invalid_frames:
                    invalid.to_csv(path, index=False)
                    with self.assertRaises(ValueError):
                        data_loader.load_data()

    def test_map_obeys_zip_filter_and_handles_missing_positions(self):
        df = dashboard.filter_data([], ["11212"], [2023, 2025], "Affordable units", "Serious crashes")
        fig = rq9_rq10.rq9(df)
        self.assertEqual(fig.data[0].type, "scattermap")
        self.assertEqual(list(fig.data[0].customdata[:, 0]), ["11212"])
        self.assertNotIn("both selected top quartiles", fig.layout.title.text)
        for positions in [None, pd.DataFrame(columns=["lat", "lon"])]:
            with patch.object(rq9_rq10, "CENTROIDS", positions):
                fallback = rq9_rq10.rq9(df)
                self.assertEqual(fallback.data[0].type, "scatter")
                self.assertIn("Coordinates unavailable", fallback.layout.title.text)
                fallback.to_json()
        zeros = dashboard.df_integrated.iloc[:4].copy()
        zeros["zip_code"] = ["10001", "10002", "10003", "10004"]
        zeros["affordable_units"] = 0
        zeros["serious_crash_count"] = 0
        self.assertTrue((rq9_rq10._zip_groups(zeros)["group"] == "Neither").all())

    def test_rq10_uses_common_zip_panel_and_handles_zero_baseline(self):
        df = dashboard.filter_data([], [], [2023, 2025], "Affordable units", "Serious crashes")
        counts = df.groupby("zip_code").year.nunique()
        common = df[df.zip_code.isin(counts[counts == 3].index)]
        expected = common.groupby("year")[["affordable_units", "severe_injuries"]].sum()
        fig = rq9_rq10.rq10(df)
        for trace, column in zip(fig.data, expected.columns):
            self.assertEqual(list(trace.customdata), list(expected[column]))
            self.assertEqual(list(trace.y), list(expected[column] / expected[column].iloc[0] * 100))
        toy = df.iloc[:2].copy()
        toy["zip_code"] = "11212"
        toy["year"] = [2023, 2024]
        toy["affordable_units"] = [0, 10]
        toy["severe_injuries"] = [0, 2]
        zero = rq9_rq10.rq10(toy)
        self.assertEqual(list(zero.data[0].y), [0, 10])
        self.assertEqual(list(zero.data[1].y), [0, 2])
        self.assertEqual(zero.layout.yaxis2.title.text, "Severe injuries")
        self.assertIn("Zero baseline", zero.layout.annotations[-1].text)
        partial = rq9_rq10.rq10(toy.assign(year=[2022, 2026]))
        self.assertEqual(len(partial.data), 0)
        self.assertIn("partial years", partial.layout.annotations[0].text)

    def test_constant_injury_count_has_no_nan_correlation_label(self):
        df = dashboard.df_integrated.iloc[:3].copy()
        df["zip_code"] = ["10001", "10002", "10003"]
        df["housing_building_count"] = [1, 2, 3]
        df["severe_injuries"] = 0
        fig = rq7_rq8.rq7(df)
        self.assertEqual(fig.data[-1].name, "Trend (constant injury count)")
        self.assertTrue(all(value == 0 for value in fig.data[-1].y))


class Person6ChartTests(unittest.TestCase):
    """RQ11 and RQ12 (Person 6)."""

    def test_rq11_groups_every_zip_once_using_per_year_averages(self):
        df = dashboard.filter_data([], [], [2022, 2026], "Affordable units", "Serious crashes")
        fig = rq11_rq12.rq11(df)
        plotted = sum(len(trace.x) for trace in fig.data)
        self.assertEqual(plotted, df["zip_code"].nunique())
        averages = df.groupby("zip_code")["affordable_units"].mean()
        all_x = sorted(x for trace in fig.data for x in trace.x)
        self.assertEqual(all_x, sorted(averages.tolist()))
        self.assertTrue(any(name.startswith("High housing, poor safety") for name in
                            (trace.name for trace in fig.data)))
        self.assertEqual(len(fig.layout.annotations), 3)  # three labelled ZIPs

    def test_rq11_zero_median_does_not_mark_every_zip_poor_safety(self):
        df = dashboard.filter_data([], [], [2022, 2026], "Affordable units", "Fatalities")
        fig = rq11_rq12.rq11(df)
        names = [trace.name for trace in fig.data]
        self.assertTrue(any("safer" in name for name in names))
        self.assertEqual(fig.layout.xaxis.type, None)  # zeros -> linear axes

    def test_rq12_one_series_per_borough_with_correlation(self):
        df = dashboard.filter_data([], [], [2022, 2026], "Affordable units", "Serious crashes")
        fig = rq11_rq12.rq12(df)
        legend = [trace.name for trace in fig.data if trace.showlegend is not False]
        self.assertEqual(len(legend), df["borough"].nunique())
        self.assertTrue(all("ρ" in name for name in legend))
        bronx = df[df.borough == "Bronx"].groupby("zip_code")[
            ["affordable_units", "serious_crash_count"]].mean()
        rho = bronx.rank().corr().iloc[0, 1]
        self.assertTrue(any(name.startswith(f"Bronx (ρ = {rho:.2f}") for name in legend))

    def test_rq11_rq12_single_zip_and_empty_selection(self):
        single = dashboard.filter_data([], ["11212"], [2023, 2023], "Affordable units", "Serious crashes")
        for chart in (rq11_rq12.rq11, rq11_rq12.rq12):
            chart(single).to_json()
            empty = chart(single.iloc[0:0])
            self.assertIn("No ZIP codes", empty.layout.annotations[0].text)
