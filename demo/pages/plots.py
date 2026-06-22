"""v0.17 chart collection — 11 sport-dashboard Plotly helpers."""
import dash
import pandas as pd
import numpy as np
from dash import dcc, html

from aspire_dash import plots as p

from ._shared import section, code_block

dash.register_page(__name__, path="/plots", title="Plots",
                    name="✨ v0.17 Plots")


# Sample data shared across panels
np.random.seed(0)
_SPORTS = ["Fencing", "Padel", "Squash", "Swimming", "Athletics"]
_DF_RHR = pd.DataFrame({
    "sport": np.repeat(_SPORTS, 30),
    "rhr":   np.concatenate([
        np.random.normal(55, 4, 30),  # Fencing
        np.random.normal(62, 6, 30),  # Padel
        np.random.normal(60, 5, 30),  # Squash
        np.random.normal(48, 3, 30),  # Swimming
        np.random.normal(52, 4, 30),  # Athletics
    ]),
})
_DF_MEDALS = pd.DataFrame([
    {"sport": s, "discipline": d, "count": c}
    for s, d, c in [
        ("Swimming",  "50 Free",   3), ("Swimming",  "100 Breast", 2),
        ("Athletics", "1500m",     2), ("Athletics", "Long Jump",  1),
        ("Fencing",   "Sabre",     5), ("Fencing",   "Epée",       3),
        ("Padel",     "Doubles",   2),
    ]
])
_DF_CAL = pd.DataFrame({
    "date":     pd.date_range("2026-01-01", "2026-05-22", freq="D"),
    "training": np.random.choice([0, 0, 30, 45, 60, 75, 90], 142),
})
_DF_BEFORE_AFTER = pd.DataFrame({
    "athlete": ["Ali", "Khaled", "Omar", "Mohammed", "Yousef"],
    "before":  [38.5, 41.2, 39.8, 42.1, 37.6],
    "after":   [41.0, 40.5, 42.4, 44.6, 39.1],
})


def _g(fig, label):
    return html.Div([
        html.Div(label, style={"fontSize": "12px", "fontWeight": 600,
                                "color": "#475569", "marginBottom": "4px"}),
        dcc.Graph(figure=fig, config={"displayModeBar": False}),
    ], className="card", style={"marginBottom": "12px"})


# Sample data for percentile_age_chart (High Jump development example)
_HJ_BANDS = [
    {"age": 13, "p10": 1.25, "p25": 1.35, "p50": 1.45, "p75": 1.58, "p90": 1.65},
    {"age": 14, "p10": 1.35, "p25": 1.45, "p50": 1.55, "p75": 1.65, "p90": 1.72},
    {"age": 15, "p10": 1.45, "p25": 1.55, "p50": 1.66, "p75": 1.78, "p90": 1.86},
    {"age": 16, "p10": 1.55, "p25": 1.66, "p50": 1.78, "p75": 1.92, "p90": 2.00},
    {"age": 17, "p10": 1.62, "p25": 1.74, "p50": 1.86, "p75": 2.00, "p90": 2.08},
    {"age": 18, "p10": 1.66, "p25": 1.80, "p50": 1.92, "p75": 2.06, "p90": 2.13},
]
_HJ_MARKS = [
    {"age": 15, "mark": 1.70}, {"age": 16, "mark": 1.85},
    {"age": 17, "mark": 1.97}, {"age": 18, "mark": 2.07, "pb": True},
]
_HJ_REF = [{"y": 2.08, "label": "U20 qualifying 2.08 m", "color": "#b3261e"}]
_HJ_OVERLAY = {"name": "Legend (same age)", "color": "#8A1538",
               "points": [{"age": 16, "mark": 2.06}, {"age": 17, "mark": 2.14},
                          {"age": 18, "mark": 2.27}]}


def layout():
    return html.Div([
        html.H1("v0.17 — chart collection",
                style={"fontSize": "28px", "fontWeight": 700,
                       "marginBottom": "8px"}),
        html.P("11 Plotly chart helpers with the Aspire template baked "
                "in. All take pandas dataframes (or label/value lists) "
                "and return a Figure ready to drop into dcc.Graph.",
                style={"color": "#64748b", "fontSize": "14px",
                       "marginBottom": "24px"}),

        section("Distribution charts"),
        _g(p.boxplot_by_group(_DF_RHR, "rhr", "sport"),
            "boxplot_by_group(df, 'rhr', 'sport')"),
        _g(p.violin_by_group(_DF_RHR, "rhr", "sport"),
            "violin_by_group(df, 'rhr', 'sport')"),
        _g(p.ridge_chart(_DF_RHR, "rhr", "sport"),
            "ridge_chart(df, 'rhr', 'sport')"),

        section("Hierarchy / proportion"),
        _g(p.sunburst(_DF_MEDALS, ["sport", "discipline"], "count"),
            "sunburst(df, ['sport', 'discipline'], 'count')"),
        _g(p.treemap(_DF_MEDALS, ["sport", "discipline"], "count"),
            "treemap(df, ['sport', 'discipline'], 'count')"),

        section("Time-series"),
        _g(p.calendar_heatmap(_DF_CAL, "date", "training"),
            "calendar_heatmap(df, 'date', 'training')"),

        section("Financial / accumulation"),
        _g(p.waterfall(
            labels=["Opening", "Lessons", "Fencing", "S&C", "Travel"],
            values=[100_000, -22_000, -45_000, -18_000, -10_000],
        ), "waterfall(labels=[...], values=[...])"),

        section("Flow"),
        _g(p.sankey(
            source=[0, 0, 1, 2, 1],
            target=[2, 3, 3, 4, 4],
            value=[5, 8, 3, 2, 4],
            labels=["Recruit", "Junior", "Senior", "Elite", "Retired"],
        ), "sankey(source=[...], target=[...], value=[...], labels=[...])"),

        section("Comparison"),
        _g(p.radar(
            categories=["Speed", "Strength", "Stamina", "Skill", "Mental"],
            series=[
                {"name": "Ali",      "values": [78, 65, 82, 90, 70]},
                {"name": "Mohammed", "values": [70, 78, 75, 72, 85]},
            ],
        ), "radar(categories=[...], series=[{...}, {...}])"),
        _g(p.slope_chart(
            pd.DataFrame({
                "phase": ["Before"] * 5 + ["After"] * 5,
                "athlete": ["Ali", "Khaled", "Omar", "Mohammed", "Yousef"] * 2,
                "jump":   [38.5, 41.2, 39.8, 42.1, 37.6,
                            41.0, 40.5, 42.4, 44.6, 39.1],
            }),
            x="phase", y="jump", group="athlete",
        ), "slope_chart(df, x='phase', y='jump', group='athlete')"),
        _g(p.dumbbell(_DF_BEFORE_AFTER, "athlete", "before", "after"),
            "dumbbell(df, 'athlete', 'before', 'after')"),

        section("Development / benchmarking"),
        _g(p.percentile_age_chart(
            _HJ_BANDS, _HJ_MARKS, reference_lines=_HJ_REF, overlay=_HJ_OVERLAY,
            y_title="Height (m)", title="High Jump — mark vs age",
        ), "percentile_age_chart(bands, marks, reference_lines=..., overlay=...)"),

        code_block(
            "# Single import — every helper at your fingertips:\n"
            "from aspire_dash import plots\n\n"
            "fig = plots.boxplot_by_group(df, 'rhr', 'sport')\n"
            "fig = plots.calendar_heatmap(df, 'date', 'training')\n"
            "fig = plots.waterfall(labels=[...], values=[...])\n"
            "fig = plots.radar(categories=[...], series=[{...}, {...}])\n"
        ),
    ], style={"padding": "24px"})
