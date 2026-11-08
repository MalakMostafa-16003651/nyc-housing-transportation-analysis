"""
Housing Growth and Road Safety in New York City - interactive website (Dash).

Run locally:    python app/app.py   then open http://127.0.0.1:8050
Run on Render:  gunicorn --chdir app app:server

Visualizations live in app/charts/ and are listed in app/charts/__init__.py.
"""

import re

import dash
from dash import Dash, Input, Output, State, dcc, html
import plotly.express as px

from charts import ALL_CHARTS
from charts.style import BOROUGH_COLORS, apply_style
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

    html.P("Choose filters, then select Generate Report to update the charts. "
           "Search applies its recognised filters immediately. Borough, ZIP and year "
           "filters apply to every chart. Housing and transportation "
           "selectors update summary totals and the selected-measures explorer; RQ8 also "
           "uses the transportation selection. "
           "Other charts keep the measures named in their research questions.",
           className="filter-help"),
    html.P("Data scope: matched ZIP-years only. Housing includes preservation and new "
           "construction. The supplied ZIP-resolved crash snapshot spans October 2022–June 2026; boundary years "
           "are partial. Totals are not citywide crash risk measures.", className="filter-help"),

    # Report output
    dcc.Store(id="search-trigger", data=0),
    dcc.Loading(type="circle", children=[
        html.Div(id="summary-row", className="summary-row"),
        html.Section(className="card", children=[
            html.H2("Explore selected measures"),
            html.P("Compare the housing and transportation measures you selected. Each "
                   "point totals one ZIP and borough across the selected years; numbered "
                   "research questions below retain their specified measures.", className="filter-help"),
            html.Div(id="exploration-chart"),
        ]),
        html.Div(id="charts-grid", className="charts-grid"),
    ]),

    # Story section
    html.Section(className="card story", children=[
        html.H2("The story: affordable housing and serious crashes share some locations"),
        html.P("These findings describe the full matched snapshot and stay fixed when report "
               "filters change. The charts above describe the current selection."),

        html.H3("Question"),
        html.P("Where do recorded affordable housing production and serious crashes overlap? "
               "We compare housing project starts with SIRTA records after aggregating each "
               "source by ZIP code and year. Housing includes preservation and new construction; "
               "this is not a measure of net housing growth, residents' exposure, or road-safety risk."),

        html.H3("Key findings"),
        html.Ul([
            html.Li("Housing and crashes go together across space: ZIP codes with more affordable "
                    "units have more serious crashes (RQ1, Spearman ρ = 0.64), and ZIPs with more "
                    "housing buildings have more severe injuries (RQ7, ρ = 0.73)."),
            html.Li("The overlap is concentrated (RQ9 map): 23 of 143 ZIP codes are in the top 25% "
                    "for both. They hold 44% of affordable units, 34% of serious crashes and 29% "
                    "of crash deaths, in two clusters: the South/Central Bronx (11 ZIPs) and "
                    "Central/East Brooklyn (8 ZIPs). These are selected counts, not a ranking "
                    "of danger to individual residents."),
            html.Li("Brooklyn leads in both housing and crashes (RQ2: 33% of units, 38% of "
                    "crashes). The Bronx records almost as many affordable units with fewer crashes per "
                    "project (RQ8: 1.94 vs 5.53 in Staten Island)."),
            html.Li("The temporal analysis does not establish an effect of housing on injuries "
                    "(RQ10). Among the 72 ZIPs represented in all of 2023–2025, recorded "
                    "affordable units fell from 25,494 to 21,562 (15.4%) while severe injuries "
                    "rose from 1,177 to 1,453 (23.4%). Annual totals and within-ZIP changes "
                    "answer different questions from cross-ZIP correlations; these patterns "
                    "do not establish causation."),
            html.Li("Over the full years, crashes rose while housing did not (RQ3): in matched "
                    "ZIP-years, 2023 to 2025 affordable units fell 2.7% while serious crashes "
                    "rose 18.9%."),
            html.Li("ZIP codes with more housing projects have more severe injuries (RQ4: "
                    "Pearson r = 0.71, Spearman ρ = 0.81 across 143 ZIPs)."),
            html.Li("High-in-both ZIP-years are a Bronx and Brooklyn pattern (RQ5): 27 of the 29 "
                    "ZIP-years in the top 25% for both in 2023-2025 are in these two boroughs."),
            html.Li("Some ZIPs have many crashes for little housing (RQ6): 11234 (Brooklyn) and "
                    "11377 (Queens) have about 65 serious crashes per 100 affordable units."),
            html.Li("High housing does not always mean poor road safety (RQ11). Comparing ZIPs "
                    "per matched year, 45 of 143 are above the median on both affordable units "
                    "and serious crashes (about 25% would be expected by chance), led by "
                    "11207, 10019, 11212 and 11203. Most are in Brooklyn (18) and the Bronx (14). "
                    "Another 27 high-housing ZIPs have below-median crashes."),
            html.Li("The link differs by borough (RQ12). Per matched year, the citywide rank "
                    "correlation is modest (ρ = 0.30), and only the Bronx shows a clear one "
                    "(ρ = 0.56; 95% bootstrap interval 0.11–0.86). Brooklyn, Manhattan and "
                    "Queens are weak (ρ = 0.12–0.20, intervals include zero). Summed totals "
                    "look stronger partly because ZIPs matched in more years have more of both."),
            html.Li("Interpretation: the spatial associations motivate further investigation. "
                    "They do not show whether housing changes crashes, whether streets were "
                    "already dangerous before projects began, or whether residents face higher risk."),
        ]),

        html.H3("Limitations"),
        html.Ul([
            html.Li("Correlation is not causation. Population, traffic, road design and other "
                    "potential confounders were not measured or controlled here."),
            html.Li("Counts are not risk rates: there is no population or traffic-volume "
                    "denominator."),
            html.Li("The supplied ZIP-resolved crash snapshot spans October 2022 to June 2026, "
                    "so 2022 and 2026 are partial; year comparisons use 2023–2025 only. "
                    "This span is not the full SIRTA program coverage. Records with missing "
                    "ZIP codes were excluded upstream (5,682 of 13,754 in the audited source), "
                    "which can bias spatial and annual comparisons."),
            html.Li("Housing is dated by project start; residents arrive years later."),
            html.Li("Only ZIP-years present in both datasets are included. The set of ZIPs "
                    "can change by year, so matched totals are not citywide totals or a balanced panel. "
                    "ZIP locations on the map are approximate averages of available source "
                    "coordinates, not crash sites or official ZIP boundaries."),
            html.Li("Some source housing-unit values are unknown, so sums of observed units "
                    "can undercount. ZIP codes are coarse and a few cross borough lines. "
                    "Project counts summed across ZIPs need not be unique citywide projects."),
        ]),

        html.H3("Why it matters for NYC"),
        html.Ul([
            html.Li("NYC DOT / Vision Zero: use overlap ZIPs as candidates for more detailed "
                    "street-level review, with traffic exposure, population and crash-location data."),
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
    """Return recognised filter values and any explicit unsupported ZIPs or years."""
    text = (text or "").lower()
    found = {}

    boroughs = []
    for word, borough in BOROUGH_ALIASES.items():
        if re.search(r"\b" + word + r"\b", text) and borough in BOROUGHS \
                and borough not in boroughs:
            boroughs.append(borough)
    if boroughs:
        found["borough"] = boroughs

    requested_zips = sorted(set(re.findall(r"\b\d{5}\b", text)))
    zips = [z for z in requested_zips if z in ZIP_CODES]
    if zips:
        found["zip"] = sorted(set(zips))

    requested_years = sorted(set(int(y) for y in re.findall(r"\b(?:19|20)\d{2}\b", text)))
    years = [y for y in requested_years if YEAR_MIN <= y <= YEAR_MAX]
    if years:
        found["years"] = [min(years), max(years)]
    invalid = [f"ZIP {z} is not in the matched dataset" for z in requested_zips if z not in ZIP_CODES]
    invalid += [f"year {y} is outside {YEAR_MIN}–{YEAR_MAX}" for y in requested_years
                if not YEAR_MIN <= y <= YEAR_MAX]
    if invalid:
        found["errors"] = invalid

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
    if found.get("errors"):
        return (dash.no_update,) * 5 + (
            "Search not applied: " + "; ".join(found["errors"]) + ". Update the search and try again.",
            dash.no_update,
        )
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
    # Summary measures and RQ8 use these helpers; fixed RQs retain their named axes.
    dff["housing_selected"] = dff[HOUSING_CATEGORIES[housing_label]]
    dff["injuries_selected"] = dff[TRANSPORT_CATEGORIES[transport_label]]
    dff["housing_label"] = housing_label
    dff["transport_label"] = transport_label
    return dff


def summary_tile(label, value):
    return html.Div([html.Div(value, className="tile-value"),
                     html.Div(label, className="tile-label")], className="tile")


def selected_measure_chart(df, housing, transport):
    totals = df.groupby(["zip_code", "borough"], as_index=False)[
        ["housing_selected", "injuries_selected"]
    ].sum()
    fig = px.scatter(
        totals, x="housing_selected", y="injuries_selected", color="borough",
        color_discrete_map=BOROUGH_COLORS, hover_data=["zip_code"],
        labels={"borough": "Borough", "zip_code": "ZIP code",
                "housing_selected": housing, "injuries_selected": transport},
    )
    return apply_style(fig, f"Selected measures: {housing} vs {transport}", housing, transport)


@app.callback(
    Output("summary-row", "children"),
    Output("charts-grid", "children"),
    Output("exploration-chart", "children"),
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
        return message, [], []

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
    exploration = dcc.Graph(figure=selected_measure_chart(dff, housing, transport),
                            config=GRAPH_CONFIG, style={"height": "420px"})
    return summary, cards, exploration


if __name__ == "__main__":
    app.run(debug=True)
