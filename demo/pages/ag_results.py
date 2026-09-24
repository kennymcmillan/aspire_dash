"""Asian Games design: discipline results page (the curved wave hero page)."""
import datetime as dt

import dash
from dash import Input, Output, State, callback, dcc, html, no_update

from aspire_dash.asian_games import (
    AG_DISCIPLINES, ag_athlete_card, ag_band, ag_choice_id, ag_empty, ag_event_capsule,
    ag_field, ag_filter_panel, ag_hero_heading, ag_page_title, ag_pill_tabs, ag_records_panel,
    ag_results_table, ag_schedule_unit, ag_section_title, ag_sort_id, ag_sort_rows,
    ag_sort_store, ag_stat, ag_subtabs, ag_unit_strip, ag_chip,
)

from ._ag_common import ag_page, sample_note
from ._ag_data import ATHLETES, EVENTS, SCHEDULE, VENUES, medallists

dash.register_page(__name__, path="/ag/results", title="AG · Results", name="AG Results")

VIEWS = ["Schedule", "Entries", "Results", "Final rank", "Medals"]
FOCUS = "QAT"


def _events_for(disc):
    return [e for e in EVENTS.values() if e["discipline"] == disc]


def _default_unit(ev):
    done = [u for u in ev["units"] if u["status"] != "scheduled"]
    return (done[-1] if done else ev["units"][0])["value"]


def _unit(ev, value):
    return next((u for u in ev["units"] if u["value"] == value), None)


def _columns(ev, mode):
    track = ev["lower"]
    cols = [
        {"key": "rank", "label": "Rank", "kind": "rank", "width": "56px", "sortable": True},
        {"key": "surname", "label": "Name", "kind": "athlete", "sortable": True},
    ]
    if mode != "Start list":
        cols.append({"key": "mark", "label": "Result", "kind": "mark", "width": "150px",
                     "align": "right", "sortable": True, "desc_default": not track})
        cols.append({"key": "gap", "label": "Gap", "kind": "gap", "width": "70px", "align": "right"})
    if track:
        cols.append({"key": "lane", "label": "Lane", "kind": "text", "width": "56px", "align": "center",
                     "sortable": True, "hide_sm": True})
        cols.append({"key": "rt", "label": "Reaction", "kind": "text", "width": "84px", "align": "right",
                     "hide_sm": True})
    return cols


def _capsule(ev, unit):
    return ag_event_capsule(ev["name"], f"{unit['phase']} {unit['label']}" if unit["label"] != unit["phase"]
                            else unit["phase"], status=unit["status"], when=unit["when"],
                            venue=VENUES[ev["discipline"]])


def layout(disc="SWM", event=None, bio=None, **_):
    disc = disc if disc in AG_DISCIPLINES else "SWM"
    label, icon = AG_DISCIPLINES[disc]
    evs = _events_for(disc)
    ev = EVENTS.get(event) if event in EVENTS and EVENTS[event]["discipline"] == disc else (evs[0] if evs else None)
    unit = _unit(ev, _default_unit(ev)) if ev else None

    hero = [
        ag_band(label, icon, ag_subtabs("res-view", VIEWS, "Results")),
        html.Div(_capsule(ev, unit) if ev else ag_hero_heading(label, lead="No results published yet."),
                 id="res-capsule", style={"padding": "22px 20px 0"}),
    ]

    if not ev:
        body = [ag_page_title(f"{label} results"),
                ag_empty(f"No results available for {label} yet. Try Swimming or Athletics from the Disciplines menu."),
                sample_note()]
        return ag_page(body, active="/ag/results", hero=hero, bio=bio)

    nocs = sorted({r["noc"] for u in ev["units"] for r in u["rows"]})
    body = [
        dcc.Store(id="res-disc", data=disc),
        ag_page_title(f"{label} results"),
        ag_pill_tabs("res-event", [{"label": e["name"], "value": e["code"]} for e in evs], ev["code"],
                     variant="outline"),
        html.Div(id="res-view-wrap", children=[
            html.Div(id="res-results-view", children=[
                ag_section_title("Units", aside="Pick a heat or final"),
                html.Div(ag_unit_strip("res-unit", ev["units"], unit["value"]), id="res-units-wrap"),
                html.Div([
                    ag_pill_tabs("res-mode", ["Start list", "Results", "Summary"], "Results"),
                ], className="ag-toolbar"),
                ag_filter_panel([
                    ag_field("NOC", dcc.Dropdown(id="res-noc", options=nocs, multi=True, placeholder="All NOCs",
                                                 className="ag-select")),
                    ag_field("Search athlete", dcc.Input(id="res-search", type="text", placeholder="Name or NOC",
                                                         debounce=False, className="ag-input")),
                ]),
                ag_sort_store("res-table", "rank", False),
                html.Div(id="res-section-title"),
                html.Div(id="res-table-wrap"),
                html.Div(id="res-records", children=ag_records_panel(ev["records"]), style={"marginTop": "22px"}),
            ]),
            html.Div(id="res-alt-view"),
        ]),
        sample_note(),
    ]
    return ag_page(body, active="/ag/results", hero=hero, bio=bio)


@callback(
    Output("res-units-wrap", "children"),
    Output("res-records", "children"),
    Output(ag_sort_id("res-table"), "data", allow_duplicate=True),
    Input(ag_choice_id("res-event"), "data"),
    prevent_initial_call=True,
)
def _on_event(code):
    ev = EVENTS.get(code)
    if not ev:
        return no_update, no_update, no_update
    return (ag_unit_strip("res-unit", ev["units"], _default_unit(ev)), ag_records_panel(ev["records"]),
            {"key": "rank", "desc": False})


@callback(
    Output("res-table-wrap", "children"),
    Output("res-capsule", "children"),
    Output("res-section-title", "children"),
    Input(ag_choice_id("res-event"), "data"),
    Input(ag_choice_id("res-unit"), "data"),
    Input(ag_choice_id("res-mode"), "data"),
    Input("res-noc", "value"),
    Input("res-search", "value"),
    Input(ag_sort_id("res-table"), "data"),
)
def _render_table(code, unit_value, mode, nocs, search, sort_state):
    ev = EVENTS.get(code)
    if not ev:
        return no_update, no_update, no_update
    unit = _unit(ev, unit_value) or _unit(ev, _default_unit(ev))
    rows = unit["rows"]
    if nocs:
        rows = [r for r in rows if r["noc"] in nocs]
    if search:
        q = search.strip().lower()
        rows = [r for r in rows if q in f"{r['surname']} {r['given']} {r['noc']}".lower()]

    title_txt = f"{unit['phase']} · {unit['label']}" if unit["label"] != unit["phase"] else unit["phase"]
    no_marks = unit["status"] == "scheduled"
    if mode == "Summary":
        ranked = [r for r in unit["rows"] if r.get("rank")]
        if not ranked:
            content = ag_empty("No summary yet: this unit has not started.")
        else:
            win = ranked[0]
            content = html.Div([
                html.Div([
                    ag_stat("Winner", f"{win['surname']} {win['given']}", f"{win['noc']} · {win['mark_display']}", gold=True),
                    ag_stat("Starters", len(unit["rows"]), unit["status"].title()),
                    ag_stat("Records", sum(1 for r in ranked if r.get("records")), "GR and PB chips"),
                    ag_stat("Spread", ranked[-1]["gap"].lstrip("+-") or "0", "first to last"),
                ], className="ag-stats"),
            ])
        return content, _capsule(ev, unit), ag_section_title("Summary", aside=title_txt)

    if mode == "Start list" or no_marks:
        state = {"key": "lane", "desc": False} if ev["lower"] else {"key": "surname", "desc": False}
        if sort_state and sort_state.get("key") in ("lane", "surname"):
            state = sort_state
        cols = [c for c in _columns(ev, "Start list") if c["key"] != "rank"]
        table = ag_results_table(cols, ag_sort_rows(rows, state), table_id="res-table",
                                 sort_state=state, focus_noc=FOCUS)
        aside = "Start list" + (" · results not published yet" if no_marks and mode != "Start list" else "")
        return table, _capsule(ev, unit), ag_section_title(title_txt, aside=aside)

    state = sort_state or {"key": "rank", "desc": False}
    table = ag_results_table(_columns(ev, "Results"), ag_sort_rows(rows, state), table_id="res-table",
                             sort_state=state, focus_noc=FOCUS,
                             empty_text="No athlete matches those filters.")
    return table, _capsule(ev, unit), ag_section_title(title_txt, aside=f"Qatar highlighted · {unit['status'].title()}")


@callback(
    Output("res-results-view", "style"),
    Output("res-alt-view", "children"),
    Input(ag_choice_id("res-view"), "data"),
    State("res-disc", "data"),
)
def _switch_view(view, disc):
    if view in (None, "Results"):
        return {}, None
    hide = {"display": "none"}
    evs = _events_for(disc)
    names = {e["name"] for e in evs}
    if view == "Schedule":
        items = []
        for day, units in SCHEDULE.items():
            mine = [u for u in units if u["event"] in names]
            if mine:
                items.append(ag_section_title(dash_date(day)))
                items.append(html.Div([ag_schedule_unit(u["time"], u["event"], phase=u["phase"], unit=u["unit"],
                                                        venue=u["venue"], status=u["status"],
                                                        icon=AG_DISCIPLINES[disc][1], medal=u["medal"])
                                       for u in mine], className="ag-sunits"))
        return hide, items or ag_empty("Nothing scheduled.")
    if view == "Entries":
        ids = sorted({r["athlete_id"] for e in evs for u in e["units"] for r in u["rows"]},
                     key=lambda a: (ATHLETES[a]["noc"], ATHLETES[a]["surname"]))
        return hide, [ag_section_title("Entries", aside=f"{len(ids)} athletes · click a card for the profile"),
                      html.Div([ag_athlete_card(ATHLETES[a]) for a in ids], className="ag-agrid")]
    if view == "Final rank":
        out = []
        for e in evs:
            final = e["units"][-1]
            out.append(ag_section_title(e["name"], aside=final["status"].title()))
            if final["status"] == "scheduled":
                out.append(ag_empty("Final not contested yet."))
            else:
                out.append(ag_results_table(_columns(e, "Results")[:4], final["rows"], focus_noc=FOCUS))
        return hide, out
    if view == "Medals":
        rows = [r for r in medallists() if r["discipline"] == disc]
        cols = [{"key": "medal", "label": "", "kind": "medal", "width": "30px"},
                {"key": "surname", "label": "Medallist", "kind": "athlete"},
                {"key": "event", "label": "Event", "kind": "text", "width": "260px", "hide_sm": True},
                {"key": "mark", "label": "Result", "kind": "mark", "width": "120px", "align": "right"}]
        return hide, [ag_section_title("Medallists", aside=f"{len(rows)} medals decided"),
                      ag_results_table(cols, rows, focus_noc=FOCUS),
                      html.Div([ag_chip("Finals still to come appear once they finish", "outline")],
                               className="ag-chipset")]
    return {}, None


def dash_date(iso):
    return dt.date.fromisoformat(iso).strftime("%A %d %B")
