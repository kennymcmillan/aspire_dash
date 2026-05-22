# Forge — aspire_dash design workflow

**Tagline:** Prototype every visual in Tailwind + DaisyUI first. Port to Dash second. Every consumer app benefits.

## Why

Whoop and Firstbeat pages in the aspire_dash showcase look dramatically sharper than the rest of the library. Reason: they were prototyped first in a Next.js + Tailwind environment, iterated visually, then translated to Dash CSS. Generic Dash components hit a "Bootstrap default" plateau because writing rich CSS inline in Python is slow and feedback-poor.

The Forge fixes that. Iterate visually in `index.html` with full Tailwind utility classes + DaisyUI semantic components. When the prototype looks great, extract the final CSS into `aspire_dash/assets/00_aspire_base.css` and ship.

## Toolchain

| Tool | Used for | How |
|---|---|---|
| **Tailwind v3 CDN** | Utility classes (`p-4`, `rounded-lg`, `text-slate-500`, etc.) | `<script src="https://cdn.tailwindcss.com">` |
| **DaisyUI v4 CDN** | Semantic components (`btn`, `card`, `badge`, `tabs`, `modal`) | `<link href="...daisyui@4.../full.min.css">` |
| **Custom `aspire` DaisyUI theme** | Aspire palette mapped to DaisyUI tokens (--p, --s, --a) | Inline `<style>` block in `index.html` |
| **Poppins font** | Aspire brand font (sniffed from aspire.qa) | Google Fonts `<link>` |
| **TailGrids / shadcn/ui / Tailwind UI** | Pattern inspiration (visual reference only — not directly importable) | Browse → translate the look |

## Workflow

### When user says "redesign this component" or "make X look amazing"

```
1. Open tools/forge/index.html in a browser
2. Add a new <section> for the component you're redesigning
3. Place BEFORE (current Dash render) and AFTER (Tailwind prototype) side-by-side
4. Iterate visually — Tailwind hot-reloads on browser refresh
5. When happy:
   a. Extract the Tailwind class string from the prototype
   b. Convert to a CSS rule in aspire_dash/assets/00_aspire_base.css
      (e.g. `.kpi-tile { ... }` mirroring the Tailwind utilities)
   c. Update the Python helper to emit the new className
   d. Sync: cp aspire_dash/assets/00_aspire_base.css demo/assets/
   e. Bump aspire_dash __version__ + setup.py + CHANGELOG
   f. Commit + push
6. Bump aspire_dash pin in consumer app's requirements.txt
7. Redeploy consumer apps — all visuals lift in one bump
```

### Why Tailwind classes → CSS rules (and not just inline Tailwind in Dash)

We could load Tailwind in every Dash app and pass utility classes directly:
```python
html.Div(..., className="bg-white border border-slate-200 rounded-lg p-4")
```

But that produces wall-of-utility-strings Python code. Better:
1. Iterate in the forge with utility classes (fast, visual)
2. Once locked in, condense to a semantic class (`.kpi-tile`) in our CSS
3. Python stays clean: `html.Div(..., className="kpi-tile accent-aspire")`

Best of both worlds: utility-first design speed in the forge, semantic-class clarity in production.

## When to reach for DaisyUI specifically

DaisyUI gives semantic Tailwind components — `btn`, `card`, `badge`, `tabs`, `modal`, `drawer`, `dropdown`, etc. **Works in pure HTML/CSS context, so it works in Dash with zero React dependency.**

Useful when:
- You need a button/badge/card that "just works" — DaisyUI's defaults are already great
- You want themable components (DaisyUI's theme system maps to our `aspire` theme via 6-8 CSS variables)
- You want consistent component classes across pages without re-deriving them every time

Not useful for:
- Custom-shaped data viz (charts, gauges, sport-specific cards) — write those in raw HTML+CSS
- One-off layouts — Tailwind utilities alone are enough

## Inspiration sources (visual reference, NOT direct importable)

- **TailGrids** — https://tailgrids.com/components — stat cards, pricing tables, dashboards
- **shadcn/ui** — https://ui.shadcn.com — accessible primitives + flawless typography (React-only, translate the look)
- **Tailwind UI** — https://tailwindui.com — paid, but free preview gives plenty of patterns
- **Whoop / Linear / Stripe** dashboards — open in browser, inspect, steal the spacing + elevation patterns
- **Aspire marketing site** — https://www.aspire.qa — actual brand source. Poppins, #004185, 5 px letter-spacing on H2s

## File map

```
aspire_dash/tools/forge/
├── index.html           ← live sandbox, edit + browser-refresh
├── FORGE.md             ← this doc
└── (prototypes/         ← optional: one HTML file per redesign for archival)
```

Once a prototype is shipped, you can either delete the section from `index.html` (keeping it light) or leave it as a regression reference.

## Naming convention for CSS classes promoted from the forge

| Pattern | Example | When |
|---|---|---|
| `.<component>` | `.kpi-tile`, `.athlete-card`, `.aspire-table` | Pure component class — anything inheriting the design system |
| `.<component>.accent-<colour>` | `.kpi-tile.accent-aspire` | Variant modifier (Aspire blue / gold / success / etc.) |
| `.<component>.is-<state>` | `.athlete-card.is-target` | State variant (selected, error, loading) |

Avoid one-off `.kpi-tile-budget` style — prefer modifier classes that compose.
