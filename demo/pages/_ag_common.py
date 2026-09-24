"""Shared shell for the Asian Games design pages.

Every page in the section calls ag_page(), so they all get the same nav,
disciplines mega-menu, footer and athlete profile modal. The modal's open
callback lives here and registers once, on first import.
"""
from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import ALL, Input, Output, callback, ctx, html, no_update

from aspire_dash.asian_games import AG_DISCIPLINES, ag_athlete_profile, ag_shell

from ._ag_data import ATHLETES

AG_NAV = [
    {"label": "Home", "href": "/ag"},
    {"label": "Results", "href": "/ag/results"},
    {"label": "Participants", "href": "/ag/athletes"},
    {"label": "Medals", "href": "/ag/medals"},
    {"label": "Schedule", "href": "/ag/schedule"},
    {"label": "Components", "href": "/ag/components"},
]

AG_DISCIPLINE_LINKS = [
    {"label": label, "icon": icon, "href": f"/ag/results?disc={code}"}
    for code, (label, icon) in AG_DISCIPLINES.items()
]

MODAL_ID = "ag-athlete-modal"


def athlete_modal(bio=None):
    a = ATHLETES.get(bio) if bio else None
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Athlete profile")),
        dbc.ModalBody(ag_athlete_profile(a) if a else None, id=f"{MODAL_ID}-body"),
    ], id=MODAL_ID, is_open=a is not None, centered=True, class_name="ag-modal",
                     dialog_class_name="ag-modal-dialog", backdrop_class_name="ag-modal-backdrop")


def ag_page(children, *, active, hero=None, hero_variant="curve", hero_kwargs=None, bio=None):
    return ag_shell(
        children, nav_items=AG_NAV, active=active, hero=hero, hero_variant=hero_variant,
        hero_kwargs=hero_kwargs, disciplines=AG_DISCIPLINE_LINKS,
        overlays=[athlete_modal(bio)],
    )


@callback(
    Output(MODAL_ID, "is_open"),
    Output(f"{MODAL_ID}-body", "children"),
    Input({"type": "ag-athlete", "id": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def _open_profile(_clicks):
    trig = ctx.triggered_id
    if not trig or not ctx.triggered or not ctx.triggered[0].get("value"):
        return no_update, no_update
    a = ATHLETES.get(trig["id"])
    if not a:
        return no_update, no_update
    return True, ag_athlete_profile(a)


def sample_note():
    return html.P("Sample data: every name, mark and medal count on these pages is invented.",
                  className="ag-note")
