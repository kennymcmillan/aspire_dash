"""Asian Games design: participants page (filterable athlete grid + profile)."""
import dash
from dash import Input, Output, callback, dcc, html

from aspire_dash.asian_games import (
    ag_athlete_card, ag_athlete_profile, ag_choice_id, ag_chip, ag_empty, ag_field,
    ag_filter_panel, ag_hero_heading, ag_page_title, ag_pill_tabs, ag_section_title,
)

from ._ag_common import ag_page, sample_note
from ._ag_data import ATHLETES

dash.register_page(__name__, path="/ag/athletes", title="AG · Participants", name="AG Participants")

SPORTS = sorted({a["sport"] for a in ATHLETES.values()})
NOCS = sorted({a["noc"] for a in ATHLETES.values()})


def _featured():
    medalled = [a for a in ATHLETES.values() if a["noc"] == "QAT" and a["medals"]]
    pool = medalled or [a for a in ATHLETES.values() if a["noc"] == "QAT"] or list(ATHLETES.values())
    return pool[0]


def layout(bio=None, **_):
    hero = ag_hero_heading("Participants", eyebrow="Athletes",
                           lead="Filter by sport, NOC and gender. Click any card to open the profile.")
    body = [
        ag_page_title("Participants"),
        html.Div([
            ag_pill_tabs("ath-gender", ["All", "Men", "Women"], "All"),
            html.Div(dcc.Input(id="ath-search", type="text", placeholder="Search name or NOC",
                               debounce=False, className="ag-input"), style={"minWidth": "260px"}),
        ], className="ag-toolbar"),
        ag_filter_panel([
            ag_field("Sport", dcc.Dropdown(id="ath-sport", options=SPORTS, multi=True, placeholder="All sports",
                                           className="ag-select")),
            ag_field("NOC", dcc.Dropdown(id="ath-noc", options=NOCS, multi=True, placeholder="All NOCs",
                                         className="ag-select")),
            ag_field("Medallists only", dcc.Checklist(id="ath-medal", options=[{"label": " Show medallists only",
                                                                                "value": "y"}], value=[])),
        ]),
        html.Div(id="ath-chips"),
        html.Div([
            html.Div([html.Div(id="ath-count"), html.Div(id="ath-grid")]),
            html.Div([ag_section_title("Featured profile"),
                      html.Div(ag_athlete_profile(_featured()), className="ag-card")]),
        ], className="ag-split"),
        sample_note(),
    ]
    return ag_page(body, active="/ag/athletes", hero=hero, hero_kwargs={"dip": 90}, bio=bio)


@callback(
    Output("ath-grid", "children"),
    Output("ath-count", "children"),
    Output("ath-chips", "children"),
    Input(ag_choice_id("ath-gender"), "data"),
    Input("ath-search", "value"),
    Input("ath-sport", "value"),
    Input("ath-noc", "value"),
    Input("ath-medal", "value"),
)
def _filter(gender, search, sports, nocs, medal):
    rows = list(ATHLETES.values())
    if gender in ("Men", "Women"):
        rows = [a for a in rows if a["gender"] == ("Male" if gender == "Men" else "Female")]
    if sports:
        rows = [a for a in rows if a["sport"] in sports]
    if nocs:
        rows = [a for a in rows if a["noc"] in nocs]
    if medal:
        rows = [a for a in rows if a["medals"]]
    if search:
        q = search.strip().lower()
        rows = [a for a in rows if q in f"{a['surname']} {a['given']} {a['noc']}".lower()]
    rows.sort(key=lambda a: (-len(a["medals"]), a["noc"], a["surname"]))
    chips = [ag_chip(x, "purple") for x in (sports or []) + (nocs or [])]
    if gender in ("Men", "Women"):
        chips.insert(0, ag_chip(gender, "purple"))
    grid = html.Div([ag_athlete_card(a) for a in rows[:60]], className="ag-agrid") if rows else \
        ag_empty("No athlete matches those filters.")
    count = ag_section_title("Athletes", aside=f"{len(rows)} shown" + (" (first 60)" if len(rows) > 60 else ""))
    return grid, count, html.Div(chips, className="ag-chipset") if chips else None
