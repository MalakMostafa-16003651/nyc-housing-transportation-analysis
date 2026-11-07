"""
Visualizations for RQ9 and RQ10 (Member 5 - Kenzy), adapted from Person5_Research_Questions.ipynb.

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
from plotly.subplots import make_subplots

from charts.style import CRASH_COLOR, HOUSING_COLOR, OTHER_COLOR, OVERLAP_COLOR, apply_style

REPO_ROOT = Path(__file__).resolve().parents[2]
CENTROID_FILES = [REPO_ROOT / "data" / "zip_centroids.csv", REPO_ROOT / "zip_centroids.csv"]

GROUP_ORDER = ["High on both", "High housing only", "High crashes only", "Neither"]
GROUP_COLORS = {"High on both": OVERLAP_COLOR, "High housing only": HOUSING_COLOR,
                "High crashes only": CRASH_COLOR, "Neither": OTHER_COLOR}
FULL_YEARS = [2023, 2024, 2025]   # interior calendar years; geography remains selective
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
    high_h = ((totals["affordable_units"] >= totals["affordable_units"].quantile(0.75))
              & (totals["affordable_units"] > 0))
    high_c = ((totals["serious_crashes"] >= totals["serious_crashes"].quantile(0.75))
              & (totals["serious_crashes"] > 0))
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
    title = "Housing and crash overlap"
    totals = _zip_groups(df)
    n_both = int((totals["group"] == "High on both").sum())
    group_order = GROUP_ORDER
    group_colors = GROUP_COLORS
    if len(totals) < 4:
        # Keep the map useful for a single-ZIP filter without calling that ZIP a hotspot.
        group_order = ["Selected ZIPs (fewer than 4)"]
        group_colors = {group_order[0]: HOUSING_COLOR}
        totals["group"] = group_order[0]
        title += ": select ≥4 ZIPs for quartile comparisons"
    else:
        title += f": {n_both} ZIPs in both selected top quartiles"

    fig = go.Figure()
    if CENTROIDS is not None:
        mapped = totals.join(CENTROIDS, on="zip_code").dropna(subset=["lat", "lon"])
    else:
        mapped = totals.iloc[:0]
    if not mapped.empty:
        max_units = max(mapped["affordable_units"].max(), 1)
        for group in reversed(group_order):              # "Neither" first, overlap on top
            g = mapped[mapped["group"] == group]
            fig.add_trace(go.Scattermap(
                lat=g["lat"], lon=g["lon"], mode="markers", name=f"{group} ({len(g)})",
                marker={"size": 7 + 26 * np.sqrt(g["affordable_units"].clip(lower=0) / max_units),
                        "color": group_colors[group], "opacity": 0.85},
                customdata=g[HOVER_COLS], hovertemplate=HOVER))
        fig = apply_style(fig, title)
        # Fit the geographic extent, rather than centring on the density-weighted
        # mean which clips Staten Island and the northern Bronx. Mercator spans
        # match the map projection; reserve room for circles on narrow screens.
        mercator_y = (1 - np.arcsinh(np.tan(np.deg2rad(mapped["lat"]))) / np.pi) / 2
        center_y = (mercator_y.min() + mercator_y.max()) / 2
        center = {"lat": float(np.rad2deg(np.arctan(np.sinh(np.pi * (1 - 2 * center_y))))),
                  "lon": float((mapped["lon"].min() + mapped["lon"].max()) / 2)}
        if len(mapped) == 1:
            zoom = 10.5
        else:
            x_span = max((mapped["lon"].max() - mapped["lon"].min()) / 360, 1e-8)
            y_span = max(mercator_y.max() - mercator_y.min(), 1e-8)
            usable_height = max(420 - fig.layout.margin.t - 40 - 80, 80)
            zoom = float(np.clip(min(np.log2(200 / (512 * x_span)),
                                     np.log2(usable_height / (512 * y_span))), 4, 11.5))
        fig.update_layout(map={"style": MAP_STYLE, "zoom": zoom, "center": center},
                          margin={"l": 10, "r": 10, "b": 40},
                          legend={"x": 0.01, "y": 0.99, "xanchor": "left", "yanchor": "top",
                                  "bgcolor": "rgba(255,255,255,0.85)", "font": {"size": 11},
                                  "traceorder": "reversed"})
        missing = len(totals) - len(mapped)
        note = "Approximate ZIP locations; circle size = affordable units."
        if missing:
            note += f" {missing} ZIP location(s) unavailable."
        fig.add_annotation(text=note, xref="paper", yref="paper", x=0, y=-0.08,
                           showarrow=False, xanchor="left", font={"size": 10, "color": "#777"})
        return fig

    # Fallback without coordinates: same groups on a scatter chart
    for group in reversed(group_order):
        g = totals[totals["group"] == group]
        fig.add_trace(go.Scatter(
            x=g["affordable_units"], y=g["serious_crashes"], mode="markers",
            name=f"{group} ({len(g)})", marker={"size": 9, "color": group_colors[group]},
            customdata=g[HOVER_COLS], hovertemplate=HOVER))
    return apply_style(fig, title + "<br>Coordinates unavailable: showing the same ZIP totals",
                       "Affordable housing units", "Serious crashes")


def rq10(df):
    """RQ10: Do years with higher affordable housing production also have higher or lower severe injuries?

    Line chart of complete years only (2023-2025), restricted to ZIPs represented
    in every selected full year. Both measures are indexed to the first year = 100.
    A zero baseline uses actual totals on labelled separate axes instead.
    """
    title = "Housing and severe injuries over time"
    years = df.loc[df["year"].isin(FULL_YEARS), "year"].unique()
    if len(years) < 2:
        return _message("Select a year range covering at least two of 2023-2025.<br>"
                        "2022 and 2026 are partial years and are not compared.", title)

    full = df[df["year"].isin(FULL_YEARS)]
    coverage = full.groupby("zip_code")["year"].nunique()
    common_zips = coverage[coverage == len(years)].index
    full = full[full["zip_code"].isin(common_zips)]
    if full.empty:
        return _message("No selected ZIP code has data in every selected complete year.", title)
    totals = (full
              .groupby("year")[["affordable_units", "severe_injuries"]].sum().sort_index())
    zero_baseline = bool((totals.iloc[0] == 0).any())
    index = totals if zero_baseline else totals / totals.iloc[0] * 100

    fig = make_subplots(specs=[[{"secondary_y": True}]]) if zero_baseline else go.Figure()
    # Housing labels below the line, injury labels above, so they never overlap
    for column, label, color, position in [
            ("affordable_units", "Affordable units", HOUSING_COLOR, "bottom center"),
            ("severe_injuries", "Severe injuries", CRASH_COLOR, "top center")]:
        trace = go.Scatter(
            x=index.index, y=index[column], name=label, mode="lines+markers+text",
            line={"color": color, "width": 3}, marker={"size": 9},
            text=[f"{v:,.0f}" for v in totals[column]], textposition=position,
            customdata=totals[column],
            hovertemplate=label + "<br>%{x}: %{customdata:,.0f}"
            + ("" if zero_baseline else " (index %{y:.1f})") + "<extra></extra>")
        if zero_baseline:
            fig.add_trace(trace, secondary_y=column == "severe_injuries")
        else:
            fig.add_trace(trace)
    if not zero_baseline:
        fig.add_hline(y=100, line_dash="dot", line_color="#999")
    fig = apply_style(fig, title, "Year")
    fig.update_xaxes(dtick=1, title_standoff=8)
    if zero_baseline:
        fig.update_yaxes(title_text="Affordable units", secondary_y=False, rangemode="tozero")
        fig.update_yaxes(title_text="Severe injuries", secondary_y=True, rangemode="tozero")
        fig.update_layout(margin={"r": 75})
    else:
        low, high = index.min().min(), index.max().max()
        fig.update_yaxes(title_text=f"Index ({int(totals.index[0])} = 100)", range=[low - 6, high + 6])
    fig.update_layout(title={"y": 0.98, "yanchor": "top"},
                      legend={"orientation": "h", "y": 1.05, "yanchor": "bottom", "x": 0},
                      margin={"t": 90, "b": 125})
    note = f"{len(common_zips)} ZIPs in every selected complete year."
    note += "<br>Labels = totals; partial 2022 and 2026 excluded."
    if zero_baseline:
        note += "<br>Zero baseline: actual totals on separate axes."
    fig.add_annotation(text=note,
                       xref="paper", yref="paper", x=0, y=-0.36, showarrow=False,
                       xanchor="left", yanchor="top", align="left",
                       font={"size": 10, "color": "#777"})
    return fig
