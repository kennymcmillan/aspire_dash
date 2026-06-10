"""aspire_dash â€” Aspire Academy shared Dash branding, components, and layouts.

Usage in any Dash app:

    from aspire_dash import setup_app, STYLESHEETS
    from aspire_dash.components import (
        topnav, register_topnav_active,   # horizontal nav (no sidebar)
        sidebar, header,                   # sidebar nav (classic layout)
        card, toast, badge,
        status_pill, freshness_banner,    # new in 0.6
        kpi_stat, aspire_tabs,            # new in 0.6
    )
    from aspire_dash.layouts import page_layout
    from aspire_dash.theme import CHART_COLORS, ACCENT
    from aspire_dash.charts import GRAPH_CONFIG

    # Skeleton shimmer placeholders (new in 0.4):
    from aspire_dash.skeletons import (
        skel_line, skel_card, skel_tile, skel_circle,
        skel_table_rows, skel_metric_tiles, skel_card_grid,
        skel_avatar_list, skel_kpi_strip,
    )

    # KPI tiles + band-coloured progress (new in 0.5):
    from aspire_dash.components import kpi_tile, kpi_tile_row
    from aspire_dash.theme import band_color, BAND_BS, BAND_HEX

    # Cache pre-warming on app boot (new in 0.5):
    from aspire_dash.cache_prewarm import cache_prewarm

    # New in 0.6 â€” modules harvested from medical, nutrition, budget,
    # attendance, training, and mapping apps:
    from aspire_dash.time import (
        period_pill_filter, period_mode_to_dates,
        sunday_of, monday_of, first_of_month, to_date, date_range,
        format_period_label, days_ago_chip_label,
    )
    from aspire_dash.athlete import (
        athlete_avatar, athlete_profile_header,
        athlete_picker, register_athlete_picker,
        PICKER_STORE_ID,
    )
    from aspire_dash.budget import (
        fmt_currency, fmt_k, fmt_m, fmt_pct,
        variance_card, utilisation_card, rollup_chips,
    )
    from aspire_dash.export import (
        excel_export_button, pdf_download_button,
        pdf_export, send_pdf,
    )
    from aspire_dash.tables import (
        aspire_grid, register_dirty_tracking, aspire_datatable,
        DEFAULT_COL_DEF, EDITABLE_COL_DEF,
        DEFAULT_GRID_OPTIONS, EDITABLE_GRID_OPTIONS,
    )

    # New in 0.7 â€” second harvest pass (modal, upload, datatable,
    # time-ago, sport dropdown, Connect user chip, step card):
    from aspire_dash.components import (
        confirm_modal, file_upload_card,
        connect_user_chip, linear_step_card,
    )
    from aspire_dash.time import format_time_ago
    from aspire_dash.sports import sport_dropdown, ASPIRE_SPORTS

    app = Dash(__name__, external_stylesheets=STYLESHEETS, use_pages=True)
    setup_app(app)
"""

import os
import shutil
import dash_bootstrap_components as dbc

__version__ = "0.49.0"


def normalised_path(pathname: str | None) -> str:
    """Strip the Posit Connect subpath prefix from a Dash pathname so
    router callbacks can dispatch on bare paths like ``"/athletes"``.

    **Why:** Connect serves apps at ``/content/<GUID>/``. A `dcc.Location`
    callback receives the full URL â€” ``/content/<GUID>/athletes`` â€” but
    router dispatch dicts use bare keys like ``"/athletes"``. Without
    stripping the prefix, every click falls back to the default page on
    Connect (works fine locally because the prefix is "/").

    Canonical fix used inside ``aspire_dash.athlete``. Promote here so
    every router callback can call one helper:

        @callback(Output("page-content", "children"), Input("url", "pathname"))
        def route(pathname):
            path = normalised_path(pathname)
            return PAGES.get(path, default_page)

    Returns a string starting with "/" (no trailing slash), or "/" for
    the root path.
    """
    import dash as _dash
    pathname = pathname or "/"
    try:
        relative = str(_dash.strip_relative_path(pathname)) or ""
    except _dash.exceptions.UnsupportedRelativePath:
        # Pathname is ALREADY bare â€” Dash auto-strips the
        # requests_pathname_prefix from dcc.Location values before
        # passing to callbacks, so /content/<GUID>/foo arrives as just
        # /foo. strip_relative_path then raises because the input no
        # longer has the prefix it expects. Treat already-bare paths
        # as a no-op (which is what we want).
        relative = pathname
    relative = relative.strip("/")
    return "/" + relative if relative else "/"

# â”€â”€ External stylesheets every Aspire app should load â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
STYLESHEETS = [
    dbc.themes.BOOTSTRAP,
    dbc.icons.FONT_AWESOME,
    # Inter font is loaded via @import in 00_aspire_base.css
]

# â”€â”€ Optional Tailwind CSS via CDN (v0.27+) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Pass to Dash(__name__, external_scripts=EXTERNAL_SCRIPTS) to unlock
# Tailwind utility classes in any consumer app:
#
#   from aspire_dash import setup_app, STYLESHEETS, EXTERNAL_SCRIPTS
#   app = Dash(__name__, external_stylesheets=STYLESHEETS,
#              external_scripts=EXTERNAL_SCRIPTS)
#
# Then write:
#   html.Div(className="grid grid-cols-3 gap-4", children=[...])
#   html.Div(className="card bg-white p-6 rounded-xl shadow-md", ...)
#
# Pairs cleanly with our semantic CSS â€” use Aspire classes for repeated
# components (kpi-tile, athlete-card-v2, etc.) and Tailwind utilities
# for one-off page layouts. Tailwind specificity is lower than our
# semantic rules so the brand always wins on owned components.
EXTERNAL_SCRIPTS = [
    {"src": "https://cdn.tailwindcss.com"},
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

    # Copy every shared asset â€” INCLUDING subdirectories.
    # v0.20 added brand/partners/ + brand/sports/ subdirs (Aspire logo +
    # federation logos + sport heroes). Previous code did a flat listdir
    # + isfile check that silently skipped subdirs, so consumer apps
    # never received those files and the /assets/brand/... URLs 404'd.
    for root, dirs, files in os.walk(_ASSETS_DIR):
        rel = os.path.relpath(root, _ASSETS_DIR)
        dst_dir = app_assets if rel == "." else os.path.join(app_assets, rel)
        os.makedirs(dst_dir, exist_ok=True)
        for f in files:
            src = os.path.join(root, f)
            dst = os.path.join(dst_dir, f)
            if not os.path.exists(dst) or os.path.getmtime(src) > os.path.getmtime(dst):
                shutil.copy2(src, dst)

    # Sidebar toggle is handled by sidebar_toggle.js (no callback needed)

    # Note: DON'T try to set requests_pathname_prefix here. It's read-only
    # on `app.config` after Dash() runs, so app.config.update(...) raises
    # AttributeError at deploy time. Dash already reads DASH_URL_BASE_PATHNAME
    # from the environment in its own constructor when `url_base_pathname`
    # isn't passed explicitly â€” Connect sets this var, so the prefix is
    # honoured automatically. The sidebar/topnav helpers route the link
    # hrefs through dash.get_relative_path() at render time which reads
    # the now-correct prefix.
