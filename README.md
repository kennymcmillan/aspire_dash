# aspire_dash

[![tests](https://github.com/kennymcmillan/aspire_dash/actions/workflows/test.yml/badge.svg)](https://github.com/kennymcmillan/aspire_dash/actions/workflows/test.yml)

> Build a fully Aspire-branded Plotly Dash app in **one command**.

Shared component, styling, callback, and chart library for every
Aspire Academy dashboard. Provides the things every app re-invents —
sidebar/topnav, KPI tiles, skeleton loaders, period filters, athlete
picker, PDF export, brand tokens — so each app focuses on its data.

```bash
pip install git+https://github.com/kennymcmillan/aspire_dash.git
python -m aspire_dash new my_app
cd my_app && python app.py     # http://localhost:8050
```

The scaffold gives you:

- Aspire-branded sidebar + header + page layout
- Two pages (Home, Reports), Home wires a KPI strip + skeleton loader
- `api_client.py` preconfigured with `httpx` + `truststore` + X-API-Key
- Toast wiring (`dispatch_toast(...)` from any callback)
- Posit Connect deploy: `manifest.json`, `deploy.bat`/`deploy.sh`
- `.env.example`, `.gitignore`, README

## What you skip writing

| Pattern | aspire_dash module | What it saves |
|---|---|---|
| Sidebar nav + active highlighting | `components.sidebar`, `callbacks.register_url_active_nav` | ~150 LOC |
| Top KPI strip from a dict | `components.kpi_strip` | 40 LOC |
| KPI tile w/ vs-target progress bar | `components.kpi_tile` | 60 LOC per tile |
| Shimmer-skeleton loaders | `skeletons.*` | 80 LOC + CSS |
| Period preset → date range | `time`, `callbacks.register_period_filter` | 50 LOC |
| Athlete picker (SAMS drill-down) | `athlete.*` | 200+ LOC |
| Toast notification system | `callbacks.register_toast`, `dispatch_toast` | 30 LOC |
| Cache pre-warm on app boot | `cache_prewarm` | 25 LOC |
| Currency / pct / k / M formatters | `budget.*` | 30 LOC |
| Excel + PDF download buttons | `export.*` | 80 LOC |
| AG Grid styling + dirty tracking | `tables.*` | 70 LOC |
| Brand tokens (colors, fonts, radius) | `theme.*` + `brand.yml` | n/a |
| Country flags + sports badges | `sports.*` | 250 LOC |
| Firstbeat ACWR + zone bars | `firstbeat.*` | 200 LOC |

Net: a typical Aspire dashboard ships in ~300 LOC of app code (versus
~1500 LOC of mostly boilerplate).

## Module map

| Module | Highlights |
|---|---|
| `aspire_dash` (top-level) | `setup_app`, `STYLESHEETS`, `__version__` |
| `aspire_dash.components` | sidebar, topnav, header, card, kpi_tile, kpi_strip, toast, badge, empty_state, info_box, status_pill, freshness_banner, aspire_tabs, dark_mode_toggle, filter_bar, graph_card, loading_overlay |
| `aspire_dash.layouts` | `page_layout`, `single_page_layout` |
| `aspire_dash.theme` | `BRAND`, `SLATE`, `ASPIRE_BLUE`, `GOLD`, `band_color`, radius + shadow tokens |
| `aspire_dash.skeletons` | shimmer loaders — `skel_line`, `skel_card`, `skel_tile`, `skel_table_rows`, `skel_metric_tiles`, `skel_card_grid`, `skel_avatar_list`, `skel_kpi_strip` |
| `aspire_dash.callbacks` | `register_period_filter`, `register_toast` + `dispatch_toast`, `register_pdf_download`, `register_url_active_nav` |
| `aspire_dash.cache_prewarm` | `cache_prewarm(name, fns)` — fire-and-forget TTL-cache warmer |
| `aspire_dash.athlete` | SAMS-style athlete picker + profile header |
| `aspire_dash.budget` | currency formatters, variance + utilisation cards |
| `aspire_dash.export` | Excel + PDF download buttons, reportlab helpers |
| `aspire_dash.tables` | AG Grid presets + dirty-tracking |
| `aspire_dash.time` | period mode → dates, sunday_of, format_period_label |
| `aspire_dash.sports` | country flags + ISO codes, placement badges, season formatting |
| `aspire_dash.viz` | progress rings, sparklines, status dots |
| `aspire_dash.firstbeat` | ACWR badges, training zone bars |
| `aspire_dash.timeseries` | SD traces, moving averages, outlier overlays |
| `aspire_dash.observability` | timed decorator, metric counters |

## Recipes

### KPI strip from a dict

```python
from aspire_dash.components import kpi_strip

kpi_strip([
    {"label": "Athletes", "value": 142,  "unit": ""},
    {"label": "Sports",   "value": 7,    "unit": ""},
    {"label": "Diaries",  "value": 1042, "unit": "YTD"},
    {"label": "Avg kcal", "value": 2104, "unit": "kcal/day"},
])
```

### KPI tile with vs-target progress bar

```python
from aspire_dash.components import kpi_tile

kpi_tile(
    label="Energy", value=1971, unit="kcal", color="#0f172a",
    target={"target_resolved_target": 3600,
            "pct_of_target": 55, "band": "below"},
)
```

### Skeleton loader while a callback fetches data

```python
from aspire_dash.skeletons import skel_table_rows
from dash import Input, Output, callback, html

def layout():
    return html.Div(skel_table_rows(n=8), id="my-list")

@callback(Output("my-list", "children"), Input("my-list", "id"))
def _load(_):
    return render_table(api.get_diaries())
```

### Period preset filter

```python
from aspire_dash.callbacks import register_period_filter, period_preset_options

# in layout
dcc.Dropdown(id="period-select",
             options=period_preset_options(),
             value="last_30", clearable=False)
dcc.Store(id="period-store")

# in app boot
register_period_filter(app, store_id="period-store",
                       period_select_id="period-select",
                       start_input_id="start-picker",
                       end_input_id="end-picker")
```

### Toast notifications

```python
from aspire_dash.callbacks import register_toast, dispatch_toast

# in layout (once)
dcc.Store(id="toast-trigger")
dbc.Toast(id="app-toast", is_open=False, dismissable=True, duration=4000)

# in app boot (once)
register_toast(app, toast_id="app-toast", trigger_store_id="toast-trigger")

# from any callback:
@callback(Output("toast-trigger", "data"), Input("save-btn", "n_clicks"))
def _on_save(n):
    api.save_thing()
    return dispatch_toast("Saved", "Diary persisted.", icon="success")
```

### Pre-warm caches on boot

```python
from aspire_dash.cache_prewarm import cache_prewarm

cache_prewarm(
    name="sams-rosters",
    fns=[(list_sport_roster, (sid,), {}) for sid in SPORTS],
)
```

## Install

```bash
# Pin to main
pip install git+https://github.com/kennymcmillan/aspire_dash.git@main

# Editable for local dev
git clone https://github.com/kennymcmillan/aspire_dash.git
cd aspire_dash && pip install -e .
```

In your app's `requirements.txt`:

```text
aspire_dash @ git+https://github.com/kennymcmillan/aspire_dash.git@main
```

## CLI

```bash
python -m aspire_dash --help
python -m aspire_dash new my_dashboard
python -m aspire_dash new my_report --port 8060 --title "Q2 Variance"
```

## Sidebar & routing — no per-app wrapping (v0.22.3+)

Pass **bare paths** to `sidebar()` / `topnav()`. The library wraps them with `dash.get_relative_path()` internally via an idempotent helper, so the same code works on local AND under Connect's `/content/<GUID>/` subpath:

```python
NAV = [
    {"label": "Overview", "href": "/",          "icon": "fa-solid fa-house"},
    {"label": "Medals",   "href": "/medals",    "icon": "fa-solid fa-medal"},
    {"label": "Athletes", "href": "/athletes",  "icon": "fa-solid fa-user"},
]
sidebar(title="My App", nav_items=NAV)   # just works everywhere
```

For pathname-dispatch router callbacks:

```python
from aspire_dash import normalised_path

@callback(Output("page-content", "children"), Input("url", "pathname"))
def render_page(pathname):
    return PAGES.get(normalised_path(pathname), default_page)
```

Pinned by `tests/test_normalised_path.py` — 18 regression tests cover bare / prefixed / no-context across local + Connect prefixes.

## Building a new app — ask Claude

When you want a new app, tell Claude `new aspire dash app` (or invoke the `aspire-dash` skill) and it walks through:

1. **Layout** — sidebar / topnav / single-page
2. **Domain** — athlete / sport reporting / financial / nutrition / generic
3. **Data sources** — SAMS / Sports DB / HANA / Aiven / none
4. **Pages** — overview / athlete picker / data table / trend charts / PDF report

You get an `app.py` with every import pre-wired for your choices + bare-path nav + `.rscignore` + manifest. No generic boilerplate to trim.

## Used by

- **aspire-nutrition** — clinical diary capture + analysis
- **medical-dashboard** — injury / illness tracking
- **endurance-dashboard** — wearables + training-load
- **mapping_app** — athlete-identifier cross-mapping
- **aspire-budget-fy2026** — finance + variance reporting
- **gcc-games-dash** — competition standings
- **iso-leg-press** — VALD-style strength reporting
- **sams-attendance-dashboard** — squad / session attendance

## Versioning

`CHANGELOG.md` has the per-version notes. The library follows
semver-within-0.x: additive minors (0.5 → 0.6), breaking changes get
a major bump when we get to 1.0.

```bash
python -c "import aspire_dash; print(aspire_dash.__version__)"
```

## Roadmap

- **0.7**: `aspire_dash.report` (Quarto + reportlab clinical-report builders)
- **0.7**: `firstbeat_sports` API client harvested from the endurance app
- **0.8**: `tests/` directory + GitHub Actions test runner
- **1.0**: API freeze + first stable release


## Contributing — the Forge workflow

> When you build a new visual or upgrade an existing one, **prototype it
> in Tailwind+DaisyUI first, then port the final CSS into `aspire_dash`**.
> This is how Whoop/Firstbeat-quality polish ships consistently across
> every Aspire app without per-app per-component CSS work.

### For humans

Read `tools/forge/FORGE.md` for the full step-by-step. TL;DR:

1. Open `tools/forge/index.html` in a browser (no build — Tailwind v3 + DaisyUI v4 + Aspire DaisyUI theme via CDN).
2. Add a `<section>` with **BEFORE** (current Dash render) and **AFTER** (your prototype).
3. Iterate visually until it looks great.
4. Extract the final Tailwind class string and condense into a CSS rule in `aspire_dash/assets/00_aspire_base.css` (use a semantic name like `.kpi-tile`).
5. Add a Python helper in `aspire_dash/v12_helpers.py` (or the appropriate topic module) that emits `className="..."`.
6. Sync demo CSS: `cp aspire_dash/assets/00_aspire_base.css demo/assets/`.
7. Bump `__version__` + `setup.py` + `CHANGELOG.md` together.
8. Update consumer apps' `requirements.txt` SHA pin to inherit the new look.

Every consumer app (fencing planner, nutrition, medical, budget, GCC, mapping, attendance, endurance, ISO leg press, etc.) inherits visual upgrades from one library bump — no per-app work required.

### For Claude users

The same workflow is encoded as a Claude Code skill at `.claude/skills/forge/SKILL.md`. It auto-triggers on phrases like _"redesign X"_, _"make Y look amazing"_, _"upgrade visual"_, _"needs polish"_, _"Whoop-style"_. Claude will open the Forge sandbox, prototype, show a screenshot, and port to CSS once you approve.

The skill ships **in-repo** so any colleague's Claude session loads it automatically — no per-machine install.

### Aspire palette cheat sheet

```
--aspire-600: #004185   (primary, brand blue)
--aspire-700: #003566   (hover / active)
--gold:       #fbb800   (highlights)
--slate-*               (neutrals)
--elev-1/2/3            (shadow tiers, low → high)
Border radius 8 px (cards/inputs), full (pills/badges)
Body bg #f7f9fc, Poppins font (Inter for tabular data)
```
