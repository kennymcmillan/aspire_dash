"""CLI for scaffolding new Aspire Dash apps.

Usage:
    python -m aspire_dash new my_app
    python -m aspire_dash new my_app --port 8070 --title "Budget Tracker"
    python -m aspire_dash new my_report --type report
"""

import argparse
import os
import sys


# ============================================================
# Templates — strings rather than .py files so users see all the
# wiring in one place when they run `aspire-dash new`.
# ============================================================

APP_PY = """\"\"\"{title} — Aspire Academy Dash App.

Quick start:
    pip install -r requirements.txt
    python app.py             # local dev on http://localhost:{port}

Deploy to Posit Connect:
    rsconnect deploy dash . --entrypoint app.app
\"\"\"

import dash
from dash import Dash, dcc, html

from aspire_dash import setup_app, STYLESHEETS
from aspire_dash.components import sidebar, header
from aspire_dash.layouts import page_layout

app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=STYLESHEETS,
    suppress_callback_exceptions=True,
)
server = app.server  # gunicorn / Posit Connect entrypoint

setup_app(app)

NAV = [
    {{"label": "Home",    "href": "/",       "icon": "fa-solid fa-house"}},
    {{"label": "Reports", "href": "/reports", "icon": "fa-solid fa-file-lines"}},
]

app.layout = html.Div([
    # App-level stores so cross-page callbacks land
    dcc.Store(id="toast-trigger", storage_type="memory"),

    page_layout(
        sidebar_el=sidebar(title="{title}", subtitle="Aspire Academy",
                            nav_items=NAV),
        header_el=header(title="{title}"),
        use_pages=True,
    ),

    # Toast container — register_toast wires it up from any callback
    # via the toast-trigger store.
    __import__("dash_bootstrap_components").Toast(
        id="app-toast",
        header="",
        is_open=False,
        dismissable=True,
        duration=4000,
        icon="primary",
        style={{"position": "fixed", "top": 80, "right": 24,
                 "zIndex": 1080, "minWidth": 320}},
    ),
])

# Wire the reusable toast callback so any other callback can
# trigger a toast by writing dispatch_toast(...) to 'toast-trigger'.
from aspire_dash.callbacks import register_toast
register_toast(app, toast_id="app-toast", trigger_store_id="toast-trigger")

if __name__ == "__main__":
    app.run(debug=True, port={port})
"""


HOME_PY = """\"\"\"Home page — KPI strip + skeleton-loaded content card.\"\"\"

import dash
from dash import Input, Output, callback, dcc, html

from aspire_dash.components import card, kpi_strip
from aspire_dash.skeletons import skel_card, skel_metric_tiles
from aspire_dash.theme import ASPIRE_BLUE, SLATE

dash.register_page(__name__, path="/", title="Home", name="Home")


def layout(**kwargs):
    return html.Div([
        html.H2("Home", className="section-title my-3"),

        # Static KPI strip (replace with real data via callback if dynamic)
        kpi_strip([
            {{"label": "Athletes", "value": 0, "unit": ""}},
            {{"label": "Sports",   "value": 0, "unit": ""}},
            {{"label": "Today",    "value": 0, "unit": "events"}},
            {{"label": "Status",   "value": 0, "unit": "active"}},
        ]),

        # Data-bound section — skeleton until the callback resolves
        html.Div(id="home-content", className="mt-4",
                  children=skel_card(height="200px")),
    ], style={{"maxWidth": "1200px", "padding": "0 16px"}})


@callback(
    Output("home-content", "children"),
    Input("home-content", "id"),  # fires once on mount
)
def _load_home(_id):
    # Replace this with your data fetch (httpx, DB, etc).
    # Until then the skeleton is visible — try setting NETWORK to
    # 'Slow 3G' in devtools to see it.
    return card([
        html.H4("Welcome", style={{"color": ASPIRE_BLUE}}),
        html.P("Replace this with your data-bound content.",
               style={{"color": SLATE["500"]}}),
    ])
"""


REPORTS_PY = """\"\"\"Reports page — placeholder.\"\"\"

import dash
from dash import html
from aspire_dash.components import card, empty_state

dash.register_page(__name__, path="/reports", title="Reports", name="Reports")


def layout(**kwargs):
    return html.Div([
        html.H2("Reports", className="section-title my-3"),
        card([empty_state(text="No reports yet",
                           hint="Add your first report here")]),
    ], style={{"maxWidth": "1200px", "padding": "0 16px"}})
"""


API_CLIENT_PY = """\"\"\"Optional: HTTP client preconfigured for Aspire APIs.

Drop in your API base URL + key. Uses truststore on the Aspire
laptop so the corp MITM cert is trusted (NOT verify=False).
\"\"\"
from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent / ".env")
except ImportError:
    pass

try:
    import truststore
    truststore.inject_into_ssl()
except ImportError:
    pass

import httpx

API_URL = os.getenv("API_URL", "").rstrip("/")
API_KEY = os.getenv("API_KEY", "")

_client = httpx.Client(
    base_url=API_URL,
    headers={{"X-API-Key": API_KEY}} if API_KEY else {{}},
    timeout=20.0,
)


def get(path: str, **kwargs):
    return _client.get(path, **kwargs).raise_for_status().json()


def post(path: str, **kwargs):
    return _client.post(path, **kwargs).raise_for_status().json()
"""


REQUIREMENTS = """\
dash>=2.18.0
dash-bootstrap-components>=1.6.0
plotly>=5.24.0
pandas>=2.2.0
gunicorn>=22.0.0
httpx>=0.27
python-dotenv>=1.0
truststore>=0.10                    # Aspire MITM corp-CA fix
aspire_dash @ git+https://github.com/kennymcmillan/aspire_dash.git@main
"""


ENV_EXAMPLE = """\
# Copy to .env and fill in. Loaded by api_client.py + python-dotenv.

# API the app talks to
API_URL=
API_KEY=

# Posit Connect (for E2E tests + deploys)
CONNECT_API_KEY=

# Aspire laptop only — Aspire's GlobalProtect MITM presents a corp CA.
# truststore handles it properly; set this to true only as a fallback.
# INSECURE_API_TLS=false
"""


MANIFEST = """\
{{"version": 1,
  "metadata": {{
    "appmode": "python-dash",
    "entrypoint": "app:server",
    "primary_document": "app.py"
  }},
  "python": {{
    "version": "3.12.0",
    "package_manager": {{
      "name": "pip",
      "version": "23.0",
      "package_file": "requirements.txt"
    }}
  }}
}}
"""


GITIGNORE = """\
__pycache__/
*.pyc
.env
.venv/
venv/

# aspire_dash copies its own assets in — don't commit duplicates
assets/00_aspire_base.css
assets/01_aspire_print.css
assets/02_aspire_skeletons.css
assets/aspire-logo.png
assets/sidebar_toggle.js
assets/dark_mode.js
"""


DEPLOY_BAT = """\
@echo off
:: Push the latest code, then deploy to Posit Connect.
:: Assumes rsconnect is configured with a saved 'aspire' server target.

git add -A
git commit -m "%~1"
git push
rsconnect deploy dash . --entrypoint app.app
"""


DEPLOY_SH = """\
#!/usr/bin/env bash
# Push the latest code, then deploy to Posit Connect.
set -euo pipefail
MSG="${{1:-deploy}}"
git add -A
git commit -m "$MSG" || true
git push
rsconnect deploy dash . --entrypoint app.app
"""


README_MD = """\
# {title}

Aspire Academy Dash app — scaffolded via `aspire-dash new`.

## Quick start

```bash
pip install -r requirements.txt
cp .env.example .env  # fill in API_URL + API_KEY
python app.py         # http://localhost:{port}
```

## Deploy

```bash
rsconnect deploy dash . --entrypoint app.app
# or, with auto-commit:
./deploy.sh "describe your changes"
```

## What you got

- Two pages: Home (KPI strip + skeleton-loaded card) and Reports
- `api_client.py` preconfigured with truststore + httpx + X-API-Key
- Toast notification wiring (use `dispatch_toast(...)` from any callback)
- `.gitignore` excludes the aspire_dash auto-copied assets
- `manifest.json` ready for Posit Connect

## Add a new page

```python
# pages/squad.py
import dash
from dash import html
from aspire_dash.components import card

dash.register_page(__name__, path="/squad", name="Squad")

def layout(**kwargs):
    return html.Div([
        html.H2("Squad"),
        card([html.P("Your content here.")]),
    ])
```

Then add it to `NAV` in `app.py`.

## Aspire-dash docs

https://github.com/kennymcmillan/aspire_dash
"""


# ============================================================
# Scaffolder
# ============================================================

def _scaffold(name, port=8050, title=None, app_type="dashboard"):
    title = title or name.replace("_", " ").replace("-", " ").title()
    target = os.path.join(os.getcwd(), name)

    if os.path.exists(target):
        print(f"Error: '{name}' already exists.")
        sys.exit(1)

    os.makedirs(os.path.join(target, "pages"))
    os.makedirs(os.path.join(target, "assets"))

    files = {
        "app.py":             APP_PY.format(title=title, port=port),
        "pages/home.py":      HOME_PY,
        "pages/reports.py":   REPORTS_PY,
        "api_client.py":      API_CLIENT_PY,
        "requirements.txt":   REQUIREMENTS,
        ".env.example":       ENV_EXAMPLE,
        "manifest.json":      MANIFEST,
        ".gitignore":         GITIGNORE,
        "deploy.bat":         DEPLOY_BAT,
        "deploy.sh":          DEPLOY_SH,
        "README.md":          README_MD.format(title=title, port=port),
    }

    for rel_path, content in files.items():
        full_path = os.path.join(target, rel_path)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

    # Make deploy.sh executable on Unix
    try:
        os.chmod(os.path.join(target, "deploy.sh"), 0o755)
    except Exception:
        pass

    print(f"Created '{name}/' with:")
    for f in sorted(files):
        print(f"  {f}")
    print()
    print("Next steps:")
    print(f"  cd {name}")
    print( "  pip install -r requirements.txt")
    print( "  cp .env.example .env   # fill in API_URL + API_KEY")
    print(f"  python app.py          # http://localhost:{port}")
    print()
    print("Then:")
    print( "  rsconnect deploy dash . --entrypoint app.app")
    print( "  # or ./deploy.sh \"describe your changes\"")


def main():
    parser = argparse.ArgumentParser(
        prog="aspire_dash",
        description="Aspire Dash CLI — scaffold new Aspire-branded Dash apps fast",
    )
    sub = parser.add_subparsers(dest="command")

    new_parser = sub.add_parser("new", help="Scaffold a new Aspire Dash app")
    new_parser.add_argument("name", help="App directory name (e.g. my_budget_app)")
    new_parser.add_argument("--port", type=int, default=8050,
                            help="Dev server port (default: 8050)")
    new_parser.add_argument("--title", help="App title (default: derived from name)")
    new_parser.add_argument("--type", default="dashboard",
                            choices=["dashboard"],
                            help="Scaffold type (only 'dashboard' for now)")

    args = parser.parse_args()
    if args.command == "new":
        _scaffold(args.name, port=args.port, title=args.title,
                   app_type=args.type)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
