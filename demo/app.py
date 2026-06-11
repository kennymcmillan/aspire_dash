"""aspire_dash — Component showcase / demo app.

Run locally:
    py -3.12 app.py

Lives inside the aspire_dash repo (was previously a separate Dropbox folder
that drifted out of sync). Now: every commit that adds a public component
should add a matching page or section in this demo.
"""
import dash
from dash import Dash, html, dcc

import aspire_dash
from aspire_dash import setup_app, STYLESHEETS
from aspire_dash.components import (
    sidebar, header, dark_mode_toggle,
    register_linear_step_toggle,
)
from aspire_dash.layouts import page_layout


app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=STYLESHEETS,
    suppress_callback_exceptions=True,
)
server = app.server

setup_app(app)

# v0.37 — wire the linear-step-card click-to-toggle for the default
# header_type used by the /linear-steps demo page. A second registration
# below covers the alternate header_type used in that page's "second
# strip" example.
register_linear_step_toggle(app)
register_linear_step_toggle(app, header_type="demo-secondary")

# Sidebar nav — grouped by what it IS, not when it shipped.
nav = [
    # Overview
    {"label": "Component Showcase", "href": "/",
     "icon": "fa-solid fa-palette",      "section": "Overview"},
    {"label": "Layouts",            "href": "/layouts",
     "icon": "fa-solid fa-square-poll-vertical"},

    # Brand foundations
    {"label": "Brand assets",       "href": "/brand",
     "icon": "fa-solid fa-flag",         "section": "Brand"},
    {"label": "Countries & flags",  "href": "/countries",
     "icon": "fa-solid fa-globe"},
    {"label": "Colour palette",     "href": "/colours",
     "icon": "fa-solid fa-swatchbook"},
    {"label": "Palette Lab",        "href": "/palette-lab",
     "icon": "fa-solid fa-flask"},

    # Building blocks (atomic UI)
    {"label": "KPIs",               "href": "/kpis",
     "icon": "fa-solid fa-chart-simple", "section": "Building blocks"},
    {"label": "Cards & layouts",    "href": "/cards",
     "icon": "fa-solid fa-table-columns"},
    {"label": "Inputs & filters",   "href": "/inputs",
     "icon": "fa-solid fa-sliders"},
    {"label": "Feedback & badges",  "href": "/feedback",
     "icon": "fa-solid fa-comment-dots"},
    {"label": "Skeletons",          "href": "/skeletons",
     "icon": "fa-solid fa-ghost"},
    {"label": "Tables & grids",     "href": "/tables",
     "icon": "fa-solid fa-table"},
    {"label": "Print & export",     "href": "/print-export",
     "icon": "fa-solid fa-print"},
    {"label": "Athlete cards + rings", "href": "/v12",
     "icon": "fa-solid fa-id-card"},
    # v0.37 — patterns promoted from aspire-nutrition
    {"label": "Linear steps",       "href": "/linear-steps",
     "icon": "fa-solid fa-list-ol"},
    {"label": "Meta + history",     "href": "/meta-history",
     "icon": "fa-solid fa-clipboard-list"},
    {"label": "Ranked dropdown",    "href": "/ranked-dropdown",
     "icon": "fa-solid fa-arrow-down-wide-short"},

    # Athlete / performance domain
    {"label": "Athlete",            "href": "/athlete",
     "icon": "fa-solid fa-user",         "section": "Athlete & performance"},
    {"label": "Anthropometric",     "href": "/v18",
     "icon": "fa-solid fa-person-rays"},
    {"label": "Medical",            "href": "/medical",
     "icon": "fa-solid fa-stethoscope"},
    {"label": "Firstbeat",          "href": "/firstbeat",
     "icon": "fa-solid fa-heart-pulse"},
    {"label": "Whoop",              "href": "/whoop",
     "icon": "fa-solid fa-bed"},
    {"label": "VALD",               "href": "/vald",
     "icon": "fa-solid fa-person-running"},
    {"label": "Nutrition",          "href": "/v19",
     "icon": "fa-solid fa-apple-whole"},
    {"label": "Adaptive trend",     "href": "/v19#adaptive_trend",
     "icon": "fa-solid fa-chart-line"},

    # Sport reporting
    {"label": "Sports patterns",    "href": "/sports",
     "icon": "fa-solid fa-medal",        "section": "Sport reporting"},
    {"label": "Physiology",         "href": "/physio",
     "icon": "fa-solid fa-lungs"},

    # Finance + admin
    {"label": "Budget",             "href": "/budget",
     "icon": "fa-solid fa-money-bill",   "section": "Finance"},
    {"label": "Financial reports",  "href": "/financial",
     "icon": "fa-solid fa-money-bill-trend-up"},

    # Charts
    {"label": "Charts & data",      "href": "/charts",
     "icon": "fa-solid fa-chart-bar",    "section": "Charts"},
    {"label": "Plot collection",    "href": "/plots",
     "icon": "fa-solid fa-chart-pie"},
    {"label": "Viz components",     "href": "/viz",
     "icon": "fa-solid fa-ring"},

    # Legacy
    {"label": "Logo & assets (legacy)", "href": "/assets",
     "icon": "fa-solid fa-image",        "section": "Reference"},
]

app.layout = page_layout(
    sidebar_el=sidebar(
        title="Aspire Demo",
        subtitle="Component Showcase",
        nav_items=nav,
        footer=html.Div([
            html.Div(style={
                "width": "6px", "height": "6px", "borderRadius": "50%",
                "backgroundColor": "#16a34a",
                "display": "inline-block", "marginRight": "8px",
            }),
            html.Span(f"aspire_dash v{aspire_dash.__version__}",
                      style={"fontSize": "11px", "color": "#93c5fd"}),
        ], style={"display": "flex", "alignItems": "center"}),
    ),
    header_el=header(title="Aspire Dash",
                     subtitle="Design System Preview",
                     right_content=dark_mode_toggle()),
    use_pages=True,
)

if __name__ == "__main__":
    app.run(debug=True, port=8060)
