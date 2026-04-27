"""Template for a new Aspire Dash app.

Copy this file as your app.py and customise the nav_items and title.

Usage:
    pip install -e ../aspire_dash   (once, from the DASH_APPS directory)
    python app_template.py          (run the app)
"""

import dash
from dash import Dash, html
from aspire_dash import setup_app, STYLESHEETS
from aspire_dash.components import sidebar, header
from aspire_dash.layouts import page_layout

app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=STYLESHEETS,
    suppress_callback_exceptions=True,
)
server = app.server  # for Posit Connect / gunicorn

# Copy shared CSS + logo into this app's assets/
setup_app(app)

# Define sidebar navigation
nav = [
    {"label": "Dashboard", "href": "/", "icon": "fa-solid fa-chart-pie", "section": "Overview"},
    {"label": "Reports", "href": "/reports", "icon": "fa-solid fa-file-lines"},
    {"label": "Settings", "href": "/settings", "icon": "fa-solid fa-gear", "section": "Admin"},
]

# Build layout
app.layout = page_layout(
    sidebar_el=sidebar(title="My App", subtitle="Aspire Academy", nav_items=nav),
    header_el=header(title="Dashboard", subtitle="Overview"),
    use_pages=True,
)

if __name__ == "__main__":
    app.run(debug=True, port=8050)
