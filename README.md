# aspire_dash

Shared **Plotly Dash** component, styling, and chart library for Aspire Academy dashboards.

Provides consistent branding, layouts, components, and chart presets so each app focuses on its data and callbacks instead of re-implementing sidebars, headers, cards, and theme tokens.

## Install

```bash
pip install git+https://github.com/kennymcmillan/aspire_dash.git
```

Or for local editable development:

```bash
git clone https://github.com/kennymcmillan/aspire_dash.git
cd aspire_dash
pip install -e .
```

## Usage

```python
import dash
from aspire_dash import setup_app, STYLESHEETS
from aspire_dash.components import sidebar, header, card, toast, badge
from aspire_dash.layouts import page_layout
from aspire_dash.theme import CHART_COLORS, ACCENT
from aspire_dash.charts import GRAPH_CONFIG

app = dash.Dash(__name__, external_stylesheets=STYLESHEETS)
setup_app(app)
app.layout = page_layout(
    sidebar(...),
    header("My Dashboard"),
    main_content,
)
```

## Modules

| Module | Purpose |
|---|---|
| `aspire_dash` | `setup_app()`, `STYLESHEETS` constant |
| `aspire_dash.components` | `sidebar`, `header`, `card`, `toast`, `badge`, etc. |
| `aspire_dash.layouts` | `page_layout` — full-page wrapper with sidebar + content slot |
| `aspire_dash.theme` | Design tokens — colours, fonts, spacing, `ACCENT`, `CHART_COLORS` |
| `aspire_dash.charts` | Chart helpers + `GRAPH_CONFIG` (Plotly default config) |
| `aspire_dash.viz` | Reusable visualisation builders |
| `aspire_dash.sports` | Sport-specific helpers (icons, palettes) |
| `aspire_dash.firstbeat` | Firstbeat-specific report cards (legacy, used by DASH_FirstBeat) |

## Templates

`aspire-dash` CLI generates a starter Dash app:

```bash
aspire-dash init my-new-app
```

## Brand tokens

Single source of truth: `aspire_dash/brand.yml`. Imported by `theme.py` into Python constants and propagated into the CSS asset bundle.

## Used by

- [DASH_VALD](https://github.com/kennymcmillan/DASH_VALD) (private) — VALD ForceDecks analytics
- [DASH_WORKBENCH](https://github.com/kennymcmillan/DASH_WORKBENCH) (private) — Sports chatbot frontend (v1)
- [DASH_WORKBENCH_v2](https://github.com/kennymcmillan/DASH_WORKBENCH_v2) (private) — Sports chatbot v2 (supervisor agents + RAG)
- DASH_FirstBeat, DASH_Vyntus, DASH_WHOOP, DASH_Budget, Abror_Project — internal Aspire dashboards

## License

MIT — see [LICENSE](LICENSE).
