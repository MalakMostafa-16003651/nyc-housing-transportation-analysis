"""
Visualizations for RQ11 and RQ12 (Person 6 — Lama).

Format: def rqN(df): ... return fig
`df` is df_integrated already filtered by the website, plus helper columns:
    housing_selected / housing_label     -> housing measure chosen in the housing dropdown
    injuries_selected / transport_label  -> road-safety measure chosen in the transportation dropdown

Why both charts use AVERAGES PER MATCHED YEAR instead of sums
-------------------------------------------------------------
ZIP codes are matched in different numbers of years (1 to 5). If we sum over
years, a ZIP matched in all five years looks "high" on BOTH housing and crashes
simply because it has more years of data. In the full matched sample, summed
affordable units and summed serious crashes each correlate strongly with the
number of matched years (Spearman 0.76 and 0.80). Averaging per matched year
reduces the direct effect of differing observation durations. It does not remove
selection bias or make the observed calendar periods identical across ZIPs.
"""

import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from charts.style import (BOROUGH_COLORS, CRASH_COLOR, HOUSING_COLOR, OTHER_COLOR,
                          OVERLAP_COLOR, apply_style)

# RQ11 groups: the question's target group gets the strongest colour
TARGET_GROUP = "High housing, poor safety"
GROUP_COLORS = {
    TARGET_GROUP: OVERLAP_COLOR,
    "High housing, safer": HOUSING_COLOR,
    "Low housing, poor safety": CRASH_COLOR,
    "Low housing, safer": OTHER_COLOR,
}


# Legend under the plot so long group/borough names do not squeeze the chart
LEGEND_BELOW = {"margin": {"b": 40},
                "legend": {"orientation": "h", "yanchor": "top", "y": -0.2, "x": 0,
                           "font": {"size": 10}}}


def _zip_year_averages(df):
    """One row per ZIP: selected measures averaged over the ZIP's matched years."""
    return (
        df.groupby("zip_code", as_index=False)
        .agg(borough=("borough", lambda s: s.mode().iat[0]),
             housing=("housing_selected", "mean"),
             safety=("injuries_selected", "mean"),
             years=("year", "nunique"))
    )


def _spearman(x, y):
    """Rank correlation (robust to the skewed counts); None if it is undefined."""
    if len(x) < 3 or x.nunique() < 2 or y.nunique() < 2:
        return None
    rho = float(np.corrcoef(x.rank(), y.rank())[0, 1])
    return 0.0 if abs(rho) < 0.005 else rho  # avoid printing "-0.00"


def _at_or_above(values, cut):
    """Values at or above the median. If the median is 0 (e.g. fatalities, where
    most ZIPs have none), only strictly positive values count as high, otherwise
    every ZIP would be labelled high."""
    return values > 0 if cut == 0 else values >= cut


def _use_log_axes(per_zip):
    """Counts are heavily right-skewed; log axes only work when every value is positive."""
    return len(per_zip) > 0 and (per_zip["housing"] > 0).all() and (per_zip["safety"] > 0).all()


def _empty(title):
    fig = go.Figure()
    fig.add_annotation(text="No ZIP codes match the current filters.", showarrow=False,
                       x=0.5, y=0.5, xref="paper", yref="paper", font={"color": "#888"})
    return apply_style(fig, title)


def rq11(df):
    """RQ11: Which ZIP codes have high housing growth but poor road safety?

    Categorized scatter: one dot per ZIP. Each ZIP is split at the MEDIAN of the
    current selection on both axes, giving four groups. "Poor safety" means the
    ZIP's average yearly road-safety count is at or above the median ZIP. The
    three worst ZIPs in the target group are labelled. Both dropdowns and all
    filters change the chart.
    """
    housing_label = df["housing_label"].iloc[0] if len(df) else "Housing"
    transport_label = df["transport_label"].iloc[0] if len(df) else "Crashes"
    title = "High housing, poor road safety: which ZIPs?"
    per_zip = _zip_year_averages(df)
    if per_zip.empty:
        return _empty(title)

    # Median split computed on the CURRENT selection, so groups adapt to the filters
    housing_cut = per_zip["housing"].median()
    safety_cut = per_zip["safety"].median()
    high_housing = _at_or_above(per_zip["housing"], housing_cut)
    poor_safety = _at_or_above(per_zip["safety"], safety_cut)
    per_zip["group"] = np.select(
        [high_housing & poor_safety, high_housing & ~poor_safety, ~high_housing & poor_safety],
        [TARGET_GROUP, "High housing, safer", "Low housing, poor safety"],
        default="Low housing, safer",
    )
    counts = per_zip["group"].value_counts()
    per_zip["group_label"] = per_zip["group"].map(lambda g: f"{g} ({counts.get(g, 0)} ZIPs)")


    order = [f"{g} ({counts.get(g, 0)} ZIPs)" for g in GROUP_COLORS]
    log_axes = _use_log_axes(per_zip)
    fig = px.scatter(
        per_zip, x="housing", y="safety", color="group_label",
        category_orders={"group_label": order},
        color_discrete_map={f"{g} ({counts.get(g, 0)} ZIPs)": c for g, c in GROUP_COLORS.items()},
        log_x=log_axes, log_y=log_axes,
        hover_data={"zip_code": True, "borough": True, "years": True, "group_label": False, "housing": ":.1f", "safety": ":.1f"},
        labels={"housing": f"{housing_label} per year", "safety": f"{transport_label} per year",
                "zip_code": "ZIP code", "borough": "Borough", "years": "Matched years"},
    )
    fig.update_traces(marker={"size": 9, "opacity": 0.85, "line": {"width": 0.5, "color": "white"}})

    # Dashed median lines show where the four groups are split
    fig.add_vline(x=housing_cut, line={"dash": "dash", "color": "#888", "width": 1})
    fig.add_hline(y=safety_cut, line={"dash": "dash", "color": "#888", "width": 1})
    # Label the 3 target-group ZIPs with the worst safety value. Arrows point
    # in different directions so the labels never sit on top of each other.
    worst = per_zip[per_zip["group"] == TARGET_GROUP].nlargest(3, "safety")
    offsets = [(35, -35), (-40, -30), (55, 15)]
    for (_, row), (ax, ay) in zip(worst.iterrows(), offsets):
        fig.add_annotation(
            x=np.log10(row["housing"]) if log_axes else row["housing"],
            y=np.log10(row["safety"]) if log_axes else row["safety"],
            text=row["zip_code"], ax=ax, ay=ay, showarrow=True, arrowhead=0,
            arrowcolor="#555", font={"size": 10, "color": "#333"},
            bgcolor="rgba(255,255,255,0.8)")

    scale = " (log)" if log_axes else ""
    fig = apply_style(fig, title, f"{housing_label} per year{scale}",
                      f"{transport_label} per year{scale}")
    fig.update_layout(**LEGEND_BELOW)
    return fig


def rq12(df):
    """RQ12: Does the relationship between affordable housing production and serious
    crashes differ across boroughs?

    Scatter coloured by borough with one trend line per borough. Each legend entry
    reports the borough's Spearman rank correlation and number of ZIPs, so the
    strength of the relationship can be compared directly. Lines are fitted on the
    log scale (straight on log axes); boroughs with fewer than 3 ZIPs get no line.
    """
    housing_label = df["housing_label"].iloc[0] if len(df) else "Housing"
    transport_label = df["transport_label"].iloc[0] if len(df) else "Crashes"
    title = "Housing vs road safety: does it differ by borough?"
    per_zip = _zip_year_averages(df)
    if per_zip.empty:
        return _empty(title)

    log_axes = _use_log_axes(per_zip)
    fig = go.Figure()
    for borough, color in BOROUGH_COLORS.items():
        group = per_zip[per_zip["borough"] == borough]
        if group.empty:
            continue
        rho = _spearman(group["housing"], group["safety"])
        stat = f"ρ = {rho:.2f}" if rho is not None else "ρ n/a"
        name = f"{borough} ({stat}, n = {len(group)})"

        fig.add_trace(go.Scatter(
            x=group["housing"], y=group["safety"], mode="markers", name=name,
            legendgroup=borough, marker={"color": color, "size": 8, "opacity": 0.8},
            customdata=np.stack([group["zip_code"], group["years"]], axis=-1),
            hovertemplate=(f"<b>%{{customdata[0]}}</b> ({borough})<br>"
                           f"{housing_label}/year: %{{x:.1f}}<br>"
                           f"{transport_label}/year: %{{y:.1f}}<br>"
                           "Matched years: %{customdata[1]}<extra></extra>"),
        ))

        # Borough trend line: least squares on log10 values when axes are log
        if rho is None:
            continue
        x, y = group["housing"].to_numpy(float), group["safety"].to_numpy(float)
        xs = np.linspace(x.min(), x.max(), 50)
        if log_axes:
            slope, intercept = np.polyfit(np.log10(x), np.log10(y), 1)
            ys = 10 ** (intercept + slope * np.log10(xs))
        else:
            slope, intercept = np.polyfit(x, y, 1)
            ys = intercept + slope * xs
        fig.add_trace(go.Scatter(
            x=xs, y=ys, mode="lines", legendgroup=borough, showlegend=False,
            line={"color": color, "width": 2}, hoverinfo="skip",
        ))

    if log_axes:
        fig.update_xaxes(type="log")
        fig.update_yaxes(type="log")
    scale = " (log)" if log_axes else ""
    fig = apply_style(fig, title, f"{housing_label} per year{scale}",
                      f"{transport_label} per year{scale}")
    fig.update_layout(**LEGEND_BELOW)
    fig.update_layout(legend_title={"text": "ρ = rank correlation within each borough", "side": "top"})
    return fig
