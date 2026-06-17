# Changelog

All notable changes to `aspire_dash`. The library follows
[Semantic Versioning](https://semver.org/) within the 0.x line —
additive minors, breaking changes get a major bump when we get there.

## [0.65.0] — 2026-06-17

### Added

- **Shared maturation / growth colour rules** in `anthropometric` (matched to the
  Power BI Development Testing Dashboard): `mat_status_colour`, `pah_colour`,
  `growth_colour`, `weight_change_colour` + `MAT_COLOUR_{GREEN,AMBER,RED}` /
  `GROWTH_RED_CM` (7.5) / `WEIGHT_RED_KG` (9). Circa-PHV / 90–95.99 %PAH = red
  (peak height velocity); ≥96 green; 85–89.99 amber; Pre-PHV / sub-threshold →
  none. So every app shades maturation status, %PAH, 12-mo growth and 12-mo
  weight change identically.

## [0.64.0] — 2026-06-17

### Changed

- **`aspire_datatable` now centres values by default, with the first column
  (name / label) left-aligned** — the Aspire table convention. Headers match
  (centre, first-column left). Callers left-align a different column (e.g. when
  column 0 is a rank `#`) by appending a `style_cell_conditional` rule.
- **`style_overrides` conditional lists now APPEND to the defaults** instead of
  replacing them — so passing `style_data_conditional` no longer silently drops
  the zebra-row striping / totals-row styling (latent bug), and
  `style_cell_conditional` adds to the default alignment.
- **`aspire_datatable` `filter_` now defaults to `False`** — the native filter
  row (input boxes under the headers) is off unless a table opts in. Cleaner
  default; pass `filter_=True` to restore it.

### Fixed

- **DataTable column-header text vanished on hover** — `th:hover` lightened the
  header to `#eef2f7` while the header text is white (blue header), so labels
  disappeared. Hover now darkens to `#003566`, keeping the text readable.

## [0.63.1] — 2026-06-16

### Fixed

- **`trend_rich` hover text was invisible** — `hoverlabel` set `bgcolor="white"`
  with no font colour, so the tooltip text rendered white-on-white. Set
  `font_color="#0f172a"`.
- **`trend_rich` zone labels now sit OUTSIDE the plot** in the right margin
  (xref=paper, coloured per zone) instead of overlapping the data at the right
  edge; the right margin widens to ~88px when `zones` are present.

## [0.63.0] — 2026-06-16

### Fixed

- **`sports.data_table` is now responsive** — a wide table (many columns) used to
  *shrink-to-fit* on a narrow viewport, cramming 10 columns into "Ve/D/SE/W/G…"
  with every cell ellipsis-truncated (shipped broken in 0.60-0.62; caught on the
  live Fencing Reports app at laptop+sidebar / tablet / mobile widths). The
  builder now gives the table a `min-width` (sum of per-column minimums) and
  wraps it in a `.aspire-data-table-scroll` horizontal-scroll container, so
  narrow screens **scroll** instead of truncating. **Note: the return is now a
  scroll wrapper around the `.aspire-data-table` div** (one extra nesting level).
  Verified with desktop + tablet + mobile screenshots. +3 tests (14 total).

## [0.62.0] — 2026-06-16

### Fixed (fleet-wide hardening)
- **`setup_app()` now eagerly registers the optional component libs** that
  aspire_dash lazy-imports inside helpers (`dash_ag_grid` in tables/v12_helpers,
  `dash_svg` in viz). Dash 4.x raises `ImportedInsideCallbackError` when a
  component library is FIRST imported during a callback — so any app that builds
  a grid/svg *inside a callback* (first-touch) would crash on Dash 4.x. Importing
  them at setup time (startup, before any callback) fixes every consumer app at
  once; guarded so a missing optional dep doesn't break `setup_app`. Surfaced by
  the component-showcase demo on Dash 4.1.0.

## [0.61.2] — 2026-06-15

### Fixed
- Scaffolder (`aspire-dash new`): generated `deploy.sh` / `deploy.bat` / README used
  `--entrypoint app.app`, which Connect reads as a package path (`app/app.py`) and
  rejects for the flat `app.py` the scaffold creates. Now emits the correct
  `--entrypoint app:app`. (Cost two failed deploys before diagnosis on padel_scout.)
- **`aspire_dash new` scaffold `.gitignore` now uses an allowlist** instead of a
  brittle named denylist. `setup_app()` copies the whole shared asset tree
  (CSS, logo, `brand/**`, JS, `body-bodymap.svg`, …) into `assets/` on every
  boot; the old template only ignored 6 files, so `brand/**` and any
  library-added asset got committed and produced version churn that never
  reflected runtime (Connect regenerates from the pinned library). Template is
  now `assets/*` + `!assets/10_app.css` — only app-owned assets are tracked.

## [0.61.0] — 2026-06-15

### Added (promoted from the Fencing Reports migration)

- **`sports.data_table` gains `row_class=callable(i, row) -> str`** — apply extra
  class(es) per row (e.g. `"is-dim"` to fade a competition whose report isn't
  available yet). New CSS `.aspire-data-row.is-dim { opacity: 0.6 }`. Also
  formalises the `wrap` (multi-line cell) + float `grow` column options added
  for the fencer-search table.

## [0.60.0] — 2026-06-15

### Added (promoted from the Fencing Reports migration)

- **`sports.data_table(columns, rows, *, highlight=…)`** — assembles a hover/
  highlight data grid from the existing `.aspire-data-row` family, with
  per-column alignment + width and an optional focus-row predicate. Replaces the
  hand-rolled `html.Div` tables (with an inline `style={}` on every header/cell)
  and the brittle `div[style*="borderRadius: 8px"]` CSS selectors in the sport
  report apps. Composes the same classes as the existing `sports.data_row()`
  primitive. New CSS: `.aspire-data-table` card-like wrapper in `00_aspire_base.css`.

### Fixed

- **`kpi_tile` / `kpi_strip` no longer crash on non-numeric values.** The value
  was unconditionally formatted with `f"{value:,.0f}"`, so any string (a rank,
  country, week label, "sweet spot") or decimal passed as text raised
  `ValueError: Unknown format code 'f' for object of type 'str'` at render. Now
  numbers are thousands-grouped as before and pre-formatted strings render
  verbatim. Surfaced by the aspire-squash-pulse ranking/Firstbeat cards.

## [0.59.0] — 2026-06-15

### Added (promoted from the Table Tennis Player Career report)

- **`sports.rank_pill(rank)`** — world/leaderboard rank pill: gold for top-10,
  blue for top-50, grey beyond, em-dash for missing (None/NaN/NA). Distinct from
  `placement_badge` (event podium, where 1/2/3 are the medals) — this is for a
  *world ranking* number. CSS: `.rank-pill .rank-top10/.rank-top50/.rank-other/
  .rank-na` in `00_aspire_base.css`, styled to match the placement-badge family.

## [0.58.0] — 2026-06-15

### Added (promoted from DASH_Vyntus)

- **`sports_science.lactate_curve(..., markers=)`** — optional threshold-speed
  vertical guides: a list of `(speed, label, color)` (LT1/LT2/FBLC/Dmax computed
  elsewhere) drawn as dashed vlines with top labels. Saves apps hand-adding
  `add_vline` after the curve.
- **`components.print_export.identity_columns(athlete, test_date)`** +
  **`identity_filename_slug(athlete, suffix)`** — stamp SAMS identity
  (Player_ID/MRN/Athlete/Sport/DOB/Age/Test_Date) on every exported row and name
  the file after the athlete (companions to `send_export`). Every picker-stamped
  export re-rolled these.

## [0.57.0] — 2026-06-11

### Added

- **`aspire_dash.sports_science.lactate_curve`** — incremental step-test
  chart: speed (x) vs blood lactate (left y) and heart rate (right y,
  dashed), one curve per test date, click a legend date to toggle both
  its lactate + HR lines (shared legendgroup). Latest test boldest with a
  soft fill; **large white-bordered circular points**; **no zone bands**;
  emphasised LT2 (4 mmol) guide line. Returns `dcc.Graph` (or the
  `go.Figure` with `as_graph=False`). First consumer: endurance /physiology.

### Changed

- **`rotating_stat` glow-up (v0.57)** — gradient panel + gradient accent
  rail + radial watermark, bigger value (size-scaled), delta as a pill chip
  ("▲ +1.4 vs last"), inline unit, active-dot highlight. New `size=`
  arg ('sm'/'md'/'lg') caps width so it reads as a solid panel, not a thin
  column or full-bleed stripe. CSS-only; back-compatible API.

## [0.56.0] — 2026-06-11

### Added

- **`aspire_dash.v12_helpers.rotating_stat`** — auto-cycling KPI card:
  flips through 2-6 metric faces with a pure-CSS 3D rotateX (no
  callbacks/intervals), pauses on hover, honours prefers-reduced-motion.
  CSS: `.rotating-stat` block in `00_aspire_base.css` (keyframes
  `rs-cycle-2..6`, visible window = 1/N of the loop). First consumer:
  endurance-dashboard physiology page (lactate markers: vVO2max,
  LT2 @4mmol, LT1, Peak VO2, La max).

## [0.55.0] — 2026-06-11

### Added — `viz.ref_band_grid` (reference-band heatmap grid)

Compact entity × metric heatmap, optionally grouped — a whole-squad at-a-glance
scan. Promoted from `development_dashboard`. Domain-agnostic: the **caller**
computes each cell's band colour (ref ranges, percentiles, z-scores, RAG), the
library renders a sticky-first-column grid with group header rows + a swatch
legend. `.heat-*` classes added to `00_aspire_base.css` (sticky athlete column,
hover zoom, navy group rows). Only data-driven cell colours stay inline.

## [0.54.0] — 2026-06-11

### Added — `report.trend_rich` polish: zone shading + PB markers

- `zones=[{y0,y1,label,color}, …]` — shaded horizontal bands with edge labels
  (the "wow" layer for maturation/load charts). Ships `report.PHV_ZONES`
  (Pre/Approaching/Circa/Post-PHV at 85/90/95.1) for %-predicted-adult-height
  trends. Bands render `layer="below"` at 7% opacity.
- `pb_mask=<per-point bool>` — gold ★ markers on personal-best points.
- (When `zones` set, the area fill is dropped so the bands read cleanly.)

## [0.53.0] — 2026-06-11

### Added — `report` module: PBI-style report shell + rich-hover trend

Promoted from `development_dashboard` (the Power BI report port). For apps that
port/replicate a Power BI report layout:

```python
from aspire_dash.report import (report_page, report_band, athlete_rail,
                                report_card, report_grid, trend_rich)
```

- `report_page(title, content, rail=, subtitle=)` — navy title band (Aspire logo,
  gold underline) + optional left rail + content. CSS: `.report-band`,
  `.report-body`, `.report-rail`, `.report-content` in `00_aspire_base.css`.
- `athlete_rail(photo_el, *controls, labels=)` — PBI slicer column (photo +
  labelled pickers).
- `report_card(label, value, sub=, accent=)` — PBI value card (uppercase label,
  big tabular value, top accent stripe). `.report-card`.
- `report_grid(items, cols=2|3|4|6)` — responsive grid (`.report-grid-N`,
  collapses 2-col on tablet, 1-col on phones).
- `trend_rich(dates, values, unit, color=, context=, reverse=, band_lines=)` —
  spline trend, branded area fill, and a **rich hover** where `context=
  {label: series}` adds athlete-state lines to the tooltip (the PBI custom-
  tooltip pattern, e.g. maturation status + height at each test). `reverse=True`
  for lower-is-better metrics; `band_lines` for PHV-style reference thresholds.

All styling is semantic classes (no inline styles) per the v0.45–0.48 rule.

## [0.52.0] — 2026-06-11

### Added — `sports.match_card()` (head-to-head result card)

Ported from the **SAMS** web app's `.match-card` (recon 2026-06-11) and
re-branded to Aspire navy/gold + Poppins. Sport-agnostic scoreline card for
TT / squash / padel / fencing / tennis report apps — the one card pattern SAMS
had that the library lacked.

```python
from aspire_dash.sports import match_card
match_card(
    {"name": "Abdulla Al-Tamimi", "country": "QAT", "sets": [11,9,11,11], "total": 3},
    {"name": "Mohamed Samir",     "country": "EGY", "sets": [8,11,7,9],   "total": 1},
    title="Qatar Squash Open 2026",
    meta=[("fa-solid fa-location-dot", "Doha"), "Quarter-Final"],
    tags=["PSA World Tour", "2026-03-14"],
)
```

- **Outcome inferred** from totals (win = emerald left-accent + score, loss =
  red, else Aspire-navy); override with `outcome=`/`score=`.
- **Per-set winner shading** computed automatically (focus set > opponent set
  → bold). `focus` competitor is bolded with a brand accent.
- Avatar = photo if `photo=` given, else navy initials chip; inline flag emoji
  from IOC/ISO code (`_flag_emoji`). Dark-mode rules included.
- New semantic classes in `00_aspire_base.css` (`.match-card`, `__header`,
  `__score`, `__players`, `__player`, `__sets`, `__set.is-won`, `__total`,
  `__outcome`, `__tag`; `.is-win/.is-loss/.is-neutral`). No inline styles.
- Ships `assets/no-image-player.png` (SAMS athlete-photo fallback).
- Forge prototype `tools/forge/match_card.html`; 5 pytest cases
  (`tests/test_match_card.py`).

## [0.51.0] — 2026-06-11

### Changed — all library athlete-card photos lazy-load by default

The five photo-rendering avatars (`athlete_card`, `athlete_card_rings`,
`athlete_card_v2`, `athlete_card_compact` in v12_helpers + `athlete_avatar`
in athlete.py) now render via `lazy_img` — every app using library cards
gets viewport-deferred SAMS photo loading with ZERO app changes.
WHOOP-dashboard validated the pattern (v0.50.0) before this default flip.

- `lazy_photos.js` gains a `beforeprint` handler: printing force-loads any
  still-deferred photos so print/PDF output never shows placeholders.
- Initials fallbacks unchanged; only the photo path defers.

## [0.50.0] — 2026-06-10

### Added — lazy_img: lazy-loading athlete photos

`v12_helpers.lazy_img(src, alt=, className=, style=, placeholder=)` — an
`html.Img` that fetches only when scrolled near the viewport. Dash 4.1's
`html.Img` rejects the native `loading="lazy"` prop, so this renders the
photo URL as `data-src` (legal wildcard prop) and the new shipped
`assets/lazy_photos.js` (IntersectionObserver, 300px root margin, with a
MutationObserver for Dash client-side re-renders) swaps it into `src`.
1×1 transparent gif placeholder avoids the broken-image flash.

Use for athlete-photo grids: 36 SAMS blob fetches on page load become only
the visible handful. First consumer: whoop_coach_dashboard.

## [0.49.0] — 2026-06-10

### Added — responsive sidebar: off-canvas drawer below 1024px (phones + iPads)

Sidebar apps finally work on phones and iPad portrait. Breakpoint design:
**≥1024px** (desktop + iPad landscape) keeps the fixed sidebar and the
existing collapse toggle, unchanged. **<1024px** (phones + iPad portrait)
the sidebar becomes an off-canvas drawer: hamburger opens it OVER the
content with a dimmed backdrop; backdrop tap / nav-link tap / Escape /
rotating past the breakpoint all close it.

- Was: `display:none` under 768px — **no navigation at all on phones**;
  iPad portrait lost 220px of an 810px screen to the fixed bar.
- `sidebar_toggle.js` grew a `matchMedia('(max-width:1023px)')` branch;
  the backdrop element is JS-injected — zero consumer-app changes needed,
  `setup_app()` ships both files on next redeploy.
- New classes: `.sidebar-mobile-open`, `.sidebar-backdrop` (+ `.is-visible`).
- `.page-content pre { max-width:100%; overflow-x:auto }` — code blocks
  scroll in their own box instead of widening the page.
- Demo home + layouts pages made wrap-friendly at phone widths.
- R4 smoke (390 / 810 / 1280): drawer open/close via hamburger, backdrop,
  nav-tap and Escape verified; desktop collapse regression-checked; zero
  horizontal overflow on the smoke path.

## [0.48.1] — 2026-06-10

### Fixed — pandas/numpy declared as runtime deps

`stats.py` (new in 0.48.0) and `timeseries.py` import numpy/pandas at
module level, but neither was in `install_requires` — a fresh
`pip install aspire_dash` crashed on `from aspire_dash.stats import …`
(caught by the CI fresh-clone import smoke). pandas (which pulls numpy)
is now a declared dependency; the `test` extra carries it too so the
pytest jobs stop relying on the runner's hand-picked list.

## [0.48.0] — 2026-06-10

### Changed — v12_helpers residual glow-up (forge loop, slice 4 of 4 — DONE)

The module was already class-first; this ports the stragglers. APIs
unchanged. Completes the 4-module legacy inline-style sweep
(sports → viz → anthropometric → v12_helpers).

- **`.card-link`** — one generic link-wrapper class replaces 4 copies of
  `{"textDecoration": "none", "color": "inherit"}` across athlete_card /
  athlete_card_rings / athlete_card_v2 / athlete_card_compact.
- **`.amc-avatar`** (+`--md`, `--initials`) — the photo-or-initials avatar
  was duplicated verbatim in two cards (40px / 44px); now one family.
- **`metric_ring`** — `.metric-ring__*` structure; ring size + tone-driven
  value colour stay inline. `.amc-body` / `.amc-rings` for the card layout.
- `date_toolbar` calendar icon styled via `.dt-display i` rule.
- 4 new class-contract tests (tests/test_v12_glowup.py).

Genuinely data-driven inline styles are KEPT by design throughout the
module: delta/trend colours, progress-stack segment widths, tracker cell
colours, graph heights, asymmetry bar widths, glass-card padding.

### Fixed

- `.amc-rings` now wraps (`flex-wrap`) — ring rows no longer overflow
  athlete cards on narrow screens.
- Demo `/v12` page: fixed `repeat(N, 1fr)` grids → `repeat(auto-fit,
  minmax(220px, 1fr))`; standalone metric_ring row wraps; AG Grid example
  wrapped in an overflow-x container; repaired mojibake in section headers.
- KNOWN (pre-existing, demo-only): AG Grid's absolutely-positioned header
  containers still inflate `document.scrollWidth` by ~112px at a 390px
  viewport on `/v12`. Grid scrolls correctly inside its own box; needs its
  own investigation before any blanket `.ag-*` CSS (16 consumer apps).

## [0.47.0] — 2026-06-10

### Changed — anthropometric.py glow-up (forge loop, slice 3 of 4)

The 3 HTML-rendering components ported to semantic classes (v0.47 CSS
section); Plotly figures (somatochart, growth_chart, zscore_radar_figure)
and iframe SVGs (skinfold_silhouette, body_fat_gauge) untouched. APIs
unchanged.

- `athlete_snapshot_card` — `.snapshot-card__*` family; last row drops its
  divider; navy header band tokenised.
- `limb_symmetry_bar` — `.limb-sym` with tone modifiers `.sym-good/warn/
  danger` cascading both the % text colour AND the track border from one
  class; bar widths stay inline (data-driven).
- `zscore_heatmap` — `.zscore-table__*` family (sticky measure column,
  group banners, mean/SD stat cells, legend bar); the 7-bucket z-cell
  colour stays inline (computed per z-score by `z_score_color`).
- New `tests/test_anthropometric.py` (3 class-contract tests — module
  previously had zero test coverage).

## [0.46.0] — 2026-06-10

### Changed — viz.py glow-up (forge loop, slice 2 of 4)

7 components in `aspire_dash.viz` ported from inline `style={}` to semantic
classes (v0.46 CSS section). SVG geometry (ring size, stroke, computed
offsets, bar %) stays inline by design. Public APIs unchanged.

- `progress_ring`/`status_ring`/`ring_row` — `.viz-ring` family; centre value
  gains tabular-nums; label uses the eyebrow tokens.
- `horizontal_bar` — `.viz-hbar` family; pct text gains tabular-nums.
- `ranked_bars` — `.ranked-bars__*` rows now hover-tint + fills animate
  (0.25s width transition).
- `metric_spark` — `.metric-spark` card: slate-tinted shadow + hover lift,
  matching `.gradient-stat` / `.card` behaviour.
- `status_dot` — `.viz-dot` structure; pulse classes compose (`viz-dot
  pulse-red`), size/colour stay inline.
- `sparkline` — `.viz-sparkline` wrapper.
- Dark-mode rules for metric-spark, ring values, ranked-bars, hbar tracks.
- 5 new class-contract tests. `body_fat_gauge` untouched (iframe-isolated SVG).

### Fixed

- Mojibake repair: the v0.45 + v0.46 CSS section comments were appended with
  a wrong codepage (`â€”` artifacts); file tail rebuilt as clean UTF-8.
  Selectors were never affected.

## [0.45.0] — 2026-06-10

### Changed — sports.py glow-up (forge loop, slice 1 of 4)

All 12 visual components in `aspire_dash.sports` ported from inline `style={}`
dicts to semantic classes in `00_aspire_base.css` (v0.45 section). Public APIs
unchanged — consumer apps inherit the upgrade on SHA bump, zero code changes.

- `placement_badge` — medal treatment: gold/silver/bronze get 135deg gradients
  + inset 1px ring; **bronze corrected from red-tint (#fef2f2) to true bronze
  (orange-800 on #ffedd5→#fed7aa)**. Classes `.placement-badge` +
  `.place-{gold,silver,bronze,top8,top16,rest}` + `--sm`.
- `data_row` — `.aspire-data-row`: hover tint (slate-50), header rows now
  11px caps + letter-spacing, last cell drops its right border, dark-mode rules.
- `competition_card` — `.competition-card__*` family; placement number tones
  via `.place-1/2/3/n`; link wrapper class. Inherits `.card` hover lift.
- `gradient_stat_card` — `.gradient-stat` structure + hover lift; caller bg /
  value colour stay inline (data-driven by API contract).
- `country_flag` / `flag_with_name` — `.flag-chip` (+`--sm/md/lg`),
  `.flag-name` + `.is-highlight`; AIN fallback pill class.
- `rank_change` / `trend_arrow` — `.rank-change .rc-{up,down,flat}` /
  `.trend-arrow .ta-{up,down,flat}` + tabular-nums.
- `mini_stat` / `header_stat` — class-based, eyebrow letter-spacing tokens.
- `color_badge` / `source_badge` — `.pill-badge` (+`--source`) structure;
  federation colours stay inline (data-driven from SOURCE_BADGE_COLORS).
- `competition_badge` / `category_badge` wrappers — `.badge-row`.
- 7 new regression tests pin the class contract
  (tests/test_sports_viz_firstbeat.py). Demo /sports page now also shows
  source_badge, competition_card, data_row, mini/header stats, trend_arrow.
- Forge record: `tools/forge/index.html#sports-glowup` (BEFORE/AFTER medals).

Deprecated `stat_card` intentionally NOT ported (removed at 1.0).

## [0.44.1] — 2026-06-10

### Fixed — sidebar shell no longer overflows on narrow screens

`.main-area` is a flex item but couldn't shrink below content width, so wide
DataTables/charts forced horizontal page overflow on phone/tablet widths
(894px at a 390px viewport) despite the mobile sidebar-hide media query.
Added `min-width: 0` in both `layouts.py` (inline) and the `.main-area` CSS
rule. Zero desktop impact. Surfaced by aspire-supplements' overflow test.

(Entry re-written from commit 8eae018's message after a checkout collision
ate the original uncommitted text.)

## [0.44.0] — 2026-06-10

### Added — ranked bars + editable-table diff (promoted from aspire-supplements)

- `viz.ranked_bars(items, *, color=None, unit="", max_label=34, max_rows=None,
  sort=False, height=14, value_fmt=None)` — a branded horizontal "top-N by
  value" leaderboard (label · rounded track · actual value), pure HTML/CSS, no
  Plotly. Fills the gap between `horizontal_bar` (single bar, % only, clamped
  label) and `progress_stack` (one segmented bar). Takes `(label, value)`
  tuples or dicts with an optional per-row `color`; can sort + cap. Generic —
  top products, athletes by load, spend by sport, etc.
- `tables.diff_rows(original, current, *, id_key="id", fields=None)` — diff the
  rows an editable table started with against the rows it holds now; returns
  `{updated: [(id, {field: val})], deleted: [id], added: [row]}`. Handles
  in-place edits, deleted rows (`row_deletable=True`), and new rows; compares as
  strings so `5 == "5"`. Pure (no Dash/AG-Grid dep) — collapses the repeated
  "compare-and-save edits" boilerplate every editable-grid app writes.

First consumer: the aspire-supplements dashboard (Top products / Assignments-by-
sport / Stock-by-category bars) and its products/receipts/assignments save flows.

## [0.43.0] — 2026-06-08

### Added — nutrition macro chips + summary (promoted from aspire-nutrition)

In `aspire_dash.nutrition` (alongside `macro_tile` / `macro_strip`):

- `macro_chips(carbs, protein, fat, kcal=None, *, per="100 g", empty=...)` —
  coloured C / P / F pills + kcal as an `html.Div` flex row, for showing a
  food's macro shape inline (a match-picker option, a diary row, a supplement
  panel). Chip colours match the analysis macro palette (carbs amber / protein
  blue / fat red) so a macro means the same colour everywhere.
- `macro_summary(carbs, protein, fat, kcal=None)` — compact
  `'C28 P7 F1 · 365 kcal'` string; skips unknown macros.

Both are pure (take explicit numbers, not a row dict) so they're data-source
agnostic. First consumer: the aspire-nutrition 24h-recall match picker.

## [0.42.0] — 2026-06-04

### Added — wearable recall panels (pair with aspire_data 0.4.0)

Promoted from the `aspire-nutrition` consultation module. Pure renderers that
take a summary dict (so the UI lib stays data-source-agnostic):

- `aspire_dash.whoop.recovery_panel(whoop_summary)` — WHOOP recovery ring +
  today KPIs + 7-day sparkline trends + 14-day recovery-zone tracker + sleep
  stages. `recovery_zone_color()` helper.
- `aspire_dash.firstbeat.load_recall_panel(firstbeat_summary)` — last-7-day
  sessions / duration / energy / TRIMP load / aerobic-TE intensity / ACWR
  + 14-day load sparkline (complements the existing session-level
  `training_card` / `acwr_badge` / `zone_bars`).

Feed both from `aspire_data.whoop.whoop_summary` / `firstbeat.firstbeat_summary`.

## [0.41.0] — 2026-06-04

### Hardened — `export.pdf_export` table rendering (printing robustness)

- **Cells now wrap.** Table cells are rendered as `Paragraph`s, so long values
  (full measurement labels, long event names, multi-part somatotype strings)
  **wrap within the column instead of clipping/overlapping** — the main
  "reports printing" failure mode.
- **XML-safe.** Cell text is escaped, so a value containing `<`, `>` or `&` (an
  athlete name, a note) no longer raises a reportlab parse error mid-render.
- Header (white bold on blue + gold underline), zebra rows, first-column bold,
  `emphasize_last_col` (green), `totals_row` (navy) and `highlight` (cream) are
  all preserved — moved onto paragraph styles where needed.
- Known limitation: Arabic/RTL glyphs still render as boxes (Helvetica has no
  Arabic coverage) — registering a Noto Sans Arabic TTF is a future enhancement.

## [0.40.0] — 2026-06-04

### Upgraded — `export.pdf_export` (exceptional PDFs, all additive)

The branded reportlab PDF builder gained four new, backward-compatible section
types plus per-page polish — every app's PDFs level up just by bumping the lib.
Existing `{heading, table, paragraphs, totals_row, highlight}` sections are
unchanged.

- **KPI band** — `{"kpis": [{"label","value","unit","sub"}, ...]}` renders a row
  of metric cards (navy left-rule, big navy value, unit + sub) matching the
  on-screen KPI strip.
- **Callout / insight box** — `{"callout": {"label","items":[...]}}` (or a bare
  list) → tinted blue box with a blue left-border.
- **Side-by-side columns** — `{"columns": [section_a, section_b]}` lays two
  table/paragraph sections across the page width (great on landscape; also used
  for Snapshot+Bilateral).
- **`emphasize_last_col`** on a table section → bold green last column (e.g. a
  "Result" column).
- **Page-numbered footer on every page** — gold rule + generated stamp +
  `Page X of Y` via a two-pass `NumberedCanvas`.
- **Gold underline** under every table's blue header row.

First consumer: `DASH_Anthro` (Individual / Longitudinal / Squad / Ruwwad
reports). Requires `reportlab` in the app's `requirements.txt` (unchanged —
still an optional extra of `aspire_dash`).

## [0.39.0] — 2026-05-29

### Redesigned — `athlete_id_card` (C-style premium glass)

User feedback after v0.37 / v0.38: the multi-pill layout felt squashed
and the inline "TARGET" text duplicated the visual gold-ring cue.
Iterated through 3 design directions + sub-variants in
`tools/forge/athlete_card_v2.html`. Locked in direction C (premium
glass) with refinements.

**Markup changes:**
- Photo gets a **corner star badge** for target athletes (gold circle
  with white star). Replaces the inline "TARGET" text badge entirely.
- **One combined Sport · Event pill** (blue) instead of two separate
  SPORT / EVENT pills.
- Identity line is now **text, not pills** — `DOB 2010-01-21 · SAMS
  2940 · 16.1 yrs` in slate-600 with subtle label spans and an emerald
  age span. Tabular-nums for stable width.
- **MRN dropped** — SAMS player_id is the durable identifier across
  Aspire systems; MRN was redundant on this card.
- Name colour changed to **Aspire navy** (`#004185`) — was slate-900.
- Background is now a **radial gradient** tinted sky-blue (default) or
  amber (target), recedes to white. Matches the premium-glass
  aesthetic prototyped in the forge.

**CSS** in `aspire_dash/assets/00_aspire_base.css`:
- `.athlete-id-card`, `.is-target`, `.is-empty` — see above.
- New BEM children: `__photo-wrap`, `__target-star`,
  `__sport-pill`, `__identity`, `__identity-label`, `__identity-sep`,
  `__identity-age`.
- Removed: `__photo-stack`, `__age`, `__target-badge`,
  `__pills-row`, `__pill.pill-{sport,event,identity}`.

**Python API** in `aspire_dash.athlete.athlete_id_card(data)`:
- Same input contract — `data` dict with `player_id`, `full_name`,
  `photo_url`, `sport`, `target_event`, `date_of_birth`, `is_target`,
  `pathway`.
- `mrn` is now ignored (was rendered in v0.37/0.38).

**Tests:** 22 covering full payload, empty state, target/non-target
styling, pathway fallback, sport-pill behaviour (combined / sport-only
/ absent), photo fallback, decimal age, fractional-age robustness.

Apps consuming v0.37/0.38 should pull v0.39 to pick up the redesign —
breaking only if they relied on `.pill-event` / `.pill-identity`
class names or the inline TARGET badge in custom CSS.

## [0.38.0] — 2026-05-26

### Polish — `athlete_id_card` v2

User feedback after the v0.37 launch: card looked squashed when placed in
a constrained-width container, and the photo / body / age columns didn't
line up cleanly. Iteration via the forge sandbox.

Changes to `.athlete-id-card` CSS in `assets/00_aspire_base.css`:

- `align-items: stretch` → `flex-start`. Photo, body, and any future
  right-side actions now top-align to a predictable baseline rather
  than stretching unevenly.
- Padding 16/18 → **20/24**; min-height **96px** floor so short content
  (one sport pill only) doesn't collapse.
- Photo bumped 56 → **64px** with stronger shadow for visual weight.
- Photo-stack column locked to **72px** width so the age badge under
  the photo stays centred regardless of pill row width.
- Body uses `gap: 10px` for even rhythm (was `margin-bottom: 8px` then
  inconsistent row gaps). Removed `justify-content: center` — content
  flows naturally top-down.
- Name bumped 16 → **17px**; pill rows gap 4 → 6px; pill internal
  padding 3/10 → 4/11.
- Age badge softened (emerald-50 / 200 instead of 100 / 300) so the
  name remains the visual hero. Tabular-nums for stable width.
- Target athletes get a slightly stronger photo shadow (gold tint).
- New `@media (max-width: 520px)` rule — photo + age stack horizontally
  with body wrapping below, for narrow containers.

No Python API changes. Apps consuming v0.37 pick up the polish on next
SHA bump with zero code edits.

### Added — `register_athlete_banner(extra_actions=...)`

- `register_athlete_banner`: new `extra_actions=` slot (Component OR
  callable returning Component) for consumer action buttons (Change /
  Clear pattern in aspire-nutrition). Rendered beneath the card and
  beneath the missing-MRN warning, wrapped in a flex row so consumers
  don't repeat the styling. Defaults to `None` — backwards-compatible
  with v0.37 callers (DOM unchanged).
- Demo: `/athlete` page now shows a static-actions and a per-athlete
  callable example with a mock store + banner.

## [0.37.0] — 2026-05-25

### Added — `athlete_id_card` (promoted from DASH_Anthro)

**New in `aspire_dash.athlete`:**

- `athlete_id_card(data)` — picker-confirmation identity strip for the
  top of any capture / single-athlete page. Photo + name + optional
  TARGET badge + 2 rows of pills (sport/event categorical above,
  dob/mrn/sams identity below) + decimal age under the photo. Gold ring
  + amber accent on Target-pathway athletes (`is_target=True` or
  `pathway=="Target"`), sky-blue otherwise. Empty payload renders the
  amber "no athlete picked" prompt. Pure data → component, no callbacks.

**New in `aspire_dash/assets/00_aspire_base.css`:**

- `.athlete-id-card` + `.is-target` / `.is-empty` modifiers + `__photo`
  / `__photo-fallback` / `__age` / `__name` / `__target-badge` /
  `__pills-row` / `__pill.pill-{sport,event,identity}` BEM children.
  Brand: sky-200/400 ring + sky→white gradient default, amber-300/500
  ring + amber→white gradient for target athletes. Designed in the
  forge sandbox (`tools/forge/index.html#athlete-identity`).

Replaces ~150 lines of inline-styled chip code in DASH_Anthro 1.x.
Drop-in for any picker-driven app — nutrition / medical / squash
dashboard / VBT / squad readiness all benefit.

### Added — 5 patterns promoted from aspire-nutrition

Single-session haul of 5 components that emerged twice (or more) inside
aspire-nutrition's diary + consultation flows. All purely additive —
shared definitions land here, the original helpers in nutrition will be
replaced by these in a follow-up.

- **`linear_step_card_collapse(*, step, title, body, collapse_id=None,
  summary_id=None, initial_open=False, header_type="linear-step-header")`**
  in `aspire_dash.components.cards`.
  Numbered, collapsible step card with click-the-header toggle, summary
  span filled by consumer's state callback, and a chevron that rotates
  when open. Replaces the duplicate `_step_card` (diary.py) +
  `_section_card` (consultation.py) helpers in aspire-nutrition.
  Supports two integration modes:
    - **Mode A — string `collapse_id`**: consumer owns the toggle
      callback (diary-style, custom open/close policy).
    - **Mode B — pattern-matched (default)**: pair with
      `register_linear_step_toggle(app)` for one-call click-to-toggle.

- **`register_linear_step_toggle(app, *, header_type="linear-step-header")`**
  in `aspire_dash.components.cards`. The MATCH-pattern callback wiring
  helper for mode B. Call once per `header_type`. The consultation page
  pattern (`{"type": "consultation-section-header", "n": N}` →
  `{"type": "consultation-section-collapse", "n": N}`) is now one line:
  `register_linear_step_toggle(app, header_type="consultation-section-header")`.

- **`selected_athlete_banner(store_id="athlete-store",
  banner_id="selected-athlete-banner")`** + **`register_athlete_banner(app,
  *, store_id="athlete-store", banner_id=...,
  on_missing_mrn_warn=True)`** in `aspire_dash.athlete`.
  Persistent page-top athlete card that lives OUTSIDE any step collapse
  so the athlete stays visible after the picker step auto-collapses.
  Gates on `player_id`, NOT `mrn` (SAMS can return players whose MRN
  isn't linked yet), and surfaces a missing-MRN warning inline when
  `on_missing_mrn_warn=True`. Re-uses the existing `athlete_card`
  helper for visual consistency. Also re-exported from
  `aspire_dash.components` for symmetry with the other v0.37 helpers.

- **`meta_inline_bar(items, *, notes=None, title="Metadata",
  fluid=False)`** in `aspire_dash.components.cards`.
  Compact label:value horizontal bar wrapped in a small card. Replaces
  the `dbc.Row` + md-column grids that wrapped a Notes cell to a second
  row even when empty. Promoted from the diary period-metadata card.
  `fluid=True` drops the card wrapper.

- **`history_table(rows, *, columns, summary_chips=None,
  status_column=None, status_palette=None,
  empty_message="...")`** in `aspire_dash.components.cards`.
  Compact striped table with optional summary chips above and a
  status-badge column driven by row data. Genericises the
  `_render_injury_history` pattern so VALD test history, training-load
  weeks, attendance logs, supplement history etc. share one look.
  Per-column `format` callable supported (date formatters, etc.).

- **`ranked_dropdown(*, label, items, toggle_color="secondary",
  size="sm", empty_label="—")`** in `aspire_dash.components.cards`.
  Bootstrap DropdownMenu where each item carries a dict id (for
  pattern-matched callbacks) and renders a bold primary label + an
  optional tone-coloured sublabel. Replaces the inline `outline-light`
  chip pattern that suffered white-text-on-white-card in the diary
  alternates cell.

### CSS

- **NEW**: `.linear-step-card` / `.linear-step-header` / `.linear-step-badge`
  / `.linear-step-title` / `.linear-step-summary` / `.linear-step-chevron`
  added to `assets/00_aspire_base.css` under a `=== linear-step-card ===`
  section.

- **ALIASED, not renamed**: the older `.capture-step-*` classes (which
  aspire-nutrition currently ships in its own `10_capture_flow.css`)
  are kept as aliases in the same rule selectors. This is the safe
  rename — existing apps that still mount the local capture-flow CSS
  continue to render unchanged. Once those apps drop their local CSS
  and pin v0.37+, the aliases can be removed. **Action for downstream
  apps using `.capture-step-*` directly**: either start emitting
  `.linear-step-*` class names alongside, or rely on the upstream
  alias and remove your local copy of `10_capture_flow.css` once you've
  switched to `linear_step_card_collapse()`.

### Demo

Three new demo pages added under `aspire_dash/demo/pages/`:
- `linear_steps.py` — covers `linear_step_card_collapse` (mode A + B +
  custom header_type) and `register_linear_step_toggle`.
- `meta_history.py` — covers `meta_inline_bar` (card + fluid forms) and
  `history_table` (with + without summary chips, with + without status
  column, empty state).
- `ranked_picker.py` — covers `ranked_dropdown` (ranked alternates,
  empty state, neutral picker).

Nav entries wired in `demo/app.py`. The default and `demo-secondary`
header types for `linear_step_card_collapse` are registered there so
the demo page's headers are click-toggleable out of the box.

## [0.36.0] — 2026-05-25

### Added — body composition, skinfold silhouette, z-score engine

Promoted from the `DASH_Anthro` Connect app — all reusable across any
Aspire app touching body composition, anthropometry, or squad z-score
analysis.

**New in `aspire_dash.viz`:**
- `body_fat_gauge(value)` / `body_fat_gauge_svg(value)` — semicircle
  SVG gauge with green→amber→red gradient arc, ticks at 5/10/15/20/25/30,
  zone labels (Athletic/Fit/Average/Above/High), needle dot, tabular
  centre value. Static render, no draw-in animation. Sits alongside the
  existing `progress_ring` / `status_ring` family.

**New in `aspire_dash.anthropometric`:**
- `skinfold_silhouette(sites)` / `skinfold_silhouette_svg(sites)` —
  front-view male anatomical outline with 8 ISAK skinfold-site dots
  tinted blue→amber by relative magnitude, hover tooltips, low/high
  gradient legend. Distinct from `medical.body_silhouette` (which
  colours injury *regions*) — these complement each other.
- `zscore_heatmap(athletes, measures, matrix, raw_values, stats)` —
  squad-vs-population matrix as a Dash `html.Table` with 7-bucket
  colour scale, group-banded headers, mean / SD columns.
- `zscore_radar_figure(athlete_name, z_items)` — per-athlete polar
  radar, ±3 clamp with the loop closed for a clean profile shape.

**New module `aspire_dash.zscores`:**
- `compute_squad_z_scores(athletes, measurement_keys)` — pure-math
  engine. Returns matrix + per-key {mean, sd, n} stats + auto-generated
  insights (best/worst on signature measures, CV variability).
- `z_score_color(z, inverted=False)` — 7-bucket (bg, text) hex pair
  matching the heatmap colour scale.
- `is_inverted(key)` / `INVERTED_MEASURES` — handles "lower-is-better"
  measures (skinfolds, %BF, fat mass) so the colour scale flips
  appropriately.
- `Z_SCORE_MEASURES` — anthropometry-default measure list, grouped by
  section. Optional — apps can pass their own.
- `z_score(value, mu, sigma)` — atomic helper; returns `None` when
  `sigma < 0.01` (no variance).

### Migration notes

- DASH_Anthro 1f8dd53+ consumes all of the above directly; its local
  copies of these components / lib/z_scores.py have been removed.
- The somatochart already lived in `aspire_dash.anthropometric.somatochart`
  since 0.x — DASH_Anthro now uses that one too instead of its byte-port.
- `medical.body_silhouette` is unchanged; it colours injury *regions*
  via SVG element IDs and is independent of the new
  `anthropometric.skinfold_silhouette`.

## [0.35.0] — 2026-05-22

### Added — sports-science module + Freefrontend extras

**New `aspire_dash.sports_science` module — 5 domain-specific charts:**

- **`force_velocity_scatter(samples, title, height, show_pmax)`**
  VALD ForceDecks FV profile — scatter + best-fit linear regression +
  Pmax star marker. Samozino/Morin approach. Aspire-blue points, gold
  Pmax star, dashed FV line.

- **`acwr_chart(dates, daily_loads, acute_days=7, chronic_days=28)`**
  Full rolling Acute:Chronic ratio line with shaded zones — green
  sweet-spot (0.8-1.3), amber caution (1.3-1.5), red danger (1.5+).
  Reference dot at 1.0.

- **`hr_zone_distribution(sessions, mode='session'|'season')`**
  Z1-Z5 stacked bar — single bar per session OR aggregated 'Season'
  bar. Zone colours: slate / green / gold / amber / red.

- **`bullet_chart(value, target, ranges, label, sub, unit)`**
  Tactical bullet chart — Plotly Indicator with bar + qualitative-
  range bg + target marker line. Better than progress bars for "actual
  vs goal" + delta from reference.

- **`session_load_bubble(sessions)`**
  sRPE × duration training-load map. Bubble size = total session-RPE
  load; colour by RPE band (green ≤4, gold 5-7, red ≥8). Reference
  bands per zone.

**Freefrontend extras in `aspire_dash.v12_helpers`:**

- **`radial_multi_track(metrics, size)`** — Apex-style concentric ring
  chart, 3+ metrics stacked outer→inner with gradient strokes + legend
  with values aligned right.

- **`add_pb_markers(fig, markers)`** — Apex marker-on-line annotation
  helper. Adds gold star markers + dashed dropline + label text per
  milestone, no legend clutter.

- **`glass_card(children, padding)`** — frosted-glass surface
  (Tailwind glass-morphism). For "current session" hero panels on
  coloured page backgrounds. `backdrop-filter: blur(12px)` + soft
  shadow + 65% white bg.

## [0.34.0] — 2026-05-22

### Added — 3 more Tremor-borrowed patterns

**`tracker_strip(cells, label, height, show_legend)`**
Tremor "Tracker" pattern — 30-cell (or N-cell) consistency timeline.
Each cell is a small coloured rectangle with hover tooltip. Tones:
success / warning / danger / aspire / neutral / empty. Hover scales the
cell 1.15× and lifts shadow. Optional 4-swatch legend below. Perfect
for attendance / recovery / training-load timelines, sync-health
dashboards.

**`callout(title, children, severity, icon, dismissable)`**
Replaces `dbc.Alert` portfolio-wide. Tremor "Callout" pattern —
left-coloured-stripe block with icon + title + body. Severities:
`info` (aspire-blue) / `success` (green) / `warning` (amber) /
`danger` (red) / `aspire` (gold). Optional × dismiss button. Auto-
picks FontAwesome icon per severity. CSS class `.aspire-callout
.callout-{severity}`.

**`stat_card_mega(label, value, series, ring_pct, ring_label, delta,
delta_pct, delta_direction, accent, sub)`**
Hero-tile combining KPI value + trend chip + mini ring + sparkline in
one composition. Best layout for "top-of-page" dashboard summary rows
when you have multiple signals per metric (current value + trend
direction + target-attainment % + recent history). All five v0.33 +
v0.34 primitives compose cleanly.

CSS prefixes: `.tracker-strip .trk-*`, `.aspire-callout .callout-*`,
`.stat-card-mega .scm-*`. All hover lift + accent stripe modifiers
match the rest of the v12 library.

## [0.33.0] — 2026-05-22

### Added — 4 Tremor-inspired component patterns

Translation of the best-in-class React+Tailwind dashboard patterns to
Plotly+Aspire. All four sit in `aspire_dash.v12_helpers`.

**`kpi_with_sparkline(label, value, series, delta, delta_direction,
accent, sub, height)`**
Tremor "Tracker" pattern — big number + trend chip on the right + an
inline area chart filling the bottom half of the tile. Aspire-tinted
fill at 0.20 opacity over a 2 px accent line. Accent stripe + hover
lift like other Aspire cards.

**`progress_stack(items, total, label, height)`**
Tremor "Category Bar" pattern — horizontal stacked progress bar with
inline category labels and a legend strip below. Each segment gets a
proportional width + colour, with hover tooltips on each. Good for
budget allocations, athlete-readiness breakdowns, sport-medal splits.

**`stat_with_trend(label, value, delta, delta_pct, delta_direction,
accent, sub)`**
Tremor "Stats" pattern — KPI value + branded `▲ +8 (+24%)` trend chip
below. No chart, just typography on a coloured-stripe card. Use for
season-over-season comparison rows.

**`donut_with_focus(values, labels, colors, centre_label, centre_value,
height)`**
Plotly donut with thick white slice borders (3 px), Aspire palette,
slate-800 hover labels, centre-text summary annotation, and rounded
corners via marker_line. Hover dims non-active segments via opacity.

All four available as `from aspire_dash.v12_helpers import …`. CSS
prefixes: `.kpi-with-sparkline .kws-*`, `.progress-stack .ps-*`,
`.stat-with-trend .swt-*`. Hover lift + accent stripe modifiers
(`--accent-aspire / success / warning / danger / gold`) match other
v12 components.

## [0.32.0] — 2026-05-22

### Fine-grained polish pass (12 of 30 audit items shipped)

Pure CSS + 1-line Python edits. No new components, no breaking change.
All auto-apply on SHA bump.

**Numbers + centering**
- `metric_ring` value text now `width:100% + textAlign:center +
  lineHeight:1` — odd-width strings like `7h12` were drifting ~0.5-1 px
  off ring centre. Plus glyph was descending below centre on Chrome.
- `kpi_tile` value gained `font-variant-numeric: tabular-nums` (class
  hook wasn't firing because component uses inline style only).
- `kpi_tile` value 0-check: `if value is not None` instead of
  `if value` — zero counts now render "0", not "—".
- `kpi_stat` value bumped 26 → 30 px so baselines align with `kpi_tile`
  in the same grid.
- `acwr_badge`, `feedback.badge`: added `font-variant-numeric:
  tabular-nums` (no more width jitter on 1.10 → 1.85).
- `sparkline_tile`: float values get `f"{v:,.2f}"` instead of raw repr.
  Flat-delta glyph "·" → "–" (en-dash) for proper baseline.

**Typography rhythm**
- `.acv2-meta` 10.5 → 11 px (no more half-pixel fuzz)
- `.acc-name` 13.5 → 13 px
- `.acc-ring-label` 8.5 → 9 px (above WCAG-readable threshold)
- `.acc-stat-label` 9 → 10, `.acc-stat-value` 11.5 → 12 px
- `.spk-value` 22 → 24 px (matches kpi tile rhythm)
- `.badge` font-weight 500 → 600 (matches every other pill)

**Brand + token consolidation**
- `info_box`: `#3b82f6 / #1e40af / #bfdbfe` → `ASPIRE[600] / [700] / [200]`
- `placement_badge` else-branch: `#f9fafb / #6b7280` → `SLATE[100] / [500]`
- `.athlete-mini-card.tone-aspire`: explicit border + score colour rules
  (was falling back accidentally to base)

**Layout / motion**
- `.acv2-target-badge / .acc-target-badge`: now inherit card hover
  lift via own `transform` transition (was static, created 2 px detach)
- `.asymmetry-bar`: float → flex (kills 1 px subpixel gap)
- `.toggle-btn`: child radius 8 → 6 (nested-pill look)
- `.toggle-btn` font-family: drop Inter override (inherit body Poppins)
- `.sidebar`: dedup'd transition declaration
- `.header`: `slate-100` → `slate-200` border (now visible separator)
- `freshness_banner`: per-chip `marginRight` → parent `gap` (no
  trailing margin on last chip)

## [0.31.4] — 2026-05-22

### Added — `is_target` modifier + whoop-card-with-face demo

Both `athlete_card_v2` and `athlete_card_compact` now accept
`is_target: bool = False`. When True:

- **🎯 emoji badge** top-right of the card header with gold drop-shadow
- **Gold outline** around the whole card (2 px gold ring outside —
  visible on hover too)
- **Photo border STAYS the zone colour** (green/yellow/red) — user
  feedback: *"the ring around the pic should be the colour that the
  recovery is e.g. green"*. Recovery signal more important to see
  at-a-glance than the target flag.

Demo: whoop showcase page (`/whoop`) now demonstrates both cards with
photo + initials fallback + all 3 zones + is_target variants.

## [0.31.0] — 2026-05-22

### Added — `athlete_card_compact` (dense whoop-style variant)

Sibling to `athlete_card_v2` (the premium 56 px photo + 3 rings card).
The compact variant trades the hero photo for higher information
density:

- **40 px avatar** (was 56 px) — fits 4+ across in grids
- **48 px rings** (was 58 px)
- **Optional bottom stats row** — `[{label, value, status_dot}]`
  e.g. `HRV / RHR / Deep` with optional coloured status dot

Use case split:
- `athlete_card_v2` — hero rows, 2-3 across, photo-prominent
- `athlete_card_compact` — squad grids, 4+ across, more info per card

Both re-exported from `aspire_dash.athlete` for easy import:
```python
from aspire_dash.athlete import athlete_card_v2, athlete_card_compact
```

Same universal `zone-{green,yellow,red,aspire,gold,neutral}` modifier
support as v2 (avatar border tinted to match).

## [0.30.1] — 2026-05-22

### Fixed (CRITICAL — whoop rings lost per-metric colour)

User report: *"the whoop visuals look worse — they have lost their color
per ring and percentage"* + *"the gradient was nicer"*.

Two bugs in `athlete_card_v2` (v0.26) surfaced after whoop migration:

1. **Per-ring colour was dropped.** `athlete_card_v2` called
   `metric_ring(value, pct, label, size)` without passing the ring's
   `color`, so every ring rendered in the default Aspire blue tone.
   Recovery / Strain / Sleep all looked identical instead of green /
   amber / red per metric.

   Fix: `metric_ring(..., color="#hex")` parameter added. When provided,
   it overrides the tone preset. `athlete_card_v2` now reads `r["color"]`
   from each ring dict and plumbs it through.

2. **Ring stroke was flat — original had a gradient.** Restored:
   each ring now has an inline `<linearGradient>` going from
   `stroke` (light, 85% opacity at top-left) to `_darken(stroke, 0.70)`
   (rich, 100% opacity at bottom-right). Premium Whoop-style sheen
   per ring.

Both fixes auto-apply via SHA bump — no consumer code change.

## [0.30.0] — 2026-05-22

### Close the v0.29 honest gaps

Three targeted edits — each routes a parallel-palette dict through the
new v0.29 `SEMANTIC_PALETTE` / theme constants. Brand swap is now ONE
file edit, not 50.

**`vald.py` VALD_COLORS — Aspire-aligned.**
17 colour entries were a Tailwind + Bootstrap parallel universe from
the Next.js port. Now every entry maps to theme constants:
- `main_line` → `ASPIRE["600"]` (was already Aspire blue from v0.23)
- `mean` → `SLATE["500"]` (was `#666666` mid-grey)
- `sd_line / sd_line_outer` → `SUCCESS / WARNING` (was Bootstrap 4 hex)
- `ma_line / ma_band` → `ASPIRE["700"] / ASPIRE["500"]` (was Tailwind blue-700/500)
- `acute_line` → `WARNING` (was Tailwind amber-500 `#f59e0b`)
- `adaptive_line` → `SUCCESS` (was Tailwind emerald-500 `#10b981`)
- `alert_red / alert_amber` → `DANGER / WARNING`
- All `rgba(...)` band fills swapped to Aspire-RGB equivalents

ForceDecks chart visuals still pixel-match the legacy Next.js SHAPE
(SD bands, 4-pt MA, acute alerts, adaptive emerald) — only the
COLOURS now sit inside the Aspire palette.

**`v12_helpers._TONE_COLOURS` — sourced from SEMANTIC_PALETTE.**
The ring tone table now reads `(stroke, text)` from theme constants
instead of hardcoded hex. Every `metric_ring`, `athlete_card_rings`,
`athlete_card_v2` ring across the portfolio updates on next deploy if
SEMANTIC_PALETTE is ever changed — single source of truth.

**`sports.STAT_COLORS` — derived from SEMANTIC_PALETTE.**
The 7-key gradient stat-card palette (blue/green/red/amber/purple/teal/
gray) now builds its `{bg, border, text}` from semantic-palette entries
via a small `_grad_bg` helper. Same visual; cascade-aware.

### Migration

Zero consumer code change required. SHA bump → every chart, every ring,
every stat-card gets the consolidated brand.

## [0.29.0] — 2026-05-22

### Cross-cutting polish (3 cascades, no consumer code change required)

Frontend-architect audit found foundations are S-tier but half the
library doesn't consume its own tokens — ~210 of 677 hardcoded `#xxx`
hits live in `sports.py` + `v12_helpers.py` + `vald.py`. v0.29 starts
the cleanup with three cascades that lift every consumer app on the
next SHA bump.

### Cascade 1 — `theme.SEMANTIC_PALETTE` (consolidate ~50 hex duplicates)

New dicts in `theme.py`:
- `SEMANTIC_PALETTE` — `{tone: {bg, border, text}}` for badges/pills.
  Replaces the duplicate hex pairs in `feedback.py:42`, `sports.py:319`,
  `v12_helpers.py:32`, `firstbeat.py:32`.
- `ZONE_BG_TONES` — `(green, yellow, red, aspire, neutral, gold)`.
- `GRADIENT_BG_TONES` — opt-in CSS-string gradients for any card.
- `semantic_tone(tone)` helper.

### Cascade 2 — `.aspire-card` + modifier system

New CSS rules — every card emits via composition:
- `.aspire-card` — base (white, 8 px radius, slate-200 border, elev-1)
- `.aspire-card--gradient` — white → slate-50 vertical wash
- `.aspire-card--interactive` — hover lift -2 px + branded shadow
- `.aspire-card--accent-{aspire,secondary,gold,success,warning,danger}`
  — 4 px left stripe matching `kpi_tile_v2` accents

### Cascade 3 — Universal `.zone-{...}` modifiers

Lifted the v0.26 athlete-card-v2 zone gradient OUT of its scope into
universal classes. Any card/tile/section can wear `zone-green`,
`zone-yellow`, `zone-red`, `zone-aspire`, `zone-gold`, `zone-neutral`.

The Whoop-style gradient bg is now portfolio-wide. 10 components
benefit on next deploy:
`firstbeat._metric_cell`, `firstbeat.training_card`, `kpi_tile`,
`variance_card`, `utilisation_card`, `injury_card`, `placement_badge`,
`freshness_banner`, `acwr_badge`, `metric_ring`.

### CSS micro-polish (auto-apply)

- **Badges/pills hover scale** 1.05× with spring ease — every badge
  becomes interactive (was static)
- **Toggle group active state** — gradient bg + inset shadow (Linear
  / Stripe segmented control pattern)
- **KPI tile gradient bg** — subtle white → slate-50 + 4→6 px stripe
  widen on hover (tactile pressed feel)
- **Graph card slate-50 wash** — charts no longer float invisibly on
  white page bg
- **Toast slide-in motion** — 200ms ease-out (Linear/Stripe feel)

### Python helper upgrades (item 6, 7, 12, 13 from audit)

- **`athlete_card_v2` re-exported from `aspire_dash.athlete`** — now
  lives where callers expect (`from aspire_dash.athlete import
  athlete_card_v2`). Same implementation as v0.26.
- **`viz.py` ring track** `#e5e7eb` → `#e2e8f0` (slate-200 token).
  Affects 5 ring/gauge sites.
- **`vald.py` `#667eea` off-brand purple → `#004185` Aspire blue.**
  17 chart traces fixed in one swap.
- **`components/nav.py` topnav title** `#1e293b` → `SLATE["800"]`.

### Migration

Zero consumer code changes required. Bump aspire_dash SHA pin → every
app inherits Cascades 1-3 + the CSS micro-polish + the 4 token swaps
on next deploy.

The new `athlete_card_v2` helper is OPT-IN — apps that want the
Whoop-style card just `from aspire_dash.athlete import athlete_card_v2`.

## [0.28.0] — 2026-05-22

### Added — Chart polish (lifts every figure portfolio-wide)

**Premium hover labels.** Aspire template now ships with
**slate-800 bg + white text + slate-900 border** (was white/grey).
Linear/Stripe tooltip feel. Replaces stock Plotly white-on-white.
Auto-applied to every chart in every app on next deploy.

**Branded modebar.** When apps opt to show the modebar, the active
icon is now Aspire-blue (was default blue).

**4 new chart-polish helpers in `aspire_dash.charts`:**

- **`add_reference_line(fig, value, kind, label)`** — branded
  horizontal reference lines. `kind` ∈ `mean / target / threshold /
  baseline` picks the colour/dash preset so every chart's reference
  lines look identical. Mean = slate dotted, Target = aspire dashed,
  Threshold = red dashdot.

- **`aspire_area_fill(trace, color, alpha_top)`** — vertical gradient
  fill for line/area charts. Matches the `.athlete-card-v2` zone-
  gradient feel — top-tinted → fade to invisible at zero. Premium
  Linear/Whoop area-chart styling without per-app math.

- **`aspire_bar_gradient(color)`** — `marker=` dict for bar/waterfall
  traces. Aspire colour + slate-tinted edge + 0.92 opacity for
  premium bar styling.

- **`add_drop_shadow_trace(fig, trace_idx, offset)`** — adds a
  slate-tinted shadow line UNDER an existing trace for subtle depth.
  Linear-style chart elevation.

- **`aspire_hover_template(unit, precision)`** — HTML hovertemplate
  string for the slate-800 bg. Bold title + value + unit on its own
  line. Drop into any trace's `hovertemplate=`.

### Migration

Hover labels + modebar auto-apply via the Aspire Plotly template (no
consumer code change). Reference lines / gradient fills / drop shadows
are opt-in — add them where they lift a specific chart.

## [0.27.0] — 2026-05-22

### Added — `EXTERNAL_SCRIPTS` (Tailwind CDN, opt-in)

Inspired by the GCPQuantum/plotly-tailwind pattern. Tailwind CSS is
now available via CDN to any consumer app that opts in. Use case:
fast one-off layouts (grid / flex / spacing) without porting to
semantic CSS first.

```python
from aspire_dash import setup_app, STYLESHEETS, EXTERNAL_SCRIPTS

app = Dash(__name__,
           external_stylesheets=STYLESHEETS,
           external_scripts=EXTERNAL_SCRIPTS)   # NEW — opt-in Tailwind

# Tailwind utilities now work in any className:
html.Div(className="grid grid-cols-3 gap-4 p-6", children=[...])
html.Div(className="bg-white rounded-xl shadow-md p-6 hover:shadow-lg", ...)
```

**Pairs cleanly with semantic CSS** — use Aspire classes
(`kpi-tile`, `athlete-card-v2`, `status-pill`, etc.) for repeated
branded components, Tailwind utilities for page-level layout. Tailwind
specificity is lower than our semantic rules so the brand always wins
on owned components.

**Trade-off:** adds a ~50 KB CDN script to every page load. Skip
`EXTERNAL_SCRIPTS` if the app doesn't need utility classes — semantic
CSS alone covers ~95% of use cases.

## [0.26.0] — 2026-05-22

### Added — `athlete_card_v2` (Whoop-style premium card, Forge-built)

Designed via the Forge skill — prototyped in
`tools/forge/index.html` first (3 zone variants, with + without photo
states), then ported to semantic CSS + Python helper.

**`aspire_dash.v12_helpers.athlete_card_v2(name, rings, zone, photo_url, meta, href)`**

Replaces the bespoke whoop card. One library helper for any future
player dashboard. Features:

- **Larger 56 px photo** (vs 44 px) — proper face presence
- **Initials fallback** with brand-gradient avatar when no photo
- **Zone-coloured gradient bg** — top-left tint → white. User feedback:
  *"the gradient in the whoop cards is super nice — we should apply
  that to some of the other components too"* — gradient now in the lib
  for reuse via `.zone-green / yellow / red / aspire / neutral`.
- **3 inline metric rings** at 58 px tighter than v0.13's variant
- **Hover lift** + `--elev-hover-card` brand-tinted shadow

CSS classes: `.athlete-card-v2 .zone-<zone> .acv2-{header,avatar,
avatar-initials,name,meta,rings,ring-block,ring-label}`.

Whoop coach dashboard now delegates its `components/athlete_card.py`
full-card render to this helper.

## [0.25.1] — 2026-05-22

### Fixed — Whoop (and any other bespoke-sidebar app) hover effects

- v0.24's premium sidebar styles (`.sidebar-link` Aspire-blue hover bg
  + 22 px slide-in + gold active marker) were unscoped, so any app
  using `className="sidebar-link"` got Aspire-blue + gold effects
  bleeding into its own theme. Whoop coach dashboard (teal/green
  palette) showed inconsistent hover states because half its links
  were Aspire-tinted.
- Now scoped to `.sidebar-nav .sidebar-link` (the wrapper class used
  by `aspire_dash.components.sidebar()`). Apps that roll their own
  sidebar keep their custom palette uncluttered.

## [0.25.0] — 2026-05-22

### Chart-palette overhaul (Aspire-anchored, premium tonal harmony)

Audit found the categorical chart palette had 4 blues, 3 greens, and
4 clashing warms — saturated primary colours competing for attention.
v0.25 replaces it with a tonally harmonic 10-step palette where every
colour sits at roughly the same lightness + saturation, hue spacing
~36° apart. Aspire blue stays the brand anchor.

**New categorical palette (`brand.yml::colors.chart`):**

1. `#004185` Aspire blue (brand anchor)
2. `#be185d` Magenta rose
3. `#c2410c` Burnt orange
4. `#a16207` Mustard
5. `#65a30d` Lime green
6. `#047857` Emerald
7. `#0e7490` Teal
8. `#0369a1` Sky blue
9. `#6d28d9` Royal purple
10. `#b91c1c` Crimson red

**New sequential + diverging scales:**

- `SEQUENTIAL_BLUE`  — Aspire 50 → 900 (magnitude)
- `SEQUENTIAL_GOLD`  — gold 50 → 900 (achievement)
- `SEQUENTIAL_RED`   — red 50 → 900 (load / risk)
- `SEQUENTIAL_GREEN` — green 50 → 900 (recovery / readiness)
- `DIVERGING_RED_GREEN` — bad ← neutral → good (variance reports)
- `DIVERGING_GREEN_RED` — high-is-bad variant

**Plotly-ready exports in `aspire_dash.charts`:**

- `ASPIRE_BLUE_SCALE` — pass to `color_continuous_scale=`
- `ASPIRE_GOLD_SCALE`
- `ASPIRE_HEAT_SCALE` (replaces stock Plotly `Reds`)
- `ASPIRE_RECOVERY_SCALE` (replaces stock `Greens`)
- `ASPIRE_VARIANCE_SCALE` (diverging — for budget / variance pages)

**Migration:** replace `color_continuous_scale="Reds"` with
`color_continuous_scale=ASPIRE_HEAT_SCALE` in any consumer chart. The
categorical palette is consumed automatically via the Aspire Plotly
template (no code change needed — every chart picks up the new colours
on next deploy).

## [0.24.0] — 2026-05-22

### Brand polish — density + premium micro-interactions

**Off-scale spacing cleanup** (~12 inline radii / paddings that were on
3/5/6/9/10/12 collapsed to canonical 4/8/12/16/20/24):

- `athlete.py` chip radius 10 → 8, padding 9/18 → 8/16, label `#f8fafc`
  → `BG_PAGE`, badge radius 3 → 4
- `sports.py` sport-card radius 10 → 8, source badge 10px → 9999px
  (proper pill), shadow rgba 0,0,0 → slate-tinted
- `anthropometric.py` limb-symmetry bar radii 3 → 4, padding 10 → 12
- `nutrition.py` macro progress 3 → 4
- `budget.py` rollup chip radius 6 → 8
- `components/inputs.py` toggle radius 6 → 8, padding 4/10 → 4/12
- `components/feedback.py` badge non-pill radius 6 → 8
- `components/print_export.py` button radius 5 → 8, header padding 10
  → 12, bg `#f8fafc` → `#f7f9fc`
- `skeletons.py` size-sm radius 6 → 8 (canonical only)
- `export.py` button radii 6 → 8

**brand.yml — design-system rhythm tokens (NEW classes):**

- **`spacing`** — 4/8/12/16/20/24/32 px scale (xs/sm/md/lg/xl/xxl/xxxl)
- **`motion`** — ease curves (`ease_out` Stripe-style, `ease_in_out`,
  `ease_spring`) + duration tokens (fast/normal/slow)
- **`z_index`** — explicit dropdown/sticky/fixed/modal/popover/tooltip/toast
- **`borders`** — thin/medium/thick (1/2/4 px, no ambiguous 3)
- **`tracking`** — letter-spacing scale (tight/normal/wide/wider/widest)
- **`density`** — compact/comfortable/spacious multipliers
- **`gold-scale`** — full 10-step gold ramp (was just 2 shades)

Exposed as `theme.SPACING / MOTION / Z_INDEX / BORDERS / TRACKING /
DENSITY / GOLD_SCALE / EYEBROW_STYLE / TRANSITION_FAST /
TRANSITION_NORMAL`. Use these everywhere instead of magic strings.

**00_aspire_base.css — premium micro-interactions** (the Linear/Stripe
feel, applied portfolio-wide via CSS — no per-app code changes):

- **Cards** — brand-tinted hover shadow + 2 px directional lift, opt-out
  in `.financial-report` scope (read-only artefacts shouldn't bounce)
- **Buttons** — gradient bg, hover lift, gold-tinted focus ring
- **Inputs** — `--glow-aspire` focus ring (4 px aspire-600 at 10% alpha)
  replacing the default Bootstrap blue rectangle
- **Status pills** — gentle scale on hover (1.03x with spring ease)
- **Sidebar links** — slide-in from left + brand-tinted bg + 3 px
  aspire-400 marker on hover; gold marker on active
- **Topnav links** — branded underline grows from center on hover
- **Section titles** — fade-up entry animation
- **AG Grid rows** — aspire-50 hover tint
- **Header backdrop** — glass effect (blur 14 px + saturate 180%)
- **Body bg** — subtle slate gradient (depth instead of flat)
- **`.pulse-gold` class** — opt-in achievement pulse (2s)
- **`.badge-new` class** — golden shimmer pill for new features
- **a11y** — full `prefers-reduced-motion` honour

### Migration

No code changes required. Bump SHA pin → every app inherits the polish.
Forge-tier and legacy modules now look the same.

## [0.23.0] — 2026-05-22

### Brand-audit polish pass (B → A across the portfolio)

Audit found the CSS layer was A-quality (after v0.19) but Python
components were importing stale `brand.yml` tokens (RADIUS_LG=12 vs
canonical 8, pure-black shadows vs slate-tinted) and writing inline
styles that bypassed the canonical CSS classes. Result: half the
portfolio rendered "premium" (Forge components) and half "Bootstrap"
(legacy inline). This release closes that gap.

**`brand.yml` — three highest-leverage edits** (radii + shadows + page
bg). Every module that imports `RADIUS_LG` / `SHADOW_SM` instantly
upgrades on next SHA bump:

- `radius.sm/md/lg` all → 8 px (was 6/8/12). 8 px is canonical.
- `shadows.sm/md/lg` → slate-tinted (`rgba(15,23,42,...)`) replacing
  pure-black `rgba(0,0,0,...)`. Matches Linear/Stripe/Whoop depth.
- New `bg_page: #f7f9fc` token — exposes the warmer-than-slate-100
  page bg as `theme.BG_PAGE` (was hardcoded in 6 modules).

**Typography:**
- `charts.py` Plotly template font Poppins → Inter (brand rule:
  tabular/numeric → Inter). Every Plotly chart in the portfolio
  shifts to the data font without per-app edits.
- `theme.py` exports `FONT_HEADING`, `FONT_DATA`, `FONT_MONO` (was
  only `FONT_FAMILY` + `FONT_MONO`).

**Empty state dedup:**
- `components.feedback.empty_state()` now delegates to
  `v12_helpers.aspire_empty()`. One implementation, branded
  gradient + dashed aspire-200 border by default. Eliminates the
  visible split between Bootstrap-grey (old) and Aspire-branded (new)
  empty states across the portfolio.

**KPI rhythm:**
- `components/kpi.py` small variant radius 6 → 8, value sizes switch
  from `rem` to two-step px scale (26 / 30) matching CSS. Progress
  bar height 5 → 4 px (on-scale).

**Card depth:**
- `components/cards.py` `summary_card` drops its inline shadow and
  routes through `.budget-card` class (already correct in CSS). Hover
  lift now works because inline `boxShadow` no longer overrides it.

**VALD palette align:**
- `vald.py` bulk-replace `#6b7280` (Tailwind gray-500) → `#64748b`
  (slate-500) and `#e5e7eb` (Tailwind gray-200) → `#e2e8f0`
  (slate-200). VALD charts now read as Aspire, not legacy palette.

**AG Grid cleanup:**
- `tables.py` deprecates `ASPIRE_AG_THEME_OVERRIDES` (CSS authoritative
  via `.ag-theme-quartz.aspire-themed`). No more duplicated CSS string.

### Migration

No consumer changes required. Bump aspire_dash SHA pin → every app
inherits the polish automatically. Forge-built modules (financial,
v12_helpers, plots, charts) were already A-quality; legacy modules
(cards, kpi, budget, athlete, viz, etc.) now match by inheritance.

## [0.22.3] — 2026-05-22

### Fixed (CRITICAL — sidebar 404s on apps that pre-wrap hrefs)

- **`_safe_relative()` is now idempotent.** Apps that were written
  BEFORE v0.10.1 (when href-wrapping was pushed into the library)
  still pre-wrap their nav hrefs with `dash.get_relative_path(...)`
  before passing to `sidebar()` (defensive habit). v0.10.1+ then
  wraps AGAIN → `/content/<GUID>/content/<GUID>/medals` → 404.

  Demo + Whoop work because their nav_items use BARE paths. GCC,
  Medical, Endurance all pre-wrap → all 404'd on sidebar clicks.

  Fix: `_safe_relative()` now checks `path.startswith(prefix)`. If
  the path is already prefixed, return as-is. Otherwise wrap once.
  Topnav + sidebar both route through `_safe_relative()` now (topnav
  was still calling `dash.get_relative_path` directly).

  **Every app — pre-wrapping or not — works on next SHA bump.**

## [0.22.2] — 2026-05-22

### Fixed (CRITICAL — every app using normalised_path was 500-ing on every click)

- **`normalised_path()` now handles already-bare paths.** Dash
  automatically strips `requests_pathname_prefix` from `dcc.Location`
  pathnames before passing them to callbacks. So a Connect URL like
  `/content/<GUID>/whoop` arrives at the callback as just `/whoop`.
  `dash.strip_relative_path()` then raised `UnsupportedRelativePath`
  because the input no longer had the prefix it expected.

  Result: every router callback wrapped with `normalised_path` 500'd
  on every click. Whoop / Medical / GCC Games — all affected — none of
  their pages opened. The traceback only showed in the Connect job
  log, which is why it took a screen of "404 / blank page" reports
  to surface.

  Now catches `UnsupportedRelativePath` and treats already-bare
  pathnames as a no-op (which is exactly what we want).

  Every app inherits the fix on next SHA bump.

## [0.22.1] — 2026-05-22

### Fixed (CRITICAL — brand subdir assets not copied)

- **`setup_app()` now recurses into asset subdirectories.** Previous
  code did `for filename in os.listdir(_ASSETS_DIR): if os.path.isfile`
  — which silently skipped the `brand/` subdirectory introduced in
  v0.20. Result: consumer apps never received the federation logos /
  sport heroes / Aspire SVG, and every `/assets/brand/...` URL 404'd.
  Now uses `os.walk()` and copies the whole tree, preserving structure.

  User report: "in brand assets, I can't see any of the logos" while
  legacy `/assets/aspire-logo.png` (top-level file) rendered fine —
  the exact symptom of the subdir-skip bug.

## [0.22.0] — 2026-05-22

### Added — `aspire_dash.vald` (exact ForceDecks compositions)

Verbatim port of the DASH_VALD chart compositions. Apps can now drop
in the same 4-panel CMJ dashboard, group heatmap, and adaptive-band
chart without reaching into the VALD deploy.

- **`VALD_LAYOUT`** — exact paper/grid/font preset (Inter, dotted grid)
- **`VALD_COLORS`** — exact 17-key palette
- **`analytics_chart(data_points, stats, mode)`** — single large chart;
  mode ∈ `{sd_bands, 4pt_ma, acute}`
- **`cmj_panel_chart(data_points, stats, mode, adaptive_obs)`** —
  compact 192 px panel for the 2×2 grid; same 4 modes + adaptive
- **`group_heatmap(athletes_data)`** — athletes × dates Z-score matrix
- **`adaptive_chart(data_points, adaptive_obs)`** — emerald LAR/UAR
  band from R Plumber Bayesian API
- **`vald_cmj_grid(panels)`** — 2×2 grid wrapper for the CMJ dashboard

All compositions sit on top of the existing `aspire_dash.timeseries`
overlay builders (`build_sd_traces`, `build_4pt_ma_traces`,
`build_acute_traces`, `build_adaptive_traces`) — same primitives the
VALD app already uses, just one layer up.

### Demo

- `/vald` page in showcase now renders the actual 4-panel CMJ dashboard,
  analytics chart with 4 mode toggles, group heatmap, and the
  17-colour palette swatch grid.

## [0.21.0] — 2026-05-22

### Added — `aspire_dash.countries` module

One-stop reference for 204 countries. Apps stop hand-rolling country
dicts; everything resolves through one import.

**Functions:**
- `lookup(code)` — full record `{ioc, iso2, iso3, name, emoji, flag_url}`
- `name(code)`, `emoji(code)`, `iso2(code)`, `iso3(code)`
- `flag_url(code, size, fmt)` — flagcdn PNG (8 sizes) or SVG
- `flag_img(code, size, shape, border)` — `html.Img` with shape
  options (`rect` / `circle` / `square`)
- `normalise(code_or_name)` — canonicalise any input → IOC
- `search(name)` — fuzzy search by partial name
- `ALL` — dict of every country, keyed by IOC

**Data:**
- 204 IOC codes mapped to ISO-2, ISO-3, full name, flag emoji
- Re-exports from `sports.py`: `IOC_TO_ISO`, `ioc_to_iso`,
  `ioc_to_iso3`, `normalize_country`, `country_flag`, `flag_with_name`

### Changed — Showcase sidebar reorganised

Nav was grouped by version (✨ v0.17 / v0.18 / v0.19 / v0.20).
Re-grouped by purpose so users find things by what they DO, not when
they shipped:

- **Brand:** Brand assets, Countries & flags, Colour palette, Palette Lab
- **Building blocks:** KPIs, Cards, Inputs, Feedback, Skeletons, Tables,
  Print & export, Athlete cards + rings
- **Athlete & performance:** Athlete, Anthropometric, Medical,
  Firstbeat, Whoop, VALD, Nutrition, Adaptive trend
- **Sport reporting:** Sports patterns
- **Finance:** Budget, Financial reports
- **Charts:** Charts & data, Plot collection, Viz components

Logo & assets demo page kept under "Reference" as legacy.

## [0.20.0] — 2026-05-22

### Added — `aspire_dash.brand_logos` (Aspire + Qatar federation library)

Sniffed from www.aspire.qa partner section. Bundles 14 Qatar
federations + 2 ministries + 2 international partners + 1 award badge
+ the official Aspire SVG mark + 14 sport hero photos.

**Files** ship in `assets/brand/partners/` and `assets/brand/sports/`,
auto-copied by `setup_app()`.

**Helpers:**

- `partner_logo(slug)` — returns Connect-safe asset URL.
- `partner_logo_img(slug, height)` — `html.Img` with auto-prefixed src.
- `partners_strip(slugs, height)` — horizontal logo row (footer use).
- `sport_hero(sport, index)` — sport hero photo URL.
- `sport_hero_img(sport, index, height, width)` — `html.Img` page banner.

**Slugs available:**

- Aspire: `aspire`
- Ministries: `moe`, `mos`
- Multi-sport: `oly`, `sc`
- Federations: `athletics`, `tt`, `squash`, `fencing`, `gymnastics`,
  `swimming`, `shooting`, `golf`, `motor`
- International: `kas_eupen`, `leonesa`, `inspirational_leader`

**Sport heroes:** `athletics`, `fencing`, `squash`, `table_tennis`,
`facility` (3 shots each, 5 for facility — football excluded per
portfolio scope).

### Demo

- `/brand` page in the showcase — every logo + sport hero + usage code.

## [0.19.1] — 2026-05-22

### Fixed (CRITICAL — visible across every connected app)

- **Sidebar Aspire logo now shows on Connect.** `sidebar()` was using
  the raw absolute path `f"/assets/{LOGO_FILENAME}"` which 404'd on
  Connect's `/content/<GUID>/` subpath. Now auto-wraps via
  `dash.get_relative_path()` — locally returns `"/assets/..."`, on
  Connect prefixes correctly. Documented in
  `tool-posit-connect` SKILL.md. **Every connected app inherits this
  fix on next SHA bump — no consumer-side change needed.**
- **Medical `body_silhouette()` SVG renders correctly on Connect.**
  Was using `dcc.Markdown(svg, dangerously_allow_html=True)` which on
  some Connect runtime versions rendered the SVG markup as raw text
  inside a `<code>` block. Switched to a base64 data URL inside
  `html.Img` — works universally, no extra deps.
- **`metric_ring()` / `athlete_card_rings()` Whoop-style rings
  render correctly on Connect.** Same root cause as the body
  silhouette — `dcc.Markdown` SVG-as-text bug. Same data-URL fix.

## [0.19.0] — 2026-05-22

### Visual polish pass (audit-driven, applied portfolio-wide)

CSS-only changes — every connected app inherits on the next SHA bump.

- **Page centred on ultrawide** — `.page-content { max-width: 1360px;
  margin: 0 auto; padding: 32px; }`. No more content hugging the left
  edge on 1440px+ screens.
- **Hover lift bump 1→2 px** — `.card / .budget-card / .athlete-card /
  .kpi-tile` now translate -2 px with `--elev-2` shadow + soft
  aspire-200 border tint on hover. Lift registers as intentional.
- **KPI rhythm tightened** — `.budget-card .card-value` 22→26 px,
  `.kpi-tile .kpi-value` 32→30 px, `.fr-kpi-value` 28→30 px. Two-step
  scale (26 / 30) reads cleaner than four discordant sizes.
- **Tabular-nums universally** — every `.kpi-value / .card-value /
  .fr-kpi-value / .amc-metric-value / .spk-value / .injury-card /
  .asymmetry-bar` gets `font-feature-settings: "tnum" 1, "lnum" 1`.
- **Branded empty state** — `.aspire-empty` now uses a gradient bg +
  dashed aspire-200 border + aspire-400 icon (instead of neutral grey).
- **Table-row hover dialled down** — switched from aspire-50 to slate-50.
  Reserves aspire-blue for primary chrome only.
- **`.medical-body-card`** — new wrapper class for `body_silhouette()`
  output. Gradient slate-50→white bg, brand-blue drop shadow on the SVG,
  centred max-width 320 px. Replaces the awkward left-hugging layout.
- **Athlete ring card** — `.athlete-mini-card` gets a hairline divider
  under the header, gap bumped 12→16 px between rings. Matches Whoop's
  spacing.
- **`.section-title-v2`** — new class with brand-coloured 3px vertical
  lozenge marker. Bigger visual differentiation between sections.
- **Financial scope `.serif` variant** — opt-in `<div className=
  "financial-report serif">` switches to Source Serif Pro for a true
  annual-report feel. Annual reports get serifs; dashboards stay sans.

### Added — `aspire_dash.plots.adaptive_trend(...)`

Time-series line with rolling adaptive reference band (mean ± k·SD).
Used by VALD jump-height trend, Whoop RHR baseline, endurance load.
Pulls math from `aspire_dash.metrics.adaptive_range`. Aspire-blue fill
at 12% alpha, dotted baseline line, solid value trace with markers.

### Added — `aspire_dash.nutrition` module

- **`macro_tile(label, value, target, unit, accent)`** — single macro
  KPI with optional progress-vs-target bar. Bar shifts amber at >100%,
  red at >110%.
- **`macro_strip(macros, targets, layout)`** — horizontal strip of
  energy/protein/carbs/fat tiles. Pre-mapped defaults (Aspire-blue for
  energy, green for protein, amber for carbs, red for fat).

Promoted from aspire-nutrition so any app that tracks macros vs targets
(nutrition diary, weekly summary, hydration vs goal, training load vs
plan) can drop in the same look.

## [0.18.0] — 2026-05-22

### Added — `aspire_dash.anthropometric` (Ruwwad report patterns)

Promoted from the Next.js DASH_Anthro app so any Aspire Dash app
touching height / weight / skinfolds / somatotype can drop in the
same visuals.

- **`somatochart(points, title, height)`** — Heath-Carter triangle.
  Vertices from Nandikolmath 2024 (DOI 10.34256/ijk2417). Multiple
  points show a trajectory.
- **`growth_chart(df, age_col, value_col, lms_table, percentiles)`** —
  CDC / WHO LMS percentile-band growth chart with athlete trace.
  Uses `metrics.percentile_to_value` (v0.16) for the bands.
- **`athlete_snapshot_card(title, measurements)`** — Ruwwad attribute
  table: label / value / unit per row, aspire-navy header.
- **`limb_symmetry_bar(label, left, right)`** — L/R proportionality
  strip with auto-coloured border (green ≥97%, amber ≥92%, red <92%).

Anthro visuals can be Forge-polished in a future pass — this v0.18
ships the data shapes + math correctly so apps can adopt immediately.

### Added — `aspire_dash.sports` extensions (Fencing-reports patterns)

Sport-agnostic so the same helpers cover Squash (PSA/ESF/ASF), TT
(ITTF/WTT), Athletics (WA/Tila), Swimming (FINA/WAQ), Padel (FIP/WPT).

- **`source_badge(label, federation)`** — coloured federation tag pill.
  16 federations pre-mapped in `SOURCE_BADGE_COLORS` (extendable).
- **`competition_card(event, date, location, result, placement,
  federation, category, href)`** — career-feed card. Gold/silver/bronze
  colour for placement 1/2/3.
- **`world_map(df, country_col, value_col, highlight_country, scope)`** —
  ISO-3 choropleth with Aspire-blue gradient + gold-outlined highlight
  country.

### Demo

- `/v18` page renders every new helper with sample data.
- `/whoop` page gains the v0.13 3-ring athlete card (also visible at
  `/v12`) so it lives where users expect.

## [0.17.0] — 2026-05-22

### Added — `aspire_dash.plots` module (chart collection)

11 Plotly chart helpers with the Aspire template + palette baked in.
All take pandas dataframes (or label/value lists) and return a
`go.Figure` ready to drop into `dcc.Graph(figure=...)`.

**Distribution charts**
- `boxplot_by_group(df, value, group, orientation, height)`
- `violin_by_group(df, value, group, show_box, height)`
- `ridge_chart(df, value, group, height)` — joy-plot stacked KDEs

**Hierarchy / proportion**
- `sunburst(df, path, value, height)`
- `treemap(df, path, value, height)`

**Time-series**
- `calendar_heatmap(df, date_col, value_col, year, height)` — GitHub-style,
  Sun first (Qatar week)

**Financial / accumulation**
- `waterfall(labels, values, total_label, height)` — Aspire-blue for
  positives, red for negatives, slate-700 for the total bar

**Flow**
- `sankey(source, target, value, labels, height)` — nodes get the
  chart palette, links use the source-node colour at 33% alpha

**Comparison**
- `radar(categories, series, range_max, height)` — multi-series polar
- `slope_chart(df, x, y, group, height)` — value-at-two-x-points,
  green/red for up/down deltas
- `dumbbell(df, label, start, end, start_label, end_label, height)`

Module name: `plots` (separate from existing `viz` which holds SVG
rings/gauges).

### Demo

- `/plots` page in the showcase — every helper rendered with sample
  sport-dashboard data + copy-pasteable code snippets.

## [0.16.0] — 2026-05-22

### Added — `aspire_dash.metrics` module

Athlete-monitoring calculations — foundation for every longitudinal
chart in the portfolio. NumPy/pandas-friendly, no hidden state.

- **SDS** — `sds(value, mean, sd)` scalar and `sds_series(series,
  baseline_window)` rolling
- **Moving averages** — `moving_average(series, window)` simple +
  `exponential_moving_average(series, span)` EWMA
- **ACWR** — `acwr(series, acute=7, chronic=28, method='rolling'|'ewma')`
  + `acwr_zone(ratio)` returning `'low' | 'ok' | 'high' | 'danger'`
  with the published sweet-spot (0.8-1.3) + danger (≥1.5) thresholds
- **Adaptive reference ranges** — `adaptive_range(series, window, k)`
  returning a DataFrame of `mean / lower / upper` for the rolling
  mean ± k·SD band. Used by VALD jump-height chart and Whoop RHR
  baseline.
- **LMS percentile bands** — `lms_to_percentile` + `percentile_to_value`
  for CDC / WHO anthropometric growth-chart percentile curves.
- **Helpers** — `coefficient_of_variation`, `z_score`, `percentile_rank`.

Use for: anthropometric growth curves, VALD adaptive-range traces,
endurance ACWR badges, HRV / RHR baselines, any athlete-monitoring
chart that shades a "normal" band over a time series.

## [0.15.0] — 2026-05-22

### Added — `aspire_dash.financial` module (scoped report style)

Distinct visual register from the default athletic-modern look. Use
this scope for monthly briefs, variance reports, quarterly KPI
summaries, spend dashboards — anything where the reader expects
"clean financial" not "premium analytics".

**Scope class:** wrap your page in `className="financial-report"` to
opt in. Inside the scope:
- Heavier value type (28 px bold, tabular-nums)
- 6 px left accent stripe (vs the athletic 4 px)
- Slate-50 KPI backgrounds (vs pure white)
- No card hover lift (read-only artefacts, not interactive)
- More white space (16-20 px padding)
- Softer H1/H2 (24 px / 16 px, no marketing letter-spacing)

**Helpers:**

- **`financial_kpi(label, value, sub, accent)`** — heavier KPI tile.
  6 accent stripes (aspire / secondary / gold / success / warning / danger).
- **`variance_cell(value, currency)`** — coloured ▲▼ delta cell. Red for
  negative, green for positive. Currency-formatted via `fmt_currency`.
- **`totals_row(label, value, currency)`** — bold totals strip with
  slate-50 bg + 2 px top border.
- **`financial_tab_bar(tabs, value, tab_id)`** — clean underline tabs
  (vs the athletic chip toggle).
- **`financial_table(records, columns, totals_filter, negative_columns,
  right_align_columns, id)`** — wrapped `dash_table.DataTable` with the
  budget-app SUMMARY_TABLE_STYLE pattern: aspire-blue header,
  slate-50 TOTAL row when filter provided, red+bold negatives.

Promoted from aspire-budget-dashboard. Outside the
`.financial-report` scope the athletic style is unchanged — both
visual registers coexist in the same app if needed.

### Demo

- `/financial` page in showcase — full BEFORE/AFTER inside the scope.

## [0.14.0] — 2026-05-22

### Added — `aspire_dash.medical` module (extracted from medical-dashboard)

- **`body_silhouette(region_metric, max_value, title)`** — branded
  body-region heatmap card. Anatomical SVG (etal/bodymap, MIT licensed)
  with SAMS region names mapped onto 14 body parts. Pass a dict of
  `{SAMS region: metric value}` and the function fills each region
  with an Aspire-blue gradient based on the value-to-max ratio.

- **`injury_list(injuries)`** — multi-injury container. Each row is a
  v0.12 `injury_card`. Auto-renders branded `aspire_empty(...)` when
  the list is empty ("No active injuries — all squad fit to train").

- **`render_svg(region_metric, max_value)`** — lower-level helper if
  you want to embed the bare SVG without the card chrome.

- **`SAMS_TO_BODYMAP`** dict — exported so apps can audit which SAMS
  regions map to which bodymap IDs.

- **`/assets/body-bodymap.svg`** (33 KB) shipped with the package.
  `setup_app()` copies it into each consumer's `/assets/` automatically.

These were duplicated maintenance liabilities in medical-dashboard's
`components/body_silhouette.py`. Promoting upstream so attendance,
training-load, and the athlete profile pages across the portfolio can
all show the same body heatmap pattern.

## [0.13.0] — 2026-05-22

### Added — Whoop rings promoted from whoop_coach_dashboard

- **`metric_ring(value, pct, label, tone, size, unit)`** in v12_helpers.
  SVG donut with value-in-centre + percent arc. Six tones (good / warn
  / danger / aspire / secondary / gold). Replaces the hand-rolled
  `recovery_ring` / `value_ring` in whoop_coach_dashboard/components/
  rings.py (~140 LOC of duplicated SVG math).

- **`athlete_card_rings(name, rings, photo_url, meta, tone, href)`** —
  Whoop-style card with photo + name + up to 4 inline metric rings.
  `rings=[{value, pct, label, tone}]` — text values OR string values
  ("7h12") supported. Pairs with `metric_ring` internally. Direct
  port of whoop_coach_dashboard's components/athlete_card.py — the
  one Kenny called out as wanting saved upstream.

### Demo

- `/v12` page gains a new "11 · metric_ring + athlete_card_rings"
  section showing 4 standalone rings + 3 athlete cards (good / warn /
  danger tones) with the same Mohammed/Khaled/Ali sample data the
  whoop_coach_dashboard uses.

## [0.12.4] — 2026-05-22

### Fixed (CRITICAL — setup_app crashed on Connect)

- **Removed the broken `app.config.update({"requests_pathname_prefix"...})` block.**
  After Dash() runs, those keys are read-only on `app.config` — calling
  `update()` raises `AttributeError: Read-only: can only be set in the
  Dash constructor or during init_app()`. So 0.12.1's "Connect subpath
  fix" actually crashed every consumer at boot on Connect.

  The whole block was also redundant: Dash already reads
  `DASH_URL_BASE_PATHNAME` from the environment in its own constructor
  when `url_base_pathname` isn't passed explicitly. Connect sets this
  env var, so the prefix is picked up correctly by Dash itself. The
  sidebar/topnav helpers then resolve link hrefs through
  `dash.get_relative_path()` at render time and the prefixed paths
  flow through end-to-end.

  Caught by the DASH_VALD deploy — Connect job log showed the
  AttributeError on `setup_app(app)`.

## [0.12.3] — 2026-05-22

### Added

- **`aspire_dash.normalised_path(pathname)`** — canonical helper for any
  router callback that dispatches on `dcc.Location` pathname. Wraps
  `dash.strip_relative_path()` and normalises to a bare leading-slash
  path so dispatch dicts can use bare keys like `"/athletes"`.

  ```python
  from aspire_dash import normalised_path

  @callback(Output("page-content", "children"), Input("url", "pathname"))
  def route(pathname):
      return PAGES.get(normalised_path(pathname), default_page)
  ```

  **Why:** Connect serves apps under `/content/<GUID>/`. Without
  stripping the prefix, `pathname` is the full URL and bare-key
  dispatch dicts always miss → every click falls back to the default
  page. Caught in the DASH_VALD upgrade where bumping to 0.12.1 fixed
  the hrefs but the app's own router dict had bare keys like
  `"/athletes"` that didn't match the prefixed pathname.

  The pattern lives inside `aspire_dash.athlete._picker_visibility`
  already — promoted here so every router callback can call one helper.

## [0.12.2] — 2026-05-22

### Fixed (CRITICAL — setup_app crashed every consumer app)

- **`setup_app()` no longer raises `UnboundLocalError: os`.** The 0.12.1
  fix added a redundant `import os` inside the function body. Python's
  parser flags that as a local binding for the whole function, so the
  earlier `os.makedirs(app_assets)` call on line 108 threw
  `UnboundLocalError`. Removed the duplicate import — `os` is already
  imported at module top. Caught when VALD's pytest suite started
  failing with the import error after pulling 0.12.1.

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
