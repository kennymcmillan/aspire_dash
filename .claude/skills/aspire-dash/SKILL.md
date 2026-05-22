# Aspire Dash — Shared Component & Styling Library + Dash Reference

> Build production-grade Plotly Dash applications with Aspire Academy branding. Covers the aspire_dash package, callbacks, components, layouts, multi-page apps, performance, deployment, and Dash Bootstrap Components.

## When to Use
- Creating, editing, debugging, or deploying Dash applications
- Styling Dash apps with Aspire Academy branding
- Using shared components (sidebar, header, cards, toasts, badges)
- Working with Dash callbacks, components, or layouts
- Building dashboards with Plotly graphs
- Using Dash Bootstrap Components for styling

---

## Pairs with `aspire_data` (CRITICAL — read first)

For any **non-UI work** in a Dash app (DB queries, Connect API calls, SAMS, scraping), reach for the sibling library `aspire_data` instead of hand-rolling httpx/asyncpg clients:

```python
# UI ← this skill (aspire_dash)
from aspire_dash.components import kpi_strip, card, sidebar
from aspire_dash.skeletons import skel_card

# Data ← aspire_data (env-driven, auto-truststore, no internal hostnames in code)
from aspire_data.sams import SamsClient
from aspire_data.connect import ConnectClient, hana_sql
from aspire_data.sports_api import SportsApi
from aspire_data.oracle import mysql_pool, with_fresh_snapshot
```

See **memory/reference_aspire_data_repo.md** for the full module reference. Repo: `kennymcmillan/aspire_data` (public).

---

## Current version: 0.9.0 (2026-05-20)

The package now ships as: `aspire_dash/components/` is a **sub-package** with 6 focused modules:

| Module | Functions |
|---|---|
| `nav` | `sidebar`, `topnav`, `header`, `hamburger_button`, `register_*_active` |
| `cards` | `card`, `graph_card`, `info_box`, `file_upload_card`, `connect_user_chip`, `linear_step_card` (plus deprecated `summary_card` w/ warning) |
| `kpi` | `kpi_tile`, `kpi_tile_row`, `kpi_strip`, `kpi_stat` |
| `feedback` | `toast`, `badge`, `empty_state`, `loading_overlay`, `status_pill`, `freshness_banner`, `confirm_modal` |
| `inputs` | `toggle_group`, `filter_bar`, `dark_mode_toggle`, `aspire_tabs` |
| `print_export` | `print_header`, `print_footer`, `export_buttons`, `send_export` |

Backwards-compatible: every `from aspire_dash.components import X` keeps working (re-export shim in `components/__init__.py`). Direct submodule imports also supported.

**Deprecated (still importable, emit `DeprecationWarning`):** `summary_card`, `stat_card` → use `kpi_tile` instead. Removed at 1.0.

---

## Package Location

**Canonical source:** `https://github.com/kennymcmillan/aspire_dash` (public repo, made public 2026-04-27)

**Local clones:**
- Personal computer: `C:\Users\kenny\Dropbox\13.DASH_APPS\aspire_dash\` (older, may have drift — push updates to GitHub from here)
- Aspire work laptop: `C:\Users\Kenneth.Mcmillan\Documents\posit-deploys\aspire_dash\` (alongside other deploys)

Demo app: `C:\Users\kenny\Dropbox\13.DASH_APPS\aspire_dash_demo\` (port 8060).

### Installing in apps

**For local dev** (editable, instant feedback):
```bash
cd <your-app>
pip install -e ../aspire_dash
```

**For Posit Connect deploys** (in your app's `requirements.txt`, NOT editable):
```
aspire_dash @ git+https://github.com/kennymcmillan/aspire_dash.git@main
```
Pin to a specific version for stability: `@v0.1.0` or commit SHA. Connect's pip clones the public repo at deploy time — no admin GitHub credential needed.

### Adding new files to the package

If you add non-`.py` files (YAML, CSS, JSON, images), they MUST be listed in `setup.py`'s `package_data` glob — otherwise pip-from-git installs omit them. Example pattern in `setup.py`:
```python
package_data={"aspire_dash": ["assets/*", "assets/**/*", "templates/*", "brand.yml"]},
```
Symptom of missing entry: `FileNotFoundError` after a downstream app installs and imports aspire_dash.

## Quick Start — New App

```python
import dash
from dash import Dash, html
from aspire_dash import setup_app, STYLESHEETS
from aspire_dash.components import sidebar, header
from aspire_dash.layouts import page_layout

app = Dash(__name__, use_pages=True, external_stylesheets=STYLESHEETS,
           suppress_callback_exceptions=True)
server = app.server  # for Posit Connect

setup_app(app)  # copies CSS + logo + sidebar_toggle.js into assets/

nav = [
    {"label": "Dashboard", "href": "/", "icon": "fa-solid fa-chart-pie", "section": "Overview"},
    {"label": "Reports", "href": "/reports", "icon": "fa-solid fa-file-lines"},
    {"label": "Settings", "href": "/settings", "icon": "fa-solid fa-gear", "section": "Admin"},
]

app.layout = page_layout(
    sidebar_el=sidebar(title="My App", subtitle="Aspire Academy", nav_items=nav),
    header_el=header(title="Dashboard"),
    use_pages=True,
)

if __name__ == "__main__":
    app.run(debug=True, port=8060)
```

### Sidebar & routing — works on local + Connect, no per-app wrapping (v0.22.3+)

**You no longer need to remember `dash.get_relative_path()` for sidebar/topnav hrefs.** Pass bare paths; the library wraps internally via the idempotent `_safe_relative()` helper.

```python
# Both styles work — pick the cleaner one:

# A. Bare paths (recommended)
NAV = [{"label": "Medals", "href": "/medals"}]

# B. Pre-wrapped (legacy, still works — no double-prefix)
NAV = [{"label": "Medals", "href": dash.get_relative_path("/medals")}]
```

**For pathname-dispatch router callbacks** — use `normalised_path()` to strip the Connect subpath cleanly:

```python
from aspire_dash import normalised_path

@callback(Output("page-content", "children"), Input("url", "pathname"))
def render_page(pathname):
    return PAGES.get(normalised_path(pathname), default_page)
```

**Three guarantees** pinned by `tests/test_normalised_path.py` (18 regression tests):
1. Sidebar/topnav links navigate correctly on Connect AND local
2. Router callbacks dispatch on bare-key dicts (`{"/foo": layout_fn}`)
3. Legacy pre-wrapped apps don't double-prefix

**Bug history avoided:**
- Pre-v0.22.3: GCC + Medical + Endurance all 404'd on sidebar clicks because they pre-wrapped hrefs AND aspire_dash sidebar wrapped again → `/content/<GUID>/content/<GUID>/medals`.
- v0.22.3 added the idempotency check + regression tests so this can't return silently.

See `tool-posit-connect` skill ⟶ "Static assets / links on Connect" for the full rule.

### Scaffold a New App — INTERACTIVE FLOW (preferred)

When the user asks to "make a new app" / "create a Dash app" / "spin up a dashboard", **don't jump straight to `python -m aspire_dash new`**. Walk through these questions via `AskUserQuestion` first, then generate a tailored scaffold:

**Question 1 — Layout shell**
- Sidebar (dark navy left panel, best for 5+ pages)
- Topnav (full-width bar, best for 2-4 pages or wide dashboards)
- Single-page (no nav, one analytical surface)

**Question 2 — Primary domain** (drives which `aspire_dash` submodules get pre-imported)
- Athlete / performance (Whoop · VALD · Firstbeat · anthropometric · medical)
- Sport reporting (rankings · competitions · country flags · source badges)
- Financial / budget (KPIs · variance cards · waterfall · financial scope CSS)
- Nutrition (macro tiles · diary grid · adherence rings)
- Mixed / generic (KPIs · cards · skeletons only)

**Question 3 — Data sources** (pre-wires the boilerplate)
- SAMS athletes (auto-import `aspire_data.sams.SamsClient`)
- Oracle Sports DB (`aspire_data.sports_api.SportsApi`)
- HANA (`aspire_data.connect.hana_client`)
- Aiven Postgres (`aspire_data.aiven`)
- None / will-decide-later

**Question 4 — Pages** (multi-select)
- Overview / dashboard
- Athlete picker + profile
- Data table / editable grid
- Trend charts (line + adaptive band)
- Print/PDF report

Then generate `app.py` pre-wired with:
- The chosen layout helper (`sidebar()` or `topnav()`) using BARE-path nav_items
- `from aspire_dash.X import …` lines matching the picked domain
- `from aspire_data.X import …` matching the data sources
- One starter page per "Pages" answer (using v0.12+ helpers like `kpi_tile_v2`, `athlete_card_rings`, `aspire_grid_v2`)
- `requirements.txt` pinned to the current aspire_dash SHA
- `.rscignore` (per the mandatory-rscignore rule below)
- `manifest.json` + `app.py` Connect-ready

**Why this beats raw `python -m aspire_dash new`:** the user gets an app where every import is already correct + the layout matches what they actually need. No guessing. No 5 minutes of trimming generic boilerplate.

---

### Deep interactive flow — page-by-page, until the user is happy

After Q1-4 above, **loop** with these per-page questions. Don't generate the scaffold until the user says "done" / "ship it" / "that's everything":

**For each page, ask in this order — start open-ended, narrow down with follow-ups, never decide for the user:**

A. **Page name + route** — `Athlete Profile / /athlete`, `Recovery Trends / /recovery`, etc.

**A2. Free-form description (open-ended, optional):**
Use `AskUserQuestion` with an "Other" option encouraging description like:
> *"In your own words — what does this page do? What's the user looking at, doing, deciding? (e.g. 'coach picks an athlete, sees their last 12 weeks of jump height with a trend band, can compare against squad mean, click to drill into individual sessions')"*

Read the answer carefully. Translate into concrete components from the menu (B). If anything's ambiguous, ASK A FOLLOW-UP before moving on. Example follow-ups:
- "When you say 'compare against squad', should that be a second line on the same chart, or a separate panel?"
- "For 'drill into sessions' — modal overlay or new page?"
- "Should the trend band be ±1 SD (acute monitoring) or 95% adaptive range (longitudinal)?"
- "What time period defaults — last 4 / 8 / 12 weeks / season?"
- "Mobile responsive needed, or desktop-first?"
- "Who's the user — coach / athlete / S&C / clinician?" (affects density + jargon level)

Keep going until you can name every component on the page. Don't infer — confirm.

B. **What goes on the page?** (multi-select; offer the relevant subset for the chosen domain)
- KPI tile row (text values, accents, deltas, sparklines, or 3-ring Whoop card)
- Athlete picker drawer (cascade Sport → Squad → Athlete)
- Editable AG Grid (aspire-themed, autosave optional)
- Trend chart (line + adaptive band / SD bands / 4pt MA / ACWR zones)
- Calendar heatmap, sunburst, treemap, sankey, radar, waterfall, dumbbell, slope
- Body silhouette region heatmap
- Injury list / availability matrix
- Macro tile strip (energy / protein / carbs / fat vs targets)
- Somatochart (Heath-Carter triangle)
- Limb symmetry bars
- Country world map / federation source badges / competition cards
- Financial KPIs (heavier `.financial-report` scope)
- Plain Markdown narrative
- Skeleton loaders for cold-start UX
- Branded empty state when no data

C. **Data binding for each chosen component:**
- "What's the data source?" (SAMS endpoint / Oracle table / HANA view / static CSV / synthetic for now)
- "What's the cache TTL?" (5 min / 1 hour / 24 hours / no cache)
- "What's the loading state?" (skeleton overlay / branded spinner / quietly fetch)

D. **Layout on the page:**
- "Full-width single column / 2-up / 3-up / KPI strip on top + content below / custom grid"

E. **After each page is captured, ask:**
- "Anything else for this page?" (loop)
- "Add another page?" (loop)
- "Add a print/PDF export?" (offers `pdf_download_button` + `a4_report_shell`)
- "Add a /analysis subpage?" (offers period filter + multi-day rollup)

**Only when the user says "we're done" / "ship it":**
1. Write `app.py` with the bare-path nav_items, all imports correct
2. Write one file per page under `pages/` using the chosen components + data wiring
3. Write `requirements.txt` pinned to the current `aspire_dash` SHA + `aspire_data` SHA + any extras (e.g. `dash-ag-grid` if grids chosen)
4. Write `.rscignore` per the mandatory rule
5. Write `manifest.json` (or let `rsconnect deploy` generate it)
6. Write a starter `README.md` summarising the app + pages
7. `git init && git add . && git commit` so the user can `git push` immediately
8. Report: which Connect GUID to deploy to (or "first deploy will get one"), and the exact `rsconnect deploy dash .` command

### What the skill knows — full picture for new-app generation

Reference these so the question flow is informed:

**aspire_dash (v0.22.3+) — 75+ helpers across 22 modules:**
- `v12_helpers`: kpi_tile_v2, date_toolbar, status_pill_v2, athlete_card, aspire_grid_v2, aspire_loading, aspire_empty, sparkline_tile, injury_card, asymmetry_bar, metric_ring, athlete_card_rings
- `medical`: body_silhouette, injury_list
- `financial`: financial_kpi, variance_cell, totals_row, financial_tab_bar, financial_table (with `.financial-report` scope class)
- `metrics`: SDS, moving_average, ACWR + zone, adaptive_range, LMS percentile, z_score
- `plots`: boxplot, violin, ridge, sunburst, treemap, calendar_heatmap, waterfall, sankey, radar, slope, dumbbell, adaptive_trend
- `nutrition`: macro_strip, macro_tile
- `anthropometric`: somatochart, growth_chart, athlete_snapshot_card, limb_symmetry_bar
- `brand_logos`: partner_logo, partners_strip, sport_hero, SPORT_HEROES (athletics, fencing, squash, table_tennis, facility), PARTNER_LOGOS (14 Qatar federations + 2 ministries + 3 international)
- `countries`: lookup, name, emoji, iso2/iso3, flag_url, flag_img (rect/circle/square), search, normalise, ALL (204 countries)
- `vald`: analytics_chart, cmj_panel_chart (4 modes), group_heatmap, adaptive_chart, vald_cmj_grid (2×2 dashboard)
- `athlete`, `sports`, `firstbeat`, `budget`, `theme`, `skeletons`, `cards`, `kpi`, `feedback`, `inputs`, `tables`, `viz`

**aspire_data — connection clients (single import per source):**
- `aspire_data.connect.ConnectClient` (+ hana / jobs / notify / render wrappers)
- `aspire_data.sports_api.SportsApi` (Oracle Sports DB; envelope handled)
- `aspire_data.sams.SamsClient` (TTL caches + parallel fan-out)
- `aspire_data.oracle.mysql_pool` + `with_fresh_snapshot` (REPEATABLE-READ fix)
- `aspire_data.aiven.aiven_postgres_conn` (SSL handled)
- `aspire_data.hetzner.HetznerClient(direct=False)` (defaults to proxy)
- All ship with `truststore` auto-injected — works on the corp-CA Aspire laptop without manual SSL setup

**Posit Connect deploy basics:**
- `rsconnect deploy dash .` — first deploy; `--app-id <GUID>` for subsequent
- `--python "C:/Users/Kenneth.Mcmillan/AppData/Local/Programs/Python/Python312/python.exe"` — Connect needs 3.12
- `--entrypoint app.app:server` ONLY if the app uses `app/` subpackage (aspire-nutrition pattern)
- Env vars at deploy: `-E NAME=value`; otherwise set in Connect UI → Vars + redeploy
- After deploy, ask "patch min_processes=1?" if it's an interactive Dash app (avoids cold-start)

**Forge workflow** for visual polish: if the user asks "make this look amazing" mid-flow, invoke the `forge` skill — prototype in tools/forge/index.html first, then port.

### Scaffold a New App — CLI fallback

```bash
python -m aspire_dash new my_app
python -m aspire_dash new my_app --port 8070 --title "Budget Tracker"
```
Creates: `app.py`, `pages/home.py`, `pages/reports.py`, `requirements.txt`, `manifest.json` (Posit Connect), `.gitignore`. Generic boilerplate — use only when the interactive flow isn't appropriate (CI, batch scripts, or user explicitly asks for the CLI).

### ⚡ MANDATORY for any app that will deploy to Connect: drop a `.rscignore`

Before the **first** `rsconnect deploy`, add `.rscignore` to the app root. `rsconnect` reads it gitignore-style and excludes matching paths from the bundle. Without one, you bundle `.git/`, `tests/`, `__pycache__/`, raw data, screenshots — Connect's `/var` fills up faster than necessary and bundles balloon 30–80%.

This is a standing rule per [[feedback_rscignore_mandatory]] and [[reference_connect_disk_cleanup]]. The scaffolder doesn't write it yet (TODO upstream — contribute to `aspire_dash/cli.py`). Until then, write it by hand:

```
.git/
.venv/
env/
.env*
tests/
test_*.py
*_test.py
conftest.py
__pycache__/
*.pyc
.pytest_cache/
.ipynb_checkpoints/
.mypy_cache/
.ruff_cache/
docs/
screenshots/
data/raw/
data/cache/
node_modules/
.DS_Store
Thumbs.db
```

**Image/PDF files are intentionally NOT excluded** — Quarto reports bundle `_*.png` brand assets, Dash apps may ship logos, and the few MB cost is worth avoiding silent breakage of deployed reports. For specific apps with junk `screenshots/` or raw PDFs, use a folder-level exclude (already in the template) rather than `*.png`.

**For existing apps under `~/Documents/posit-deploys/`** without an `.rscignore`: add one before their next deploy. Full skill section: [[tool-posit-connect]] → "MANDATORY: drop a `.rscignore` at the root of every app".

### Multi-Page App Structure
```
app.py
pages/
  home.py
  analytics.py
  settings.py
assets/          # setup_app() copies shared CSS/JS here
  custom.css     # app-specific overrides
```

```python
# pages/home.py
import dash
from dash import html, dcc
dash.register_page(__name__, path="/", title="Home", name="Home")

layout = html.Div([
    html.H1("Home Page"),
    dcc.Link("Go to Analytics", href="/analytics")
])
```

### Pages with URL Parameters
```python
# pages/asset.py
import dash
from dash import html
dash.register_page(__name__, path_template="/assets/<asset_id>")

def layout(asset_id=None, **kwargs):
    return html.Div([html.H1(f"Asset: {asset_id}")])
```

## Package Structure

```
aspire_dash/
  __init__.py          # setup_app(), STYLESHEETS
  __main__.py          # CLI: python -m aspire_dash new <name>
  brand.yml            # Single source of truth (colours, fonts, radius, shadows)
  theme.py             # Python constants from brand.yml
  components.py        # sidebar(), header(), card(), summary_card(), graph_card(),
                       # export_buttons(), send_export(), toast(), badge(), info_box(),
                       # empty_state(), toggle_group(), filter_bar(),
                       # hamburger_button(), dark_mode_toggle(), print_header(), print_footer()
  layouts.py           # page_layout(), single_page_layout()
  sports.py            # country_flag(), flag_with_name(), nation_selector(),
                       # stat_card(), placement_badge(), rank_change(), trend_arrow(),
                       # competition_badge(), category_badge(), data_row(),
                       # gradient_stat_card(), mini_stat(), header_stat(), color_badge(),
                       # format_season(), get_current_season(),
                       # IOC_TO_ISO mapping (230+ codes), ioc_to_iso(), ioc_to_iso3()
  charts.py            # Plotly "aspire" template, GRAPH_CONFIG
  viz.py               # Custom SVG: progress_ring(), status_ring(), sparkline(),
                       # horizontal_bar(), status_dot(), metric_spark(), ring_row()
  firstbeat.py         # HR zone bars, ACWR badges, metric trio, training cards,
                       # zone_stacked_bar(), add_acwr_zones(), get_acwr_status()
  assets/
    00_aspire_base.css # Base CSS (~1200 lines, includes dark mode rules)
    01_aspire_print.css# Print stylesheet (hides sidebar, expands tables, preserves SVG)
    aspire-logo.png    # Brand logo
    sidebar_toggle.js  # Pure JS sidebar toggle (no Dash callback)
    dark_mode.js       # Dark mode toggle with localStorage persistence
  templates/
    app_template.py    # Copy-paste starter for new apps
```

## Brand Colours (from aspire.qa)

| Token | Hex | Usage |
|-------|-----|-------|
| `--aspire-900` | `#001d3d` | Sidebar background (deep navy) |
| `--aspire-800` | `#002855` | Sidebar hover |
| `--aspire-700` | `#003566` | Sidebar active, borders |
| `--aspire-600` | `#004185` | **PRIMARY** — brand blue (buttons, accents) |
| `--aspire-500` | `#0059b3` | Links, highlights |
| `--aspire-400` | `#3b82f6` | Info / interactive, focus-visible outlines |
| `--aspire-50` | `#eff6ff` | Near-white blue wash |
| `--gold` | `#fbb800` | Awards, emphasis (from aspire.qa --yellow) |

Canvas background: `--slate-100` (#f1f5f9) — light grey-white.

## Key Imports

```python
# Setup
from aspire_dash import setup_app, STYLESHEETS

# Theme tokens
from aspire_dash.theme import (
    ACCENT, ACCENT_HOVER, ASPIRE_BLUE, ASPIRE_NAVY, GOLD,
    CHART_COLORS, SLATE, ASPIRE, FONT_FAMILY, FONT_MONO,
    SIDEBAR_WIDTH, SIDEBAR_BG, SHADOW_SM, SHADOW_MD, SHADOW_LG,
    RADIUS_SM, RADIUS_MD, RADIUS_LG, RADIUS_FULL,
    SUCCESS, WARNING, DANGER, INFO,
)

# Components
from aspire_dash.components import (
    sidebar, header, hamburger_button, dark_mode_toggle,
    card, summary_card, graph_card, info_box, empty_state,
    export_buttons, send_export,
    toast, badge, toggle_group, filter_bar,
    print_header, print_footer, TOAST_STYLE,
)

# Sports report components (flags, stat cards, badges, rankings)
from aspire_dash.sports import (
    country_flag, flag_with_name, nation_selector,
    stat_card, gradient_stat_card, mini_stat, header_stat,
    placement_badge, rank_change, trend_arrow,
    competition_badge, category_badge, color_badge, data_row,
    format_season, get_current_season,
    IOC_TO_ISO, ioc_to_iso, ioc_to_iso3, FOCUS_NATIONS,
)

# Custom SVG visualisations (requires dash-svg)
from aspire_dash.viz import (
    progress_ring, status_ring, ring_row,
    sparkline, horizontal_bar, status_dot, metric_spark,
)

# Firstbeat / Training Load components
from aspire_dash.firstbeat import (
    zone_bars, zone_stacked_bar, acwr_badge, metric_trio,
    training_card, get_acwr_status, add_acwr_zones,
    ZONE_CONFIG, ZONE_COLORS, ACWR_THRESHOLDS,
)

# Layouts
from aspire_dash.layouts import page_layout, single_page_layout

# Charts
from aspire_dash.charts import GRAPH_CONFIG, apply_template
```

## Aspire Component API

### sidebar(title, subtitle, nav_items, logo_gradient, footer)
- `nav_items`: list of `{"label", "href", "icon", "section"}` dicts
- When `section` changes between items, a divider + section label is inserted
- Sidebar width is **220px** (set in brand.yml)
- Sidebar links are `rgba(255,255,255,0.7)` muted, brighten to white on hover
- Toggle is handled by pure JS (`sidebar_toggle.js`), copied by `setup_app()`

### header(title, subtitle, right_content)
- Sticky with backdrop blur: `blur(12px) saturate(1.2)` (in base CSS)
- Includes hamburger button automatically

### card(children, className, style)
- White card with 12px radius and shadow-sm
- Cards and `.chart-card` have `border: 1px solid var(--slate-200)`

### summary_card(label, value, sub, icon, color_class)
- KPI card with label + big value + optional subtitle
- Value font: **22px**, weight 700, `font-variant-numeric: tabular-nums`

### graph_card(figure, config, title, style, **graph_kwargs)
- Wraps `dcc.Graph` in a white card with rounded corners (12px), border (slate-200), and shadow-md
- Optional `title` string rendered above the chart
- Pass any extra kwargs (e.g. `id`) through to `dcc.Graph`

### export_buttons(export_id, csv, excel, style) + send_export(triggered_id, df, filename_base, sheet_name)
- `export_buttons("my-export")` renders CSV + Excel buttons with `dcc.Download`
- Button IDs: `{export_id}-csv`, `{export_id}-xlsx`; Download ID: `{export_id}-download`
- In your callback, use `send_export(ctx.triggered_id, df, "filename")` to return the download dict

```python
# Layout
from aspire_dash.components import export_buttons
export_buttons("my-export")

# Callback
from aspire_dash.components import send_export

@callback(Output("my-export-download", "data"),
          Input("my-export-csv", "n_clicks"), Input("my-export-xlsx", "n_clicks"),
          State("store-data", "data"), prevent_initial_call=True)
def do_export(csv_n, xlsx_n, data):
    df = pd.DataFrame(data)
    return send_export(ctx.triggered_id, df, "my_data", sheet_name="Sheet1")
```

### toast(toast_id) / badge(text, color, pill) / info_box(title, children, icon)
### empty_state(icon, text, hint) / toggle_group(toggle_id, options, value) / filter_bar(children)

## Sports Components (aspire_dash.sports)

Sport-agnostic components for report apps across fencing, athletics, swimming, squash, and padel. Demo usage in the Fencing Dash App.

### Country Flags & IOC Codes

```python
from aspire_dash.sports import country_flag, flag_with_name, IOC_TO_ISO, ioc_to_iso, ioc_to_iso3

# Flag image from flagcdn.com (IOC 3-letter code → ISO-2 → PNG)
country_flag("QAT", size="md", show_text=True)   # 🇶🇦 QAT
country_flag("USA", size="lg")                     # large flag only
flag_with_name("FRA", "MEINHARDT Race", highlight_nation="QAT")  # flag + name, bold if match

# IOC code lookups (230+ mappings)
ioc_to_iso("QAT")   # → "QA"
ioc_to_iso3("QAT")  # → "QAT" (ISO-3166 alpha-3, different from IOC for some)
IOC_TO_ISO["GER"]   # → "DE"
```

### Stat Cards

```python
from aspire_dash.sports import stat_card, gradient_stat_card, mini_stat, header_stat

# Standard stat card (green/blue/red/amber/purple/teal/gray presets)
stat_card("Pool Win Rate", "79.3%", sub="138/174 bouts", icon="fa-solid fa-swords", color="green")

# Gradient stat card (custom gradient + emoji accent)
gradient_stat_card("Total Fencers", 268, emoji="👥",
                   bg="linear-gradient(135deg, #dbeafe, #bfdbfe)", color="#1e40af")

# Mini stat for dense grids (fencer cards, report summaries)
mini_stat("W/M", "4/6", color="#1e40af")
mini_stat("Win%", "67%", color="#16a34a")

# Header stat (centered label+value for profile headers)
header_stat("Competitions", 105)
header_stat("Pool Bouts", 174)
```

### Badges & Indicators

```python
from aspire_dash.sports import placement_badge, rank_change, trend_arrow, color_badge, competition_badge, category_badge

# Placement badge (gold/silver/bronze for 1-3, blue 4-8, green 9-16, gray 17+)
placement_badge(1, size="md")  # 🏆 1 (gold)
placement_badge(8, size="sm")  # 8 (blue)

# Custom-color badge (any hex bg + text color)
color_badge("FIE", "#e0e7ff", "#3730a3")
color_badge("EuroF", "#ccfbf1", "#115e59")
color_badge("FTL", "#ffedd5", "#9a3412")

# Rank change arrow (green up / red down / gray dash)
rank_change(current=3, previous=7)  # ↑4 (green)

# Trend arrow from historical values (oldest first)
trend_arrow([42, 27, 11])  # improving (green up)

# Competition tier badge
competition_badge("grand_prix", source="fie")

# Category badge with optional weapon/gender
category_badge("Senior", weapon="Foil", gender="Men")
```

### Nation Selector & Season Formatting

```python
from aspire_dash.sports import nation_selector, format_season, get_current_season, FOCUS_NATIONS

# Dropdown with FOCUS_NATIONS (QAT, UAE, KSA, BHR, OMA, KUW + major fencing nations)
nation_selector(selector_id="highlight-nation", value="QAT")

# Season formatting
format_season("2026")       # → "2025-2026"
format_season("2025-2026")  # → "2025-2026"
get_current_season()        # → "2025-2026" (based on current date, Sep cutoff)
```

### Data Row

```python
from aspire_dash.sports import data_row

# Styled row for custom tables (header/highlight variants)
data_row(["#1", "CHEUNG Ka Long", "HKG", "152"], header=False, highlight=True)
```

## Viz Components (aspire_dash.viz)

Custom SVG visualisations (requires `dash-svg`). Demo at `/viz` in the demo app.

- **`progress_ring(value, max_val, size, stroke_width, color, label, display, unit)`** — circular progress ring
- **`status_ring(value, max_val, thresholds, size, label, unit)`** — auto green/yellow/red ring
- **`ring_row(rings, gap)`** — horizontal row of rings
- **`sparkline(values, color, width, height)`** — inline SVG sparkline
- **`horizontal_bar(value, max_val, color, height, label, show_pct)`** — progress bar
- **`status_dot(status, size, pulse)`** — coloured indicator dot
- **`metric_spark(label, value, unit, trend_values, color)`** — metric card with sparkline

## Firstbeat / Training Load Components (aspire_dash.firstbeat)

HR zone, ACWR, and training load components. Reusable across Firstbeat, WHOOP, and any training-load app. Demo at `/firstbeat` in the demo app.

### Constants

```python
ZONE_COLORS = {"zone1": "#60A5FA", "zone2": "#2DD4BF", "zone3": "#4ADE80", "zone4": "#FACC15", "zone5": "#F87171"}
ZONE_CONFIG = [
    {"key": "zone1", "label": "Z1", "name": "Recovery",  "color": "#60A5FA"},
    {"key": "zone2", "label": "Z2", "name": "Easy",      "color": "#2DD4BF"},
    {"key": "zone3", "label": "Z3", "name": "Aerobic",   "color": "#4ADE80"},
    {"key": "zone4", "label": "Z4", "name": "Threshold", "color": "#FACC15"},
    {"key": "zone5", "label": "Z5", "name": "Max",       "color": "#F87171"},
]
ACWR_THRESHOLDS = {
    "detraining": {"max": 0.8, ...},   # Blue
    "optimal":    {"max": 1.3, ...},    # Green
    "caution":    {"max": 1.5, ...},    # Amber
    "danger":     {"max": 99.0, ...},   # Red
}
```

### get_acwr_status(acwr) -> dict
Returns `{"status", "label", "color", "bg", "text"}` for any ACWR value (or None).

### acwr_badge(acwr, show_value=True)
Pill badge auto-coloured by ACWR status. `show_value=False` shows label only.

### zone_bars(zones, show_labels=True, show_duration=True, bar_height=16)
Horizontal HR zone bars — one bar per zone (Z1-Z5). `zones` is `{"zone1": float, ...}` in minutes.

### zone_stacked_bar(zones, width=120, height=16)
Compact inline stacked bar for table cells. Hover shows tooltip with all zone values.

### metric_trio(hr_avg, hr_peak, aerobic_te, anaerobic_te, trimp, hr_avg_pct, hr_peak_pct)
3-column metric display — Heart Rate (red) / Training Effect (emerald) / TRIMP (orange).

### training_card(athlete_name, sport, date_str, time_str, zones, hr_avg, hr_peak, aerobic_te, anaerobic_te, trimp, acwr, duration_min, title, hr_avg_pct, hr_peak_pct, on_click_id)
Complete training session card with header, HR zone bars, and metric trio. Includes ACWR badge and duration pill.

### add_acwr_zones(fig, opacity=0.5)
Add coloured ACWR reference bands (Detraining/Optimal/Caution/Danger) to any Plotly figure.

### Example Usage

```python
from aspire_dash.firstbeat import zone_bars, acwr_badge, training_card, add_acwr_zones

# Zone bars
zone_bars({"zone1": 15, "zone2": 42, "zone3": 65, "zone4": 18, "zone5": 9})

# ACWR badge
acwr_badge(1.05)                    # "1.05 - Optimal" (green pill)
acwr_badge(1.42, show_value=False)  # "Caution" (amber pill)

# Training card
training_card("Ali Al-Marri", "Fencing", "Mar 14, 2026",
              zones=zones, hr_avg=152, hr_peak=188,
              aerobic_te=4.5, anaerobic_te=2.1, trimp=245, acwr=1.05)

# ACWR zones on Plotly chart
fig = go.Figure(go.Scatter(x=dates, y=acwr_values))
add_acwr_zones(fig)
```

## Dark Mode

Add `dark_mode_toggle()` to header `right_content`. Toggles `.dark` class on `<html>`, saved to localStorage.

```python
header_el=header(title="My App", right_content=dark_mode_toggle())
```

CSS rules in `00_aspire_base.css` handle: main area, header, cards, tables, dropdowns, Plotly charts. Print always forces light mode.

## Print Support

Use `print_header()` and `print_footer()` components (hidden on screen, shown on print). `01_aspire_print.css` hides sidebar/header/buttons, expands DataTables, preserves SVG ring colours.

```python
from aspire_dash.components import print_header, print_footer
# Add to page layout:
print_header(title="Budget Report", subtitle="Q1 2026")
print_footer(text="Aspire Academy — Confidential")
```

## CSS Design Details

- **Tooltips/hovers**: white background with black text
- **Focus-visible**: `outline: 2px solid var(--aspire-400); outline-offset: 2px`
- **Page enter animation**: `pageEnter 0.25s ease-out` (opacity + translateY)
- **Animations**: `pulse-red`, `pulse-ring`, `cell-pulse`, `shimmer`, `tooltipFade`, `pageEnter`

## CSS Classes Available

**Layout:** `.app-container`, `.sidebar`, `.sidebar-collapsed`, `.main-area`, `.main-area-expanded`, `.header`, `.page-content`
**Cards:** `.card`, `.budget-card`, `.athlete-card`, `.card-green`, `.card-yellow`, `.card-red`, `.chart-card`
**Badges:** `.badge`, `.badge-gray`, `.badge-blue`, `.badge-green`, `.badge-red`, `.badge-amber`, `.status-badge`
**Controls:** `.controls-bar`, `.control-label`, `.toggle-group`, `.toggle-btn`, `.filter-pill`
**Progress:** `.progress-bar-bg`, `.progress-bar-fill`, `.mini-progress`
**Text:** `.section-title`, `.chart-title`, `.stat-value`, `.stat-label`
**State:** `.empty-state`, `.skeleton` (shimmer animation)

## CSS Variables

All Tailwind-equivalent colour scales: `--slate-*`, `--emerald-*`, `--amber-*`, `--blue-*`, `--red-*`, `--green-*`, `--aspire-*`
Plus: `--radius-sm/md/lg/full`, `--shadow-sm/md/lg`, `--gold`

## Aspire Charts

```python
from aspire_dash.charts import GRAPH_CONFIG, apply_template
import plotly.express as px

fig = px.bar(df, x="sport", y="budget")
# Template auto-applied (Inter font, Aspire colour palette, clean grid)
dcc.Graph(figure=fig, config=GRAPH_CONFIG)  # modebar hidden
```

## Sidebar Toggle — How It Works

Uses **pure JavaScript** (`assets/sidebar_toggle.js`), NOT a Dash `clientside_callback`. Critical because clientside callbacks conflict with Dash 4 Pages ("Wrong length output_spec").

- `setup_app()` copies `sidebar_toggle.js` into app's assets/
- JS uses event delegation so it works even if the button renders late
- `register_sidebar_toggle()` exists as legacy — **do NOT use it**
- `layouts.py` has no `dcc.Store` for sidebar state

## Existing Apps Using aspire_dash

- `DASH_Budget` — Budget tracker
- `DASH_WHOOP` — WHOOP coach dashboard
- `DASH_VALD` — VALD force plate explorer
- `DASH_Vyntus` — CPET analysis (port 8055) — uses `graph_card`, `export_buttons`, `send_export`
- `DASH_FirstBeat` — Firstbeat training load monitor (port 8065) — uses `firstbeat` components
- `DASH_Fencing_Reports_App` — Fencing competition reports (port 8050) — uses `sports` components heavily: `country_flag`, `stat_card`, `gradient_stat_card`, `placement_badge`, `nation_selector`, `color_badge`, `mini_stat`, `header_stat`. 8 pages, 22 API endpoints, Word export (.docx via python-docx). Location: `C:\Users\kenny\Dropbox\6. NEXT_JS_PROJECTS\DASH_Fencing_Reports_App\`
- `aspire_dash_demo` — Component showcase (port 8060, includes `/firstbeat` page)

---

# Dash Framework Reference

## Callbacks

### Basic Callback
```python
from dash import Input, Output, State, callback

@callback(
    Output("output-div", "children"),
    Input("input-field", "value"),
    State("other-field", "value")  # State doesn't trigger callback
)
def update(input_val, state_val):
    return f"Input: {input_val}, State: {state_val}"
```

### Multiple Outputs
```python
@callback(
    Output("graph", "figure"),
    Output("table", "data"),
    Output("status", "children"),
    Input("dropdown", "value")
)
def update(val):
    fig = px.bar(...)
    data = df.to_dict("records")
    return fig, data, f"Showing: {val}"
```

### Prevent Initial Call
```python
@callback(Output("result", "children"), Input("button", "n_clicks"), prevent_initial_call=True)
def on_click(n):
    return f"Clicked {n} times"
```

### Callback Context (which input triggered)
```python
from dash import ctx

@callback(Output("out", "children"), Input("btn1", "n_clicks"), Input("btn2", "n_clicks"))
def update(n1, n2):
    triggered_id = ctx.triggered_id  # "btn1" or "btn2"
    return f"Triggered by: {triggered_id}"
```

### Pattern-Matching Callbacks
```python
from dash import MATCH, ALL

# ALL - matches all components with matching key structure
@callback(Output("totals", "children"), Input({"type": "checklist", "index": ALL}, "value"))
def update_totals(all_values):
    return f"Total checked: {sum(len(v) for v in all_values)}"

# MATCH - matches the specific component that triggered
@callback(
    Output({"type": "output", "index": MATCH}, "children"),
    Input({"type": "input", "index": MATCH}, "value")
)
def update_matched(value):
    return f"Value: {value}"
```

### Clientside Callbacks (JavaScript - no server round-trip)
```python
from dash import clientside_callback

clientside_callback(
    """function(data, scale) {
        return {'data': data, 'layout': {'yaxis': {'type': scale}}}
    }""",
    Output("graph", "figure"),
    Input("store", "data"),
    Input("scale-radio", "value")
)
```

### Background Callbacks (long-running tasks)
```python
from dash import DiskcacheManager
import diskcache

cache = diskcache.Cache("./cache")
background_callback_manager = DiskcacheManager(cache)
app = Dash(__name__, background_callback_manager=background_callback_manager)

@app.callback(
    Output("result", "children"), Input("start", "n_clicks"),
    running=[(Output("start", "disabled"), True, False)],
    progress=[Output("progress", "children")],
    cancel=[Input("cancel", "n_clicks")],
    background=True, prevent_initial_call=True
)
def long_task(set_progress, n_clicks):
    import time
    for i in range(10):
        set_progress(f"Step {i+1}/10")
        time.sleep(1)
    return "Done!"
```

### No Update / Conditional Updates
```python
from dash import no_update
from dash.exceptions import PreventUpdate

@callback(Output("out", "children"), Input("in", "value"))
def update(val):
    if not val: raise PreventUpdate
    if len(val) < 3: return no_update
    return f"Result: {val}"
```

### Partial Property Updates (Dash 2.9+)
```python
from dash import Patch

@callback(Output("graph", "figure"), Input("color-picker", "value"))
def update_color(color):
    patched_fig = Patch()
    patched_fig["layout"]["paper_bgcolor"] = color
    return patched_fig
```

---

## Core Components (dcc)

### Graph
```python
dcc.Graph(id="my-graph", figure=px.scatter(df, x="col1", y="col2", color="category"),
          config=GRAPH_CONFIG, style={"height": "500px"})
# Click data: Input("my-graph", "clickData") -> clickData["points"][0]
```

### Dropdown
```python
dcc.Dropdown(["NYC", "MTL", "SF"], "NYC", id="city-dd")
dcc.Dropdown(options=[{"label": "New York", "value": "NYC"}],
             value="NYC", id="city-dd", multi=True, clearable=True, searchable=True)
```

### Slider / RangeSlider
```python
dcc.Slider(min=0, max=100, step=5, value=50, id="slider",
           marks={0: "0", 50: "50", 100: "100"},
           tooltip={"placement": "bottom", "always_visible": True})
dcc.RangeSlider(min=0, max=100, value=[25, 75], id="range")
```

### Input / Textarea
```python
dcc.Input(id="input", type="text", value="", placeholder="Enter...", debounce=True)
dcc.Textarea(id="textarea", value="", style={"width": "100%", "height": 200})
```

### Checklist / RadioItems
```python
dcc.Checklist(options=["A", "B", "C"], value=["A"], id="check", inline=True)
dcc.RadioItems(options=["Linear", "Log"], value="Linear", id="radio", inline=True)
```

### DatePicker
```python
dcc.DatePickerSingle(id="date", date="2026-01-01")
dcc.DatePickerRange(id="date-range", start_date="2026-01-01", end_date="2026-12-31")
```

### Store / Interval / Loading
```python
dcc.Store(id="my-store", storage_type="memory")  # memory, session, local
dcc.Interval(id="interval", interval=5000, n_intervals=0)
dcc.Loading(id="loading", type="circle", children=[html.Div(id="output")])
```

### Tabs
```python
dcc.Tabs(id="tabs", value="tab-1", children=[
    dcc.Tab(label="Tab 1", value="tab-1", children=[html.Div("Content 1")]),
    dcc.Tab(label="Tab 2", value="tab-2", children=[html.Div("Content 2")]),
])
```

### Upload / Download
```python
dcc.Upload(id="upload", children=html.Div(["Drag and Drop or ", html.A("Select Files")]),
           style={"borderStyle": "dashed", "borderWidth": "1px", "textAlign": "center"}, multiple=True)

dcc.Download(id="download")
# In callback: return dcc.send_data_frame(df.to_csv, "data.csv", index=False)
# Also: dcc.send_file("path/to/file.xlsx"), dcc.send_bytes(bytes_val, "file.pdf")
```

### Markdown
```python
dcc.Markdown("### Title\n**bold**, *italic*, [links](url), LaTeX: $E=mc^2$",
             mathjax=True, dangerously_allow_html=True)
```

---

## HTML Components (html)

```python
html.Div(children=[], id="", className="", style={})
html.H1("Title")  # H1-H6
html.P("Paragraph") / html.Span("Inline") / html.A("Link", href="/page")
html.Img(src="/assets/image.png", style={"width": "200px"})
html.Button("Click", id="btn", n_clicks=0)
html.Table([html.Tr([html.Th("Col1"), html.Th("Col2")])])
html.Hr() / html.Br() / html.Pre("preformatted") / html.Code("code")
html.Details([html.Summary("Click to expand"), html.P("Hidden content")])
html.Label("Label", htmlFor="input-id")
html.Ul([html.Li("Item 1"), html.Li("Item 2")])
```

---

## Athlete photos — pass SAMS public URL directly (no proxy)

**Canonical pattern across all Aspire Dash apps** (medical-dashboard, sams-attendance-dashboard, endurance-dashboard). Use this verbatim — do NOT build a Flask proxy route.

```python
photo_url = profile.get("imageUrl")  # SAMS API field, e.g. via /api/ExternalApps/player/{id}/details
photo_el = (
    html.Img(src=photo_url,
             style={"width": "44px", "height": "44px",
                    "borderRadius": "50%", "objectFit": "cover",
                    "border": "2px solid #e2e8f0"})
    if photo_url else
    html.Div(_initials(name), style={...})  # fallback initials circle
)
```

**Why direct works:** SAMS photos live on `https://azfpictures.blob.core.windows.net/sports/player/{MRN}.jpg` — a **publicly readable** Azure blob (HTTP 200, no auth headers needed). Browser fetches it directly with no roundtrip through your app.

**Why a Flask `/photo/<id>` proxy route does NOT work on Connect:**
- Browser hits `/photo/123`, but Connect serves your app under `/content/<guid>/` prefix → 404.
- Wrapping with `dash.get_relative_path("/photo/123")` produces the right URL but the route still has to serve images on every page render, doubling load time.
- Lost in 2026-05-11 endurance-dashboard rework: spent ~2h building a working proxy that broke on Connect anyway. The medical-dashboard pattern (pass URL through, browser caches the blob) is simpler and faster.

**The few "auth-required" SAMS image patterns** (`sports.aspire.qa/uploads/...?t=...`) are rare — for the small number of athletes whose `imageUrl` is from that path, just accept the broken image; user can re-upload to the standard blob path via SAMS UI. Adding auth-headers to your app to support these is over-engineering.

**For new Sales/HR/non-SAMS image sources:** if the URL is publicly readable, pass it directly. If it requires auth, prefer fixing the upstream auth (or moving to a public blob) over building a server-side proxy.

---

## DataTable

```python
from dash import dash_table

dash_table.DataTable(
    id="table", data=df.to_dict("records"),
    columns=[{"name": col, "id": col, "type": "numeric", "format": {"specifier": ",.0f"}} for col in df.columns],
    sort_action="native", filter_action="native", page_action="native", page_size=20,
    row_selectable="multi", editable=True, export_format="csv",
    style_table={"overflowX": "auto", "maxHeight": "500px", "overflowY": "auto"},
    style_cell={"textAlign": "left", "padding": "8px", "minWidth": "100px"},
    style_header={"backgroundColor": "#f8f9fa", "fontWeight": "bold"},
    style_data_conditional=[
        {"if": {"row_index": "odd"}, "backgroundColor": "#f8f9fa"},
        {"if": {"filter_query": "{score} > 90"}, "backgroundColor": "#d4edda"},
    ],
    fixed_rows={"headers": True},
    virtualization=True,  # for 10k+ rows
)
```

---

## Dash Bootstrap Components (dbc)

### Layout Grid
```python
dbc.Container([
    dbc.Row([
        dbc.Col(html.Div("col-4"), width=4),
        dbc.Col(html.Div("col-8"), width=8),
    ], className="mb-3"),
], fluid=True)
# Breakpoints: xs, sm, md, lg, xl, xxl
```

### Modal
```python
modal = dbc.Modal([
    dbc.ModalHeader(dbc.ModalTitle("Title")),
    dbc.ModalBody("Modal content here"),
    dbc.ModalFooter(dbc.Button("Close", id="close-modal")),
], id="modal", is_open=False, size="lg")

@callback(Output("modal", "is_open"), Input("open-modal", "n_clicks"),
          Input("close-modal", "n_clicks"), State("modal", "is_open"))
def toggle_modal(n1, n2, is_open):
    if n1 or n2: return not is_open
    return is_open
```

### Accordion / Offcanvas
```python
dbc.Accordion([dbc.AccordionItem("Content", title="Section 1")], start_collapsed=True)
dbc.Offcanvas(html.P("Content"), id="offcanvas", title="Menu", is_open=False, placement="start")
```

### Alerts & Toasts
```python
dbc.Alert("Success!", color="success", dismissable=True, duration=4000)
dbc.Toast("Body", header="Title", icon="success", is_open=True, dismissable=True, duration=4000,
          style={"position": "fixed", "top": 10, "right": 10})
```

### Buttons / Forms / Spinners / Progress
```python
dbc.Button("Primary", color="primary", outline=False, size="lg")
dbc.ButtonGroup([dbc.Button("Left"), dbc.Button("Right")])
dbc.Spinner(color="primary", size="sm")
dbc.Progress(value=75, label="75%", striped=True, animated=True, color="success")
dbc.Badge("New", color="danger", pill=True)
```

### Forms
```python
dbc.Form([
    dbc.Row([dbc.Label("Email", width=2),
             dbc.Col(dbc.Input(type="email", placeholder="Enter email"), width=10)], className="mb-3"),
    dbc.Button("Submit", color="primary"),
])
```

### Popover & Tooltip
```python
dbc.Button("Hover me", id="tooltip-target")
dbc.Tooltip("Tooltip text", target="tooltip-target", placement="top")
dbc.Popover([dbc.PopoverHeader("Title"), dbc.PopoverBody("Content")],
            target="popover-target", trigger="click")
```

### Tabs / ListGroup / Table
```python
dbc.Tabs([dbc.Tab(label="Tab 1", tab_id="tab-1", children=[...])], active_tab="tab-1")
dbc.ListGroup([dbc.ListGroupItem("Active", active=True), dbc.ListGroupItem("Item 2", href="/page-2")])
dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True, responsive=True)
```

---

## Plotly Express Quick Reference

```python
import plotly.express as px

fig = px.scatter(df, x="x", y="y", color="cat", size="val", hover_data=["extra"])
fig = px.line(df, x="date", y="value", color="series", markers=True)
fig = px.bar(df, x="cat", y="val", color="group", barmode="group")  # "stack", "relative"
fig = px.histogram(df, x="val", nbins=30, color="cat", marginal="box")
fig = px.box(df, x="cat", y="val", color="group", notched=True)
fig = px.violin(df, x="cat", y="val", box=True, points="all")
fig = px.pie(df, names="cat", values="val", hole=0.4)
fig = px.sunburst(df, path=["region", "country"], values="pop")
fig = px.treemap(df, path=["region", "country"], values="pop")
fig = px.heatmap(df.corr(), text_auto=".2f", color_continuous_scale="RdBu_r")
fig = px.area(df, x="date", y="val", color="series")
fig = px.funnel(df, x="val", y="stage")
fig = px.scatter_mapbox(df, lat="lat", lon="lon", mapbox_style="open-street-map")
fig = px.choropleth(df, locations="iso_alpha", color="gdp", projection="natural earth")

fig.update_layout(
    title="Title", template="plotly_white", height=500,
    margin=dict(l=40, r=40, t=50, b=40),
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
    hovermode="x unified",
)
fig.add_hline(y=50, line_dash="dash", line_color="red", annotation_text="Target")
fig.add_vrect(x0="2026-01-01", x1="2026-06-30", fillcolor="green", opacity=0.1)
```

---

## Performance & Caching

```python
from flask_caching import Cache
cache = Cache(app.server, config={"CACHE_TYPE": "filesystem", "CACHE_DIR": "cache"})

@cache.memoize(timeout=300)
def query_data(filter_val):
    return expensive_query(filter_val)
```

**Tips:**
- `dcc.Store` to share data between callbacks (compute once, use many)
- `prevent_initial_call=True` to skip unnecessary initial renders
- `clientside_callback` for simple transforms (no server round-trip)
- `Patch()` for partial property updates
- `virtualization=True` on DataTable for 10k+ rows
- `render_mode="webgl"` for 100k+ scatter points
- `dcc.Store(storage_type="memory")` not `"local"` for large data

---

## Deployment

```python
server = app.server  # Flask instance — use for WSGI / Posit Connect
```

```bash
# Linux
gunicorn app:server --bind 0.0.0.0:8050 --workers 4 --timeout 120
# Windows
waitress-serve --host=0.0.0.0 --port=8050 app:server
```

All Aspire apps deploy to **Posit Connect** via `server = app.server`.

---

## Gotchas

1. **No emoji surrogate pairs** — orjson (Dash 4) crashes. Use FontAwesome icons.
2. **`html.Input` does not exist** — use `dbc.Input` or `dcc.Input` (with `id`).
3. **Do NOT call `register_sidebar_toggle()`** — conflicts with Dash Pages. JS handles it.
4. **Callback outputs must be unique** — two callbacks cannot target the same Output. Use `allow_duplicate=True` for shared outputs.
5. **Circular dependencies** not allowed (A -> B -> A). `dcc.Store` Input+Output in same callback = infinite loop. Use `dcc.Interval` instead.
6. **`style` uses camelCase** — `backgroundColor` not `background-color`.
7. **`className` not `class`**, **`htmlFor` not `for`**.
8. **DataTable `data` must be list of dicts** — `df.to_dict("records")`.
9. **`n_clicks` starts as None** — check before using.
10. **Multi-page apps**: each page must call `dash.register_page(__name__)`.
11. **`debug=True`** enables hot reload (disable in production, kills background processes).
12. **Port 8055 reserved** for VYNTUS CPET. Demo uses 8060. Fencing uses 8050.
13. **CSS loads alphabetically** — `00_aspire_base.css` loads first.
14. **Inline styles beat CSS classes** — use `!important` when CSS must override Python-set styles.
15. **Dropdown value resets when options change** — if initial `options=[]` with `value="X"`, Dash clears the value when options load. Pre-populate options with at least `[{"label": "X", "value": "X"}]`.
16. **Always use `safe_int()`/`safe_float()`** for API field conversions — API fields can be None, empty string, or non-numeric. Raw `int()`/`float()` will crash.
17. **`prevent_initial_call="initial_duplicate"`** needed when using `allow_duplicate=True` on a callback that shouldn't fire on page load.

---

## dash-ag-grid (35.x) Notes

Use AG Grid (`pip install dash-ag-grid`) instead of `DataTable` for editable, scrollable tables with frozen columns — `DataTable`'s `fixed_columns` clashes with column headers on horizontal scroll.

**Read user edits via `virtualRowData`, not `rowData`:**
```python
# rowData is one-way (Dash -> grid). Edits do NOT propagate back.
State("athlete-table", "virtualRowData")  # ← reflects current displayed state including in-flight edits
```

**Don't trigger a `rowData` rebuild from `cellValueChanged`** — it resets the grid mid-keystroke and the user's typing disappears. Update other stores (e.g. dirty-tracking) but leave `rowData` alone during editing.

**Pinned columns live in a different DOM container than centre columns:**
- Pinned-left: `.ag-pinned-left-cols-container [row-index='N'] [col-id='X']`
- Centre: `.ag-center-cols-container [row-index='N'] [col-id='X']`
- Cross-container locator (Playwright): `[row-index='N'][role='row'] [col-id='X']`

**Initial loading state:** set `dashGridOptions={"loading": True}` so the grid shows AG Grid's built-in spinner instead of "No Rows To Show". Flip to `loading: False` from the build callback once data arrives.

**For UI tests**, `app.run(debug=True)` spawns a Flask reloader child process that survives the parent — killing the launcher leaves the child listening on the port. Read port + debug from env so tests can disable both:
```python
if __name__ == "__main__":
    port  = int(os.environ.get("APP_PORT", "8051"))
    debug = os.environ.get("DASH_DEBUG", "1") not in ("0", "false", "False")
    app.run(debug=debug, port=port, use_reloader=debug)
```
**For Playwright tests on Aspire laptop:** use `channel='chrome'` against system Chrome (CDN-blocked install fails). Pick a free port at runtime via `socket.bind(("127.0.0.1", 0))` to avoid conflicts.

Reference implementation: `~/Documents/posit-deploys/mapping_app/` — has the editable-grid pattern, dirty-row tracking, retry/audit on Oracle writes (`updated_by` from `RSTUDIO_USER_NAME`), and a Playwright UI smoke test (`test_ui.py`).

---

## Dash Version History

### Current: Dash 4.1.0 (2025-03-23) — upgraded from 4.0.0 on 2026-03-31

**New features:**
- **Dropdown `debounce` prop** — delays search/filter callbacks while user is typing
- **Dropdown searchable on focus** — dropdowns now searchable when focused, without opening first
- **Dropdown performance** — significantly faster with large option collections
- **Multiselect component labels** — multiselect dropdown now renders properly when labels contain Dash components (not just strings)
- **DatePickerRange same-date** — can select identical start and end dates
- **DatePicker `Y` token** — Moment.js `Y` year format now supported
- **Pattern-matching perf** — improved browser performance for apps with many pattern-matching callbacks; new API endpoint for latest `computeGraph` calls
- **`_Wildcard` backward compat** — alias added for backward compatibility

**No breaking changes.**

### Dash 4.0.0 (2025-02-03)
- Complete redesign of core components with modernized default styling
- New `allow_direct_input` prop on sliders

### Multi-Backend Support (4.1.0rc0+)
Dash now supports **FastAPI** and **Quart** backends in addition to Flask:
```bash
pip install dash[fastapi]   # FastAPI backend
pip install dash[quart]     # Quart (async Flask) backend
```
Custom backends via `BaseDashServer` subclass. Flask remains default.

## Conventions

- All apps deploy to **Posit Connect** via `server = app.server`
- App-specific CSS goes in `assets/custom.css`
- Use `pip install -e ../aspire_dash` from any app directory
- `GRAPH_CONFIG = {"displayModeBar": False}` standard on all graphs
