"""
Member 2 charts - REPLACE the placeholders with your real charts.

Team format: def chart_x(df): ... return fig
`df` is df_integrated already filtered by the website, plus:
    housing_selected   -> housing column chosen in the housing dropdown
    injuries_selected  -> injury column chosen in the transportation dropdown
Use apply_style(fig, title, x_title, y_title) from charts.style so all charts match.
See member4.py for a full example.
"""

from charts.style import apply_style, placeholder  # noqa: F401


def chart_1(df):
    """Q1: How have affordable housing production and serious crashes changed over time?"""
    return placeholder(2, "How have affordable housing production and serious crashes changed over time?")


def chart_2(df):
    """Q2: Do ZIP codes with more housing projects also have more severe crash injuries?"""
    return placeholder(2, "Do ZIP codes with more housing projects also have more severe crash injuries?")
