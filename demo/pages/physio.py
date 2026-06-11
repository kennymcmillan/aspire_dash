"""v0.57 — Physiology glow-up: rotating_stat + lactate_curve."""
import dash
import pandas as pd
from dash import html

from aspire_dash.v12_helpers import rotating_stat
from aspire_dash.sports_science import lactate_curve

from ._shared import section, code_block

dash.register_page(__name__, path="/physio", title="Physiology", name="🫁 Physiology")


_FACES = [
    {"label": "vVO₂max", "value": "18.1", "sub": "km/h", "delta": "+1.4", "delta_direction": "up"},
    {"label": "LT2 @ 4 mmol", "value": "15.2", "sub": "km/h", "delta": "+1.3", "delta_direction": "up"},
    {"label": "LT1 @ 2 mmol", "value": "13.7", "sub": "km/h", "delta": "+0.6", "delta_direction": "up"},
    {"label": "Peak VO₂", "value": "55.8", "sub": "ml/kg/min", "delta": "+2.1", "delta_direction": "up"},
    {"label": "La max", "value": "12.5", "sub": "mmol/L", "delta": "+3.4", "delta_direction": "down"},
]

_CURVES = {
    "14 Sep 2022": pd.DataFrame({
        "speed": [10, 12, 13, 14, 15, 16, 17],
        "la": [1.71, 1.89, 2.38, 3.28, 4.34, 6.1, 9.14],
        "hr": [158, 178, 186, 193, 200, 206, 210]}),
    "02 Oct 2025": pd.DataFrame({
        "speed": [12, 13, 14, 15, 16, 17],
        "la": [2.17, 1.43, 1.6, 2.24, 3.14, 4.49],
        "hr": [153, 163, 169, 172, 179, 185]}),
}


def layout():
    return html.Div([
        section("rotating_stat — auto-cycling KPI card (3 sizes)"),
        html.P("Pure-CSS 3D flip through 2–6 metric faces; gradient panel + "
               "accent rail, pill delta chip, active-dot highlight. No callbacks, "
               "pauses on hover, respects prefers-reduced-motion.",
               style={"fontSize": "13px", "color": "#475569", "marginBottom": "12px"}),
        html.Div([
            rotating_stat(_FACES, size="sm", seconds_per_face=2.4),
            rotating_stat(_FACES, size="md", seconds_per_face=2.6),
            rotating_stat(_FACES, size="lg", seconds_per_face=2.8),
        ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap",
                  "alignItems": "flex-start", "marginBottom": "12px"}),
        code_block(
            "from aspire_dash.v12_helpers import rotating_stat\n\n"
            "rotating_stat([\n"
            "    {'label': 'vVO₂max', 'value': '18.1', 'sub': 'km/h',\n"
            "     'delta': '+1.4', 'delta_direction': 'up'},\n"
            "    {'label': 'La max', 'value': '12.5', 'sub': 'mmol/L',\n"
            "     'delta': '+3.4', 'delta_direction': 'down'},\n"
            "], size='lg')"
        ),

        section("lactate_curve — step-test lactate vs speed + HR (dual axis)"),
        html.P("One curve per test date — click a date in the legend to toggle "
               "both its lactate + HR lines. Latest test boldest with soft fill; "
               "large circular points; emphasised LT2 (4 mmol) guide line.",
               style={"fontSize": "13px", "color": "#475569", "marginBottom": "12px"}),
        html.Div(lactate_curve(_CURVES), className="card",
                 style={"padding": "12px 16px"}),
        code_block(
            "from aspire_dash.sports_science import lactate_curve\n\n"
            "lactate_curve({\n"
            "    '14 Sep 2022': df_old,   # cols: speed, la, hr\n"
            "    '02 Oct 2025': df_new,\n"
            "})  # → dcc.Graph; as_graph=False returns the go.Figure"
        ),
    ], style={"padding": "24px"})
