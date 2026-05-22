"""VALD — exact ForceDecks graphs lifted from the DASH_VALD app."""
import datetime as dt
import numpy as np
import dash
from dash import dcc, html

from aspire_dash.vald import (
    analytics_chart, cmj_panel_chart, group_heatmap,
    vald_cmj_grid, GRAPH_CONFIG, VALD_COLORS,
)
from aspire_dash.stats import compute_stats

from ._shared import section, code_block

dash.register_page(__name__, path="/vald", title="VALD", name="VALD")


# ── Sample data — synthetic but shape-matches real VALD output ───────────
np.random.seed(42)
_DATES = [(dt.date(2026, 1, 5) + dt.timedelta(weeks=i)).isoformat()
           for i in range(20)]


def _synth(base, sd, trend=0.0):
    return [round(base + trend * i + np.random.normal(0, sd), 2)
            for i in range(20)]


_PANELS = [
    {"title": "Jump Height (cm)",       "unit": " cm",  "color": "#01b8aa",
      "values": _synth(38.5, 1.4, 0.1)},
    {"title": "Peak Power (W/kg)",      "unit": " W/kg", "color": "#f59e0b",
      "values": _synth(48.0, 2.2, 0.05)},
    {"title": "Concentric Imp. (N·s)",  "unit": " N·s",  "color": "#7c3aed",
      "values": _synth(220, 8.0, 0.3)},
    {"title": "RSI (m/s)",               "unit": " m/s",  "color": "#dc2626",
      "values": _synth(1.85, 0.12, 0.005)},
]


def _data_points(values):
    return [{"date": d, "value": v} for d, v in zip(_DATES, values)]


def layout():
    panels = [{
        "title": p["title"],
        "color": p["color"],
        "figure": cmj_panel_chart(
            _data_points(p["values"]),
            compute_stats(p["values"]),
            color=p["color"], unit=p["unit"],
            mode="sd_bands",
        ),
    } for p in _PANELS]

    # Large analytics chart for the main metric
    main = _PANELS[0]
    analytics_fig = analytics_chart(
        _data_points(main["values"]),
        compute_stats(main["values"]),
        mode="sd_bands", color=main["color"],
        unit=main["unit"],
        metric_name=main["title"],
    )

    # Group heatmap — 6 athletes, last 8 dates
    athletes = ["A. Owaida", "K. Hussein", "M. AlHazaa",
                 "O. Karim", "Y. Saleh", "F. Bashir"]
    group_data = [{
        "name": n,
        "dates":  _DATES[-8:],
        "values": _synth(38.5, 2.0)[-8:],
    } for n in athletes]
    heatmap_fig = group_heatmap(group_data, unit=" cm")

    return html.Div([
        html.H1("VALD — exact ForceDecks graphs",
                style={"fontSize": "28px", "fontWeight": 700,
                       "marginBottom": "6px"}),
        html.P("Verbatim port from DASH_VALD. Inter font + dotted grid + "
                "VALD-exact 17-key palette + SD/MA/Acute/Adaptive overlays. "
                "Drop these into any future Aspire app — same look, no "
                "per-app reimplementation.",
                style={"color": "#64748b", "fontSize": "14px",
                       "marginBottom": "24px"}),

        section("vald_cmj_grid — CMJ 4-panel dashboard"),
        vald_cmj_grid(panels),
        code_block(
            "from aspire_dash.vald import vald_cmj_grid, cmj_panel_chart\n"
            "from aspire_dash.stats import compute_stats\n\n"
            "panels = [\n"
            "    {'title': 'Jump Height (cm)', 'color': '#01b8aa',\n"
            "     'figure': cmj_panel_chart(jh_data,\n"
            "                                compute_stats(jh_values),\n"
            "                                color='#01b8aa', unit=' cm',\n"
            "                                mode='sd_bands')},\n"
            "    # ... 3 more panels\n"
            "]\n"
            "vald_cmj_grid(panels)\n"
        ),

        section("analytics_chart — single large chart (sd_bands mode)"),
        html.Div([
            dcc.Graph(figure=analytics_fig, config=GRAPH_CONFIG),
        ], className="card", style={"padding": "16px"}),

        section("4 overlay modes — single panel, mode keyword changes overlay"),
        html.Div([
            _mode_card("sd_bands",  main),
            _mode_card("4pt_ma",    main),
            _mode_card("acute",     main),
            _mode_card("adaptive",  main, fallback=True),
        ], style={"display": "grid",
                   "gridTemplateColumns": "repeat(2, 1fr)",
                   "gap": "12px"}),
        code_block(
            "cmj_panel_chart(data, stats, mode='sd_bands')   # ±1/±2 SD bands\n"
            "cmj_panel_chart(data, stats, mode='4pt_ma')     # 4pt moving avg + ±1 SD blue\n"
            "cmj_panel_chart(data, stats, mode='acute')      # rolling ±1.5 SD amber\n"
            "cmj_panel_chart(data, stats, mode='adaptive',\n"
            "                adaptive_obs=...)                # Bayesian LAR/UAR emerald\n"
        ),

        section("group_heatmap — athletes × dates Z-score"),
        html.Div([
            dcc.Graph(figure=heatmap_fig, config=GRAPH_CONFIG),
        ], className="card", style={"padding": "16px"}),
        code_block(
            "from aspire_dash.vald import group_heatmap\n\n"
            "group_heatmap([\n"
            "    {'name': 'A. Owaida', 'dates': [...], 'values': [...]},\n"
            "    {'name': 'K. Hussein', 'dates': [...], 'values': [...]},\n"
            "    # one entry per athlete\n"
            "], unit=' cm')\n"
        ),

        section("VALD_COLORS — exact 17-key palette"),
        html.Div([
            html.Div([
                html.Div(style={
                    "width": "22px", "height": "22px",
                    "borderRadius": "4px", "background": v,
                    "border": "1px solid rgba(15,23,42,0.1)",
                }),
                html.Code(k, style={"fontSize": "10.5px",
                                       "color": "#475569",
                                       "marginLeft": "8px",
                                       "fontFamily": "monospace"}),
            ], style={"display": "flex", "alignItems": "center",
                       "marginBottom": "4px"})
            for k, v in VALD_COLORS.items()
        ], className="card",
           style={"padding": "16px",
                   "columns": 3, "columnGap": "24px"}),

    ], style={"padding": "24px"})


def _mode_card(mode, panel, fallback=False):
    fig = cmj_panel_chart(
        _data_points(panel["values"]),
        compute_stats(panel["values"]),
        color=panel["color"], unit=panel["unit"],
        mode=mode,
    )
    label = f"mode='{mode}'"
    if fallback:
        label += "  (no adaptive_obs → falls back to sd_bands)"
    return html.Div([
        html.Div(label, style={
            "fontSize": "11px", "fontWeight": 600,
            "color": "#374151", "textTransform": "uppercase",
            "letterSpacing": "0.5px", "marginBottom": "6px",
            "fontFamily": "monospace",
        }),
        dcc.Graph(figure=fig, config=GRAPH_CONFIG),
    ], className="card", style={"padding": "14px"})
