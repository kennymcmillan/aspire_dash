"""v0.12.0 — all new components in one place.

Ported from tools/forge/ prototypes. The 10 patterns here lift the
whole library — every consumer app inherits them on next aspire_dash
bump."""
import dash
from dash import html

from aspire_dash.v12_helpers import (
    kpi_tile_v2, date_toolbar, status_pill_v2, athlete_card,
    aspire_grid_v2, aspire_loading, aspire_empty, sparkline_tile,
    injury_card, asymmetry_bar, metric_ring, athlete_card_rings,
)

from ._shared import section, example, code_block

dash.register_page(__name__, path="/v12", title="v0.12 New",
                    name="✨ v0.12.0 New")


def layout():
    return html.Div([
        html.H1("v0.12.0 — Forge-designed components",
                style={"fontSize": "28px", "fontWeight": 700,
                       "marginBottom": "8px"}),
        html.P("Ported from tools/forge/ Tailwind+DaisyUI prototypes. "
                "Whoop/Firstbeat-level polish, ready to drop into any "
                "consumer app via `from aspire_dash.v12_helpers import ...`.",
                style={"color": "#64748b", "fontSize": "14px",
                       "marginBottom": "24px"}),

        # 1. KPI tile v2
        section("1 · kpi_tile_v2 — delta arrows + accent stripes"),
        html.Div([
            kpi_tile_v2("Sessions", 423, delta="+12",
                          delta_direction="up", sub="vs last month",
                          accent="aspire"),
            kpi_tile_v2("Attendance", "87%", delta="+5%",
                          delta_direction="up", sub="vs last week",
                          accent="success"),
            kpi_tile_v2("At risk", 3, delta="-2",
                          delta_direction="down", sub="from yesterday",
                          accent="danger"),
            kpi_tile_v2("Pending", 12, delta="0",
                          delta_direction="flat", sub="unchanged",
                          accent="gold"),
        ], style={"display": "grid",
                   "gridTemplateColumns": "repeat(auto-fit, minmax(220px, 1fr))",
                   "gap": "12px", "marginBottom": "12px"}),
        code_block(
            "from aspire_dash.v12_helpers import kpi_tile_v2\n\n"
            'kpi_tile_v2("Sessions", 423,\n'
            '            delta="+12", delta_direction="up",\n'
            '            sub="vs last month", accent="aspire")'
        ),

        # 2. Date toolbar
        section("2 · date_toolbar — unified [◀ date ▶ TODAY]"),
        html.Div(
            date_toolbar(prev_id="dt-prev", next_id="dt-next",
                          today_id="dt-today",
                          display_text="22 May 2026",
                          display_id="dt-display"),
            style={"marginBottom": "12px"},
        ),
        code_block(
            "from aspire_dash.v12_helpers import date_toolbar\n\n"
            "date_toolbar(\n"
            '    prev_id="prev", next_id="next", today_id="today",\n'
            '    display_text="22 May 2026", display_id="date-display",\n'
            ")"
        ),

        # 3. Status pill v2
        section("3 · status_pill_v2 — leading icon + tone palette"),
        html.Div([
            status_pill_v2("Saved", tone="success"),
            status_pill_v2("Syncing", tone="info"),
            status_pill_v2("Stale", tone="warning"),
            status_pill_v2("Failed", tone="danger"),
            status_pill_v2("Idle", tone="neutral"),
        ], style={"display": "flex", "gap": "6px",
                   "flexWrap": "wrap", "marginBottom": "8px"}),
        html.Div([
            status_pill_v2("Active", tone="success", solid=True),
            status_pill_v2("Pending", tone="warning", solid=True),
            status_pill_v2("Sidelined", tone="danger", solid=True),
        ], style={"display": "flex", "gap": "6px",
                   "flexWrap": "wrap", "marginBottom": "12px"}),
        code_block(
            "from aspire_dash.v12_helpers import status_pill_v2\n\n"
            'status_pill_v2("Saved", tone="success")\n'
            'status_pill_v2("Failed", tone="danger", solid=True)'
        ),

        # 4. Athlete card
        section("4 · athlete_card — Whoop-style mini cards"),
        html.Div([
            athlete_card(
                "Ali Turki Owaida", meta="SENIOR · Fencing",
                score=68, tone="good",
                sub_metrics=[
                    {"label": "Strain", "value": "15.8"},
                    {"label": "HRV",    "value": "52ms"},
                    {"label": "Sleep",  "value": "7h12"},
                ],
            ),
            athlete_card(
                "Mohammed AlHazaa", meta="SENIOR · Fencing",
                score=42, tone="warn",
                sub_metrics=[
                    {"label": "Strain", "value": "18.6"},
                    {"label": "HRV",    "value": "38ms"},
                    {"label": "Sleep",  "value": "5h48"},
                ],
            ),
            athlete_card(
                "Khaled Hussein", meta="SENIOR · Fencing",
                score=23, tone="danger",
                sub_metrics=[
                    {"label": "Strain", "value": "20.3"},
                    {"label": "HRV",    "value": "28ms"},
                    {"label": "Sleep",  "value": "4h32"},
                ],
            ),
        ], style={"display": "grid",
                   "gridTemplateColumns": "repeat(auto-fit, minmax(220px, 1fr))",
                   "gap": "12px", "marginBottom": "12px"}),
        code_block(
            "from aspire_dash.v12_helpers import athlete_card\n\n"
            "athlete_card(\n"
            '    "Ali Turki Owaida", meta="SENIOR · Fencing",\n'
            '    score=68, tone="good",\n'
            "    sub_metrics=[\n"
            "        {'label': 'Strain', 'value': '15.8'},\n"
            "        {'label': 'HRV',    'value': '52ms'},\n"
            "        {'label': 'Sleep',  'value': '7h12'},\n"
            "    ],\n"
            ")"
        ),

        # 5. AG Grid Aspire theme
        section("5 · aspire_grid_v2 — branded AG Grid (uppercase blue header)"),
        html.Div(aspire_grid_v2(
            "v12-grid",
            columnDefs=[
                {"field": "fencer", "headerName": "Fencer", "pinned": "left"},
                {"field": "ag", "headerName": "AG"},
                {"field": "sessions", "headerName": "Sessions"},
                {"field": "min", "headerName": "Total min"},
            ],
            rowData=[
                {"fencer": "Ali Turki", "ag": "SENIOR", "sessions": 423, "min": 11505},
                {"fencer": "Khaled H.", "ag": "SENIOR", "sessions": 410, "min": 11220},
                {"fencer": "Omar Deif", "ag": "U17",    "sessions": 397, "min": 10845},
            ],
            height="180px",
        ), style={"overflowX": "auto", "maxWidth": "100%"}),
        code_block(
            "from aspire_dash.v12_helpers import aspire_grid_v2\n\n"
            "aspire_grid_v2('my-grid', columnDefs=[...], rowData=[...])"
        ),

        # 6 + 7 — loading + empty
        section("6 + 7 · aspire_loading + aspire_empty"),
        html.Div([
            html.Div(aspire_loading("Syncing SAMS data",
                                      "should take a few seconds..."),
                      style={"flex": 1, "border": "1px solid #e2e8f0",
                              "borderRadius": "8px", "background": "white"}),
            html.Div(aspire_empty("No sessions yet",
                                    "Coach hasn't logged any volumes for this period.",
                                    icon="fa-calendar-xmark"),
                      style={"flex": 1, "border": "1px solid #e2e8f0",
                              "borderRadius": "8px", "background": "white"}),
        ], style={"display": "flex", "gap": "12px",
                   "marginBottom": "12px"}),
        code_block(
            "from aspire_dash.v12_helpers import aspire_loading, aspire_empty\n\n"
            'aspire_loading("Syncing SAMS data", "should take a few seconds")\n'
            'aspire_empty("No sessions yet",\n'
            '             "Coach has not logged volumes",\n'
            '             icon="fa-calendar-xmark")'
        ),

        # 8. Sparkline tile
        section("8 · sparkline_tile — KPI + inline mini-line-chart"),
        html.Div([
            sparkline_tile("Daily strain", 15.8,
                            series=[12, 14, 18, 16, 17, 19, 15.8],
                            delta="+0.7", delta_direction="up",
                            color="#6366f1"),
            sparkline_tile("Recovery", 68,
                            series=[55, 62, 70, 60, 72, 65, 68],
                            delta="-4", delta_direction="down",
                            color="#16a34a"),
            sparkline_tile("Sleep hrs", 7.2,
                            series=[6.8, 7.5, 8.0, 6.2, 7.0, 7.4, 7.2],
                            delta="+0.2", delta_direction="up",
                            color="#0369a1"),
        ], style={"display": "grid",
                   "gridTemplateColumns": "repeat(auto-fit, minmax(220px, 1fr))",
                   "gap": "12px", "marginBottom": "12px"}),
        code_block(
            "from aspire_dash.v12_helpers import sparkline_tile\n\n"
            "sparkline_tile('Daily strain', 15.8,\n"
            "               series=[12, 14, 18, 16, 17, 19, 15.8],\n"
            "               delta='+0.7', delta_direction='up',\n"
            "               color='#6366f1')"
        ),

        # 8b. Sparkline tile — accent / zone / empty modifiers (v0.67)
        section("8b · sparkline_tile modifiers — group accent, asymmetry zone, empty"),
        html.Div([
            sparkline_tile("Jump Height", 38.4, series=[34, 35, 36, 37, 38, 38.4],
                            delta="1.2", delta_direction="up", delta_tone="good",
                            accent="aspire", color="#004185", unit="cm", sub="6 sessions"),
            sparkline_tile("Best Contact Time", 182, series=[210, 200, 195, 188, 182],
                            delta="6", delta_direction="down", delta_tone="good",
                            accent="gold", color="#fbb800", unit="ms", sub="5 sessions"),
            sparkline_tile("Ecc. Braking Asym", 7.4, series=[3.1, 5.2, 6.8, 7.4],
                            delta="2.2", delta_direction="up", zone="yellow",
                            color="#d97706", unit="%", sub="4 sessions"),
            sparkline_tile("Peak Vertical Force", "—", series=[], unit="N",
                            sub="no data"),
        ], style={"display": "grid",
                   "gridTemplateColumns": "repeat(auto-fit, minmax(240px, 1fr))",
                   "gap": "12px", "marginBottom": "12px"}),
        code_block(
            "sparkline_tile('Jump Height', 38.4, series=[...],\n"
            "               delta='1.2', delta_direction='up', delta_tone='good',\n"
            "               accent='aspire', color='#004185', unit='cm', sub='6 sessions')\n\n"
            "sparkline_tile('Ecc. Braking Asym', 7.4, series=[...],\n"
            "               delta='2.2', delta_direction='up', zone='yellow',\n"
            "               color='#d97706', unit='%')   # zone tints + colours the value\n\n"
            "sparkline_tile('Peak Vertical Force', '—', series=[], unit='N', sub='no data')"
        ),

        # 9. Injury card
        section("9 · injury_card — medical-domain card with severity stripe"),
        html.Div([
            injury_card("L Hamstring", severity="severe", status="Out 4 wk",
                         detail="Grade II strain, mid-belly.",
                         onset_date="2026-05-15", days_out=7),
            injury_card("R Achilles", severity="moderate",
                         status="Modified training",
                         detail="Tendinopathy. Pain on push-off.",
                         onset_date="2026-04-22", days_out=30),
            injury_card("Lower back", severity="mild", status="Monitoring",
                         detail="DOMS after Sat session.",
                         onset_date="2026-05-18", days_out=4),
            injury_card("L Quad", severity="resolved", status="Cleared",
                         detail="Strain recovered. Full training Mon.",
                         onset_date="2026-04-08", days_out=42),
        ], style={"display": "grid",
                   "gridTemplateColumns": "repeat(auto-fit, minmax(220px, 1fr))",
                   "gap": "12px", "marginBottom": "12px"}),
        code_block(
            "from aspire_dash.v12_helpers import injury_card\n\n"
            "injury_card('L Hamstring', severity='severe', status='Out 4 wk',\n"
            "            detail='Grade II strain, mid-belly.',\n"
            "            onset_date='2026-05-15', days_out=7)"
        ),

        # 11. Metric ring + athlete_card_rings
        section("11 · metric_ring + athlete_card_rings — Whoop-style"),
        html.Div([
            metric_ring(68, pct=68, label="Recovery", tone="good", size=100),
            metric_ring("15.8", pct=75, label="Strain", tone="aspire", size=100),
            metric_ring("7h12", pct=72, label="Sleep", tone="good", size=100),
            metric_ring(38, pct=38, label="HRV", tone="warn", size=100, unit="ms"),
        ], style={"display": "flex", "flexWrap": "wrap", "gap": "18px",
                   "marginBottom": "16px"}),
        code_block(
            "from aspire_dash.v12_helpers import metric_ring\n\n"
            'metric_ring(68, pct=68, label="Recovery", tone="good")\n'
            'metric_ring("7h12", pct=72, label="Sleep", tone="good")\n'
            '# tone: good | warn | danger | aspire | secondary | gold'
        ),

        html.Div([
            athlete_card_rings(
                "Ali Turki Owaida", meta="SENIOR · Fencing", tone="good",
                rings=[
                    {"value": 68,     "pct": 68, "label": "Recovery", "tone": "good"},
                    {"value": "15.8", "pct": 75, "label": "Strain",   "tone": "aspire"},
                    {"value": "7h12", "pct": 72, "label": "Sleep",    "tone": "good"},
                ],
            ),
            athlete_card_rings(
                "Mohammed AlHazaa", meta="SENIOR · Fencing", tone="warn",
                rings=[
                    {"value": 42,     "pct": 42, "label": "Recovery", "tone": "warn"},
                    {"value": "18.6", "pct": 88, "label": "Strain",   "tone": "danger"},
                    {"value": "5h48", "pct": 58, "label": "Sleep",    "tone": "warn"},
                ],
            ),
            athlete_card_rings(
                "Khaled Hussein", meta="SENIOR · Fencing", tone="danger",
                rings=[
                    {"value": 23,     "pct": 23, "label": "Recovery", "tone": "danger"},
                    {"value": "20.3", "pct": 95, "label": "Strain",   "tone": "danger"},
                    {"value": "4h32", "pct": 45, "label": "Sleep",    "tone": "danger"},
                ],
            ),
        ], style={"display": "grid",
                   "gridTemplateColumns": "repeat(auto-fit, minmax(220px, 1fr))",
                   "gap": "12px", "marginBottom": "12px"}),
        code_block(
            "from aspire_dash.v12_helpers import athlete_card_rings\n\n"
            "athlete_card_rings(\n"
            '    "Ali Turki Owaida",\n'
            '    meta="SENIOR · Fencing",\n'
            '    tone="good",\n'
            '    rings=[\n'
            '        {"value": 68,     "pct": 68, "label": "Recovery", "tone": "good"},\n'
            '        {"value": "15.8", "pct": 75, "label": "Strain",   "tone": "aspire"},\n'
            '        {"value": "7h12", "pct": 72, "label": "Sleep",    "tone": "good"},\n'
            "    ],\n"
            ")"
        ),

        # 10. Asymmetry bar
        section("10 · asymmetry_bar — VALD-style L/R split"),
        html.Div([
            html.Div([html.Div("Symmetric (<5% deviation)",
                                style={"fontSize": "11px",
                                        "color": "#64748b",
                                        "marginBottom": "4px"}),
                       asymmetry_bar(52)]),
            html.Div([html.Div("Warning (5-10% deviation)",
                                style={"fontSize": "11px",
                                        "color": "#64748b",
                                        "margin": "10px 0 4px 0"}),
                       asymmetry_bar(58)]),
            html.Div([html.Div("Danger (>10% deviation)",
                                style={"fontSize": "11px",
                                        "color": "#64748b",
                                        "margin": "10px 0 4px 0"}),
                       asymmetry_bar(64)]),
        ], style={"marginBottom": "12px"}),
        code_block(
            "from aspire_dash.v12_helpers import asymmetry_bar\n\n"
            "asymmetry_bar(58)  # 58% L / 42% R → 8% deviation → amber border"
        ),

    ], style={"padding": "24px"})
