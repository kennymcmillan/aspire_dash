# Changelog

All notable changes to `aspire_dash`. The library follows
[Semantic Versioning](https://semver.org/) within the 0.x line —
additive minors, breaking changes get a major bump when we get there.

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
