"""VALD ForceDecks chart compositions — verbatim port from DASH_VALD.

This module makes the EXACT graphs from the deployed VALD app available
in any aspire_dash consumer. Composes on top of the existing
`aspire_dash.timeseries` overlay builders (SD bands, 4pt MA, acute,
adaptive) which the VALD app already uses.

Four chart compositions:
- analytics_chart       — single large chart (mode: sd_bands|4pt_ma|acute)
- cmj_panel_chart       — compact panel for 2×2 dashboard grid
- group_heatmap         — athletes × dates Z-score heatmap
- adaptive_chart        — emerald LAR/UAR bands from Bayesian R API

Plus presets:
- VALD_LAYOUT  — exact white-paper, dotted-grid, Inter-font layout
- VALD_COLORS  — exact 17-key palette
- vald_cmj_grid(panels) — 2×2 grid wrapper for the CMJ dashboard
"""
from __future__ import annotations

from datetime import datetime

import numpy as np
import plotly.graph_objects as go
from dash import html, dcc

from .timeseries import (
    build_sd_traces        as _build_sd_traces_base,
    build_4pt_ma_traces    as _build_4pt_ma_traces_base,
    build_acute_traces     as _build_acute_traces_base,
    build_adaptive_traces  as _build_adaptive_traces_base,
    build_sd_outlier_traces as _build_sd_outlier_traces_base,
    build_main_line_trace  as _build_main_line_trace_base,
)


# ── VALD-exact layout preset ───────────────────────────────────────────────

VALD_LAYOUT = dict(
    paper_bgcolor="white",
    plot_bgcolor="white",
    margin=dict(l=50, r=20, t=12, b=40),
    font=dict(family="Inter, -apple-system, sans-serif",
               size=12, color="#64748b"),
    xaxis=dict(
        gridcolor="#e2e8f0", griddash="dot", gridwidth=1,
        zeroline=False, showline=False,
        tickfont=dict(size=10, color="#64748b", family="Inter"),
    ),
    yaxis=dict(
        gridcolor="#e2e8f0", griddash="dot", gridwidth=1,
        zeroline=False, showline=False,
        tickfont=dict(size=12, color="#64748b", family="Inter"),
        tickformat=".1f",
    ),
    hovermode="x unified",
    hoverlabel=dict(
        bgcolor="white", bordercolor="#e2e8f0",
        font=dict(size=12, color="#171717", family="Inter"),
    ),
    legend=dict(
        orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
        font=dict(size=11, color="#64748b"),
        bgcolor="rgba(0,0,0,0)",
    ),
)


VALD_COLORS = {
    "main_line":       "#004185",
    "mean":            "#666666",
    "sd_fill_inner":   "rgba(40, 167, 69, 0.25)",
    "sd_fill_outer":   "rgba(255, 193, 7, 0.15)",
    "sd_line":         "#28a745",
    "sd_line_outer":   "#ffc107",
    "ma_fill":         "rgba(219, 234, 254, 0.6)",
    "ma_line":         "#1d4ed8",
    "ma_band":         "#3b82f6",
    "acute_fill":      "rgba(254, 243, 199, 0.6)",
    "acute_line":      "#f59e0b",
    "acute_rolling":   "#64748b",
    "adaptive_fill":   "rgba(209, 250, 229, 0.6)",
    "adaptive_line":   "#10b981",
    "alert_red":       "#ef4444",
    "alert_amber":     "#f59e0b",
    "normal_dot":      "#004185",
}


GRAPH_CONFIG = {"displayModeBar": False, "staticPlot": False}


def _format_date(d):
    """Format date like Next.js: '26 Oct 25'."""
    try:
        return datetime.strptime(d[:10], "%Y-%m-%d").strftime("%d %b %y")
    except (ValueError, TypeError):
        return d[:10] if d else ""


# Thin colour-forwarding wrappers so the VALD palette is preserved
def _sd_traces(d, v, s):         return _build_sd_traces_base(d, v, s, colors=VALD_COLORS)
def _4pt_ma_traces(d, v):        return _build_4pt_ma_traces_base(d, v, colors=VALD_COLORS)
def _acute_traces(d, v):         return _build_acute_traces_base(d, v, colors=VALD_COLORS)
def _adaptive_traces(d, l, u):   return _build_adaptive_traces_base(d, l, u, colors=VALD_COLORS)
def _sd_outliers(d, v, s):       return _build_sd_outlier_traces_base(d, v, s, colors=VALD_COLORS)


# ── 1. analytics_chart — single large chart ───────────────────────────────

def analytics_chart(data_points, stats, *, mode: str = "sd_bands",
                     height: int = 384,
                     color: str = "#004185",
                     metric_name: str = "", unit: str = ""):
    """Single large chart with mode-selectable overlay.

    `data_points` — list of `{date, value}` dicts (newest last).
    `mode` — one of: ``sd_bands`` (default), ``4pt_ma``, ``acute``.
    `stats` — `{mean, std, ...}` from `aspire_dash.stats.compute_stats`.
    """
    if not data_points:
        return go.Figure(layout={**VALD_LAYOUT, "height": height})

    dates  = [p["date"]  for p in data_points]
    values = [p["value"] for p in data_points]
    fig = go.Figure()

    if mode == "sd_bands":
        for t in _sd_traces(dates, values, stats): fig.add_trace(t)
    elif mode == "4pt_ma":
        for t in _4pt_ma_traces(dates, values): fig.add_trace(t)
    elif mode == "acute":
        for t in _acute_traces(dates, values): fig.add_trace(t)

    fig.add_trace(_build_main_line_trace_base(
        dates, values, color=color, metric_name=metric_name,
        unit=unit, shape="linear",
    ))

    if mode == "sd_bands":
        for t in _sd_outliers(dates, values, stats): fig.add_trace(t)

    y_min, y_max = min(values), max(values)
    if stats and stats.get("std", 0) > 0:
        m_, s_ = stats.get("mean", 0), stats.get("std", 0)
        y_min, y_max = min(y_min, m_ - 2 * s_), max(y_max, m_ + 2 * s_)
    pad = (y_max - y_min if y_max > y_min else abs(y_max) * 0.2) * 0.10

    fig.update_layout(**{
        **VALD_LAYOUT, "height": height,
        "yaxis": {**VALD_LAYOUT["yaxis"], "range": [y_min - pad, y_max + pad]},
    })
    return fig


# ── 2. cmj_panel_chart — compact for 2×2 dashboard ────────────────────────

def cmj_panel_chart(data_points, stats, *,
                     color: str = "#01b8aa",
                     height: int = 192, unit: str = "",
                     metric_name: str = "",
                     mode: str = "sd_bands",
                     adaptive_obs=None):
    """Compact panel for CMJ 2×2 dashboard (192 px high, tight margins).

    `mode`: sd_bands | 4pt_ma | acute | adaptive.
    `adaptive_obs`: required when mode='adaptive' — list of
    `{test_time, value, LAR, UAR, outcome}` from `compute_adaptive_ranges`.
    """
    if not data_points:
        return go.Figure(layout={
            **VALD_LAYOUT, "height": height,
            "margin": dict(l=45, r=12, t=8, b=32),
        })

    dates  = [p["date"]  for p in data_points]
    values = [p["value"] for p in data_points]
    n = len(values)
    fig = go.Figure()

    # Mode-specific band
    if mode == "adaptive" and adaptive_obs:
        odates = [o["test_time"][:10] for o in adaptive_obs]
        lars   = [o["LAR"] for o in adaptive_obs]
        uars   = [o["UAR"] for o in adaptive_obs]
        for t in _adaptive_traces(odates, lars, uars): fig.add_trace(t)
    elif mode == "adaptive":
        # Fall back to SD bands if no adaptive observations
        for t in _sd_traces(dates, values, stats): fig.add_trace(t)
        mode = "sd_bands"
    elif mode == "sd_bands":
        for t in _sd_traces(dates, values, stats): fig.add_trace(t)
    elif mode == "4pt_ma":
        for t in _4pt_ma_traces(dates, values): fig.add_trace(t)
    elif mode == "acute":
        for t in _acute_traces(dates, values): fig.add_trace(t)

    # Main line
    fig.add_trace(go.Scatter(
        x=dates, y=values, mode="lines+markers",
        line=dict(color=color, width=2.5, shape="linear"),
        marker=dict(size=5, color=color, line=dict(width=1.5, color="white")),
        hovertemplate="%{y:.1f}" + unit + "<extra></extra>",
        showlegend=False,
    ))

    # Mode-appropriate breach markers
    alert_d, alert_v = [], []
    if mode == "adaptive" and adaptive_obs:
        alert_d = [o["test_time"][:10] for o in adaptive_obs if o.get("outcome") == "Abnormal"]
        alert_v = [o["value"] for o in adaptive_obs if o.get("outcome") == "Abnormal"]
    elif mode == "acute" and n >= 4:
        rm = [float(np.mean(values[max(0, i - 3):i + 1])) for i in range(n)]
        rs = [float(np.std(values[max(0, i - 3):i + 1]))  for i in range(n)]
        for i in range(n):
            if rs[i] > 0 and (values[i] > rm[i] + 1.5 * rs[i]
                              or values[i] < rm[i] - 1.5 * rs[i]):
                alert_d.append(dates[i]); alert_v.append(values[i])
    elif mode == "4pt_ma" and n >= 4:
        rm = [float(np.mean(values[max(0, i - 3):i + 1])) for i in range(n)]
        rs = [float(np.std(values[max(0, i - 3):i + 1]))  for i in range(n)]
        for i in range(n):
            if rs[i] > 0 and (values[i] > rm[i] + rs[i]
                              or values[i] < rm[i] - rs[i]):
                alert_d.append(dates[i]); alert_v.append(values[i])
    elif mode == "sd_bands" and n >= 4:
        last4 = values[-4:]
        acute_limit = np.mean(last4) - 1.5 * np.std(last4)
        for i in range(n):
            if values[i] < acute_limit:
                alert_d.append(dates[i]); alert_v.append(values[i])

    if alert_d:
        fig.add_trace(go.Scatter(
            x=alert_d, y=alert_v, mode="markers",
            marker=dict(size=12, color="rgba(245,158,11,0.25)",
                        line=dict(width=2, color=VALD_COLORS["alert_amber"])),
            showlegend=False, hoverinfo="skip",
        ))

    y_min, y_max = min(values), max(values)
    if stats and stats.get("std", 0) > 0:
        m_, s_ = stats.get("mean", 0), stats.get("std", 0)
        y_min, y_max = min(y_min, m_ - 2 * s_), max(y_max, m_ + 2 * s_)
    if adaptive_obs:
        lars = [o["LAR"] for o in adaptive_obs]
        uars = [o["UAR"] for o in adaptive_obs]
        y_min, y_max = min(y_min, min(lars)), max(y_max, max(uars))
    pad = (y_max - y_min if y_max > y_min else abs(y_max) * 0.2) * 0.10

    fig.update_layout(**{
        **VALD_LAYOUT, "height": height,
        "margin": dict(l=45, r=12, t=8, b=32),
        "yaxis": {**VALD_LAYOUT["yaxis"], "range": [y_min - pad, y_max + pad]},
    })
    return fig


# ── 3. group_heatmap — athletes × dates Z-score ──────────────────────────

def group_heatmap(athletes_data, *, metric_name: str = "", unit: str = "",
                   height: int = 400):
    """Heatmap for group analysis. Rows=athletes, cols=test dates, cell=Z-score."""
    if not athletes_data:
        return go.Figure(layout={**VALD_LAYOUT, "height": height})

    all_dates = sorted(set(d for a in athletes_data for d in a["dates"]))
    if len(all_dates) > 10:
        all_dates = all_dates[-10:]
    names = [a["name"] for a in athletes_data]

    z = []
    for a in athletes_data:
        date_val = dict(zip(a["dates"], a["values"]))
        z.append([date_val.get(d) for d in all_dates])

    # Z-score normalise per athlete (row)
    z_scores = []
    for row in z:
        vals = [v for v in row if v is not None]
        if len(vals) >= 2:
            m, s = np.mean(vals), np.std(vals)
            z_scores.append([((v - m) / s if s > 0 else 0) if v is not None else None
                             for v in row])
        else:
            z_scores.append(row)

    fig = go.Figure(go.Heatmap(
        z=z_scores,
        x=[_format_date(d) for d in all_dates],
        y=names,
        customdata=z,
        colorscale=[
            [0.0, "#dc2626"], [0.25, "#f59e0b"],
            [0.5, "#f3f4f6"],
            [0.75, "#86efac"], [1.0, "#16a34a"],
        ],
        hovertemplate="%{y}<br>%{x}: %{customdata:.1f}" + unit + "<extra></extra>",
        colorbar=dict(title=dict(text="Z-Score", font=dict(size=11)),
                      thickness=12, len=0.6),
        zmin=-2, zmax=2,
    ))
    fig.update_layout(**{
        **VALD_LAYOUT, "height": height,
        "yaxis": {"tickfont": {"size": 11, "family": "Inter"},
                   "autorange": "reversed"},
        "xaxis": {"tickfont": {"size": 10, "family": "Inter"},
                   "side": "top"},
    })
    return fig


# ── 4. adaptive_chart — Bayesian LAR/UAR bands ────────────────────────────

def adaptive_chart(data_points, adaptive_obs, *,
                    color: str = "#004185",
                    height: int = 384, unit: str = ""):
    """Adaptive reference-range chart — emerald LAR/UAR band from R API.
    Falls back to `analytics_chart` (sd_bands) when no adaptive_obs given."""
    if not data_points or not adaptive_obs:
        return analytics_chart(data_points, {}, mode="sd_bands",
                                height=height, color=color, unit=unit)

    dates  = [p["date"]  for p in data_points]
    values = [p["value"] for p in data_points]
    fig = go.Figure()

    lars = [o.get("LAR", 0) for o in adaptive_obs]
    uars = [o.get("UAR", 0) for o in adaptive_obs]
    odates = [o.get("test_time", "")[:10] for o in adaptive_obs]

    fig.add_trace(go.Scatter(
        x=odates, y=uars, mode="lines",
        line=dict(color=VALD_COLORS["adaptive_line"], width=2, dash="dashdot"),
        showlegend=False, hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=odates, y=lars, mode="lines",
        line=dict(color=VALD_COLORS["adaptive_line"], width=2, dash="dashdot"),
        fill="tonexty", fillcolor=VALD_COLORS["adaptive_fill"],
        showlegend=False, hoverinfo="skip",
    ))

    fig.add_trace(go.Scatter(
        x=dates, y=values, mode="lines+markers",
        line=dict(color=color, width=3, shape="linear"),
        marker=dict(size=7, color=color, line=dict(width=2, color="white")),
        hovertemplate="<b>%{x}</b><br>Value: %{y:.2f}" + unit + "<extra></extra>",
    ))

    abnormal = [o for o in adaptive_obs if o.get("outcome") == "Abnormal"]
    if abnormal:
        fig.add_trace(go.Scatter(
            x=[o["test_time"][:10] for o in abnormal],
            y=[o["value"] for o in abnormal],
            mode="markers",
            marker=dict(size=16, color="rgba(245,158,11,0.3)",
                        symbol="circle",
                        line=dict(width=2.5, color=VALD_COLORS["alert_amber"])),
            name="Abnormal", hoverinfo="skip",
        ))

    y_min, y_max = min(values), max(values)
    y_min, y_max = min(y_min, min(lars)), max(y_max, max(uars))
    pad = (y_max - y_min if y_max > y_min else abs(y_max) * 0.2) * 0.10

    fig.update_layout(**{
        **VALD_LAYOUT, "height": height,
        "yaxis": {**VALD_LAYOUT["yaxis"], "range": [y_min - pad, y_max + pad]},
    })
    return fig


# ── 5. vald_cmj_grid — 2×2 dashboard wrapper ──────────────────────────────

def vald_cmj_grid(panels: list[dict]):
    """Render the CMJ 4-panel dashboard.

    Each panel dict: ``{title, unit, color, figure}`` (figure = one of the
    chart helpers above). The grid keeps the exact VALD app spacing:
    2 columns × 2 rows, 12 px gap, panel-title above each.

    >>> vald_cmj_grid([
    ...     {"title": "Jump Height (cm)", "color": "#01b8aa",
    ...      "figure": cmj_panel_chart(jh_data, jh_stats)},
    ...     {"title": "Peak Power (W/kg)", "color": "#f59e0b",
    ...      "figure": cmj_panel_chart(pp_data, pp_stats)},
    ...     {"title": "Concentric Imp. (N·s)", "color": "#7c3aed",
    ...      "figure": cmj_panel_chart(ci_data, ci_stats)},
    ...     {"title": "RSI (m/s)", "color": "#dc2626",
    ...      "figure": cmj_panel_chart(rsi_data, rsi_stats)},
    ... ])
    """
    cards = []
    for p in panels:
        cards.append(html.Div([
            html.Div(p.get("title", ""), style={
                "fontSize": "12px", "fontWeight": 600,
                "color": "#374151", "textTransform": "uppercase",
                "letterSpacing": "0.5px", "marginBottom": "8px",
            }),
            dcc.Graph(figure=p["figure"], config=GRAPH_CONFIG),
        ], className="card", style={"padding": "16px"}))
    return html.Div(cards, style={
        "display": "grid",
        "gridTemplateColumns": "repeat(2, 1fr)",
        "gap": "12px",
    })
