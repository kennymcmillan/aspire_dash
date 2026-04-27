"""aspire_dash — Aspire Academy shared Dash branding, components, and layouts.

Usage in any Dash app:

    from aspire_dash import setup_app, STYLESHEETS
    from aspire_dash.components import sidebar, header, card, toast, badge
    from aspire_dash.layouts import page_layout
    from aspire_dash.theme import CHART_COLORS, ACCENT
    from aspire_dash.charts import GRAPH_CONFIG

    app = Dash(__name__, external_stylesheets=STYLESHEETS, use_pages=True)
    setup_app(app)
"""

import os
import shutil
import dash_bootstrap_components as dbc

__version__ = "0.1.0"

# ── External stylesheets every Aspire app should load ────────────────────────
STYLESHEETS = [
    dbc.themes.BOOTSTRAP,
    dbc.icons.FONT_AWESOME,
    # Inter font is loaded via @import in 00_aspire_base.css
]

# Path to this package's assets directory
_ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")


def setup_app(app):
    """Copy shared CSS + logo into the app's assets/ folder.

    Call this once after creating the Dash app instance::

        app = Dash(__name__, external_stylesheets=STYLESHEETS, use_pages=True)
        setup_app(app)

    This copies:
    - 00_aspire_base.css   (base stylesheet)
    - 01_aspire_print.css  (print stylesheet)
    - aspire-logo.png      (brand logo)

    Files are prefixed with 00_/01_ so Dash loads them before any app-specific
    CSS in the assets/ folder (Dash loads CSS alphabetically).
    """
    app_assets = getattr(app, "config", {}).get("assets_folder", None)
    if app_assets is None:
        # Default Dash assets folder is ./assets relative to the app
        app_assets = os.path.join(os.getcwd(), "assets")

    os.makedirs(app_assets, exist_ok=True)

    # Copy each shared asset
    for filename in os.listdir(_ASSETS_DIR):
        src = os.path.join(_ASSETS_DIR, filename)
        dst = os.path.join(app_assets, filename)
        if os.path.isfile(src):
            # Only overwrite if source is newer or file doesn't exist
            if not os.path.exists(dst) or os.path.getmtime(src) > os.path.getmtime(dst):
                shutil.copy2(src, dst)

    # Sidebar toggle is handled by sidebar_toggle.js (no callback needed)
