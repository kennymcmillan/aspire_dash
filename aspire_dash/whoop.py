"""WHOOP recovery & sleep recall panel.

Pure renderer — takes a `whoop_summary` dict (see
`aspire_data.whoop.whoop_summary`) and returns a Dash component. No data
fetching here, so the UI lib stays data-source-agnostic.

    from aspire_data.whoop import whoop_summary
    from aspire_dash.whoop import recovery_panel
    panel = recovery_panel(whoop_summary(player_id=2930))
"""
from __future__ import annotations

__all__ = ["recovery_panel", "recovery_zone_color"]

from dash import html
import dash_bootstrap_components as dbc

from .v12_helpers import (
    kpi_with_sparkline, metric_ring, progress_stack, stat_with_trend, tracker_strip,
)


def recovery_zone_color(score) -> str:
    if score is None:
        return "#94a3b8"
    return "#16a34a" if score >= 67 else ("#fbb800" if score >= 34 else "#dc2626")


def _tone(score) -> str:
    if score is None:
        return "neutral"
    return "green" if score >= 67 else ("yellow" if score >= 34 else "red")


def _f(v, fmt="{:.0f}", dash="—"):
    try:
        return fmt.format(float(v))
    except (TypeError, ValueError):
        return dash


def recovery_panel(summary: dict | None, *, note: bool = True):
    """Render a WHOOP recovery/sleep recall from a whoop_summary dict:
    today's recovery ring + KPIs, 7-day sparkline trends, a 14-day recovery
    tracker, and the last-sleep stage breakdown."""
    s = summary or {}
    head = html.Div([
        html.I(className="fa-solid fa-circle-info me-2 text-muted"),
        html.Span("Recall only — WHOOP recovery, sleep & strain.",
                  className="text-muted small"),
    ], className="mb-2") if note else None

    if not s.get("matched"):
        return html.Div([head, dbc.Alert(
            "No WHOOP profile mapped for this athlete.",
            color="secondary", className="py-2 mb-0 small")])
    if not s.get("has_data"):
        return html.Div([head, dbc.Alert(
            f"WHOOP profile mapped ({s.get('athlete_name')}) but no recent data.",
            color="secondary", className="py-2 mb-0 small")])

    t = s.get("today") or {}
    rec = t.get("recovery")
    a7 = s.get("avg7") or {}
    stg = s.get("sleep_stages") or {}

    ring = metric_ring(_f(rec), float(rec) if rec is not None else 0,
                       label="Recovery", color=recovery_zone_color(rec),
                       unit="%", size=96)

    sleep_h = (f"{_f((t.get('sleep_mins') or 0) / 60, '{:.1f}')}h"
               if t.get("sleep_mins") else "—")
    strip = dbc.Row([
        dbc.Col(stat_with_trend("HRV", f"{_f(t.get('hrv'))} ms"), md=2, sm=4),
        dbc.Col(stat_with_trend("Resting HR", f"{_f(t.get('rhr'))} bpm"), md=2, sm=4),
        dbc.Col(stat_with_trend("Day strain", _f(t.get("strain"), "{:.1f}")), md=2, sm=4),
        dbc.Col(stat_with_trend("Sleep", sleep_h), md=3, sm=6),
        dbc.Col(stat_with_trend("Sleep perf", f"{_f(t.get('sleep_perf'))}%"), md=3, sm=6),
    ], className="g-2")

    sparks = dbc.Row([
        dbc.Col(kpi_with_sparkline("Recovery · 7d avg", f"{_f(a7.get('recovery'))}%",
                                   s.get("recovery_series") or [], accent="green"), md=4),
        dbc.Col(kpi_with_sparkline("Strain · 7d avg", _f(a7.get("strain"), "{:.1f}"),
                                   s.get("strain_series") or [], accent="aspire"), md=4),
        dbc.Col(kpi_with_sparkline(
            "Sleep · 7d avg",
            f"{_f((a7.get('sleep_mins') or 0)/60, '{:.1f}')}h" if a7.get("sleep_mins") else "—",
            [(v or 0) / 60 for v in (s.get("sleep_series") or [])], accent="gold"), md=4),
    ], className="g-2 mt-1")

    cells = [{"tone": _tone(v), "tooltip": f"{v:.0f}%"}
             for v in (s.get("recovery_series") or [])]
    tracker = tracker_strip(cells, label="Recovery — last 14 days") if cells else None

    stack = progress_stack([
        {"label": "Deep", "value": stg.get("deep") or 0, "color": "#1e3a8a"},
        {"label": "REM", "value": stg.get("rem") or 0, "color": "#0891b2"},
        {"label": "Light", "value": stg.get("light") or 0, "color": "#93c5fd"},
        {"label": "Awake", "value": stg.get("awake") or 0, "color": "#cbd5e1"},
    ], label="Last sleep — stages (mins)")

    foot = html.Div(
        f"WHOOP · {s.get('athlete_name')} · {s.get('n_days')} days · latest {t.get('date')}",
        className="text-muted mt-2", style={"fontSize": "0.72rem"})

    return html.Div([
        head,
        dbc.Row([dbc.Col(ring, md="auto"), dbc.Col(strip, md=True)],
                className="g-3 align-items-center mb-1"),
        sparks,
        html.Div(tracker, className="mt-3") if tracker else None,
        html.Div(stack, className="mt-3"),
        foot,
    ])
