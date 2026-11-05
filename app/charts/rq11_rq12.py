"""
Visualizations for RQ11 and RQ12.

Format: def rqN(df): ... return fig
`df` is df_integrated already filtered by the website, plus helper columns:
    housing_selected / housing_label     -> housing measure chosen in the housing dropdown
    injuries_selected / transport_label  -> road-safety measure chosen in the transportation dropdown
Use apply_style(fig, title, x_title, y_title) from charts.style so every chart matches.
See rq7_rq8.py for a complete example.
"""

from charts.style import apply_style, placeholder  # noqa: F401


def rq11(df):
    """RQ11: Which ZIP codes have high housing growth but poor road safety?"""
    return placeholder(11, "Which ZIP codes have high housing growth but poor road safety?")


def rq12(df):
    """RQ12: Does the relationship between affordable housing production and serious crashes differ across boroughs?"""
    return placeholder(12, "Does the relationship between affordable housing production and serious crashes differ across boroughs?")
