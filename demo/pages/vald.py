"""VALD — ForceDecks / DynaMo visualisation conventions.

VALD components currently live in DASH_VALD. This page documents the
conventions so when they get promoted to aspire_dash, palettes and
chart shapes stay consistent.
"""
import dash
import plotly.graph_objects as go
from dash import dcc, html

from ._shared import section, code_block

dash.register_page(__name__, path="/vald", title="VALD", name="VALD")


VALD_COLOURS = {
    "left":      "#0369a1",   # blue
    "right":     "#dc2626",   # red
    "asymmetric_ok":   "#16a34a",  # green
    "asymmetric_warn": "#fbbf24",  # amber
    "asymmetric_bad":  "#dc2626",  # red
}


def _asymmetry_bar(left_pct=53, right_pct=47):
    """Single-row asymmetry bar — coloured by deviation from 50/50."""
    deviation = abs(left_pct - 50)
    bar_color = ("#16a34a" if deviation < 5 else
                 "#fbbf24" if deviation < 10 else "#dc2626")
    return html.Div([
        html.Div([
            html.Div(f"{left_pct}% L", style={"position": "absolute",
                                                "left": "8px", "top": "4px",
                                                "color": "white",
                                                "fontWeight": 700,
                                                "fontSize": "13px"}),
            html.Div(f"R {right_pct}%", style={"position": "absolute",
                                                  "right": "8px", "top": "4px",
                                                  "color": "white",
                                                  "fontWeight": 700,
                                                  "fontSize": "13px"}),
            html.Div(style={"width": f"{left_pct}%",
                             "background": VALD_COLOURS["left"],
                             "height": "100%", "float": "left"}),
            html.Div(style={"width": f"{right_pct}%",
                             "background": VALD_COLOURS["right"],
                             "height": "100%", "float": "left"}),
        ], style={"position": "relative", "height": "26px",
                   "borderRadius": "4px", "overflow": "hidden",
                   "border": f"2px solid {bar_color}"}),
    ], style={"marginBottom": "8px"})


def _jump_height_trend():
    sessions = list(range(1, 13))
    jh = [38.2, 39.1, 37.8, 38.9, 40.1, 41.5, 40.8, 42.0, 41.3,
           42.6, 43.1, 42.8]
    fig = go.Figure()
    fig.add_scatter(x=sessions, y=jh, mode="lines+markers",
                     marker_color=VALD_COLOURS["left"],
                     line=dict(width=2),
                     name="Jump height (cm)")
    fig.update_layout(
        height=200, margin=dict(t=20, b=40, l=40, r=10),
        template="simple_white",
        xaxis_title="Session #",
        yaxis_title="cm",
    )
    fig.add_hrect(y0=38, y1=44, fillcolor="#dbeafe",
                   opacity=0.3, line_width=0,
                   annotation_text="Adaptive range",
                   annotation_position="top left")
    return fig


def _peak_force_lr():
    sessions = list(range(1, 9))
    left  = [1850, 1900, 1920, 1880, 1950, 1980, 1995, 2010]
    right = [1820, 1860, 1870, 1810, 1880, 1920, 1925, 1940]
    fig = go.Figure()
    fig.add_bar(x=sessions, y=left,  name="Left",
                 marker_color=VALD_COLOURS["left"])
    fig.add_bar(x=sessions, y=right, name="Right",
                 marker_color=VALD_COLOURS["right"])
    fig.update_layout(
        height=220, margin=dict(t=20, b=40, l=40, r=10),
        barmode="group", template="simple_white",
        xaxis_title="Session #",
        yaxis_title="Peak force (N)",
        legend=dict(orientation="h", y=-0.25),
    )
    return fig


def layout():
    return html.Div([
        html.H1("VALD", style={"fontSize": "28px", "fontWeight": 700,
                                 "marginBottom": "8px"}),
        html.P("ForceDecks / DynaMo conventions — left/right asymmetry, "
                "jump-height trends, adaptive ranges. Components live in "
                "DASH_VALD today; promote here when first reused.",
                style={"color": "#64748b", "fontSize": "14px",
                       "marginBottom": "24px"}),

        section("Left/right asymmetry bar",
                 "Blue = left, red = right. Border colour: green (<5%), "
                 "amber (5-10%), red (>10%). Compact enough for tables."),
        _asymmetry_bar(53, 47),
        _asymmetry_bar(58, 42),
        _asymmetry_bar(63, 37),

        section("Jump height trend",
                 "Session-by-session line with adaptive-range band (blue "
                 "shaded). The band updates from rolling mean ± SD."),
        dcc.Graph(figure=_jump_height_trend(),
                   config={"displayModeBar": False},
                   style={"marginBottom": "18px"}),

        section("Peak force, left vs right (per session)",
                 "Grouped bars. Useful for catching unilateral regression "
                 "before it shows in jump height."),
        dcc.Graph(figure=_peak_force_lr(),
                   config={"displayModeBar": False},
                   style={"marginBottom": "18px"}),

        section("Palette tokens"),
        code_block(
            "VALD_COLOURS = {\n"
            "    'left':              '#0369a1',  # blue\n"
            "    'right':             '#dc2626',  # red\n"
            "    'asymmetric_ok':     '#16a34a',  # <5%\n"
            "    'asymmetric_warn':   '#fbbf24',  # 5-10%\n"
            "    'asymmetric_bad':    '#dc2626',  # >10%\n"
            "}\n\n"
            "# Adaptive-range band: rolling 8-session mean ± SD\n"
            "# (see aspire_dash.timeseries.build_adaptive_traces)"
        ),

        html.Div([
            html.A("→ See live in DASH_VALD",
                    href="https://posit.aspire.qa/connect/#/apps?search=vald",
                    target="_blank",
                    style={"fontSize": "12px", "color": "#0369a1"}),
        ]),
    ], style={"padding": "24px"})
