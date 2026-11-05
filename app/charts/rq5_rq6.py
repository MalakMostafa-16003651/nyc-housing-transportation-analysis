"""
Visualizations for RQ5 and RQ6, adapted from dataEngP3.ipynb for the website.

In the notebook both charts use 2023-2025. On the website they use whatever
borough, ZIP code and year filters are selected.
"""

import plotly.express as px
import plotly.graph_objects as go

from charts.style import apply_style


def _empty(title, message):
    fig = go.Figure()
    fig.add_annotation(text=message, showarrow=False, x=0.5, y=0.5,
                       xref="paper", yref="paper", font={"color": "#888"})
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return apply_style(fig, title)


def rq5(df):
    """RQ5: Which ZIP codes have both high affordable housing production and
    high serious-crash activity?

    Scatter of ZIP-year records. "High" means at or above the 75th percentile
    of the selected data, shown by the dashed lines.
    """
    data = df.copy()
    housing_limit = data["affordable_units"].quantile(0.75)
    crash_limit = data["serious_crash_count"].quantile(0.75)

    data["category"] = (
        (data["affordable_units"] >= housing_limit)
        & (data["serious_crash_count"] >= crash_limit)
    ).map({True: "High in both", False: "Other"})

    fig = px.scatter(
        data,
        x="affordable_units",
        y="serious_crash_count",
        color="category",
        hover_data=["zip_code", "year", "borough"],
        labels={
            "affordable_units": "Affordable Housing Units",
            "serious_crash_count": "Serious Crash Count",
            "category": "Category",
            "zip_code": "ZIP code",
            "year": "Year",
            "borough": "Borough",
        },
    )
    fig.add_vline(x=housing_limit, line_dash="dash")
    fig.add_hline(y=crash_limit, line_dash="dash")
    return apply_style(fig, "Affordable Housing vs Serious Crashes",
                       "Affordable Housing Units", "Serious Crash Count")


def rq6(df):
    """RQ6: Which ZIP codes have the highest number of serious crashes relative
    to affordable housing production?

    Top-10 bar chart of crashes per 100 affordable units. Only ZIP codes present
    in every selected year and with at least 100 affordable units are ranked.
    """
    title = "Top 10 ZIP Codes: Serious Crashes Relative to Affordable Units"
    n_years = df["year"].nunique()

    per_zip = (
        df.groupby(["zip_code", "borough"], as_index=False)
        .agg(
            affordable_units=("affordable_units", "sum"),
            serious_crash_count=("serious_crash_count", "sum"),
            years_observed=("year", "nunique"),
        )
    )
    per_zip = per_zip[
        (per_zip["years_observed"] == n_years)
        & (per_zip["affordable_units"] >= 100)
    ].copy()
    if per_zip.empty:
        return _empty(title, "No ZIP code meets the ranking rules for these filters")

    per_zip["crashes_per_100_units"] = (
        per_zip["serious_crash_count"] / per_zip["affordable_units"] * 100
    )
    top10 = per_zip.nlargest(10, "crashes_per_100_units")

    fig = px.bar(
        top10.sort_values("crashes_per_100_units"),
        x="crashes_per_100_units",
        y="zip_code",
        color="borough",
        orientation="h",
        hover_data=["affordable_units", "serious_crash_count"],
        labels={
            "crashes_per_100_units": "Crashes per 100 Affordable Units",
            "zip_code": "ZIP Code",
            "borough": "Borough",
            "affordable_units": "Affordable units",
            "serious_crash_count": "Serious crashes",
        },
    )
    fig.update_yaxes(type="category")
    return apply_style(fig, title, "Crashes per 100 Affordable Units", "ZIP Code")
