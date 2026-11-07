"""Shared look for every visualization, so all charts on the website match."""

import textwrap

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
OVERLAP_COLOR = "#6a3d9a"
OTHER_COLOR = "#c9ced3"


def apply_style(fig, title, x_title=None, y_title=None):
    """Common title, fonts, margins and hover style."""
    title = "<br>".join(line for part in title.split("<br>")
                         for line in textwrap.wrap(part, 42))
    title_lines = title.count("<br>") + 1
    fig.update_layout(
        title={"text": title, "x": 0.02, "font": {"size": 15}},
        template="plotly_white",
        font={"family": "Inter, Arial, sans-serif", "size": 12},
        margin={"l": 60, "r": 20, "t": 45 + 20 * title_lines, "b": 50},
        height=420,
        hoverlabel={"font_size": 12},
        legend={"title": None},
    )
    if x_title is not None:
        fig.update_xaxes(title=x_title)
    if y_title is not None:
        fig.update_yaxes(title=y_title)
    return fig


def placeholder(rq_number, question):
    """Empty chart shown until the real visualization for this research question is added."""
    fig = go.Figure()
    wrapped = "<br>".join(textwrap.wrap(question, 55))
    fig.add_annotation(
        text=f"<b>Chart coming soon</b><br><br>{wrapped}",
        showarrow=False, font={"size": 13, "color": "#888"},
        x=0.5, y=0.5, xref="paper", yref="paper",
    )
    for update in (fig.update_xaxes, fig.update_yaxes):
        update(showgrid=False, zeroline=False, showticklabels=False)
    return apply_style(fig, f"RQ{rq_number}")
