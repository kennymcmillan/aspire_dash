---
name: forge
description: Aspire Dash design Forge — Tailwind+DaisyUI sandbox for prototyping any visual component before porting to aspire_dash CSS. Auto-trigger on "redesign", "make X look amazing", "upgrade visual", "needs polish", "looks too dash", "Whoop-style", "Firstbeat-style".
---

# Aspire Dash Forge — design any new visual the right way

## When to use this skill

User says (or implies) any of:
- "redesign the X"
- "make this look amazing / sharper / more premium"
- "this looks too Dash-like"
- "upgrade [component]"
- "needs polish / styling"
- "Whoop-style" / "Firstbeat-style" / "more like aspire.qa"
- New component request for aspire_dash
- Any visual quality concern about a Dash app

**Default workflow:** prototype in Tailwind+DaisyUI first, port to semantic CSS second. Whoop and Firstbeat pages in aspire_dash look dramatically sharper than the rest because they followed this loop. Generic Dash components hit a "Bootstrap default" plateau because writing rich CSS inline in Python is slow and feedback-poor.

## The 4-step loop

```
1. Open  aspire_dash/tools/forge/index.html
2. Add   <section id="..."> with BEFORE (current Dash render) +
         AFTER (Tailwind+DaisyUI prototype) side-by-side
3. Port  extract final Tailwind class string -> semantic CSS rule
         in aspire_dash/assets/00_aspire_base.css
4. Wire  Python helper emitting className="…" -> aspire_dash/v12_helpers.py
         (or other topic module). Sync demo/assets/ + bump version.
```

## Toolchain (CDN-loaded — zero build step)

| Tool | Loaded via | Used for |
|---|---|---|
| Tailwind v3 | `<script src="https://cdn.tailwindcss.com">` | utility classes (`p-4 rounded-lg bg-white`) |
| DaisyUI v4 | `<link href=".../daisyui@4.../full.min.css">` | semantic components (`btn`, `card`, `badge`, `tabs`, `modal`) |
| Custom `aspire` DaisyUI theme | inline `<style>` in index.html | maps DaisyUI tokens to Aspire palette |
| Poppins | Google Fonts | brand-correct body font |
| Inter | Google Fonts | data-heavy contexts (tabular-nums) |

## Aspire palette (cheat sheet)

```css
--aspire-600: #004185   /* PRIMARY — brand blue */
--aspire-700: #003566   /* hover / active */
--aspire-secondary: #1876ab  /* links */
--gold: #fbb800         /* highlights, badges */
--slate-50..900         /* neutrals */

/* Semantic */
--success: #16a34a    --warning: #d97706    --danger: #dc2626

/* Page bg */
body { background: #f7f9fc; }    /* warmer than slate-100 */

/* Elevation */
--elev-1: 0 1px 2px rgba(15,23,42,0.04), 0 1px 3px rgba(15,23,42,0.03);
--elev-2: 0 4px 12px rgba(15,23,42,0.08);
--elev-3: 0 12px 32px rgba(15,23,42,0.12);

/* Canonical radius: 8px for cards/inputs/code, full for pills */
```

## Existing classes — reuse before inventing

Promote new classes only when the existing ones don't fit. Audit first.

| Class | Purpose |
|---|---|
| `.kpi-tile` `.accent-aspire/secondary/gold/success/warning/danger` | KPI tile with accent stripe (use `kpi_tile_v2()`) |
| `.athlete-mini-card` `.tone-good/warn/danger/aspire` | Whoop-style card (use `athlete_card()`) |
| `.sparkline-tile` `.spk-label/value/delta/chart` | KPI + inline line chart (use `sparkline_tile()`) |
| `.injury-card` `.severity-mild/moderate/severe/resolved` | Medical-domain card (use `injury_card()`) |
| `.asymmetry-bar` `.dev-warn/danger` | VALD L/R split bar (use `asymmetry_bar()`) |
| `.status-pill` `.status-success/warning/danger/info/neutral` `.is-solid` | Pill, hides with `:empty` (use `status_pill_v2()`) |
| `.date-toolbar` `.dt-btn` `.dt-display` `.dt-today` | Unified date control (use `date_toolbar()`) |
| `.ag-theme-quartz.aspire-themed` / `.ag-theme-aspire` | Branded AG Grid header |
| `.aspire-loading` `.aspire-loading-spinner` | Branded loader (use `aspire_loading()`) |
| `.aspire-empty` `.aspire-empty-icon` | Branded empty state (use `aspire_empty()`) |
| `.aspire-table` | Drop-in styled `<table>` |
| `.aspire-section-heading` | Marketing-site H2 (5 px tracking + 500 + uppercase) |
| `.budget-card` / `.card` / `.athlete-card` | Generic elevated cards (auto-lift on hover) |
| All `skel_*` skeletons + `skel_sync_overlay` | Loading placeholders |

If you need something not listed, **prototype it in the Forge first** — don't write inline styles in Python.

## Naming convention for new classes

| Pattern | Example | When |
|---|---|---|
| `.<component>` | `.kpi-tile`, `.athlete-card` | Pure component |
| `.<component>.accent-<colour>` | `.kpi-tile.accent-gold` | Variant modifier |
| `.<component>.is-<state>` | `.athlete-card.is-target` | State variant |
| `.<component>.dev-<level>` | `.asymmetry-bar.dev-warn` | Domain-specific severity |

Avoid one-off `.kpi-tile-budget` — use composable modifiers.

## Step-by-step procedure (what I should do when triggered)

### Step 1 — assess scope
- Is there an existing class/helper that fits? Check the table above + grep `aspire_dash/assets/00_aspire_base.css`.
- If yes → just use it, skip the Forge.
- If no → continue.

### Step 2 — prototype in Forge
- Open `~/Documents/posit-deploys/aspire_dash/tools/forge/index.html`
- Add a `<section id="...">` block with:
  - H2 + 1-line goal
  - BEFORE (current render, simple recreation)
  - AFTER (Tailwind+DaisyUI prototype using the aspire theme)
- Use Tailwind utilities + DaisyUI semantic classes. Aspire palette via Tailwind arbitrary-value syntax: `border-l-[#004185]`, `text-[#0f172a]`.
- Iterate (browser refresh) until visually great.
- Show user a screenshot of the prototype before porting.

### Step 3 — port to semantic CSS
- Extract the final Tailwind string and condense into one CSS rule in `aspire_dash/assets/00_aspire_base.css`. Use the v0.12 section as the template.
- Follow the naming convention above.

### Step 4 — Python helper
- Add to `aspire_dash/v12_helpers.py` (or topic module like `components/kpi.py` if it logically belongs there).
- Emit `className="my-component accent-aspire"` from a small `def my_component(...)`. Keep API minimal + named-arg-only for the modifiers.

### Step 5 — demo + sync + ship
- Add a section in `aspire_dash/demo/pages/v12.py` (or the appropriate topic page) with live render + code snippet.
- `cp aspire_dash/assets/00_aspire_base.css demo/assets/` (setup_app only copies once).
- Run `py -3.12 "$LOCALAPPDATA/Temp/sweep_demo_pages.py"` — all pages must pass.
- Run `py -3.12 -m pytest tests/ -q` — must stay green.
- Bump `aspire_dash/__init__.py __version__` + `setup.py version` + CHANGELOG entry.
- `git add -A && git commit -m "feat(forge): <component>"` and push.
- Capture the new SHA: `git rev-parse HEAD`.
- Update consumer app's `requirements.txt` to the new SHA.
- Deploy consumer apps via `rsconnect deploy …`.

### Step 6 — record the work
- Note the new component in CHANGELOG under the version bump.
- If it's a significant pattern, add an entry to `MEMORY.md` (don't duplicate this skill).

## Inspiration sources (visual reference — NOT directly importable)

- **TailGrids** — https://tailgrids.com/components — dashboard layouts, stat cards
- **shadcn/ui** — https://ui.shadcn.com — gold-standard typography + spacing (React-only, translate the look)
- **Tailwind UI** — https://tailwindui.com — paid, but free previews
- **Whoop / Linear / Stripe** dashboards — inspect, steal spacing + elevation
- **aspire.qa marketing** — actual brand source. Poppins, #004185, 5 px letter-spacing on H2s

## Hard rules

1. **Never write rich inline styles in Python** for visual components. If you find yourself building a 10-key `style={}` dict, that's a sign the component belongs in `00_aspire_base.css` with a class name.
2. **Never invent a new palette colour.** Use a token from `brand.yml` / `--aspire-*` / `--slate-*`. If you need a new colour, add it to brand.yml first.
3. **Bump CHANGELOG + __version__ + setup.py together** — past drift bug ([[feedback_keep_aspire_libs_current]]).
4. **Always sync `demo/assets/00_aspire_base.css`** after editing the source — `setup_app()` only copies once.
5. **Always pin to a SHA in consumer apps** ([[feedback_rsconnect_use_app_id]]).
6. **Test the sweep + pytest** before pushing.

## Quick reference paths

```
~/Documents/posit-deploys/aspire_dash/
├── aspire_dash/
│   ├── assets/00_aspire_base.css         ← SEMANTIC CSS RULES GO HERE
│   ├── assets/brand/                      ← Aspire logo + favicons
│   ├── v12_helpers.py                     ← NEW PYTHON HELPERS GO HERE
│   ├── components/{kpi,inputs,feedback,print_export,cards,nav}.py
│   ├── tables.py, athlete.py, budget.py, charts.py, sports.py, firstbeat.py
│   ├── theme.py, skeletons.py, layouts.py
│   ├── brand.yml                          ← palette + fonts source of truth
│   └── __init__.py                        ← __version__
├── tools/forge/
│   ├── index.html                         ← PROTOTYPE HERE FIRST
│   └── FORGE.md                           ← workflow doc for humans
├── demo/
│   ├── app.py + pages/                    ← showcase, sweep tests
│   └── requirements.txt                   ← aspire_dash SHA pin
├── CHANGELOG.md
└── setup.py
```

## Related memories

- [[feedback_forge_workflow]] — short-form reminder pointing back to this skill
- [[reference_aspire_brand_sniff]] — Poppins + #004185 confirmation from aspire.qa
- [[reference_aspire_dash_demo]] — Connect GUID + page list + sweep tool
- [[feedback_keep_aspire_libs_current]] — version/CHANGELOG drift bug history
