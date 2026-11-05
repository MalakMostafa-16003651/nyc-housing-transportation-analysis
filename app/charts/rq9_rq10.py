"""
Visualizations for RQ9 and RQ10.

Format: def rqN(df): ... return fig
`df` is df_integrated already filtered by the website, plus helper columns:
    housing_selected / housing_label     -> housing measure chosen in the housing dropdown
    injuries_selected / transport_label  -> road-safety measure chosen in the transportation dropdown
Use apply_style(fig, title, x_title, y_title) from charts.style so every chart matches.
See rq7_rq8.py for a complete example.
"""

from charts.style import apply_style, placeholder  # noqa: F401


def rq9(df):
    """RQ9: Where in NYC do high affordable housing production and high serious-crash levels overlap?"""
    return placeholder(9, "Where in NYC do high affordable housing production and high serious-crash levels overlap?")


def rq10(df):
    """RQ10: Do years with higher affordable housing production also have higher or lower severe injuries?"""
    return placeholder(10, "Do years with higher affordable housing production also have higher or lower severe injuries?")
