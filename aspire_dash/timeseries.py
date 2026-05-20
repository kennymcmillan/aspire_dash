"""Plotly overlay builders for athlete monitoring time-series charts.

These were originally written for DASH_VALD (force plate trends) but
apply to any per-session athlete metric:
  - SD bands (±1SD inner, ±2SD outer) — show typical range
  - 4-point moving average — smooths short-term noise
  - Acute alert band — flags points >1.5 SD outside rolling window
  - Outlier markers — points beyond ±2 SD from mean

All builders return a *list* of Plotly Scatter traces that the caller adds
to a Figure in their own order. Pass `colors=...` to override the default
Aspire palette.

A higher-level helper, `aggregate_sessions`, collapses a list of trial
records into one value per date, respecting a metric's "trend direction"
(higher-is-better vs lower-is-better).
"""
from __future__ import annotations

from typing import Callable, Iterable

import numpy as np
import plotly.graph_objects as go

__all__ = [
    "DEFAULT_COLORS",
    "build_sd_traces", "build_4pt_ma_traces", "build_acute_traces",
    "build_sd_outlier_traces", "build_main_line_trace",
    "aggregate_sessions",
]


# Default trace styling (Aspire palette where applicable)
DEFAULT_COLORS = {
    "main_line": "#667eea",
    "mean": "#666666",
    "sd_fill_inner": "rgba(40, 167, 69, 0.25)",
    "sd_fill_outer": "rgba(255, 193, 7, 0.15)",
    "sd_line": "#28a745",
    "sd_line_outer": "#ffc107",
    "ma_fill": "rgba(219, 234, 254, 0.6)",
    "ma_line": "#1d4ed8",
    "ma_band": "#3b82f6",
    "acute_fill": "rgba(254, 243, 199, 0.6)",
    "acute_line": "#f59e0b",
    "acute_rolling": "#6b7280",
    "alert_red": "#ef4444",
    "alert_amber": "#f59e0b",
}


# ── Trace builders ─────────────────────────────────────────────────────────

def build_sd_traces(dates, values, stats, colors=DEFAULT_COLORS):
    """Return ±1SD (green) + ±2SD (yellow) bands + mean line (5 traces).

    Empty list returned if std is 0 or no values.
    """
    n = len(values)
    mean_val = stats.get("mean", 0)
    std_val = stats.get("std", 0)
    if std_val <= 0 or n == 0:
        return []

    return [
        go.Scatter(x=dates, y=[mean_val + 2 * std_val] * n, mode="lines",
                    line=dict(width=0), showlegend=False, hoverinfo="skip"),
        go.Scatter(x=dates, y=[mean_val - 2 * std_val] * n, mode="lines",
                    line=dict(width=0), fill="tonexty",
                    fillcolor=colors["sd_fill_outer"], showlegend=False, hoverinfo="skip"),
        go.Scatter(x=dates, y=[mean_val + std_val] * n, mode="lines",
                    line=dict(color=colors["sd_line"], width=1.5, dash="dash"),
                    showlegend=False, hoverinfo="skip"),
        go.Scatter(x=dates, y=[mean_val - std_val] * n, mode="lines",
                    line=dict(color=colors["sd_line"], width=1.5, dash="dash"),
                    fill="tonexty", fillcolor=colors["sd_fill_inner"],
                    showlegend=False, hoverinfo="skip"),
        go.Scatter(x=[dates[0], dates[-1]], y=[mean_val, mean_val], mode="lines",
                    line=dict(color=colors["mean"], dash="dash", width=2),
                    name="Mean", showlegend=False, hoverinfo="skip"),
    ]


def build_4pt_ma_traces(dates, values, window=4, colors=DEFAULT_COLORS):
    """Rolling mean + ±1SD band. Needs ≥`window` points."""
    n = len(values)
    if n < window:
        return []
    rolling_mean = [np.mean(values[max(0, i - window + 1):i + 1]) for i in range(n)]
    rolling_std = [np.std(values[max(0, i - window + 1):i + 1]) for i in range(n)]
    upper = [m + s for m, s in zip(rolling_mean, rolling_std)]
    lower = [m - s for m, s in zip(rolling_mean, rolling_std)]
    return [
        go.Scatter(x=dates, y=upper, mode="lines",
                    line=dict(color=colors["ma_band"], width=1.5, dash="dashdot"),
                    showlegend=False, hoverinfo="skip"),
        go.Scatter(x=dates, y=lower, mode="lines",
                    line=dict(color=colors["ma_band"], width=1.5, dash="dashdot"),
                    fill="tonexty", fillcolor=colors["ma_fill"],
                    showlegend=False, hoverinfo="skip"),
        go.Scatter(x=dates, y=rolling_mean, mode="lines",
                    line=dict(color=colors["ma_line"], width=2),
                    name="4pt MA", hoverinfo="skip"),
    ]


def build_acute_traces(dates, values, window=4, sd_mult=1.5, colors=DEFAULT_COLORS):
    """Rolling mean ±`sd_mult`×SD band + alert markers for breaches."""
    n = len(values)
    if n < window:
        return []
    rolling_mean = [np.mean(values[max(0, i - window + 1):i + 1]) for i in range(n)]
    rolling_std = [np.std(values[max(0, i - window + 1):i + 1]) for i in range(n)]
    upper = [m + sd_mult * s for m, s in zip(rolling_mean, rolling_std)]
    lower = [m - sd_mult * s for m, s in zip(rolling_mean, rolling_std)]

    traces = [
        go.Scatter(x=dates, y=upper, mode="lines",
                    line=dict(color=colors["acute_line"], width=1.5, dash="dashdot"),
                    showlegend=False, hoverinfo="skip"),
        go.Scatter(x=dates, y=lower, mode="lines",
                    line=dict(color=colors["acute_line"], width=1.5, dash="dashdot"),
                    fill="tonexty", fillcolor=colors["acute_fill"],
                    showlegend=False, hoverinfo="skip"),
        go.Scatter(x=dates, y=rolling_mean, mode="lines",
                    line=dict(color=colors["acute_rolling"], width=1, dash="dot"),
                    name="Rolling Mean", hoverinfo="skip"),
    ]

    alert_dates = [dates[i] for i in range(n)
                    if values[i] < lower[i] or values[i] > upper[i]]
    alert_vals = [values[i] for i in range(n)
                   if values[i] < lower[i] or values[i] > upper[i]]
    if alert_dates:
        # Amber, not red — acute fires on rolling ±1.5 SD which can be
        # tighter than the ±2 SD bands shown. Reserving red for true
        # outliers (build_sd_outlier_traces) avoids "red dot inside the
        # band" confusion.
        traces.append(go.Scatter(
            x=alert_dates, y=alert_vals, mode="markers",
            marker=dict(size=14, color="rgba(245,158,11,0.25)", symbol="circle",
                        line=dict(width=2, color=colors["alert_amber"])),
            name="Acute", hoverinfo="skip",
        ))
    return traces


def build_sd_outlier_traces(dates, values, stats, sd_threshold=2, colors=DEFAULT_COLORS):
    """Markers for points outside ±`sd_threshold`×SD."""
    mean_val = stats.get("mean", 0)
    std_val = stats.get("std", 0)
    if std_val <= 0:
        return []
    outlier_dates, outlier_vals = [], []
    for i in range(len(values)):
        if abs(values[i] - mean_val) > sd_threshold * std_val:
            outlier_dates.append(dates[i])
            outlier_vals.append(values[i])
    if not outlier_dates:
        return []
    return [go.Scatter(
        x=outlier_dates, y=outlier_vals, mode="markers",
        marker=dict(size=16, color="rgba(239,68,68,0.25)", symbol="circle",
                    line=dict(width=2.5, color=colors["alert_red"])),
        name="Outlier", hoverinfo="skip",
    )]


def build_main_line_trace(dates, values, *, color="#667eea",
                           metric_name="", unit="", shape="linear"):
    """The data line that sits on top of any overlays.

    `shape="linear"` is the safer default — `shape="spline"` invents
    smooth curves between discrete test points (misleading).
    """
    return go.Scatter(
        x=dates, y=values, mode="lines+markers",
        line=dict(color=color, width=3, shape=shape),
        marker=dict(size=7, color=color, line=dict(width=2, color="white")),
        name=metric_name or "Value",
        hovertemplate="<b>%{x}</b><br>" + (metric_name or "Value") +
                       ": %{y:.2f}" + unit + "<extra></extra>",
    )


# ── Session aggregation ────────────────────────────────────────────────────

def _aggregator(trend_direction):
    """min for 'down' metrics, max for everything else."""
    return min if (trend_direction or "").lower() == "down" else max


def aggregate_sessions(
    records: Iterable[dict],
    *,
    date_key: str = "date",
    value_key: str = "value",
    trend_direction: str | None = None,
) -> list[dict]:
    """Collapse multiple per-trial records into one value per calendar day.

    For each ``date`` key in the records, aggregate the ``value`` field
    using min (when ``trend_direction == "down"``) or max (everything
    else). Returns a date-sorted list of ``{date, value}`` dicts.

    Example::

        rows = [
            {"date": "2026-01-01", "value": 30.0},
            {"date": "2026-01-01", "value": 32.0},   # same day → max wins
            {"date": "2026-01-15", "value": 28.0},
        ]
        aggregate_sessions(rows, trend_direction="up")
        # → [{"date": "2026-01-01", "value": 32.0},
        #    {"date": "2026-01-15", "value": 28.0}]

    Use this from a higher-level app helper that knows how to extract
    trials → records (e.g. DASH_VALD's ``extract_metric_values``).
    """
    agg = _aggregator(trend_direction)
    by_date: dict[str, float] = {}
    for r in records:
        d = r.get(date_key)
        v = r.get(value_key)
        if not d or v is None:
            continue
        d = str(d)[:10]
        prev = by_date.get(d)
        by_date[d] = v if prev is None else agg(prev, v)
    return [{"date": d, "value": v} for d, v in sorted(by_date.items())]
