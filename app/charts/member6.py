"""
Member 6 charts - REPLACE the placeholders with your real charts.

Team format: def chart_x(df): ... return fig
`df` is df_integrated already filtered by the website, plus:
    housing_selected   -> housing column chosen in the housing dropdown
    injuries_selected  -> injury column chosen in the transportation dropdown
Use apply_style(fig, title, x_title, y_title) from charts.style so all charts match.
See member4.py for a full example.
"""

from charts.style import apply_style, placeholder  # noqa: F401


def chart_1(df):
    """Q1: Which ZIP codes have high housing growth but poor road safety?"""
    return placeholder(6, "Which ZIP codes have high housing growth but poor road safety?")


def chart_2(df):
    """Q2: Does the housing-crash relationship differ across boroughs?"""
    return placeholder(6, "Does the housing-crash relationship differ across boroughs?")
