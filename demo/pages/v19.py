"""v0.19 — polish pass + adaptive_trend + nutrition macro_strip."""
import dash
import pandas as pd
import numpy as np
from dash import dcc, html

from aspire_dash.plots import adaptive_trend
from aspire_dash.nutrition import macro_strip, macro_tile

from ._shared import section, code_block

dash.register_page(__name__, path="/v19", title="v0.19", name="✨ v0.19 New")


# Sample VALD jump-height series with trend + noise
np.random.seed(7)
_dates = pd.date_range("2026-02-01", periods=24, freq="W")
_jump = 38.5 + np.cumsum(np.random.normal(0.15, 0.4, 24))
_VALD = pd.DataFrame({"date": _dates, "jump_cm": _jump})


def layout():
    return html.Div([
        html.H1("v0.19 — Polish pass + adaptive trend + nutrition macros",
                style={"fontSize": "28px", "fontWeight": 700,
                       "marginBottom": "8px"}),
        html.P("CSS polish lands portfolio-wide (page centred on ultrawide, "
                "hover lift 2px, KPI rhythm tightened, tabular nums everywhere, "
                "branded empty state). Plus two new Python helpers.",
                style={"color": "#64748b", "fontSize": "14px",
                       "marginBottom": "24px"}),

        section("adaptive_trend — VALD-style line + adaptive band"),
        html.Div([
            dcc.Graph(figure=adaptive_trend(
                _VALD, x="date", y="jump_cm",
                window=8, k=1.0,
                title="CMJ jump height (cm) — 8-week adaptive range",
                band_label="±1 SD adaptive band",
            ), config={"displayModeBar": False}),
        ], className="card"),
        code_block(
            "from aspire_dash.plots import adaptive_trend\n\n"
            "adaptive_trend(\n"
            "    df, x='date', y='jump_cm',\n"
            "    window=8,    # rolling baseline window\n"
            "    k=1.0,       # 1 SD band (use 1.96 for 95% range)\n"
            "    band_label='±1 SD adaptive band',\n"
            ")"
        ),

        section("macro_strip — nutrition macro KPI row"),
        macro_strip(
            macros={"energy": 2400, "protein": 110,
                     "carbs": 280,  "fat": 75},
            targets={"energy": 2800, "protein": 140,
                      "carbs": 320,  "fat": 80},
        ),
        code_block(
            "from aspire_dash.nutrition import macro_strip\n\n"
            "macro_strip(\n"
            "    macros={'energy': 2400, 'protein': 110, 'carbs': 280, 'fat': 75},\n"
            "    targets={'energy': 2800, 'protein': 140, 'carbs': 320, 'fat': 80},\n"
            ")"
        ),

        section("Over-target state (amber >100%, red >110%)"),
        macro_strip(
            macros={"energy": 3100, "protein": 165,
                     "carbs": 380,  "fat": 90},
            targets={"energy": 2800, "protein": 140,
                      "carbs": 320,  "fat": 80},
        ),

        section("Single macro_tile (any metric vs target)"),
        html.Div([
            macro_tile("Hydration", 1.8, target=3.0, unit=" L",
                        accent="#0369a1"),
            macro_tile("Sleep",     6.5, target=8.0, unit=" h",
                        accent="#7c3aed"),
            macro_tile("Steps",     8200, target=10000, unit="",
                        accent="#16a34a"),
        ], style={"display": "flex", "gap": "10px",
                   "marginBottom": "12px"}),
        code_block(
            "from aspire_dash.nutrition import macro_tile\n\n"
            "macro_tile('Hydration', 1.8, target=3.0, unit=' L',\n"
            "           accent='#0369a1')"
        ),

        section("Polish pass — what's CSS-only and applies portfolio-wide"),
        html.Ul([
            html.Li("Page centred on ultrawide (max-width 1360 + auto margin)"),
            html.Li("Hover lift bumped 1→2 px so it registers"),
            html.Li("KPI value rhythm: 26 / 30 px two-step scale"),
            html.Li("Tabular nums + lining figures everywhere numeric"),
            html.Li("Branded empty state — aspire gradient + dashed border"),
            html.Li("Table-row hover slate-50 (reserves aspire-blue for chrome)"),
            html.Li(".medical-body-card centred SVG with brand drop shadow"),
            html.Li(".athlete-mini-card hairline header divider + 16 px ring gap"),
            html.Li(".section-title-v2 brand lozenge marker"),
            html.Li(".financial-report.serif Source Serif Pro opt-in"),
        ], style={"fontSize": "13px", "color": "#475569",
                   "lineHeight": "1.7", "paddingLeft": "20px"}),

    ], style={"padding": "24px"})
