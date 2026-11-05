"""Member 2's specified research questions using the integrated CSV.

These website implementations do not replace the missing transportation EDA
and cleaning notebook. Borough, ZIP code and year filters apply to both charts.
"""
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from charts.style import BOROUGH_COLORS, CRASH_COLOR, HOUSING_COLOR, apply_style


def rq3(df):
    """Annual totals with separately labelled axes for the different units."""
    totals = df.groupby("year", as_index=False)[["affordable_units", "serious_crash_count"]].sum()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    for column, label, color, secondary in [
        ("affordable_units", "Affordable housing units", HOUSING_COLOR, False),
        ("serious_crash_count", "Serious crashes", CRASH_COLOR, True),
    ]:
        fig.add_trace(go.Scatter(x=totals["year"], y=totals[column],
                                mode="lines+markers", name=label,
                                line={"color": color}), secondary_y=secondary)
    fig = apply_style(fig, "Housing and crashes over time — boundary years may be partial", "Year")
    fig.update_xaxes(dtick=1)
    fig.update_yaxes(title_text="Affordable housing units", secondary_y=False)
    fig.update_yaxes(title_text="Serious crashes", secondary_y=True)
    fig.update_layout(margin={"r": 80})
    return fig


def rq4(df):
    """One point per ZIP code, summed over the selected years."""
    totals = df.groupby(["zip_code", "borough"], as_index=False)[
        ["housing_project_count", "severe_injuries"]
    ].sum()
    fig = px.scatter(
        totals, x="housing_project_count", y="severe_injuries", color="borough",
        color_discrete_map=BOROUGH_COLORS, hover_data=["zip_code"],
        labels={"borough": "Borough", "zip_code": "ZIP code"},
    )
    return apply_style(fig, "Housing projects vs severe injuries by ZIP code",
                       "Housing projects (sum of ZIP-year counts)", "Severe injuries")
