"""v0.18 — anthropometric module + sport federation + competition card + world map."""
import dash
import pandas as pd
import numpy as np
from dash import dcc, html

from aspire_dash.anthropometric import (
    somatochart, athlete_snapshot_card, limb_symmetry_bar,
)
from aspire_dash.sports import (
    source_badge, competition_card, world_map,
)

from ._shared import section, code_block

dash.register_page(__name__, path="/v18", title="v0.18", name="✨ v0.18 New")


# Sample data
_WORLD_DF = pd.DataFrame({
    "iso": ["QAT", "EGY", "KSA", "UAE", "BRN", "OMN", "KWT",
            "FRA", "ITA", "USA", "JPN", "KOR", "CHN", "GBR", "GER"],
    "medals": [12, 8, 7, 6, 5, 4, 3, 18, 16, 22, 14, 12, 20, 10, 11],
})


def layout():
    return html.Div([
        html.H1("v0.18 — Anthropometric + Fencing extractions",
                style={"fontSize": "28px", "fontWeight": 700,
                       "marginBottom": "8px"}),
        html.P("Heath-Carter somatochart, athlete snapshot card, limb "
                "symmetry bar (Ruwwad pattern). Plus sport-agnostic source "
                "badge / competition card / world map (Fencing reports pattern).",
                style={"color": "#64748b", "fontSize": "14px",
                       "marginBottom": "24px"}),

        # ── Anthropometric ───────────────────────────────────────────────
        section("somatochart — Heath-Carter triangle"),
        html.Div([
            dcc.Graph(figure=somatochart([
                {"name": "Ali",      "endo": 1.8, "meso": 5.0, "ecto": 2.3},
                {"name": "Khaled",   "endo": 2.5, "meso": 4.2, "ecto": 3.1},
                {"name": "Mohammed", "endo": 3.0, "meso": 4.8, "ecto": 1.9},
            ]), config={"displayModeBar": False}),
        ], className="card"),
        code_block(
            "from aspire_dash.anthropometric import somatochart\n\n"
            "somatochart([\n"
            "    {'name': 'Ali',    'endo': 1.8, 'meso': 5.0, 'ecto': 2.3},\n"
            "    {'name': 'Khaled', 'endo': 2.5, 'meso': 4.2, 'ecto': 3.1},\n"
            "])"
        ),

        section("athlete_snapshot_card — Ruwwad attribute table"),
        athlete_snapshot_card("Ruwwad Snapshot — Ibrahim Al-Naimi", [
            {"label": "Body Mass",      "value": "83.5", "unit": "kg"},
            {"label": "Stature",         "value": "184.6", "unit": "cm"},
            {"label": "BMI",             "value": "24.5", "unit": "kg/m²"},
            {"label": "Sum of 8 SF",     "value": "56.4", "unit": "mm"},
            {"label": "Sum of 4 SF",     "value": "27.7", "unit": "mm"},
            {"label": "Body Fat %",      "value": "12.1", "unit": "%"},
            {"label": "Fat Free Mass",   "value": "73.4", "unit": "kg"},
            {"label": "Fat Mass",        "value": "10.1", "unit": "kg"},
            {"label": "Somatotype",      "value": "1.8 - 5.0 - 2.3",
             "unit": ""},
        ]),
        code_block(
            "from aspire_dash.anthropometric import athlete_snapshot_card\n\n"
            "athlete_snapshot_card('Athlete Snapshot', [\n"
            "    {'label': 'Body Mass',  'value': '83.5', 'unit': 'kg'},\n"
            "    {'label': 'Stature',    'value': '184.6', 'unit': 'cm'},\n"
            "    {'label': 'BMI',        'value': '24.5', 'unit': 'kg/m²'},\n"
            "    {'label': 'Somatotype', 'value': '1.8 - 5.0 - 2.3', 'unit': ''},\n"
            "])"
        ),

        section("limb_symmetry_bar — L/R proportionality (Ruwwad style)"),
        html.Div([
            limb_symmetry_bar("Arm Relaxed",      31.9, 31.9),  # 99.8%
            limb_symmetry_bar("Proximal Thigh",   60.5, 61.0),  # 99.1%
            limb_symmetry_bar("Mid-Thigh",        56.7, 57.3),  # 99.0%
            limb_symmetry_bar("Distal Thigh",     44.7, 45.9),  # 98.2%
            limb_symmetry_bar("Calf (max)",       38.2, 37.5),  # 98.0%
        ], className="card", style={"padding": "16px"}),
        code_block(
            "from aspire_dash.anthropometric import limb_symmetry_bar\n\n"
            "limb_symmetry_bar('Mid-Thigh', 56.7, 57.3)"
        ),

        # ── Sport federation + competition card ──────────────────────────
        section("source_badge — sport-federation tag"),
        html.Div([
            source_badge("FIE"),     source_badge("EuroF"), source_badge("FTL"),
            source_badge("PSA"),     source_badge("ESF"),   source_badge("ASF"),
            source_badge("ITTF"),    source_badge("WTT"),
            source_badge("WA"),      source_badge("Tila"),
            source_badge("FIP"),     source_badge("WPT"),
            source_badge("FINA"),    source_badge("Olympic"),
            source_badge("GCC"),     source_badge("Unknown"),
        ], style={"display": "flex", "flexWrap": "wrap", "gap": "6px",
                   "padding": "16px", "background": "white",
                   "borderRadius": "8px",
                   "border": "1px solid var(--slate-200)",
                   "marginBottom": "12px"}),
        code_block(
            "from aspire_dash.sports import source_badge\n\n"
            "source_badge('FIE')\n"
            "source_badge('Top 8', federation='FIE')  # custom label, FIE colours\n"
            "source_badge('PSA')   # squash auto-coloured"
        ),

        section("competition_card — career-feed pattern"),
        html.Div([
            competition_card("Cairo World Cup", date="2026-04-12",
                              location="Cairo · EGY",
                              result="Top 8", placement=5,
                              federation="FIE", category="Sabre M"),
            competition_card("Asian Championships",
                              date="2026-03-08",
                              location="Tashkent · UZB",
                              result="Gold", placement=1,
                              federation="FIE",
                              category="Sabre M Individual"),
            competition_card("GCC Games Doha 2026",
                              date="2026-05-18",
                              location="Doha · QAT",
                              result="Silver", placement=2,
                              federation="GCC",
                              category="Sabre M Team"),
        ], style={"display": "grid",
                   "gridTemplateColumns": "repeat(auto-fill, minmax(280px, 1fr))",
                   "gap": "12px", "marginBottom": "12px"}),
        code_block(
            "from aspire_dash.sports import competition_card\n\n"
            "competition_card(\n"
            "    'Cairo World Cup', date='2026-04-12',\n"
            "    location='Cairo · EGY', placement=5, result='Top 8',\n"
            "    federation='FIE', category='Sabre M',\n"
            ")"
        ),

        # ── World map ────────────────────────────────────────────────────
        section("world_map — Aspire choropleth with QAT gold highlight"),
        html.Div([
            dcc.Graph(figure=world_map(
                _WORLD_DF, country_col="iso", value_col="medals",
                highlight_country="QAT",
            ), config={"displayModeBar": False}),
        ], className="card"),
        code_block(
            "from aspire_dash.sports import world_map\n\n"
            "world_map(df, country_col='iso', value_col='medals',\n"
            "          highlight_country='QAT')"
        ),

    ], style={"padding": "24px"})
