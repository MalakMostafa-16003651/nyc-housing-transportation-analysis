"""
Visualizations for RQ9 and RQ10 (Member 5 - Kenzy), adapted from Person5_RQ9_RQ10_Story.ipynb.

`df` is df_integrated already filtered by the website (borough, ZIP code, years).
Both charts keep the measures named in their research questions, so they react to the
borough, ZIP and year filters but not to the category dropdowns.

RQ9 needs a map position for each ZIP. df_integrated has no coordinates, so the notebook
saves data/zip_centroids.csv (average location of each ZIP's housing buildings and SIRTA
crashes). If that file is missing, RQ9 falls back to a scatter chart with the same groups.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from charts.style import CRASH_COLOR, HOUSING_COLOR, apply_style

REPO_ROOT = Path(__file__).resolve().parents[2]
CENTROID_FILES = [REPO_ROOT / "data" / "zip_centroids.csv", REPO_ROOT / "zip_centroids.csv"]

BOTH_COLOR = "#6a3d9a"
OTHER_COLOR = "#c9ced3"
GROUP_ORDER = ["High on both", "High housing only", "High crashes only", "Neither"]
GROUP_COLORS = {"High on both": BOTH_COLOR, "High housing only": HOUSING_COLOR,
                "High crashes only": CRASH_COLOR, "Neither": OTHER_COLOR}
FULL_YEARS = [2023, 2024, 2025]   # only complete calendar years in both datasets
MAP_STYLE = "carto-positron"      # free basemap, no token needed


def _load_centroids():
    for path in CENTROID_FILES:
        if path.is_file():
            c = pd.read_csv(path, dtype={"zip_code": "string"})
            c["zip_code"] = c["zip_code"].str.zfill(5)
            return c.set_index("zip_code")[["lat", "lon"]]
    return None


CENTROIDS = _load_centroids()


def _message(text, title):
    fig = go.Figure()
    fig.add_annotation(text=text, showarrow=False, x=0.5, y=0.5, xref="paper", yref="paper",
                       font={"size": 13, "color": "#888"})
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return apply_style(fig, title)


def _zip_groups(df):
    """Total each ZIP over the selected years and label it by the top-25% rule."""
    totals = (df.groupby("zip_code", as_index=False)
              .agg(borough=("borough", lambda s: s.mode().iat[0]),
                   affordable_units=("affordable_units", "sum"),
                   serious_crashes=("serious_crash_count", "sum"),
                   severe_injuries=("severe_injuries", "sum"),
                   fatalities=("fatalities", "sum")))
    high_h = totals["affordable_units"] >= totals["affordable_units"].quantile(0.75)
    high_c = totals["serious_crashes"] >= totals["serious_crashes"].quantile(0.75)
    totals["group"] = np.select([high_h & high_c, high_h, high_c], GROUP_ORDER[:3], "Neither")
    return totals


HOVER = ("<b>ZIP %{customdata[0]}</b> - %{customdata[1]}<br>"
         "Affordable units: %{customdata[2]:,.0f}<br>"
         "Serious crashes: %{customdata[3]:,.0f}<br>"
         "Severe injuries: %{customdata[4]:,.0f}<br>"
         "Fatalities: %{customdata[5]:,.0f}<extra></extra>")
HOVER_COLS = ["zip_code", "borough", "affordable_units", "serious_crashes",
              "severe_injuries", "fatalities"]


def rq9(df):
    """RQ9: Where in NYC do high affordable housing production and high serious-crash levels overlap?

    Map: one circle per ZIP; colour = overlap group, size = affordable units.
    "High" = top 25% of the ZIP codes in the current selection.
    """
    title = "Housing and crash hotspots"
    if df["zip_code"].nunique() < 4:
        return _message("Select at least 4 ZIP codes to compare overlap groups.", title)

    totals = _zip_groups(df)
    n_both = int((totals["group"] == "High on both").sum())

    fig = go.Figure()
    if CENTROIDS is not None:
        totals = totals.join(CENTROIDS, on="zip_code").dropna(subset=["lat", "lon"])
        max_units = max(totals["affordable_units"].max(), 1)
        for group in reversed(GROUP_ORDER):              # "Neither" first, hotspots on top
            g = totals[totals["group"] == group]
            fig.add_trace(go.Scattermap(
                lat=g["lat"], lon=g["lon"], mode="markers", name=f"{group} ({len(g)})",
                marker={"size": 7 + 26 * np.sqrt(g["affordable_units"].clip(lower=0) / max_units),
                        "color": GROUP_COLORS[group], "opacity": 0.85},
                customdata=g[HOVER_COLS], hovertemplate=HOVER))
        fig = apply_style(fig, f"{title}: {n_both} ZIPs top 25% in both")
        fig.update_layout(map={"style": MAP_STYLE, "zoom": 9.2,
                               "center": {"lat": float(totals["lat"].mean()),
                                          "lon": float(totals["lon"].mean())}},
                          margin={"l": 10, "r": 10, "t": 50, "b": 10},
                          legend={"x": 0.01, "y": 0.99, "xanchor": "left", "yanchor": "top",
                                  "bgcolor": "rgba(255,255,255,0.85)", "font": {"size": 11},
                                  "traceorder": "reversed"})
        return fig

    # Fallback without coordinates: same groups on a scatter chart
    for group in reversed(GROUP_ORDER):
        g = totals[totals["group"] == group]
        fig.add_trace(go.Scatter(
            x=g["affordable_units"], y=g["serious_crashes"], mode="markers",
            name=f"{group} ({len(g)})", marker={"size": 9, "color": GROUP_COLORS[group]},
            customdata=g[HOVER_COLS], hovertemplate=HOVER))
    return apply_style(fig, f"{title}: {n_both} ZIPs top 25% in both",
                       "Affordable housing units", "Serious crashes")


def rq10(df):
    """RQ10: Do years with higher affordable housing production also have higher or lower severe injuries?

    Line chart of complete years only (2023-2025), both measures indexed to the first
    selected full year = 100 so they share one axis. Labels show the real totals.
    """
    title = "Affordable housing vs severe injuries, complete years only"
    years = df.loc[df["year"].isin(FULL_YEARS), "year"].unique()
    if len(years) < 2:
        return _message("Select a year range covering at least two of 2023-2025.<br>"
                        "2022 and 2026 are partial years and are not compared.", title)

    totals = (df[df["year"].isin(FULL_YEARS)]
              .groupby("year")[["affordable_units", "severe_injuries"]].sum().sort_index())
    base = totals.iloc[0].replace(0, np.nan)
    index = totals / base * 100

    fig = go.Figure()
    # Housing labels below the line, injury labels above, so they never overlap
    for column, label, color, position in [
            ("affordable_units", "Affordable units", HOUSING_COLOR, "bottom center"),
            ("severe_injuries", "Severe injuries", CRASH_COLOR, "top center")]:
        fig.add_trace(go.Scatter(
            x=index.index, y=index[column], name=label, mode="lines+markers+text",
            line={"color": color, "width": 3}, marker={"size": 9},
            text=[f"{v:,.0f}" for v in totals[column]], textposition=position,
            customdata=totals[column],
            hovertemplate=label + "<br>%{x}: %{customdata:,.0f} (index %{y:.1f})<extra></extra>"))
    fig.add_hline(y=100, line_dash="dot", line_color="#999")
    fig = apply_style(fig, title, "Year", f"Index ({int(totals.index[0])} = 100)")
    fig.update_xaxes(dtick=1)
    low, high = index.min().min(), index.max().max()
    fig.update_yaxes(range=[low - 6, high + 6])
    fig.update_layout(legend={"orientation": "h", "y": 1.02, "yanchor": "bottom", "x": 0})
    fig.add_annotation(text="Labels = actual totals. 2022 and 2026 are partial years, not compared.",
                       xref="paper", yref="paper", x=0, y=-0.22, showarrow=False, xanchor="left",
                       font={"size": 10, "color": "#777"})
    return fig
