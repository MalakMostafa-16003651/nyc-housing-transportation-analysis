"""
Member 3 charts - REPLACE the placeholders with your real charts.

Team format: def chart_x(df): ... return fig
`df` is df_integrated already filtered by the website, plus:
    housing_selected   -> housing column chosen in the housing dropdown
    injuries_selected  -> injury column chosen in the transportation dropdown
Use apply_style(fig, title, x_title, y_title) from charts.style so all charts match.
See member4.py for a full example.
"""

from charts.style import apply_style, placeholder  # noqa: F401


def chart_1(df):
    """Q1: Which ZIP codes have both high affordable housing production and high serious-crash activity?"""
    return placeholder(3, "Which ZIP codes have both high affordable housing production and high serious-crash activity?")


def chart_2(df):
    """Q2: Which ZIP codes have the highest serious crashes relative to affordable housing production?"""
    return placeholder(3, "Which ZIP codes have the highest serious crashes relative to affordable housing production?")
