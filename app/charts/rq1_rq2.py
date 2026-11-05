"""Member 1's questions, adapted from Person1_Research_Questions.ipynb.

Geographic and year filters apply before aggregation. Measures stay fixed to
these research questions, as in the member's notebook.
"""
import plotly.express as px
import plotly.graph_objects as go

from charts.style import BOROUGH_COLORS, CRASH_COLOR, HOUSING_COLOR, apply_style


def rq1(df):
    """One point per ZIP code, summed over the selected years."""
    totals = df.groupby(["zip_code", "borough"], as_index=False)[
        ["affordable_units", "serious_crash_count"]
    ].sum()
    fig = px.scatter(
        totals, x="affordable_units", y="serious_crash_count", color="borough",
        color_discrete_map=BOROUGH_COLORS, hover_data=["zip_code"],
        labels={"borough": "Borough", "zip_code": "ZIP code"},
    )
    return apply_style(fig, "Affordable housing vs serious crashes by ZIP code",
                       "Affordable housing units", "Serious crashes")


def rq2(df):
    """Compare shares on a common scale; preserve raw totals in hover."""
    totals = df.groupby("borough")[["affordable_units", "serious_crash_count"]].sum()
    fig = go.Figure()
    for column, label, color in [
        ("affordable_units", "Affordable housing units", HOUSING_COLOR),
        ("serious_crash_count", "Serious crashes", CRASH_COLOR),
    ]:
        denominator = totals[column].sum()
        shares = totals[column] / denominator * 100 if denominator else totals[column] * 0
        fig.add_bar(x=totals.index, y=shares, name=label, marker_color=color,
                    customdata=totals[column].to_numpy().reshape(-1, 1),
                    hovertemplate="%{x}<br>%{y:.1f}%<br>Total: %{customdata[0]:,}<extra>%{fullData.name}</extra>")
    fig.update_layout(barmode="group")
    return apply_style(fig, "Housing and crash shares by borough (selected data)",
                       "Borough", "Share of selected total (%)")
