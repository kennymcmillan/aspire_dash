"""Whoop — wearable visualisation conventions.

Whoop-specific components don't live in aspire_dash yet — they're still
embedded in whoop_coach_dashboard. This page documents the conventions
so when we promote them, they ship with consistent palettes.
"""
import dash
import plotly.graph_objects as go
from dash import dcc, html

from ._shared import section, code_block

dash.register_page(__name__, path="/whoop", title="Whoop", name="Whoop")


# Whoop palette — green/amber/red recovery, royal-purple strain
WHOOP_COLOURS = {
    "recovery_high":   "#16a34a",   # green
    "recovery_mid":    "#fbbf24",   # amber
    "recovery_low":    "#dc2626",   # red
    "strain":          "#6366f1",   # indigo
    "sleep_deep":      "#1e3a8a",   # navy
    "sleep_rem":       "#8b5cf6",   # purple
    "sleep_light":     "#93c5fd",   # pale blue
    "sleep_awake":     "#e5e7eb",   # slate-200
}


def _recovery_donut():
    fig = go.Figure(go.Pie(
        values=[68, 32], labels=["Recovered", ""],
        marker_colors=["#16a34a", "#e5e7eb"],
        hole=0.7, sort=False, textinfo="none",
        showlegend=False,
    ))
    fig.update_layout(
        height=160, margin=dict(t=10, b=10, l=10, r=10),
        annotations=[{"text": "<b>68</b><br>Recovery",
                       "x": 0.5, "y": 0.5, "showarrow": False,
                       "font": {"size": 16, "color": "#0f172a"}}],
        template="simple_white",
    )
    return fig


def _strain_chart():
    days = [f"D-{i}" for i in range(6, -1, -1)]
    strain = [12.3, 15.8, 8.4, 18.6, 14.2, 16.9, 11.5]
    fig = go.Figure(go.Bar(x=days, y=strain,
                            marker_color=WHOOP_COLOURS["strain"]))
    fig.update_layout(
        height=200, margin=dict(t=20, b=40, l=30, r=10),
        template="simple_white",
        yaxis=dict(title="Daily Strain", range=[0, 21]),
    )
    fig.add_hline(y=18, line_dash="dash", line_color="#dc2626",
                   annotation_text="High strain")
    return fig


def _sleep_stages():
    stages = ["Deep", "REM", "Light", "Awake"]
    minutes = [78, 95, 240, 22]
    colours = [WHOOP_COLOURS[k] for k in
                ("sleep_deep", "sleep_rem", "sleep_light", "sleep_awake")]
    fig = go.Figure(go.Bar(x=stages, y=minutes, marker_color=colours))
    fig.update_layout(
        height=200, margin=dict(t=20, b=40, l=30, r=10),
        template="simple_white",
        yaxis=dict(title="Minutes"),
    )
    return fig


def layout():
    return html.Div([
        html.H1("Whoop", style={"fontSize": "28px", "fontWeight": 700,
                                  "marginBottom": "8px"}),
        html.P("Wearable conventions for Whoop dashboards (recovery, strain, "
                "sleep). Components currently live in whoop_coach_dashboard; "
                "promote here when first reused.",
                style={"color": "#64748b", "fontSize": "14px",
                       "marginBottom": "24px"}),

        section("Recovery donut",
                 "0-33 red · 34-66 amber · 67-100 green. Big number "
                 "centred, ring shows percent."),
        html.Div(dcc.Graph(figure=_recovery_donut(),
                             config={"displayModeBar": False}),
                  style={"maxWidth": "200px", "marginBottom": "18px"}),

        section("Daily strain (week view)",
                 "Indigo bars, 0-21 scale. Dashed line at 18 = high strain "
                 "threshold."),
        dcc.Graph(figure=_strain_chart(),
                   config={"displayModeBar": False},
                   style={"marginBottom": "18px"}),

        section("Sleep stages",
                 "Stacked or grouped — Deep, REM, Light, Awake. Palette is "
                 "navy → purple → pale-blue → slate."),
        dcc.Graph(figure=_sleep_stages(),
                   config={"displayModeBar": False},
                   style={"marginBottom": "18px"}),

        section("Palette tokens", "Source: whoop_coach_dashboard convention."),
        code_block(
            "WHOOP_COLOURS = {\n"
            "    'recovery_high': '#16a34a',  # green\n"
            "    'recovery_mid':  '#fbbf24',  # amber\n"
            "    'recovery_low':  '#dc2626',  # red\n"
            "    'strain':        '#6366f1',  # indigo\n"
            "    'sleep_deep':    '#1e3a8a',  # navy\n"
            "    'sleep_rem':     '#8b5cf6',  # purple\n"
            "    'sleep_light':   '#93c5fd',  # pale blue\n"
            "    'sleep_awake':   '#e5e7eb',  # slate-200\n"
            "}"
        ),

        html.Div([
            html.A("→ See live in whoop_coach_dashboard",
                    href="https://posit.aspire.qa/connect/#/apps?search=whoop",
                    target="_blank",
                    style={"fontSize": "12px", "color": "#0369a1"}),
        ]),

        # ── Whoop 3-ring athlete card (v0.13.0) ──────────────────────────
        section("Whoop 3-ring athlete card (saved in lib as v0.13)",
                 "Drop the Whoop card into any future player dashboard "
                 "with one import. Recovery + Strain + Sleep rings inline."),
        html.Div([
            _athlete_card(
                "Ali Turki Owaida", "SENIOR · Fencing", "good",
                [(68,  68, "Recovery", "good"),
                 ("15.8", 75, "Strain",   "aspire"),
                 ("7h12", 72, "Sleep",    "good")],
            ),
            _athlete_card(
                "Mohammed AlHazaa", "SENIOR · Fencing", "warn",
                [(42,  42, "Recovery", "warn"),
                 ("18.6", 88, "Strain",   "danger"),
                 ("5h48", 58, "Sleep",    "warn")],
            ),
            _athlete_card(
                "Khaled Hussein", "SENIOR · Fencing", "danger",
                [(23,  23, "Recovery", "danger"),
                 ("20.3", 95, "Strain",   "danger"),
                 ("4h32", 45, "Sleep",    "danger")],
            ),
        ], style={"display": "grid",
                   "gridTemplateColumns": "repeat(3, 1fr)",
                   "gap": "12px", "marginBottom": "12px"}),
        code_block(
            "from aspire_dash.v12_helpers import athlete_card_rings\n\n"
            "athlete_card_rings(\n"
            '    "Ali Turki Owaida", meta="SENIOR · Fencing", tone="good",\n'
            "    rings=[\n"
            '        {"value": 68,     "pct": 68, "label": "Recovery", "tone": "good"},\n'
            '        {"value": "15.8", "pct": 75, "label": "Strain",   "tone": "aspire"},\n'
            '        {"value": "7h12", "pct": 72, "label": "Sleep",    "tone": "good"},\n'
            "    ],\n"
            ")"
        ),
    ], style={"padding": "24px"})


# Local helper — imports v0.13's athlete_card_rings with the right shape
def _athlete_card(name, meta, tone, rings):
    from aspire_dash.v12_helpers import athlete_card_rings
    return athlete_card_rings(
        name, meta=meta, tone=tone,
        rings=[{"value": v, "pct": p, "label": l, "tone": t}
               for v, p, l, t in rings],
    )
