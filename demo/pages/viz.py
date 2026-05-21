"""Viz Components — rings, sparklines, bars, metrics showcase."""

import dash
from dash import html
from aspire_dash.components import card
from aspire_dash.theme import SLATE, ACCENT, SUCCESS, WARNING, DANGER, GOLD
from aspire_dash.viz import (
    progress_ring, status_ring, ring_row,
    sparkline, horizontal_bar, status_dot, metric_spark,
)

dash.register_page(__name__, path="/viz", title="Viz Components", name="Viz Components")


def layout(**kwargs):
    return html.Div([
        html.H2("Viz Components", className="section-title", style={"marginTop": "0"}),
        html.P("Reusable SVG visualisations from aspire_dash.viz — rings, sparklines, bars, metrics.",
               style={"fontSize": "13px", "color": SLATE["500"], "marginBottom": "24px"}),

        # ── Progress Rings ──
        html.H3("Progress Rings", style={"fontSize": "15px", "fontWeight": "600", "marginBottom": "12px"}),
        card([
            html.Div("Basic progress_ring() — custom colour, size, label", style={
                "fontSize": "12px", "color": SLATE["500"], "marginBottom": "12px",
            }),
            ring_row([
                progress_ring(75, label="Budget", color=ACCENT, size=100, unit="%"),
                progress_ring(42, label="Timeline", color=WARNING, size=100, unit="%"),
                progress_ring(91, label="Athletes", color=SUCCESS, size=100, unit="%"),
                progress_ring(18, label="Risk", color=DANGER, size=100, unit="%"),
                progress_ring(3.2, max_val=5, label="Rating", color=GOLD, size=100,
                              display="3.2", unit="/5"),
            ]),
        ]),

        # ── Status Rings ──
        html.H3("Status Rings (auto-colour)", style={"fontSize": "15px", "fontWeight": "600", "marginBottom": "12px"}),
        card([
            html.Div("status_ring() — auto green/yellow/red based on thresholds", style={
                "fontSize": "12px", "color": SLATE["500"], "marginBottom": "12px",
            }),
            ring_row([
                status_ring(85, label="Recovery", size=90, unit="%"),
                status_ring(52, label="Readiness", size=90, unit="%"),
                status_ring(23, label="Fatigue", size=90, unit="%"),
            ]),
        ]),

        # ── Size Variants ──
        html.H3("Size Variants", style={"fontSize": "15px", "fontWeight": "600", "marginBottom": "12px"}),
        card([
            ring_row([
                progress_ring(72, size=40, stroke_width=4, label="xs", color=ACCENT),
                progress_ring(72, size=56, stroke_width=5, label="sm", color=ACCENT),
                progress_ring(72, size=80, stroke_width=6, label="md", color=ACCENT),
                progress_ring(72, size=120, stroke_width=8, label="lg", color=ACCENT, unit="%"),
                progress_ring(72, size=160, stroke_width=10, label="xl", color=ACCENT, unit="%"),
            ], gap="32px"),
        ]),

        # ── Sparklines ──
        html.H3("Sparklines", style={"fontSize": "15px", "fontWeight": "600", "marginBottom": "12px"}),
        card([
            html.Div("Inline SVG sparkline() — perfect for tables and metric cards", style={
                "fontSize": "12px", "color": SLATE["500"], "marginBottom": "12px",
            }),
            html.Div([
                html.Div([
                    html.Span("HRV trend", style={"fontSize": "12px", "color": SLATE["600"], "marginRight": "8px"}),
                    sparkline([45, 52, 48, 55, 61, 58, 63, 67, 59, 72], color=SUCCESS, width=160, height=32),
                ], style={"display": "flex", "alignItems": "center", "gap": "8px"}),
                html.Div([
                    html.Span("Strain trend", style={"fontSize": "12px", "color": SLATE["600"], "marginRight": "8px"}),
                    sparkline([12, 15, 8, 18, 14, 11, 16, 19, 13, 10], color=DANGER, width=160, height=32),
                ], style={"display": "flex", "alignItems": "center", "gap": "8px"}),
                html.Div([
                    html.Span("Budget burn", style={"fontSize": "12px", "color": SLATE["600"], "marginRight": "8px"}),
                    sparkline([10, 18, 25, 32, 41, 48, 55, 62, 70, 78], color=ACCENT, width=160, height=32),
                ], style={"display": "flex", "alignItems": "center", "gap": "8px"}),
            ], style={"display": "flex", "flexDirection": "column", "gap": "12px"}),
        ]),

        # ── Horizontal Bars ──
        html.H3("Horizontal Bars", style={"fontSize": "15px", "fontWeight": "600", "marginBottom": "12px"}),
        card([
            html.Div([
                horizontal_bar(87, label="Football", color=SUCCESS, show_pct=True),
                horizontal_bar(72, label="Athletics", color=SUCCESS, show_pct=True),
                horizontal_bar(95, label="Swimming", color=DANGER, show_pct=True),
                horizontal_bar(58, label="Fencing", color=WARNING, show_pct=True),
                horizontal_bar(43, label="Squash", color=ACCENT, show_pct=True),
            ], style={"display": "flex", "flexDirection": "column", "gap": "8px"}),
        ]),

        # ── Status Dots ──
        html.H3("Status Dots", style={"fontSize": "15px", "fontWeight": "600", "marginBottom": "12px"}),
        card([
            html.Div([
                html.Div([status_dot("green"), html.Span(" Active", style={"fontSize": "13px", "marginLeft": "6px"})],
                         style={"display": "flex", "alignItems": "center"}),
                html.Div([status_dot("yellow"), html.Span(" Pending", style={"fontSize": "13px", "marginLeft": "6px"})],
                         style={"display": "flex", "alignItems": "center"}),
                html.Div([status_dot("red", pulse=True), html.Span(" Alert (pulse)", style={"fontSize": "13px", "marginLeft": "6px"})],
                         style={"display": "flex", "alignItems": "center"}),
                html.Div([status_dot(ACCENT, size=10), html.Span(" Custom colour", style={"fontSize": "13px", "marginLeft": "6px"})],
                         style={"display": "flex", "alignItems": "center"}),
            ], style={"display": "flex", "gap": "24px", "flexWrap": "wrap"}),
        ]),

        # ── Metric Spark Cards ──
        html.H3("Metric + Sparkline Cards", style={"fontSize": "15px", "fontWeight": "600", "marginBottom": "12px"}),
        html.Div([
            metric_spark("HRV", "67", unit="ms",
                         trend_values=[45, 52, 48, 55, 61, 58, 63, 67], color=SUCCESS),
            metric_spark("RHR", "54", unit="bpm",
                         trend_values=[58, 56, 55, 57, 54, 55, 54, 54], color=ACCENT),
            metric_spark("Strain", "14.2", unit="",
                         trend_values=[12, 15, 8, 18, 14, 11, 16, 14], color=WARNING),
            metric_spark("Sleep", "7.4", unit="hrs",
                         trend_values=[6.8, 7.1, 7.5, 6.9, 7.8, 7.2, 7.6, 7.4], color="#7c3aed"),
        ], style={
            "display": "grid",
            "gridTemplateColumns": "repeat(auto-fill, minmax(250px, 1fr))",
            "gap": "12px", "marginBottom": "24px",
        }),

        # ── Usage Code ──
        html.H3("Usage", style={"fontSize": "15px", "fontWeight": "600", "marginBottom": "12px"}),
        card([
            html.Pre("""from aspire_dash.viz import (
    progress_ring, status_ring, ring_row,
    sparkline, horizontal_bar, status_dot, metric_spark,
)

# Basic ring
progress_ring(75, label="Budget", color=ACCENT, size=100, unit="%")

# Auto-colour status ring
status_ring(85, label="Recovery", size=90, unit="%")

# Row of rings
ring_row([ring1, ring2, ring3])

# Inline sparkline
sparkline([45, 52, 48, 55, 61], color=SUCCESS, width=120)

# Metric card with sparkline
metric_spark("HRV", "67", unit="ms", trend_values=[...])""",
                     style={
                         "fontSize": "12px", "fontFamily": "monospace",
                         "background": SLATE["50"], "padding": "16px",
                         "borderRadius": "8px", "overflow": "auto",
                         "border": f"1px solid {SLATE['200']}",
                     }),
        ]),

    ], style={"maxWidth": "1200px"})
