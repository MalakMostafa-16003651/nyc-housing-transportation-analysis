"""
Visualizations for RQ3 and RQ4.

Format: def rqN(df): ... return fig
`df` is df_integrated already filtered by the website, plus helper columns:
    housing_selected / housing_label     -> housing measure chosen in the housing dropdown
    injuries_selected / transport_label  -> road-safety measure chosen in the transportation dropdown
Use apply_style(fig, title, x_title, y_title) from charts.style so every chart matches.
See rq7_rq8.py for a complete example.
"""

from charts.style import apply_style, placeholder  # noqa: F401


def rq3(df):
    """RQ3: How have affordable housing production and serious crashes changed over time?"""
    return placeholder(3, "How have affordable housing production and serious crashes changed over time?")


def rq4(df):
    """RQ4: Do ZIP codes with more housing projects also have more severe crash injuries?"""
    return placeholder(4, "Do ZIP codes with more housing projects also have more severe crash injuries?")
