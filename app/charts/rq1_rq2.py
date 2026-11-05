"""
Visualizations for RQ1 and RQ2.

Format: def rqN(df): ... return fig
`df` is df_integrated already filtered by the website, plus helper columns:
    housing_selected / housing_label     -> housing measure chosen in the housing dropdown
    injuries_selected / transport_label  -> road-safety measure chosen in the transportation dropdown
Use apply_style(fig, title, x_title, y_title) from charts.style so every chart matches.
See rq7_rq8.py for a complete example.
"""

from charts.style import apply_style, placeholder  # noqa: F401


def rq1(df):
    """RQ1: Do ZIP codes with more affordable housing units also have more serious crashes?"""
    return placeholder(1, "Do ZIP codes with more affordable housing units also have more serious crashes?")


def rq2(df):
    """RQ2: Which boroughs have the highest affordable housing production and serious crash counts?"""
    return placeholder(2, "Which boroughs have the highest affordable housing production and serious crash counts?")
