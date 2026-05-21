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
from aspire_dash.components import sidebar, header, dark_mode_toggle
from aspire_dash.layouts import page_layout


app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=STYLESHEETS,
    suppress_callback_exceptions=True,
)
server = app.server

setup_app(app)

# Sidebar nav — grouped by aspire_dash subpackage.
nav = [
    # Overview
    {"label": "Component Showcase", "href": "/",
     "icon": "fa-solid fa-palette",      "section": "Overview"},

    # Brand foundations
    {"label": "Colour Palette",     "href": "/colours",
     "icon": "fa-solid fa-swatchbook",   "section": "Brand"},
    {"label": "Palette Lab",        "href": "/palette-lab",
     "icon": "fa-solid fa-flask"},

    # Components — by submodule
    {"label": "KPIs",               "href": "/kpis",
     "icon": "fa-solid fa-chart-simple", "section": "Components"},
    {"label": "Cards & Layouts",    "href": "/cards",
     "icon": "fa-solid fa-table-columns"},
    {"label": "Inputs & Filters",   "href": "/inputs",
     "icon": "fa-solid fa-sliders"},
    {"label": "Feedback",           "href": "/feedback",
     "icon": "fa-solid fa-comment-dots"},
    {"label": "Skeletons",          "href": "/skeletons",
     "icon": "fa-solid fa-ghost"},
    {"label": "Tables & Grids",     "href": "/tables",
     "icon": "fa-solid fa-table"},
    {"label": "Print & Export",     "href": "/print-export",
     "icon": "fa-solid fa-print"},

    # Domain components
    {"label": "Athlete",            "href": "/athlete",
     "icon": "fa-solid fa-user",         "section": "Domain"},
    {"label": "Budget",             "href": "/budget",
     "icon": "fa-solid fa-money-bill"},
    {"label": "Sports",             "href": "/sports",
     "icon": "fa-solid fa-medal"},
    {"label": "Firstbeat",          "href": "/firstbeat",
     "icon": "fa-solid fa-heart-pulse"},

    # Viz patterns
    {"label": "Charts & Data",      "href": "/charts",
     "icon": "fa-solid fa-chart-bar",    "section": "Charts"},
    {"label": "Viz Components",     "href": "/viz",
     "icon": "fa-solid fa-ring"},
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
