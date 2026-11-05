"""
Member 4 charts.

Every chart function follows the team format:
    def chart_x(df): ... return fig
`df` is df_integrated ALREADY FILTERED by the website, plus two helper columns:
    housing_selected   -> the housing column picked in the housing dropdown
    injuries_selected  -> the injury column picked in the transportation dropdown
"""

import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from charts.style import BOROUGH_COLORS, CRASH_COLOR, apply_style


def chart_1(df):
    """Q1: Is a higher number of housing buildings associated with more severe injuries?
    Scatter: one dot per ZIP code (summed over the selected years) + trendline."""
    per_zip = (
        df.groupby(["zip_code", "borough"], as_index=False)
        .agg(n_buildings=("n_buildings", "sum"),
             injuries=("injuries_selected", "sum"))
    )
    fig = px.scatter(
        per_zip, x="n_buildings", y="injuries", color="borough",
        color_discrete_map=BOROUGH_COLORS,
        hover_data={"zip_code": True, "borough": True},
        labels={"n_buildings": "Housing buildings", "injuries": "Serious injuries"},
    )
    # Least-squares trendline (no statsmodels needed)
    if len(per_zip) >= 2 and per_zip["n_buildings"].nunique() > 1:
        slope, intercept = np.polyfit(per_zip["n_buildings"], per_zip["injuries"], 1)
        xs = np.linspace(per_zip["n_buildings"].min(), per_zip["n_buildings"].max(), 50)
        r = np.corrcoef(per_zip["n_buildings"], per_zip["injuries"])[0, 1]
        fig.add_trace(go.Scatter(
            x=xs, y=slope * xs + intercept, mode="lines",
            name=f"Trend (r = {r:.2f})", line={"color": "#333", "dash": "dash"},
        ))
    return apply_style(fig, "Housing buildings vs serious injuries by ZIP code",
                       "Housing buildings", "Serious injuries")


def chart_2(df):
    """Q2: Which boroughs have the highest number of serious crashes per housing project?
    Bar chart of injuries / projects per borough."""
    per_borough = (
        df.groupby("borough", as_index=False)
        .agg(injuries=("injuries_selected", "sum"),
             projects=("n_projects", "sum"))
    )
    # Avoid dividing by zero: boroughs with no projects are left out
    per_borough = per_borough[per_borough["projects"] > 0].copy()
    per_borough["per_project"] = per_borough["injuries"] / per_borough["projects"]
    per_borough = per_borough.sort_values("per_project", ascending=False)

    fig = px.bar(
        per_borough, x="borough", y="per_project",
        text=per_borough["per_project"].round(2),
        hover_data={"injuries": True, "projects": True, "per_project": ":.2f"},
        labels={"per_project": "Serious injuries per housing project",
                "borough": "Borough"},
    )
    fig.update_traces(marker_color=CRASH_COLOR, textposition="outside")
    return apply_style(fig, "Serious injuries per housing project by borough",
                       "Borough", "Injuries per project")
