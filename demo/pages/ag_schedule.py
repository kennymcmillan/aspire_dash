"""Asian Games design: competition schedule (date strip + by-discipline view)."""
import datetime as dt

import dash
from dash import Input, Output, callback, dcc, html

from aspire_dash.asian_games import (
    AG_DISCIPLINES, ag_choice_id, ag_date_strip, ag_discipline_card, ag_empty, ag_hero_heading,
    ag_legend, ag_page_title, ag_pill_tabs, ag_schedule_unit, ag_section_title,
)

from ._ag_common import ag_page, sample_note
from ._ag_data import SCHEDULE, TODAY, days_strip, discipline_days

dash.register_page(__name__, path="/ag/schedule", title="AG · Schedule", name="AG Schedule")

DISCS = sorted({u["discipline"] for units in SCHEDULE.values() for u in units},
               key=lambda c: AG_DISCIPLINES[c][0])


def layout(bio=None, **_):
    hero = ag_hero_heading("Competition schedule", eyebrow="Schedule",
                           lead="Pick a day on the strip. Gold days award medals; today is shaded light blue.")
    body = [
        ag_page_title("Competition schedule"),
        html.Div([
            ag_pill_tabs("sch-mode", ["Daily", "By discipline"], "Daily"),
            ag_legend([("Competition day", "outline"), ("Medal day", "gold"), ("Live", "live")]),
        ], className="ag-toolbar"),
        html.Div(id="sch-daily", children=[
            ag_date_strip("sch-day", days_strip(), TODAY),
            html.Div(dcc.Dropdown(id="sch-disc", options=[{"label": AG_DISCIPLINES[d][0], "value": d} for d in DISCS],
                                  multi=True, placeholder="All disciplines", className="ag-select"),
                     style={"maxWidth": "420px", "margin": "6px 0 4px"}),
            html.Div(id="sch-units"),
        ]),
        html.Div(id="sch-bydisc"),
        sample_note(),
    ]
    return ag_page(body, active="/ag/schedule", hero=hero, hero_variant="rounded", bio=bio)


@callback(
    Output("sch-units", "children"),
    Input(ag_choice_id("sch-day"), "data"),
    Input("sch-disc", "value"),
)
def _day(day, discs):
    units = SCHEDULE.get(day or TODAY, [])
    if discs:
        units = [u for u in units if u["discipline"] in discs]
    title = ag_section_title(dt.date.fromisoformat(day or TODAY).strftime("%A %d %B"),
                             aside=f"{len(units)} units")
    if not units:
        return [title, ag_empty("Nothing scheduled for that filter.")]
    return [title, html.Div([
        ag_schedule_unit(u["time"], u["event"], phase=u["phase"], unit=u["unit"], venue=u["venue"],
                         status=u["status"], icon=AG_DISCIPLINES[u["discipline"]][1], medal=u["medal"])
        for u in units], className="ag-sunits")]


@callback(
    Output("sch-daily", "style"),
    Output("sch-bydisc", "children"),
    Input(ag_choice_id("sch-mode"), "data"),
)
def _mode(mode):
    if mode != "By discipline":
        return {}, None
    per = discipline_days()
    live_now = {u["discipline"] for u in SCHEDULE[TODAY] if u["status"] == "live"}
    cards = [ag_discipline_card(AG_DISCIPLINES[c][0], AG_DISCIPLINES[c][1], per[c], live=c in live_now)
             for c in DISCS]
    return {"display": "none"}, [ag_section_title("By discipline", aside=f"{len(cards)} disciplines"),
                                 html.Div(cards, className="ag-discgrid")]
