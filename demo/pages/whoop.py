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

        # ── athlete_card_v2 — Whoop-style premium card (v0.26+) ─────────
        section("athlete_card_v2 — premium card w/ face photo + zone gradient",
                 "v0.26 added 56 px photo + zone-coloured top-left gradient. "
                 "v0.30.1 added per-ring colour override + gradient ring stroke. "
                 "v0.31.4 added 🎯 target-athlete indicator."),
        html.Div([
            _card_v2("Ali Turki Owaida", "SENIOR · Fencing", "green",
                      photo_url="https://i.pravatar.cc/100?img=11",
                      rings=[(68, 68, "Recovery", "#16a34a"),
                             ("15.8", 75, "Strain", "#004185"),
                             ("7h12", 72, "Sleep", "#16a34a")],
                      is_target=True),
            _card_v2("Mohammed AlHazaa", "SENIOR · Fencing", "yellow",
                      photo_url=None,  # initials fallback
                      rings=[(42, 42, "Recovery", "#d97706"),
                             ("18.6", 88, "Strain", "#dc2626"),
                             ("5h48", 58, "Sleep", "#d97706")]),
            _card_v2("Khaled Hussein", "SENIOR · Fencing", "red",
                      photo_url="https://i.pravatar.cc/100?img=33",
                      rings=[(23, 23, "Recovery", "#dc2626"),
                             ("20.3", 95, "Strain", "#dc2626"),
                             ("4h32", 45, "Sleep", "#dc2626")],
                      is_target=True),
        ], style={"display": "grid",
                   "gridTemplateColumns": "repeat(3, 1fr)",
                   "gap": "16px", "marginBottom": "12px"}),
        code_block(
            "from aspire_dash.athlete import athlete_card_v2\n\n"
            "athlete_card_v2(\n"
            '    "Ali Turki Owaida", meta="SENIOR · Fencing", zone="green",\n'
            '    photo_url="https://...",   # SAMS imageUrl/profileImageUrl\n'
            "    is_target=True,            # 🎯 Aspire pathway indicator\n"
            "    rings=[\n"
            '        {"value": 68,     "pct": 68, "label": "Recovery", "color": "#16a34a"},\n'
            '        {"value": "15.8", "pct": 75, "label": "Strain",   "color": "#004185"},\n'
            '        {"value": "7h12", "pct": 72, "label": "Sleep",    "color": "#16a34a"},\n'
            "    ],\n"
            ")"
        ),

        # ── athlete_card_compact — denser variant (v0.31) ───────────────
        section("athlete_card_compact — dense variant (4+ across)",
                 "Smaller 40 px avatar + 48 px rings + optional bottom stats "
                 "row (HRV / RHR / Deep). Use for squad grids when you need "
                 "more cards visible."),
        html.Div([
            _card_compact("Ali Turki Owaida", "Fencing", "green",
                           photo_url="https://i.pravatar.cc/100?img=11",
                           rings=[(68, 68, "Recovery", "#16a34a"),
                                  ("15.8", 75, "Strain", "#004185"),
                                  ("7h12", 72, "Sleep", "#16a34a")],
                           stats=[("HRV", "62 ms", None),
                                  ("RHR", "52 bpm", "green"),
                                  ("Deep", "98 m", None)],
                           is_target=True),
            _card_compact("Mohammed AlHazaa", "Fencing", "yellow",
                           photo_url=None,
                           rings=[(42, 42, "Recovery", "#d97706"),
                                  ("18.6", 88, "Strain", "#dc2626"),
                                  ("5h48", 58, "Sleep", "#d97706")],
                           stats=[("HRV", "48 ms", None),
                                  ("RHR", "61 bpm", "yellow"),
                                  ("Deep", "76 m", None)]),
            _card_compact("Khaled Hussein", "Fencing", "red",
                           photo_url="https://i.pravatar.cc/100?img=33",
                           rings=[(23, 23, "Recovery", "#dc2626"),
                                  ("20.3", 95, "Strain", "#dc2626"),
                                  ("4h32", 45, "Sleep", "#dc2626")],
                           stats=[("HRV", "38 ms", None),
                                  ("RHR", "68 bpm", "red"),
                                  ("Deep", "52 m", None)]),
            _card_compact("Ziad Morsy", "Swimming", "aspire",
                           photo_url=None,
                           rings=[(55, 55, "Recovery", "#0059b3"),
                                  ("12.4", 60, "Strain", "#004185"),
                                  ("6h30", 65, "Sleep", "#0059b3")],
                           stats=[("HRV", "54 ms", None),
                                  ("RHR", "57 bpm", "aspire"),
                                  ("Deep", "82 m", None)]),
        ], style={"display": "grid",
                   "gridTemplateColumns": "repeat(4, 1fr)",
                   "gap": "12px", "marginBottom": "12px"}),
        code_block(
            "from aspire_dash.athlete import athlete_card_compact\n\n"
            "athlete_card_compact(\n"
            '    "Ali Owaida", meta="Fencing", zone="green",\n'
            '    photo_url="https://...",\n'
            "    is_target=True,\n"
            "    rings=[{...}, {...}, {...}],\n"
            "    stats=[\n"
            '        {"label": "HRV", "value": "62 ms"},\n'
            '        {"label": "RHR", "value": "52 bpm", "status_dot": "green"},\n'
            '        {"label": "Deep", "value": "98 m"},\n'
            "    ],\n"
            ")"
        ),

        # ── radial_multi_track — concentric ring chart (v0.35) ──────────
        section("radial_multi_track — concentric ring chart (v0.35)",
                 "Three (or more) metrics stacked as concentric rings — "
                 "outer/middle/inner. Apex-style. Packs multiple progress "
                 "signals into one tile. Better than 3-ring row for "
                 "small dashboard tiles."),
        html.Div([
            _radial_demo(),
        ], style={"display": "grid",
                   "gridTemplateColumns": "repeat(2, 1fr)",
                   "gap": "16px", "marginBottom": "12px"}),
        code_block(
            "from aspire_dash.v12_helpers import radial_multi_track\n\n"
            "radial_multi_track([\n"
            '    {"value": "68%", "pct": 68, "label": "Recovery", "color": "#16a34a"},\n'
            '    {"value": "75%", "pct": 75, "label": "Strain",   "color": "#004185"},\n'
            '    {"value": "72%", "pct": 72, "label": "Sleep",    "color": "#fbb800"},\n'
            "])"
        ),

        # ── progress_stack — stacked horizontal bar (v0.33) ─────────────
        section("progress_stack — stacked horizontal bar (v0.33)",
                 "Tremor 'Category Bar' pattern — proportional segments "
                 "with inline labels + legend strip below. For budget "
                 "allocations, athlete-readiness breakdowns, sport-medal "
                 "splits."),
        html.Div([
            _progress_demo(),
        ], style={"marginBottom": "12px"}),
        code_block(
            "from aspire_dash.v12_helpers import progress_stack\n\n"
            "progress_stack(\n"
            "    label='Squad readiness breakdown',\n"
            "    items=[\n"
            '        {"label": "Ready",   "value": 12, "color": "#16a34a"},\n'
            '        {"label": "Caution", "value":  6, "color": "#d97706"},\n'
            '        {"label": "Alert",   "value":  3, "color": "#dc2626"},\n'
            "    ],\n"
            ")"
        ),
    ], style={"padding": "24px"})


def _radial_demo():
    from aspire_dash.v12_helpers import radial_multi_track
    return radial_multi_track([
        {"value": "68%", "pct": 68, "label": "Recovery", "color": "#16a34a"},
        {"value": "75%", "pct": 75, "label": "Strain",   "color": "#004185"},
        {"value": "72%", "pct": 72, "label": "Sleep",    "color": "#fbb800"},
    ])


def _progress_demo():
    from aspire_dash.v12_helpers import progress_stack
    return progress_stack(
        label="Squad readiness breakdown",
        items=[
            {"label": "Ready",   "value": 12, "color": "#16a34a"},
            {"label": "Caution", "value":  6, "color": "#d97706"},
            {"label": "Alert",   "value":  3, "color": "#dc2626"},
        ],
    )


def _card_v2(name, meta, zone, photo_url, rings, is_target=False):
    from aspire_dash.athlete import athlete_card_v2
    return athlete_card_v2(
        name, meta=meta, zone=zone, photo_url=photo_url, is_target=is_target,
        rings=[{"value": v, "pct": p, "label": l, "color": c}
               for v, p, l, c in rings],
    )


def _card_compact(name, meta, zone, photo_url, rings, stats, is_target=False):
    from aspire_dash.athlete import athlete_card_compact
    return athlete_card_compact(
        name, meta=meta, zone=zone, photo_url=photo_url, is_target=is_target,
        rings=[{"value": v, "pct": p, "label": l, "color": c}
               for v, p, l, c in rings],
        stats=[{"label": l, "value": v,
                 **({"status_dot": d} if d else {})}
               for l, v, d in stats],
    )


# Local helper — imports v0.13's athlete_card_rings with the right shape
def _athlete_card(name, meta, tone, rings):
    from aspire_dash.v12_helpers import athlete_card_rings
    return athlete_card_rings(
        name, meta=meta, tone=tone,
        rings=[{"value": v, "pct": p, "label": l, "tone": t}
               for v, p, l, t in rings],
    )
