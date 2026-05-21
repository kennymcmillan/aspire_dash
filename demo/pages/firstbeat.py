"""Firstbeat Components — HR zones, ACWR badges, training cards, load charts."""

import dash
from dash import html, dcc
import plotly.graph_objects as go
from aspire_dash.components import card
from aspire_dash.charts import GRAPH_CONFIG
from aspire_dash.theme import SLATE
from aspire_dash.firstbeat import (
    zone_bars, zone_stacked_bar, acwr_badge, metric_trio,
    training_card, get_acwr_status, add_acwr_zones,
    ZONE_CONFIG, ZONE_COLORS, ACWR_THRESHOLDS,
)

dash.register_page(__name__, path="/firstbeat", title="Firstbeat Components", name="Firstbeat Components")

# ── Sample data ──────────────────────────────────────────────────────────────

SAMPLE_ZONES_HIGH = {"zone1": 8.2, "zone2": 15.7, "zone3": 32.4, "zone4": 22.1, "zone5": 11.6}
SAMPLE_ZONES_EASY = {"zone1": 25.0, "zone2": 35.5, "zone3": 18.0, "zone4": 5.2, "zone5": 1.3}
SAMPLE_ZONES_SPRINT = {"zone1": 3.0, "zone2": 5.0, "zone3": 8.5, "zone4": 18.0, "zone5": 25.5}

SAMPLE_TREND = [
    {"date": "2026-02-10", "acwr": 0.72, "acuteLoad": 180, "chronicLoad": 250},
    {"date": "2026-02-12", "acwr": 0.85, "acuteLoad": 210, "chronicLoad": 247},
    {"date": "2026-02-14", "acwr": 0.92, "acuteLoad": 230, "chronicLoad": 250},
    {"date": "2026-02-16", "acwr": 1.05, "acuteLoad": 265, "chronicLoad": 252},
    {"date": "2026-02-18", "acwr": 1.18, "acuteLoad": 300, "chronicLoad": 254},
    {"date": "2026-02-20", "acwr": 1.32, "acuteLoad": 340, "chronicLoad": 258},
    {"date": "2026-02-22", "acwr": 1.45, "acuteLoad": 380, "chronicLoad": 262},
    {"date": "2026-02-24", "acwr": 1.28, "acuteLoad": 340, "chronicLoad": 266},
    {"date": "2026-02-26", "acwr": 1.12, "acuteLoad": 300, "chronicLoad": 268},
    {"date": "2026-02-28", "acwr": 0.98, "acuteLoad": 265, "chronicLoad": 270},
    {"date": "2026-03-02", "acwr": 1.08, "acuteLoad": 295, "chronicLoad": 273},
    {"date": "2026-03-04", "acwr": 1.15, "acuteLoad": 318, "chronicLoad": 276},
]


def _acwr_trend_demo():
    """ACWR trend chart with coloured zone bands."""
    fig = go.Figure()
    add_acwr_zones(fig, opacity=0.4)
    fig.add_trace(go.Scatter(
        x=[p["date"] for p in SAMPLE_TREND],
        y=[p["acwr"] for p in SAMPLE_TREND],
        mode="lines+markers",
        line=dict(color="#8B5CF6", width=2),
        marker=dict(size=5, color="#8B5CF6"),
        name="ACWR", connectgaps=True,
        hovertemplate="Date: %{x}<br>ACWR: %{y:.2f}<extra></extra>",
    ))
    fig.update_layout(
        height=280, margin=dict(l=40, r=20, t=10, b=40),
        yaxis=dict(range=[0, 2.5], tickvals=[0, 0.8, 1.0, 1.3, 1.5, 2.0]),
        xaxis=dict(tickformat="%b %d"),
        showlegend=False,
    )
    return fig


def _load_comparison_demo():
    """Acute vs Chronic load comparison chart."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[p["date"] for p in SAMPLE_TREND],
        y=[p["acuteLoad"] for p in SAMPLE_TREND],
        mode="lines+markers", name="Acute Load",
        line=dict(color="#F97316", width=2),
        marker=dict(size=4, color="#F97316"),
    ))
    fig.add_trace(go.Scatter(
        x=[p["date"] for p in SAMPLE_TREND],
        y=[p["chronicLoad"] for p in SAMPLE_TREND],
        mode="lines+markers", name="Chronic Load",
        line=dict(color="#6366F1", width=2, dash="dash"),
        marker=dict(size=4, color="#6366F1"),
    ))
    fig.update_layout(
        height=280, margin=dict(l=40, r=20, t=10, b=40),
        xaxis=dict(tickformat="%b %d"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    return fig


def layout(**kwargs):
    return html.Div([
        html.H2("Firstbeat Components", className="section-title", style={"marginTop": "0"}),
        html.P(
            "Training load, HR zone, and ACWR components from aspire_dash.firstbeat "
            "- reusable across Firstbeat, WHOOP, and any training-load app.",
            style={"fontSize": "13px", "color": SLATE["500"], "marginBottom": "24px"},
        ),

        # ── Zone Colours ──
        html.H3("Zone Colour System", style={"fontSize": "15px", "fontWeight": "600", "marginBottom": "12px"}),
        card([
            html.Div("Standard Firstbeat HR zone colours (Z1 Recovery -> Z5 Max)", style={
                "fontSize": "12px", "color": SLATE["500"], "marginBottom": "12px",
            }),
            html.Div([
                html.Div([
                    html.Div(style={
                        "width": "40px", "height": "40px", "borderRadius": "8px",
                        "backgroundColor": z["color"],
                    }),
                    html.Div([
                        html.Div(z["label"], style={"fontWeight": "700", "fontSize": "13px"}),
                        html.Div(z["name"], style={"fontSize": "11px", "color": SLATE["500"]}),
                        html.Div(z["color"], style={"fontSize": "10px", "color": SLATE["400"], "fontFamily": "monospace"}),
                    ]),
                ], style={"display": "flex", "alignItems": "center", "gap": "10px"})
                for z in ZONE_CONFIG
            ], style={"display": "flex", "gap": "32px", "flexWrap": "wrap"}),
        ]),

        # ── ACWR Badges ──
        html.H3("ACWR Badges", style={"fontSize": "15px", "fontWeight": "600", "marginBottom": "12px"}),
        card([
            html.Div("acwr_badge() - auto-coloured by Acute:Chronic Workload Ratio", style={
                "fontSize": "12px", "color": SLATE["500"], "marginBottom": "12px",
            }),
            html.Div([
                html.Div([
                    acwr_badge(0.65, show_value=True),
                    html.Span(" < 0.8", style={"fontSize": "11px", "color": SLATE["400"], "marginLeft": "8px"}),
                ], style={"display": "flex", "alignItems": "center"}),
                html.Div([
                    acwr_badge(1.05, show_value=True),
                    html.Span(" 0.8 - 1.3", style={"fontSize": "11px", "color": SLATE["400"], "marginLeft": "8px"}),
                ], style={"display": "flex", "alignItems": "center"}),
                html.Div([
                    acwr_badge(1.42, show_value=True),
                    html.Span(" 1.3 - 1.5", style={"fontSize": "11px", "color": SLATE["400"], "marginLeft": "8px"}),
                ], style={"display": "flex", "alignItems": "center"}),
                html.Div([
                    acwr_badge(1.78, show_value=True),
                    html.Span(" > 1.5", style={"fontSize": "11px", "color": SLATE["400"], "marginLeft": "8px"}),
                ], style={"display": "flex", "alignItems": "center"}),
                html.Div([
                    acwr_badge(None),
                    html.Span(" None / unknown", style={"fontSize": "11px", "color": SLATE["400"], "marginLeft": "8px"}),
                ], style={"display": "flex", "alignItems": "center"}),
            ], style={"display": "flex", "gap": "24px", "flexWrap": "wrap"}),
            # Compact badges (no value)
            html.Div([
                html.Div("Compact (show_value=False):", style={
                    "fontSize": "12px", "color": SLATE["500"], "marginTop": "16px", "marginBottom": "8px",
                }),
                html.Div([
                    acwr_badge(0.65, show_value=False),
                    acwr_badge(1.05, show_value=False),
                    acwr_badge(1.42, show_value=False),
                    acwr_badge(1.78, show_value=False),
                ], style={"display": "flex", "gap": "8px"}),
            ]),
        ]),

        # ── Zone Bars ──
        html.H3("Zone Bars", style={"fontSize": "15px", "fontWeight": "600", "marginBottom": "12px"}),
        card([
            html.Div("zone_bars() - horizontal HR zone bars (one per zone)", style={
                "fontSize": "12px", "color": SLATE["500"], "marginBottom": "16px",
            }),
            html.Div([
                html.Div([
                    html.Div("High Intensity Session", style={
                        "fontSize": "12px", "fontWeight": "600", "color": SLATE["600"], "marginBottom": "8px",
                    }),
                    zone_bars(SAMPLE_ZONES_HIGH),
                ], style={"flex": "1", "minWidth": "200px"}),
                html.Div([
                    html.Div("Easy Recovery Session", style={
                        "fontSize": "12px", "fontWeight": "600", "color": SLATE["600"], "marginBottom": "8px",
                    }),
                    zone_bars(SAMPLE_ZONES_EASY),
                ], style={"flex": "1", "minWidth": "200px"}),
                html.Div([
                    html.Div("Sprint / Max Effort", style={
                        "fontSize": "12px", "fontWeight": "600", "color": SLATE["600"], "marginBottom": "8px",
                    }),
                    zone_bars(SAMPLE_ZONES_SPRINT),
                ], style={"flex": "1", "minWidth": "200px"}),
            ], style={"display": "flex", "gap": "32px", "flexWrap": "wrap"}),
        ]),

        # ── Zone Stacked Bars ──
        html.H3("Zone Stacked Bars (Inline)", style={"fontSize": "15px", "fontWeight": "600", "marginBottom": "12px"}),
        card([
            html.Div("zone_stacked_bar() - compact inline bar for table cells (hover for tooltip)", style={
                "fontSize": "12px", "color": SLATE["500"], "marginBottom": "16px",
            }),
            html.Div([
                html.Div([
                    html.Span("Default (120x16)", style={"fontSize": "12px", "color": SLATE["600"], "width": "120px"}),
                    zone_stacked_bar(SAMPLE_ZONES_HIGH),
                ], style={"display": "flex", "alignItems": "center", "gap": "12px"}),
                html.Div([
                    html.Span("Wide (200x14)", style={"fontSize": "12px", "color": SLATE["600"], "width": "120px"}),
                    zone_stacked_bar(SAMPLE_ZONES_EASY, width=200, height=14),
                ], style={"display": "flex", "alignItems": "center", "gap": "12px"}),
                html.Div([
                    html.Span("Narrow (80x12)", style={"fontSize": "12px", "color": SLATE["600"], "width": "120px"}),
                    zone_stacked_bar(SAMPLE_ZONES_SPRINT, width=80, height=12),
                ], style={"display": "flex", "alignItems": "center", "gap": "12px"}),
                html.Div([
                    html.Span("Empty state", style={"fontSize": "12px", "color": SLATE["600"], "width": "120px"}),
                    zone_stacked_bar({}),
                ], style={"display": "flex", "alignItems": "center", "gap": "12px"}),
            ], style={"display": "flex", "flexDirection": "column", "gap": "10px"}),
        ]),

        # ── Metric Trio ──
        html.H3("Metric Trio (HR / TE / TRIMP)", style={"fontSize": "15px", "fontWeight": "600", "marginBottom": "12px"}),
        card([
            html.Div("metric_trio() - 3-column session metrics display", style={
                "fontSize": "12px", "color": SLATE["500"], "marginBottom": "16px",
            }),
            metric_trio(
                hr_avg=152, hr_peak=188, hr_avg_pct=81, hr_peak_pct=100,
                aerobic_te=4.5, anaerobic_te=2.1, trimp=245,
            ),
            html.Div(style={"height": "16px"}),
            html.Div("With missing values:", style={
                "fontSize": "12px", "color": SLATE["500"], "marginBottom": "8px",
            }),
            metric_trio(hr_avg=130, hr_peak=165, aerobic_te=3.2, anaerobic_te=None, trimp=None),
        ]),

        # ── Training Cards ──
        html.H3("Training Session Cards", style={"fontSize": "15px", "fontWeight": "600", "marginBottom": "12px"}),
        html.Div([
            training_card(
                athlete_name="Ali Al-Marri",
                sport="Fencing",
                date_str="Mar 14, 2026",
                time_str="9:30 AM",
                zones=SAMPLE_ZONES_HIGH,
                hr_avg=152, hr_peak=188, hr_avg_pct=81, hr_peak_pct=100,
                aerobic_te=4.5, anaerobic_te=2.1, trimp=245,
                acwr=1.05, duration_min=90,
                title="Fencing Training",
            ),
            training_card(
                athlete_name="Mohammed Hassan",
                sport="Padel",
                date_str="Mar 14, 2026",
                time_str="2:15 PM",
                zones=SAMPLE_ZONES_EASY,
                hr_avg=128, hr_peak=155,
                aerobic_te=2.8, anaerobic_te=0.9, trimp=120,
                acwr=0.72, duration_min=65,
                title="Recovery Session",
            ),
            training_card(
                athlete_name="Khalid Ibrahim",
                sport="Endurance",
                date_str="Mar 14, 2026",
                time_str="7:00 AM",
                zones=SAMPLE_ZONES_SPRINT,
                hr_avg=168, hr_peak=195, hr_avg_pct=88, hr_peak_pct=103,
                aerobic_te=5.0, anaerobic_te=4.2, trimp=380,
                acwr=1.62, duration_min=60,
                title="Interval Sprints",
            ),
        ], style={
            "display": "grid",
            "gridTemplateColumns": "repeat(auto-fill, minmax(340px, 1fr))",
            "gap": "16px", "marginBottom": "24px",
        }),

        # ── ACWR Trend Chart ──
        html.H3("ACWR Trend Chart", style={"fontSize": "15px", "fontWeight": "600", "marginBottom": "12px"}),
        card([
            html.Div("add_acwr_zones(fig) adds coloured reference bands to any Plotly figure", style={
                "fontSize": "12px", "color": SLATE["500"], "marginBottom": "8px",
            }),
            dcc.Graph(figure=_acwr_trend_demo(), config=GRAPH_CONFIG),
        ]),

        # ── Load Comparison Chart ──
        html.H3("Acute vs Chronic Load", style={"fontSize": "15px", "fontWeight": "600", "marginBottom": "12px"}),
        card([
            html.Div("Acute (solid orange) vs Chronic (dashed indigo) training load", style={
                "fontSize": "12px", "color": SLATE["500"], "marginBottom": "8px",
            }),
            dcc.Graph(figure=_load_comparison_demo(), config=GRAPH_CONFIG),
        ]),

        # ── Usage Code ──
        html.H3("Usage", style={"fontSize": "15px", "fontWeight": "600", "marginBottom": "12px"}),
        card([
            html.Pre("""from aspire_dash.firstbeat import (
    zone_bars, zone_stacked_bar, acwr_badge, metric_trio,
    training_card, get_acwr_status, add_acwr_zones,
    ZONE_CONFIG, ZONE_COLORS, ACWR_THRESHOLDS,
)

# HR zone bars (one bar per zone)
zone_bars({"zone1": 15, "zone2": 42, "zone3": 65, "zone4": 18, "zone5": 9})

# Compact inline stacked bar for tables
zone_stacked_bar(zones, width=120, height=16)

# ACWR status badge
acwr_badge(1.05)                      # "1.05 - Optimal" (green)
acwr_badge(1.42, show_value=False)    # "Caution" (amber)

# 3-column metric display
metric_trio(hr_avg=152, hr_peak=188, aerobic_te=4.5,
            anaerobic_te=2.1, trimp=245)

# Full training session card
training_card(athlete_name="Ali", sport="Fencing", date_str="Mar 14",
              zones=zones, hr_avg=152, hr_peak=188,
              aerobic_te=4.5, anaerobic_te=2.1, trimp=245, acwr=1.05)

# Add ACWR zone bands to any Plotly chart
fig = go.Figure(go.Scatter(x=dates, y=acwr_values))
add_acwr_zones(fig)

# Get ACWR status dict
status = get_acwr_status(1.42)
# -> {"status": "caution", "label": "Caution", "color": "#f59e0b", ...}""",
                     style={
                         "fontSize": "12px", "fontFamily": "monospace",
                         "background": SLATE["50"], "padding": "16px",
                         "borderRadius": "8px", "overflow": "auto",
                         "border": f"1px solid {SLATE['200']}",
                     }),
        ]),

    ], style={"maxWidth": "1200px"})
