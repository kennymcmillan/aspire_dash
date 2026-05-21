"""Feedback — toast, status_pill, freshness_banner, badge, empty_state, loading_overlay."""
import dash
from dash import html

from aspire_dash.components.feedback import (
    toast, status_pill, badge, empty_state,
    freshness_banner, loading_overlay,
)

from ._shared import section, example

dash.register_page(__name__, path="/feedback", title="Feedback", name="Feedback")


def layout():
    return html.Div([
        html.H1("Feedback Components",
                style={"fontSize": "28px", "fontWeight": 700,
                       "marginBottom": "8px"}),
        html.P("Status pills, badges, freshness banners, empty states.",
                style={"color": "#64748b", "fontSize": "14px",
                       "marginBottom": "24px"}),

        section("badge", "Tiny coloured pill — labels, tags, statuses."),
        example("Coloured badges",
                 html.Div([
                     badge("Active", color="emerald"),
                     badge("Pending", color="amber"),
                     badge("Error",   color="red"),
                     badge("Info",    color="blue"),
                     badge("Neutral", color="gray"),
                 ], style={"display": "flex", "gap": "6px"}),
                 "badge('Active', color='emerald')"),

        section("status_pill",
                 "Larger pill with icon — used for save/sync confirmations."),
        example("Status indicators",
                 html.Div([
                     status_pill("Saved", color="emerald", icon="fa-check"),
                     status_pill("Syncing…", color="blue", icon="fa-rotate fa-spin"),
                     status_pill("Failed", color="red", icon="fa-xmark"),
                 ], style={"display": "flex", "gap": "8px"}),
                 "status_pill('Saved', color='emerald', icon='fa-check')"),

        section("empty_state",
                 "Drop-in for 'no data' panels — icon + title + hint."),
        example("Empty state",
                 empty_state(icon="fa-solid fa-inbox",
                              text="No sessions yet",
                              hint="Coach hasn't logged any volumes for this period."),
                 "empty_state(\n"
                 "    icon='fa-solid fa-inbox',\n"
                 "    text='No sessions yet',\n"
                 "    hint='Coach hasn\\'t logged any volumes for this period.',\n"
                 ")"),

        section("freshness_banner",
                 "Surfaces last-synced timestamp — staleness colour-coded."),
        example("Fresh", freshness_banner(days=0),
                 "freshness_banner(days=0)"),
        example("Stale", freshness_banner(days=14),
                 "freshness_banner(days=14)"),

        section("loading_overlay",
                 "Wraps children with a translucent overlay + spinner during loads. "
                 "Note: do NOT wrap an editable AG Grid in this — see tables page."),
        example("Overlay",
                 loading_overlay(
                     html.Div("Page content goes here.",
                               style={"padding": "30px", "background": "#f1f5f9",
                                      "borderRadius": "4px"}),
                 ),
                 "loading_overlay(html.Div('Page content'))"),
    ], style={"padding": "24px"})
