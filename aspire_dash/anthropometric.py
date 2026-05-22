"""Anthropometric components — Heath-Carter somatochart, LMS growth bands,
athlete snapshot card.

Ported from the Next.js DASH_Anthro app (Ruwwad report). Built so any
Aspire Dash app touching height / weight / skinfolds / somatotype can
drop in the same visuals without re-implementing the math.
"""
from __future__ import annotations

import math
from typing import Iterable

import pandas as pd
import plotly.graph_objects as go
from dash import html

from .theme import ASPIRE, SLATE, CHART_COLORS
from .charts import apply_template
from .metrics import lms_to_percentile, percentile_to_value


# ── 1. Heath-Carter somatochart ────────────────────────────────────────────

# Vertices from Nandikolmath et al. 2024 (DOI: 10.34256/ijk2417)
# X = ectomorphy - endomorphy ; Y = 2*mesomorphy - (endomorphy + ectomorphy)
_SOMATO_VERTICES = {
    "ENDOMORPH":  (-6, -6),
    "ECTOMORPH":  ( 6, -6),
    "MESOMORPH":  ( 0, 12),
}


def _somato_xy(endo: float, meso: float, ecto: float) -> tuple[float, float]:
    """Convert (endo, meso, ecto) somatotype to (x, y) on the somatochart."""
    return ecto - endo, 2 * meso - (endo + ecto)


def somatochart(
    points: list[dict],
    *,
    title: str | None = None,
    height: int = 380,
):
    """Heath-Carter somatochart.

    `points` is a list of `{name, endo, meso, ecto, color, date}`.
    Multiple points (e.g. one per measurement date) show a trajectory.

        >>> somatochart([
        ...     {"name": "Ali", "endo": 1.8, "meso": 5.0, "ecto": 2.3},
        ... ])
    """
    fig = go.Figure()
    # Triangle outline
    xs = [_SOMATO_VERTICES[k][0] for k in ["ENDOMORPH", "ECTOMORPH", "MESOMORPH", "ENDOMORPH"]]
    ys = [_SOMATO_VERTICES[k][1] for k in ["ENDOMORPH", "ECTOMORPH", "MESOMORPH", "ENDOMORPH"]]
    fig.add_trace(go.Scatter(
        x=xs, y=ys, mode="lines",
        line=dict(color=SLATE["300"], width=1.5, dash="dot"),
        hoverinfo="skip", showlegend=False,
    ))
    # Vertex labels
    for label, (x, y) in _SOMATO_VERTICES.items():
        fig.add_annotation(x=x, y=y, text=label,
                            showarrow=False, yshift=(20 if y > 0 else -16),
                            font=dict(size=10, color=SLATE["500"],
                                      family="Poppins"))
    # Athlete points
    for i, p in enumerate(points):
        x, y = _somato_xy(p["endo"], p["meso"], p["ecto"])
        color = p.get("color", CHART_COLORS[i % len(CHART_COLORS)])
        name = p.get("name", "")
        label = f"{p['endo']:.1f}-{p['meso']:.1f}-{p['ecto']:.1f}"
        fig.add_trace(go.Scatter(
            x=[x], y=[y], mode="markers+text",
            text=[label], textposition="top center",
            marker=dict(size=10, color=color, line=dict(color="white", width=2)),
            name=name, textfont=dict(size=10),
            hovertemplate=f"<b>{name}</b><br>"
                           f"Endo: {p['endo']:.1f}<br>"
                           f"Meso: {p['meso']:.1f}<br>"
                           f"Ecto: {p['ecto']:.1f}<extra></extra>",
        ))
    fig.update_layout(
        title=title, height=height,
        xaxis=dict(range=[-12, 12], visible=False, fixedrange=True),
        yaxis=dict(range=[-10, 16], visible=False, fixedrange=True,
                    scaleanchor="x", scaleratio=1),
        plot_bgcolor="white",
        margin=dict(t=24 if title else 8, b=8, l=8, r=8),
        showlegend=len(points) > 1,
    )
    return apply_template(fig)


# ── 2. LMS growth chart ────────────────────────────────────────────────────

def growth_chart(
    df: pd.DataFrame,
    *,
    age_col: str,
    value_col: str,
    lms_table: pd.DataFrame,
    age_in_lms: str = "age",
    title: str | None = None,
    height: int = 360,
    percentiles: Iterable[float] = (3, 15, 50, 85, 97),
):
    """CDC/WHO-style LMS percentile-band growth chart with athlete trace.

    `df`           — measurements: columns `[age_col, value_col]`
    `lms_table`    — reference LMS values per age: columns `[age, L, M, S]`
    `percentiles`  — bands to draw (default 3rd/15th/50th/85th/97th)

        >>> growth_chart(athlete_df, age_col="age_yr", value_col="bmi",
        ...              lms_table=who_bmi_lms_male)
    """
    fig = go.Figure()
    # Percentile band lines
    ages = lms_table[age_in_lms].values
    band_colors = ["#cbd5e1", "#94a3b8", ASPIRE["600"], "#94a3b8", "#cbd5e1"]
    band_widths = [1, 1.2, 2, 1.2, 1]
    for pct, color, width in zip(percentiles, band_colors, band_widths):
        ys = [percentile_to_value(pct, row.L, row.M, row.S)
              for row in lms_table.itertuples()]
        fig.add_trace(go.Scatter(
            x=ages, y=ys, mode="lines",
            line=dict(color=color, width=width,
                       dash=("solid" if int(pct) == 50 else "dot")),
            name=f"{int(pct)}th",
            hoverinfo="skip",
        ))
    # Athlete trace
    fig.add_trace(go.Scatter(
        x=df[age_col], y=df[value_col],
        mode="lines+markers", name="Athlete",
        line=dict(color=ASPIRE["700"], width=2.5),
        marker=dict(size=8, color=ASPIRE["700"],
                     line=dict(color="white", width=1.5)),
    ))
    fig.update_layout(
        title=title, height=height,
        xaxis_title=age_col, yaxis_title=value_col,
        legend=dict(orientation="h", y=-0.18, x=0,
                     font=dict(size=10)),
    )
    return apply_template(fig)


# ── 3. Athlete snapshot card (Ruwwad-style attribute table) ────────────────

def athlete_snapshot_card(
    title: str,
    measurements: list[dict],
    *,
    accent: str = "aspire",
):
    """Ruwwad-style attribute table: label / value / unit per row.

    `measurements` is a list of `{label, value, unit}` dicts.

        >>> athlete_snapshot_card(
        ...     "Athlete Snapshot",
        ...     measurements=[
        ...         {"label": "Body Mass", "value": "83.5", "unit": "kg"},
        ...         {"label": "Stature",   "value": "184.6", "unit": "cm"},
        ...         {"label": "BMI",       "value": "24.5", "unit": "kg/m²"},
        ...         {"label": "Body Fat %","value": "12.1", "unit": "%"},
        ...         {"label": "Somatotype","value": "1.8-5.0-2.3", "unit": ""},
        ...     ],
        ... )
    """
    rows = []
    for m in measurements:
        rows.append(html.Div([
            html.Span(m["label"], style={"flex": "1",
                                           "color": SLATE["600"],
                                           "fontSize": "13px"}),
            html.Span(str(m["value"]), style={"fontWeight": 700,
                                                "color": SLATE["900"],
                                                "fontSize": "14px",
                                                "fontVariantNumeric": "tabular-nums",
                                                "marginRight": "4px"}),
            html.Span(m.get("unit", ""),
                       style={"fontSize": "10px",
                              "color": SLATE["400"],
                              "fontWeight": 500}),
        ], style={"display": "flex", "alignItems": "baseline",
                   "padding": "8px 0",
                   "borderBottom": f"1px solid {SLATE['100']}"}))
    return html.Div([
        html.Div(title, style={
            "padding": "10px 16px", "background": ASPIRE["900"],
            "color": "white", "fontSize": "11px", "fontWeight": 600,
            "textTransform": "uppercase", "letterSpacing": "0.5px",
        }),
        html.Div(rows, style={"padding": "8px 16px"}),
    ], className=f"card accent-{accent}")


# ── 4. Limb symmetry bar ───────────────────────────────────────────────────

def limb_symmetry_bar(label: str, left: float, right: float, *,
                       max_value: float | None = None):
    """Per-limb L/R symmetry strip — Ruwwad's right-column pattern.

    Shows a horizontal bar with left + right values, plus the symmetry %
    on the right (clipped between 0-100). Border tinted by deviation.
    """
    max_value = max_value or max(abs(left), abs(right)) * 1.1
    sym_pct = 100 * (1 - abs(left - right) / max(left, right, 1e-9))
    color = ("#16a34a" if sym_pct >= 97 else
             "#f59e0b" if sym_pct >= 92 else "#dc2626")
    return html.Div([
        html.Div([
            html.Span(label, style={"fontSize": "11px",
                                       "fontWeight": 600,
                                       "color": SLATE["700"]}),
            html.Span(f"{sym_pct:.1f}%",
                       style={"marginLeft": "auto",
                              "fontWeight": 700, "color": color,
                              "fontVariantNumeric": "tabular-nums",
                              "fontSize": "11px"}),
        ], style={"display": "flex", "marginBottom": "3px"}),
        html.Div([
            # Left bar (blue)
            html.Div(f"L {left:.1f}", style={
                "width": f"{100 * left / max_value:.1f}%",
                "background": ASPIRE["600"], "color": "white",
                "padding": "3px 6px", "fontSize": "10px",
                "fontWeight": 600,
                "borderRadius": "3px 0 0 3px",
            }),
            # Right bar (slate)
            html.Div(f"{right:.1f} R", style={
                "width": f"{100 * right / max_value:.1f}%",
                "background": SLATE["500"], "color": "white",
                "padding": "3px 6px", "fontSize": "10px",
                "fontWeight": 600, "textAlign": "right",
                "borderRadius": "0 3px 3px 0",
            }),
        ], style={"display": "flex", "borderRadius": "3px",
                   "overflow": "hidden",
                   "border": f"1px solid {color}"}),
    ], style={"marginBottom": "10px"})
