# Changelog

All notable changes to `aspire_dash`. The library follows
[Semantic Versioning](https://semver.org/) within the 0.x line —
additive minors, breaking changes get a major bump when we get there.

## [0.12.1] — 2026-05-22

### Fixed (CRITICAL — sidebar nav broken on Connect)

- **Sidebar links now navigate correctly on Posit Connect.** Two-layer
  fix because the bug surfaced again in the VALD app + showcase:

  1. **`setup_app()` now reads `DASH_URL_BASE_PATHNAME` env var** (set by
     Connect for Python apps) and applies it to `app.config` —
     `requests_pathname_prefix` / `routes_pathname_prefix` /
     `url_base_pathname`. Without this, `dash.get_relative_path()` at
     module-load time always returned `"/foo"` instead of
     `"/content/<GUID>/foo"`, so clicks 404'd. **Every consumer app
     gets this fix for free on the next bump** — no app-side code change
     needed. Documented in [[feedback_connect_relative_path_links]].

  2. **Sidebar uses `html.A` instead of `dcc.Link`.** dcc.Link does
     client-side React-Router routing which has intermittent issues
     with Connect subpath + SSO + scrollable containers. html.A does a
     full-page nav (~200 ms extra) but is bulletproof across every
     Connect/proxy/SSO/cached-bundle scenario. Topnav stays on dcc.Link
     (it sits above the fold + the prefix fix now makes the href
     correct).

## [0.12.0] — 2026-05-22

10 new components ported from the `tools/forge/` Tailwind+DaisyUI
prototypes. **Zero API breaks** — all additions live in the new
`aspire_dash.v12_helpers` module + new CSS classes. Existing helpers
unchanged.

### Added (in `aspire_dash.v12_helpers`)

1. **`kpi_tile_v2(label, value, delta, delta_direction, sub, accent)`**
   — KPI tile with optional ▲▼ delta arrow + 6 accent-stripe colours
   (aspire / secondary / gold / success / warning / danger).
2. **`date_toolbar(prev_id, next_id, today_id, display_text)`**
   — unified `[◀ date ▶ TODAY]` control. Replaces the visually
   disjointed `dcc.DatePickerSingle + buttons + Today` pattern.
3. **`status_pill_v2(label, tone, icon, solid)`** — pill with leading
   icon + auto-icon-from-tone. 5 tones × subtle/solid = 10 variants.
4. **`athlete_card(name, photo_url, meta, score, tone, sub_metrics)`**
   — Whoop-style compact card: photo + name + meta + main score (tone-
   coloured) + up to 4 inline sub-metrics in tabular-nums.
5. **`aspire_grid_v2(grid_id, columnDefs, rowData, editable)`** —
   AG Grid wrapped with the new `.ag-theme-quartz.aspire-themed` CSS
   (uppercase aspire-blue header, slate borders, aspire-50 row hover).
6. **`aspire_loading(text, sub)`** — branded full-area loading state
   with the Aspire-blue ring spinner.
7. **`aspire_empty(text, hint, icon)`** — empty state with Aspire-blue
   tinted icon, friendly copy.
8. **`sparkline_tile(label, value, series, delta, color)`** — KPI value
   + inline mini-line-chart (Plotly), perfect for trend tiles.
9. **`injury_card(body_part, severity, status, detail, ...)`** —
   medical-domain card with severity-coloured left stripe.
10. **`asymmetry_bar(left_pct, right_pct)`** — VALD-style left/right
    split bar with deviation-coloured border (green <5%, amber 5-10%,
    red >10%).

### CSS additions in `00_aspire_base.css`

- `.kpi-delta-up/down/flat` colours
- `.date-toolbar` + `.dt-btn` + `.dt-display` + `.dt-today` (unified date control)
- `.status-pill.status-<tone>` (5 tones × `.is-solid` variant)
- `.athlete-mini-card` + `.tone-good/warn/danger/aspire` + `.amc-*` sub-elements
- `.ag-theme-aspire` (also applied via `.aspire-themed` modifier on quartz/alpine)
- `.aspire-loading-spinner` + `@keyframes aspire-spin`
- `.aspire-empty` + `.aspire-empty-icon`
- `.sparkline-tile` + `.spk-*`
- `.injury-card.severity-mild/moderate/severe/resolved`
- `.asymmetry-bar.dev-warn/danger`

### Demo

- New `/v12` page in the showcase — every new helper rendered with
  copy-pasteable code snippets. Pinned to top of sidebar nav.

## [0.11.0] — 2026-05-22

### Brand correction

- **Font: Inter → Poppins.** Sniff of https://www.aspire.qa confirms
  Poppins (weights 100-900 via Google Fonts) is the actual brand font.
  We were rendering off-brand for years. Inter stays loaded as the
  fallback for tabular-heavy contexts (better tabular-nums) via the new
  `data` font token in `brand.yml`.

### Changed (design-audit fixes — all visual, no API breaks)

- **Warmer page background `#f7f9fc`** (was `--slate-100 #f1f5f9`). Cards
  now read more elevated without needing heavier shadows.
- **3-tier elevation system** `--elev-1/2/3` with slate-tinted shadows
  instead of pure black. Existing `--shadow-sm/md/lg` kept as aliases.
- **Border radius collapsed to 8 px canonical.** `--radius-sm` and
  `--radius-lg` are now aliases for `--radius-md` (8 px). Was visually
  fragmented across 4 different sizes that no two components agreed on.
- **Card hover lift**: `.card`, `.budget-card`, `.athlete-card` all
  share the same 1 px translateY + elev-2 shadow on hover. Stripe/Linear/
  Whoop-style "premium analytics" feel.
- **Plotly defaults tightened** in `charts.py`: vertical gridlines
  removed, axis-line on Y dropped, horizontal legend at y=-0.18,
  margins tightened to `(40, 16, 8, 32)`, gridcolor dropped to slate-50
  (near-invisible). Existing charts pick this up automatically.

### Added

- `.kpi-tile` CSS class with `.accent-aspire / .accent-secondary /
  .accent-gold / .accent-success / .accent-warning / .accent-danger`
  modifiers. Sub-elements `.kpi-label`, `.kpi-value`, `.kpi-sub`
  give consistent type scale across the library.
- `.aspire-table` CSS class — uppercase header row with 2 px aspire-blue
  bottom border, slate-50 zebra striping, aspire-50 row hover. Drop-in
  for any plain `<table>` to make it feel branded.
- `.aspire-section-heading` CSS class — 5 px letter-spacing, weight
  500, uppercase Poppins. Matches the H2 style on aspire.qa marketing.
- `brand.yml`: new `data` font token for tabular contexts where Inter
  is preferable (medical tables, GCC medal counts, etc.).

## [0.10.1] — 2026-05-22

### Fixed

- **`sidebar()` nav links now route correctly under a Connect subpath.**
  Was using raw `href=item["href"]` which resolved to the Connect root
  (`posit.aspire.qa/skeletons`) instead of the app
  (`/content/<GUID>/skeletons`) — sidebar clicks silently 404'd in
  production deploys. Now uses `dash.get_relative_path(item["href"])`
  the same way `topnav()` did. Caught by the aspire_dash component
  showcase deploy.

## [0.10.0] — 2026-05-22

### Added

- **`skel_sync_overlay(caption, sub_caption, rows, overlay_id, height)`**
  in `skeletons.py`. Initial-load skeleton with spinning icon + caption
  + N shimmer placeholder rows. Hide via a callback on
  `Output(overlay_id, "style")` once your upstream sync completes.
  Caller pattern shipped in the fencing-planner Data Entry page
  (15-20 s SAMS cold sync). Pairs with a sibling Div that holds the
  real grid (`display: none` initial → revealed by the same callback).

- **`date_picker_single(picker_id, value, display_format, width)`** in
  `components/inputs.py`. Wrapper around `dcc.DatePickerSingle` with
  `"D MMM YYYY"` as the default format — avoids the **`ddd` rendering
  bug** in dash's underlying picker (renders `Tu19 19 May 2026`
  instead of `Tue 19 May 2026` because of broken token splitting).
  Docstring documents the safe vs unsafe format tokens.

- **`a4_report_shell(title, body, subtitle, back_href, ...)`** in
  `components/print_export.py`. Standard printable A4 layout:
  no-print toolbar (Back + Print button) above an A4-sized white page
  with the Aspire title bar and the caller's body. Lifted from
  weekly-report, fencer-report and monthly-brief pages in the fencing
  planner — same shape across all three.

- **`register_print_button(app, button_id)`** companion clientside
  callback to wire `window.print()` to a button.

- **`safe_markdown_label(name)`** utility: strips `[]()` from strings
  before they get embedded in markdown link labels. Defensive against
  upstream-data names that contain those characters.

- **`NUMERIC_COL_DEF`** preset in `tables.py`: `{type: numericColumn,
  cellDataType: number, cellEditor: agNumberCellEditor}`. Documented
  replacement for the custom `valueParser` shape that silently
  blocked edit mode in some dash-ag-grid 35.x builds.

- **`.skeleton-row` CSS rule** in `00_aspire_base.css` — backing for
  `skel_sync_overlay`.

### Changed

- **`aspire_grid` (`EDITABLE_GRID_OPTIONS`)** now includes
  `enterNavigatesVertically`, `enterNavigatesVerticallyAfterEdit`,
  `undoRedoCellEditing` — Excel-style Tab/Enter commit behaviour. Also
  explicitly notes in the docstring that **wrapping the grid in
  `dcc.Loading` is a footgun**: the spinner overlays on every
  cellClicked callback (even when the callback returns no_update),
  producing a 'screen reloads on click' visual flash. Use
  `skel_sync_overlay` as a sibling above the grid instead.

## [0.9.0] — 2026-05-20

### Changed

- **`components.py` split into a focused sub-package**: the 1,361-line
  single-file module is now `components/` with 6 submodules:
    nav            sidebar, topnav, header + active-link callbacks
    cards          card, summary_card, graph_card, info_box,
                   linear_step_card, file_upload_card, connect_user_chip
    kpi            kpi_tile, kpi_strip, kpi_tile_row, kpi_stat
    feedback       toast, badge, empty_state, loading_overlay,
                   status_pill, freshness_banner, confirm_modal
    inputs         toggle_group, filter_bar, dark_mode_toggle, aspire_tabs
    print_export   print_header, print_footer, export_buttons, send_export

  Backwards-compatible — every `from aspire_dash.components import X`
  keeps working via `components/__init__.py` re-exports. Direct
  submodule imports (`from aspire_dash.components.kpi import kpi_tile`)
  also supported for the more discriminating caller.

  Verified: aspire_dash 122/122 tests pass post-split, aspire-nutrition
  (downstream consumer) 237/237 tests pass against the new layout.

- Bumped `__version__` to 0.9.0 across `__init__.py` + `setup.py`.

## [0.8.0] — 2026-05-20

### Added

- **`tests/test_scaffold_e2e.py`** — end-to-end smoke for the scaffolder:
  runs `python -m aspire_dash new <name>`, AST-parses every generated
  `.py`, imports the app module, verifies modern components are used
  (`kpi_strip`, `skeletons`, `register_toast`, `truststore`), and (slow
  leg, gated on Playwright + Chrome) launches the scaffolded app in
  a subprocess and uses a real browser to verify the Home page renders
  with the KPI strip + callback-replaced content.
- Pytest `slow` marker registered in `pyproject.toml`.

### Changed

- **Deprecated `summary_card` + `stat_card`**: both now emit a
  `DeprecationWarning` pointing to `kpi_tile`. Aliases preserved
  through 0.x; will be removed at 1.0.
- Bumped `__version__` to 0.8.0 across `__init__.py` + `setup.py`.

### Fixed

- **Scaffolder template bugs caught by the e2e**: `MANIFEST`,
  `HOME_PY`, `REPORTS_PY`, `API_CLIENT_PY`, and `DEPLOY_SH` had
  doubled `{{}}` braces from a copy-paste of `.format()`-escape syntax
  even though those templates aren't `.format()`-ed. Result: invalid
  manifest.json, broken Home page callback (`Cannot read properties
  of undefined`). Replaced with proper single braces.

## [Unreleased]

### Added

- **`tests/`** — pytest suite covering import-smoke for every module,
  theme constants, all component-returning functions, observability
  counters, stats/timeseries helpers, time arithmetic, budget formatters,
  athlete picker, sports/viz/firstbeat renderers. **103 tests; ~1.2 s run.**
- **`.github/workflows/test.yml`** — CI matrix runs pytest on
  py3.10/3.11/3.12 + a separate `pip install .` smoke job on a fresh
  clone (catches `package_data` / wheel issues).
- **`__all__` lists** on the modules with stable public APIs:
  `observability`, `stats`, `timeseries`, `charts`, `layouts`.
  Larger modules (components, sports, athlete) intentionally deferred
  until the maintainer sets the contract.
- **README test-status badge.**

### Changed

- **`install_requires` now has upper bounds**: `dash>=2.14,<5`,
  `dash-bootstrap-components>=1.5,<3`, `plotly>=5.18,<7`,
  `pyyaml>=6.0,<7`, `dash-svg>=0.0.12,<1`. Prevents a silent break
  when downstream apps pip-install after a major release of any of
  these. Loosen when we've actually tested the new majors.
- **`extras_require={"test": [...]}`** — `pip install aspire_dash[test]`
  pulls pytest + numpy for downstream consumers who want to test
  against the live package.

## [0.6.0] — 2026-05-20

### Added

- **`aspire_dash.athlete`** — SAMS-style athlete picker, profile
  header, avatar, picker store wiring. Harvested from the nutrition
  + mapping apps so other dashboards don't reimplement the
  drill-down sport → roster → athlete pattern.
- **`aspire_dash.budget`** — currency / k / M / pct formatters,
  variance + utilisation cards, rollup chips. Harvested from the
  Aspire Budget FY26 report.
- **`aspire_dash.export`** — Excel + PDF download buttons,
  reportlab PDF builders, `send_pdf` helper. Harvested from the
  medical + budget reports.
- **`aspire_dash.tables`** — AG Grid presets (`aspire_grid`,
  `EDITABLE_GRID_OPTIONS`, dirty-tracking helper) so editable grids
  share one styling source.
- **`aspire_dash.time`** — period-mode dropdown filter,
  `period_mode_to_dates`, `sunday_of`/`monday_of`/`first_of_month`,
  `format_period_label`, `days_ago_chip_label`. Replaces the
  hand-rolled date-arithmetic in every app.
- **`aspire_dash.callbacks`** — reusable callback registrators:
  `register_period_filter`, `register_toast` + `dispatch_toast`,
  `register_pdf_download`, `register_url_active_nav`. Skip the 30-line
  boilerplate per app.
- **New components**: `status_pill`, `freshness_banner`, `kpi_stat`,
  `aspire_tabs`, `kpi_strip` (dict-driven one-liner).
- **Beefier scaffolder** (`python -m aspire_dash new <name>`):
  template now includes `kpi_strip`, skeleton-loaded card, working
  toast wiring, `api_client.py` with truststore + httpx,
  `.env.example`, `deploy.bat`/`deploy.sh`, and a real README.

### Notes
- All modules expose their public API via `from aspire_dash.X import …`
- `__main__.py` is now editable in one place — every Aspire app spun
  up from this version onwards inherits the same conventions.

## [0.5.0] — 2026-05-20

### Added

- **`aspire_dash.theme.band_color(band, as_hex=False)`** — shared map
  for the in/below/above classification used by KPI tiles + clinical
  reports. Also exports `BAND_BS` (bootstrap class) + `BAND_HEX`.
- **`aspire_dash.components.kpi_tile`** — generic KPI card with the
  Aspire signature: uppercase label, big value, unit subtitle,
  left-color accent stripe, optional vs-target progress bar.
- **`aspire_dash.components.kpi_tile_row`** — render a row from a
  spec list, optionally driven by `target_by_key`.
- **`aspire_dash.cache_prewarm.cache_prewarm(name, fns)`** —
  fire-and-forget daemon-thread warmer for TTL caches. Idempotent
  within a process. Used by the nutrition app on Dash boot so the
  SAMS picker is instant after a redeploy.

## [0.4.0] — 2026-05-19

### Added

- **`aspire_dash.skeletons`** — shimmer-loading placeholders.
  Primitives: `skel_line`, `skel_pill`, `skel_circle`, `skel_card`,
  `skel_tile`, `skel_row`. Composites: `skel_table_rows`,
  `skel_metric_tiles`, `skel_card_grid`, `skel_avatar_list`,
  `skel_kpi_strip`. CSS in `assets/02_aspire_skeletons.css`
  auto-copied by `setup_app`.

## [0.3.0] — 2026-05

### Added

- Initial public release with `sidebar`, `topnav`, `header`, `card`,
  `summary_card`, `toast`, `badge`, `empty_state`, `loading_overlay`,
  `dark_mode_toggle`, `filter_bar`, sports helpers (flags, badges,
  placement), `viz` (rings, sparklines), `firstbeat` (ACWR), and the
  CLI scaffolder.
