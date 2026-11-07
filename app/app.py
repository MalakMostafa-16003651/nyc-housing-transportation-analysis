"""
Housing Growth and Road Safety in New York City - interactive website (Dash).

Run locally:    python app/app.py   then open http://127.0.0.1:8050
Run on Render:  gunicorn --chdir app app:server

Visualizations live in app/charts/ and are listed in app/charts/__init__.py.
"""

import re

import dash
from dash import Dash, Input, Output, State, dcc, html

from charts import ALL_CHARTS
from data_loader import HOUSING_CATEGORIES, TRANSPORT_CATEGORIES, load_data

# --------------------------------------------------------------------------
# Data (loaded once when the server starts)
# --------------------------------------------------------------------------
df_integrated, IS_DUMMY = load_data()

BOROUGHS = sorted(df_integrated["borough"].unique())
ZIP_CODES = sorted(df_integrated["zip_code"].unique())
YEAR_MIN = int(df_integrated["year"].min())
YEAR_MAX = int(df_integrated["year"].max())
DEFAULT_HOUSING = list(HOUSING_CATEGORIES)[0]
DEFAULT_TRANSPORT = list(TRANSPORT_CATEGORIES)[0]

# Words people may type in the search box -> filter values
BOROUGH_ALIASES = {
    "manhattan": "Manhattan", "brooklyn": "Brooklyn", "queens": "Queens",
    "bronx": "Bronx", "staten island": "Staten Island", "staten": "Staten Island",
}
# Checked in order, so more specific phrases come first
HOUSING_KEYWORDS = {
    "total units": "Total housing units", "total housing": "Total housing units",
    "affordable": "Affordable units", "units": "Affordable units",
    "buildings": "Housing buildings", "building": "Housing buildings",
    "projects": "Housing projects", "project": "Housing projects",
}
TRANSPORT_KEYWORDS = {
    "non-severe": "Non-severe injuries", "non severe": "Non-severe injuries",
    "minor": "Non-severe injuries",
    "severe": "Severe injuries", "injuries": "Severe injuries", "injury": "Severe injuries",
    "fatalities": "Fatalities", "fatality": "Fatalities", "deaths": "Fatalities",
    "fatal": "Fatalities",
    "crashes": "Serious crashes", "crash": "Serious crashes",
}

GRAPH_CONFIG = {"displaylogo": False, "responsive": True}

# --------------------------------------------------------------------------
# Layout
# --------------------------------------------------------------------------
app = Dash(__name__, title="NYC Housing & Road Safety")
server = app.server  # used by gunicorn on Render


def filter_block(label, component):
    return html.Div([html.Label(label, className="filter-label"), component],
                    className="filter-block")


app.layout = html.Div(className="page", children=[
    # Header
    html.Header(className="header", children=[
        html.H1("Housing Growth and Road Safety in New York City"),
        html.P("How does affordable housing production relate to serious traffic "
               "injuries across NYC ZIP codes and boroughs?"),
        html.Div("Showing DUMMY data - the real merged dataset is not added yet.",
                 className="dummy-banner") if IS_DUMMY else None,
    ]),

    # Search
    html.Section(className="card", children=[
        html.H2("Search"),
        html.Div(className="search-row", children=[
            dcc.Input(id="search-input", type="text", debounce=False,
                      placeholder='Try "Brooklyn 2023 2025 severe" or "11212 affordable fatalities"',
                      className="search-input"),
            html.Button("Search", id="search-btn", n_clicks=0, className="btn btn-secondary"),
        ]),
        html.Div(id="search-feedback", className="search-feedback"),
    ]),

    # Filters
    html.Section(className="card", children=[
        html.H2("Filters"),
        html.Div(className="filter-grid", children=[
            filter_block("Borough", dcc.Dropdown(
                id="borough-filter", options=BOROUGHS, value=[], multi=True,
                placeholder="All boroughs")),
            filter_block("ZIP code", dcc.Dropdown(
                id="zip-filter", options=ZIP_CODES, value=[], multi=True,
                placeholder="All ZIP codes (type to search)")),
            filter_block("Housing category", dcc.Dropdown(
                id="housing-filter", options=list(HOUSING_CATEGORIES),
                value=DEFAULT_HOUSING, clearable=False)),
            filter_block("Transportation category", dcc.Dropdown(
                id="transport-filter", options=list(TRANSPORT_CATEGORIES),
                value=DEFAULT_TRANSPORT, clearable=False)),
        ]),
        filter_block("Years", dcc.RangeSlider(
            id="year-filter", min=YEAR_MIN, max=YEAR_MAX, step=1,
            value=[YEAR_MIN, YEAR_MAX],
            marks={y: str(y) for y in range(YEAR_MIN, YEAR_MAX + 1)})),
        html.Button("Generate Report", id="generate-btn", n_clicks=0,
                    className="btn btn-primary"),
    ]),

    html.P("Borough, ZIP and year filters apply to every chart. Housing and transportation "
           "selectors update summary totals; RQ8 also uses the transportation selection. "
           "Other charts keep the measures named in their research questions.",
           className="filter-help"),
    html.P("Data scope: matched ZIP-years only. Housing includes preservation and new "
           "construction. Crash records cover October 2022–June 2026; boundary years "
           "are partial. Totals are not citywide crash risk measures.", className="filter-help"),

    # Report output
    dcc.Store(id="search-trigger", data=0),
    dcc.Loading(type="circle", children=[
        html.Div(id="summary-row", className="summary-row"),
        html.Div(id="charts-grid", className="charts-grid"),
    ]),

    # Story section
    html.Section(className="card story", children=[
        html.H2("The story: building homes where the streets are most dangerous"),

        html.H3("Question"),
        html.P("New York produces about 29,000 affordable homes a year, and every new resident "
               "walks, cycles, rides or drives on the streets around them. Is affordable housing "
               "being built where serious crashes happen, and does more housing mean more people "
               "badly hurt? If the city's most affordable homes sit on its most dangerous streets, "
               "the families least able to afford a car or a hospital bill are the most exposed."),

        html.H3("Key findings"),
        html.Ul([
            html.Li("Housing and crashes go together across space: ZIP codes with more affordable "
                    "units have more serious crashes (RQ1, Spearman ρ = 0.64), and ZIPs with more "
                    "housing buildings have more severe injuries (RQ7, ρ = 0.73)."),
            html.Li("The overlap is concentrated (RQ9 map): 23 of 143 ZIP codes are in the top 25% "
                    "for both. They hold 44% of affordable units, 34% of serious crashes and 29% "
                    "of crash deaths, in two clusters: the South/Central Bronx (11 ZIPs) and "
                    "Central/East Brooklyn (8 ZIPs). East New York (11207) and Brownsville (11212) "
                    "are the worst."),
            html.Li("Brooklyn leads in both housing and crashes (RQ2: 33% of units, 38% of "
                    "crashes). The Bronx builds almost as much housing with fewer crashes per "
                    "project (RQ8: 1.94 vs 5.53 in Staten Island)."),
            html.Li("More housing does not bring more injuries over time (RQ10): from 2023 to 2025 "
                    "citywide affordable production was flat (+0.6%) while severe injuries rose "
                    "17.5%. Within ZIP codes, years with more new housing did not have more "
                    "injuries (ρ = -0.09, not significant)."),
            html.Li("Over the full years, crashes rose while housing did not (RQ3): in matched "
                    "ZIP-years, 2023 to 2025 affordable units fell 2.7% while serious crashes "
                    "rose 18.9%."),
            html.Li("ZIP codes with more housing projects have more severe injuries (RQ4: "
                    "Pearson r = 0.71, Spearman ρ = 0.81 across 143 ZIPs)."),
            html.Li("High-in-both ZIP-years are a Bronx and Brooklyn pattern (RQ5): 27 of the 29 "
                    "ZIP-years in the top 25% for both in 2023-2025 are in these two boroughs."),
            html.Li("Some ZIPs have many crashes for little housing (RQ6): 11234 (Brooklyn) and "
                    "11377 (Queens) have about 65 serious crashes per 100 affordable units."),
            # TODO (Lama): one html.Li each for RQ11 and RQ12
            html.Li("What surprised us: the link is about place, not construction. Affordable "
                    "housing is going up in neighbourhoods that were already dangerous, and "
                    "injuries there keep rising."),
        ]),

        html.H3("Limitations"),
        html.Ul([
            html.Li("Correlation is not causation: dense, lower-income areas with wide arterial "
                    "roads tend to have both more housing and more crashes."),
            html.Li("Counts are not risk rates: there is no population or traffic-volume "
                    "denominator."),
            html.Li("Crash records cover October 2022 to June 2026, so 2022 and 2026 are partial; "
                    "year comparisons use 2023-2025 only (three points)."),
            html.Li("Housing is dated by project start; residents arrive years later."),
            html.Li("Only ZIP-years present in both datasets are included; about 16% of crashes "
                    "have no coordinates and are counted but not mapped. ZIP codes are coarse "
                    "and a few cross borough lines. Housing includes preservation, not only new "
                    "buildings."),
        ]),

        html.H3("Why it matters for NYC"),
        html.Ul([
            html.Li("NYC DOT / Vision Zero: prioritise the 23 overlap ZIPs for street redesigns "
                    "(daylighting, protected bike lanes, leading pedestrian intervals, speed "
                    "cameras); one project there protects current and future residents."),
            html.Li("HPD and City Planning: add a street-safety check to site selection for large "
                    "affordable projects in overlap ZIPs and coordinate with DOT before move-in."),
            html.Li("Community boards and housing advocates in the Bronx and East Brooklyn: use "
                    "the map to ask for safety investment alongside new housing."),
        ]),
    ]),

    html.Footer("ICS503 Data Engineering and Visualization - Winter 2026",
                className="footer"),
])


# --------------------------------------------------------------------------
# Search: turn typed text into filter values
# --------------------------------------------------------------------------
def parse_search(text):
    """Return a dict of filter values found in the text, plus a list of notes."""
    text = (text or "").lower()
    found = {}

    boroughs = []
    for word, borough in BOROUGH_ALIASES.items():
        if re.search(r"\b" + word + r"\b", text) and borough in BOROUGHS \
                and borough not in boroughs:
            boroughs.append(borough)
    if boroughs:
        found["borough"] = boroughs

    zips = [z for z in re.findall(r"\b\d{5}\b", text) if z in ZIP_CODES]
    if zips:
        found["zip"] = sorted(set(zips))

    years = [int(y) for y in re.findall(r"\b(?:19|20)\d{2}\b", text)
             if YEAR_MIN <= int(y) <= YEAR_MAX]
    if years:
        found["years"] = [min(years), max(years)]

    # Phrases are checked in order, so "non-severe" is matched before "severe"
    for word, category in TRANSPORT_KEYWORDS.items():
        if re.search(r"\b" + re.escape(word) + r"\b", text):
            found["transport"] = category
            break
    for word, category in HOUSING_KEYWORDS.items():
        if re.search(r"\b" + re.escape(word) + r"\b", text):
            found["housing"] = category
            break
    return found


@app.callback(
    Output("borough-filter", "value"),
    Output("zip-filter", "value"),
    Output("year-filter", "value"),
    Output("housing-filter", "value"),
    Output("transport-filter", "value"),
    Output("search-feedback", "children"),
    Output("search-trigger", "data"),
    Input("search-btn", "n_clicks"),
    Input("search-input", "n_submit"),
    State("search-input", "value"),
    State("search-trigger", "data"),
    prevent_initial_call=True,
)
def apply_search(_clicks, _submit, text, trigger):
    found = parse_search(text)
    if not found:
        return (dash.no_update,) * 5 + (
            "No filters recognised. Try a borough, a year, a ZIP code, a housing word "
            "('affordable', 'buildings', 'projects') or a road-safety word "
            "('crashes', 'severe', 'non-severe', 'fatalities').",
            dash.no_update,
        )

    # Anything not mentioned in the search goes back to "all"
    borough = found.get("borough", [])
    zips = found.get("zip", [])
    years = found.get("years", [YEAR_MIN, YEAR_MAX])
    housing = found.get("housing", DEFAULT_HOUSING)
    transport = found.get("transport", DEFAULT_TRANSPORT)

    applied = []
    if "borough" in found:
        applied.append("Borough: " + ", ".join(borough))
    if "zip" in found:
        applied.append("ZIP: " + ", ".join(zips))
    if "years" in found:
        applied.append(f"Years: {years[0]}-{years[1]}")
    if "housing" in found:
        applied.append("Housing: " + housing)
    if "transport" in found:
        applied.append("Transportation: " + transport)

    feedback = "Applied - " + " | ".join(applied)
    # Changing search-trigger makes the report regenerate automatically
    return borough, zips, years, housing, transport, feedback, (trigger or 0) + 1


# --------------------------------------------------------------------------
# Generate Report: filter the data and redraw every chart
# --------------------------------------------------------------------------
def filter_data(boroughs, zips, years, housing_label, transport_label):
    dff = df_integrated
    if boroughs:
        dff = dff[dff["borough"].isin(boroughs)]
    if zips:
        dff = dff[dff["zip_code"].isin(zips)]
    if years:
        dff = dff[dff["year"].between(years[0], years[1])]
    dff = dff.copy()
    # Helper columns so every chart respects the category dropdowns
    dff["housing_selected"] = dff[HOUSING_CATEGORIES[housing_label]]
    dff["injuries_selected"] = dff[TRANSPORT_CATEGORIES[transport_label]]
    dff["housing_label"] = housing_label
    dff["transport_label"] = transport_label
    return dff


def summary_tile(label, value):
    return html.Div([html.Div(value, className="tile-value"),
                     html.Div(label, className="tile-label")], className="tile")


@app.callback(
    Output("summary-row", "children"),
    Output("charts-grid", "children"),
    Input("generate-btn", "n_clicks"),
    Input("search-trigger", "data"),
    State("borough-filter", "value"),
    State("zip-filter", "value"),
    State("year-filter", "value"),
    State("housing-filter", "value"),
    State("transport-filter", "value"),
)
def generate_report(_clicks, _trigger, boroughs, zips, years, housing, transport):
    dff = filter_data(boroughs, zips, years, housing, transport)

    if dff.empty:
        message = html.Div(
            "No data matches these filters. Try fewer filters or a wider year range.",
            className="empty-message")
        return message, []

    summary = [
        summary_tile(housing, f"{int(dff['housing_selected'].sum()):,}"),
        summary_tile(transport, f"{int(dff['injuries_selected'].sum()):,}"),
        summary_tile("ZIP codes", f"{dff['zip_code'].nunique():,}"),
        summary_tile("Years", f"{dff['year'].min()}-{dff['year'].max()}"),
    ]

    cards = []
    for rq_number, chart_fn in ALL_CHARTS:
        try:
            content = dcc.Graph(figure=chart_fn(dff), config=GRAPH_CONFIG,
                                style={"height": "420px"})
        except Exception as err:  # one broken chart must not break the website
            content = html.Div(f"RQ{rq_number} chart error: {err}",
                               className="chart-error")
        cards.append(html.Div([content, html.Div(f"RQ{rq_number}",
                                                 className="chart-label")],
                              className="chart-card"))
    return summary, cards


if __name__ == "__main__":
    app.run(debug=True)
