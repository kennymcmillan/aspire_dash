"""CLI for scaffolding new Aspire Dash apps.

Usage:
    python -m aspire_dash new my_app
    python -m aspire_dash new my_app --port 8070 --title "Budget Tracker"
"""

import os
import sys
import argparse
import shutil

_TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")


def _scaffold(name, port=8050, title=None):
    """Create a new Aspire Dash app directory with all boilerplate."""
    title = title or name.replace("_", " ").replace("-", " ").title()
    target = os.path.join(os.getcwd(), name)

    if os.path.exists(target):
        print(f"Error: '{name}' already exists.")
        sys.exit(1)

    # Create directory structure
    os.makedirs(os.path.join(target, "pages"))
    os.makedirs(os.path.join(target, "assets"))

    # app.py
    app_py = f'''"""{ title } — Aspire Academy Dash App."""

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

setup_app(app)

nav = [
    {{"label": "Dashboard", "href": "/", "icon": "fa-solid fa-chart-pie", "section": "Overview"}},
    {{"label": "Reports", "href": "/reports", "icon": "fa-solid fa-file-lines"}},
]

app.layout = page_layout(
    sidebar_el=sidebar(title="{ title }", subtitle="Aspire Academy", nav_items=nav),
    header_el=header(title="{ title }"),
    use_pages=True,
)

if __name__ == "__main__":
    app.run(debug=True, port={ port })
'''

    # pages/home.py
    home_py = f'''"""Home page."""

import dash
from dash import html
from aspire_dash.components import card, summary_card
from aspire_dash.theme import SLATE

dash.register_page(__name__, path="/", title="Dashboard", name="Dashboard")


def layout(**kwargs):
    return html.Div([
        html.H2("Dashboard", className="section-title"),

        # KPI row
        html.Div([
            summary_card("Total", "0", sub="All items", icon="fa-solid fa-chart-bar"),
            summary_card("Active", "0", sub="In progress", icon="fa-solid fa-circle-check"),
            summary_card("Pending", "0", sub="Awaiting review", icon="fa-solid fa-clock"),
        ], style={{
            "display": "grid",
            "gridTemplateColumns": "repeat(auto-fill, minmax(200px, 1fr))",
            "gap": "12px",
            "marginBottom": "24px",
        }}),

        card([
            html.P("Add your content here.", style={{"color": SLATE["500"]}}),
        ]),
    ], style={{"maxWidth": "1200px"}})
'''

    # pages/reports.py
    reports_py = '''"""Reports page."""

import dash
from dash import html
from aspire_dash.components import card, empty_state

dash.register_page(__name__, path="/reports", title="Reports", name="Reports")


def layout(**kwargs):
    return html.Div([
        html.H2("Reports", className="section-title"),
        card([empty_state(text="No reports yet", hint="Add your first report")]),
    ], style={"maxWidth": "1200px"})
'''

    # requirements.txt
    requirements = """dash>=2.18.0
dash-bootstrap-components>=1.6.0
plotly>=5.24.0
pandas>=2.2.0
gunicorn>=22.0.0
aspire-dash
"""

    # manifest.json for Posit Connect
    manifest = f'''{{"version": 1,
  "metadata": {{
    "appmode": "python-dash",
    "entrypoint": "app:server",
    "primary_document": "app.py"
  }},
  "python": {{
    "version": "3.11.0",
    "package_manager": {{
      "name": "pip",
      "version": "23.0",
      "package_file": "requirements.txt"
    }}
  }}
}}
'''

    # .gitignore
    gitignore = """__pycache__/
*.pyc
.env
assets/00_aspire_base.css
assets/01_aspire_print.css
assets/aspire-logo.png
assets/sidebar_toggle.js
assets/dark_mode.js
"""

    # Write all files
    files = {
        "app.py": app_py,
        "pages/home.py": home_py,
        "pages/reports.py": reports_py,
        "requirements.txt": requirements,
        "manifest.json": manifest,
        ".gitignore": gitignore,
    }

    for rel_path, content in files.items():
        full_path = os.path.join(target, rel_path)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

    print(f"Created '{name}/' with:")
    print(f"  app.py              (port {port})")
    print(f"  pages/home.py       (dashboard)")
    print(f"  pages/reports.py    (placeholder)")
    print(f"  requirements.txt    (Posit Connect ready)")
    print(f"  manifest.json       (Posit Connect deploy)")
    print(f"  .gitignore")
    print()
    print(f"Next steps:")
    print(f"  cd {name}")
    print(f"  python app.py")


def main():
    parser = argparse.ArgumentParser(prog="aspire_dash", description="Aspire Dash CLI tools")
    sub = parser.add_subparsers(dest="command")

    new_parser = sub.add_parser("new", help="Scaffold a new Aspire Dash app")
    new_parser.add_argument("name", help="App directory name (e.g. my_budget_app)")
    new_parser.add_argument("--port", type=int, default=8050, help="Dev server port (default: 8050)")
    new_parser.add_argument("--title", help="App title (default: derived from name)")

    args = parser.parse_args()

    if args.command == "new":
        _scaffold(args.name, port=args.port, title=args.title)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
