"""
Visualizations for RQ7 and RQ8.

Every chart function follows the same format:
    def chart_x(df): ... return fig
`df` is df_integrated ALREADY FILTERED by the website (borough, ZIP code, years),
plus two helper columns that follow the category dropdowns:
    housing_selected   -> the housing column chosen in the housing dropdown
    injuries_selected  -> the transportation column chosen in the transportation dropdown
    housing_label / transport_label -> the dropdown labels, for axis titles
"""

import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from charts.style import BOROUGH_COLORS, CRASH_COLOR, apply_style


def rq7(df):
    """RQ7: Is a higher number of housing buildings associated with more severe injuries?

    Scatter plot: one dot per ZIP code, totalled over the selected years.
    The axes are fixed to the question (buildings vs severe injuries), so this
    chart reacts to the borough, ZIP and year filters.
    """
    per_zip = (
        df.groupby(["zip_code", "borough"], as_index=False)
        .agg(buildings=("housing_building_count", "sum"),
             severe=("severe_injuries", "sum"))
    )
    fig = px.scatter(
        per_zip, x="buildings", y="severe", color="borough",
        color_discrete_map=BOROUGH_COLORS,
        hover_data={"zip_code": True, "borough": True},
        labels={"buildings": "Housing buildings", "severe": "Severe injuries",
                "zip_code": "ZIP code", "borough": "Borough"},
    )
    fig.update_traces(marker={"size": 9, "opacity": 0.8})

    # Least-squares trendline + Pearson r (no statsmodels needed)
    if len(per_zip) >= 3 and per_zip["buildings"].nunique() > 1:
        slope, intercept = np.polyfit(per_zip["buildings"], per_zip["severe"], 1)
        xs = np.linspace(per_zip["buildings"].min(), per_zip["buildings"].max(), 50)
        trend_label = "Trend (constant injury count)"
        if per_zip["severe"].nunique() > 1:
            r = np.corrcoef(per_zip["buildings"], per_zip["severe"])[0, 1]
            trend_label = f"Trend (r = {r:.2f})"
        fig.add_trace(go.Scatter(
            x=xs, y=slope * xs + intercept, mode="lines",
            name=trend_label, line={"color": "#333", "dash": "dash"},
            hoverinfo="skip",
        ))
    return apply_style(fig, "Housing buildings vs severe injuries by ZIP code",
                       "Housing buildings<br>(sum of ZIP-year counts)", "Severe injuries")


def rq8(df):
    """RQ8: Which boroughs have the highest number of serious crashes per housing project?

    Bar chart: (selected transportation measure) / housing projects, per borough.
    Default measure is serious crashes; the transportation dropdown changes it.
    """
    label = df["transport_label"].iloc[0]
    per_borough = (
        df.groupby("borough", as_index=False)
        .agg(measure=("injuries_selected", "sum"),
             projects=("housing_project_count", "sum"))
    )
    # Avoid dividing by zero: boroughs with no projects are left out
    per_borough = per_borough[per_borough["projects"] > 0].copy()
    per_borough["per_project"] = per_borough["measure"] / per_borough["projects"]
    per_borough = per_borough.sort_values("per_project", ascending=False)

    fig = px.bar(
        per_borough, x="borough", y="per_project",
        text=per_borough["per_project"].round(2),
        hover_data={"measure": True, "projects": True, "per_project": ":.2f"},
        labels={"per_project": f"{label} per housing project", "borough": "Borough",
                "measure": label, "projects": "Summed ZIP-year project counts"},
    )
    fig.update_traces(marker_color=CRASH_COLOR, textposition="outside", cliponaxis=False)
    fig = apply_style(fig, f"{label} per housing project count by borough",
                      "Borough", f"{label} per summed project count")
    fig.add_annotation(text="Denominator sums ZIP-year project counts;<br>a project may repeat across ZIPs or years.",
                       xref="paper", yref="paper", x=0, y=-0.25, showarrow=False,
                       xanchor="left", font={"size": 10, "color": "#777"})
    fig.update_layout(margin={"b": 85})
    return fig
