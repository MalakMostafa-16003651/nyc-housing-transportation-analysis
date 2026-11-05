"""Shared look for every chart, so all 12 charts match (Person 5 can tune this)."""

import plotly.graph_objects as go

BOROUGH_COLORS = {
    "Manhattan": "#2a6fdb",
    "Brooklyn": "#e0702b",
    "Queens": "#2f9e6e",
    "Bronx": "#c43d5a",
    "Staten Island": "#7d5bbe",
}
HOUSING_COLOR = "#2a6fdb"
CRASH_COLOR = "#c43d5a"


def apply_style(fig, title, x_title=None, y_title=None):
    """Common title, fonts, margins and hover style."""
    fig.update_layout(
        title={"text": title, "x": 0.02, "font": {"size": 16}},
        template="plotly_white",
        font={"family": "Inter, Arial, sans-serif", "size": 12},
        margin={"l": 60, "r": 20, "t": 60, "b": 50},
        height=420,
        hoverlabel={"font_size": 12},
        legend={"title": None},
    )
    if x_title is not None:
        fig.update_xaxes(title=x_title)
    if y_title is not None:
        fig.update_yaxes(title=y_title)
    return fig


def placeholder(member, question):
    """Empty chart shown until a member adds their real chart."""
    fig = go.Figure()
    fig.add_annotation(
        text=f"Member {member}: chart coming soon<br><sup>{question}</sup>",
        showarrow=False, font={"size": 14, "color": "#888"},
        x=0.5, y=0.5, xref="paper", yref="paper",
    )
    for update in (fig.update_xaxes, fig.update_yaxes):
        update(showgrid=False, zeroline=False, showticklabels=False)
    return apply_style(fig, question)
