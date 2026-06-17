"""Anthropometric components — Heath-Carter somatochart, LMS growth bands,
athlete snapshot card, skinfold silhouette, squad z-score heatmap + radar.

Ported from the Next.js DASH_Anthro app (Ruwwad report). Built so any
Aspire Dash app touching height / weight / skinfolds / somatotype can
drop in the same visuals without re-implementing the math.

The z-score helpers re-export from ``aspire_dash.zscores`` so callers can
pull both the math engine and the renderers from one module if they want.

Note on naming
--------------
``skinfold_silhouette`` (8-site ISAK dots) deliberately uses a different
name from ``aspire_dash.medical.body_silhouette`` (injury-region
heatmap). Two genuinely different visuals, two different SVGs, two
different domains — keep them addressable side-by-side.
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
from .zscores import (
    INVERTED_MEASURES,
    Z_SCORE_MEASURES,
    compute_squad_z_scores,
    is_inverted,
    z_score,
    z_score_color,
)

__all__ = [
    "somatochart",
    "growth_chart",
    "athlete_snapshot_card",
    "limb_symmetry_bar",
    "skinfold_silhouette",
    "skinfold_silhouette_svg",
    "zscore_heatmap",
    "zscore_radar_figure",
    # Maturation / growth colour rules (shared so every app shades the same way).
    "MAT_COLOUR_GREEN",
    "MAT_COLOUR_AMBER",
    "MAT_COLOUR_RED",
    "GROWTH_RED_CM",
    "WEIGHT_RED_KG",
    "mat_status_colour",
    "pah_colour",
    "growth_colour",
    "weight_change_colour",
    # Re-exported from .zscores for one-stop imports.
    "INVERTED_MEASURES",
    "Z_SCORE_MEASURES",
    "compute_squad_z_scores",
    "is_inverted",
    "z_score",
    "z_score_color",
]


# ── Maturation / growth colour rules ───────────────────────────────────────
# The Aspire athlete-development colour convention (matched to the Power BI
# "Development Testing Dashboard" card conditional-formatting). Maturation
# status & % predicted adult height share the PHV bands; Circa-PHV / 90–95.99%
# PAH = RED (peak height velocity, highest injury-risk window). 12-month growth
# ≥ 7.5 cm and 12-month weight gain ≥ 9 kg flag red. Colours match the app
# palette (maturation chips, ref-range bands). Pre-PHV / sub-threshold → None.
MAT_COLOUR_GREEN = "#27AE60"
MAT_COLOUR_AMBER = "#E67E22"
MAT_COLOUR_RED = "#E74C3C"
GROWTH_RED_CM = 7.5
WEIGHT_RED_KG = 9.0


def mat_status_colour(status: str | None) -> str | None:
    """Maturation-status label → hex. Pre-PHV / unknown → None (no fill)."""
    return {"Post-PHV": MAT_COLOUR_GREEN, "Approaching-PHV": MAT_COLOUR_AMBER,
            "Circa-PHV": MAT_COLOUR_RED}.get(status)


def pah_colour(pah: float | None) -> str | None:
    """% Predicted Adult Height → hex band. ≥96 green · 90–95.99 red (Circa,
    peak growth) · 85–89.99 amber · ≤84.99 / no data → None."""
    if pah is None or pd.isna(pah):
        return None
    if pah >= 96:
        return MAT_COLOUR_GREEN
    if pah >= 90:
        return MAT_COLOUR_RED
    if pah >= 85:
        return MAT_COLOUR_AMBER
    return None


def growth_colour(height_yoy_cm: float | None) -> str | None:
    """12-month height growth → red at ≥ 7.5 cm/yr, else None."""
    if height_yoy_cm is None or pd.isna(height_yoy_cm):
        return None
    return MAT_COLOUR_RED if height_yoy_cm >= GROWTH_RED_CM else None


def weight_change_colour(weight_yoy_kg: float | None) -> str | None:
    """12-month weight change → red at ≥ 9 kg/yr, else None."""
    if weight_yoy_kg is None or pd.isna(weight_yoy_kg):
        return None
    return MAT_COLOUR_RED if weight_yoy_kg >= WEIGHT_RED_KG else None


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
            html.Span(m["label"], className="snapshot-card__label"),
            html.Span(str(m["value"]), className="snapshot-card__value"),
            html.Span(m.get("unit", ""), className="snapshot-card__unit"),
        ], className="snapshot-card__row"))
    return html.Div([
        html.Div(title, className="snapshot-card__header"),
        html.Div(rows, className="snapshot-card__body"),
    ], className=f"card snapshot-card accent-{accent}")


# ── 4. Limb symmetry bar ───────────────────────────────────────────────────

def limb_symmetry_bar(label: str, left: float, right: float, *,
                       max_value: float | None = None):
    """Per-limb L/R symmetry strip — Ruwwad's right-column pattern.

    Shows a horizontal bar with left + right values, plus the symmetry %
    on the right (clipped between 0-100). Border tinted by deviation.
    """
    max_value = max_value or max(abs(left), abs(right)) * 1.1
    sym_pct = 100 * (1 - abs(left - right) / max(left, right, 1e-9))
    tone = ("sym-good" if sym_pct >= 97 else
            "sym-warn" if sym_pct >= 92 else "sym-danger")
    return html.Div([
        html.Div([
            html.Span(label, className="limb-sym__name"),
            html.Span(f"{sym_pct:.1f}%", className="limb-sym__pct"),
        ], className="limb-sym__head"),
        html.Div([
            # bar widths are data-driven — stay inline
            html.Div(f"L {left:.1f}", className="limb-sym__left",
                     style={"width": f"{100 * left / max_value:.1f}%"}),
            html.Div(f"{right:.1f} R", className="limb-sym__right",
                     style={"width": f"{100 * right / max_value:.1f}%"}),
        ], className="limb-sym__track"),
    ], className=f"limb-sym {tone}")


# ── 5. Skinfold silhouette ─────────────────────────────────────────────────
#
# Front-view male anatomical SVG outline with 8 ISAK skinfold-site dots,
# dots tinted blue→amber by relative magnitude (largest = amber).
#
# Source: the body outline path comes from the open-source
# `react-native-body-highlighter` project (MIT, Copyright (c) 2022
# ELABBASSI Hicham). Skinfold-site positions are hand-placed for the
# 0 0 724 1448 viewBox.
#
# Distinct from ``aspire_dash.medical.body_silhouette`` (injury-region
# heatmap built off the bodymap SVG with named region IDs). Both are
# valid Aspire visuals; this one is for body-comp / ISAK contexts.

# Front-view male body outline (MIT, react-native-body-highlighter).
_SKINFOLD_BODY_PATH = (
    "M 309.48 168.91 Q 305.84 164.32 303.32 169.76 C 298.49 180.21 308.31 200.03 314.51 208.74 "
    "C 316.34 211.31 318.01 208.95 318.58 207.26 A 0.67 0.66 57.6 0 1 319.87 207.55 "
    "C 319.06 215.09 318.68 227.40 324.34 232.47 C 327.22 235.05 326.97 235.88 326.92 239.51 "
    "Q 326.68 255.16 323.97 266.82 Q 323.85 267.35 323.48 267.73 Q 308.61 282.73 290.26 293.23 "
    "C 278.34 300.05 267.53 299.26 253.00 298.03 Q 237.49 296.72 224.74 305.21 "
    "C 208.71 315.86 190.95 335.73 189.24 355.50 Q 186.95 381.81 190.53 412.66 "
    "C 190.79 414.92 190.69 417.49 191.02 419.92 Q 191.09 420.43 190.88 420.90 "
    "C 187.89 427.65 183.99 434.89 181.93 441.29 C 177.25 455.76 176.31 470.23 176.20 486.02 "
    "Q 176.20 486.51 175.90 486.90 C 159.84 507.69 147.56 529.29 141.49 554.95 "
    "Q 140.10 560.80 138.16 574.66 Q 131.28 623.74 118.11 671.52 "
    "C 115.99 679.21 112.98 690.29 104.08 693.63 Q 90.70 698.65 79.29 707.27 "
    "C 73.17 711.89 69.48 719.95 66.12 726.62 C 62.44 733.91 47.57 737.30 49.20 746.00 "
    "C 49.75 748.96 51.89 750.13 54.75 750.02 Q 67.27 749.50 74.18 740.00 "
    "C 76.03 737.45 77.93 736.62 80.54 735.24 Q 81.02 734.98 81.24 735.48 "
    "Q 84.59 743.00 80.47 750.73 Q 71.41 767.75 62.21 784.70 Q 60.53 787.81 59.49 791.20 "
    "C 57.52 797.69 65.78 800.84 69.45 795.20 C 76.80 783.92 82.72 773.30 92.55 762.52 "
    "Q 93.00 762.04 92.84 762.67 Q 87.89 783.24 79.07 802.44 C 77.36 806.17 75.64 812.30 79.19 815.18 "
    "C 89.50 823.53 107.08 773.44 109.24 767.88 A 0.37 0.36 -30.3 0 1 109.94 768.06 "
    "C 108.51 777.44 106.43 787.14 105.28 796.13 C 104.34 803.43 103.67 808.49 104.41 814.32 "
    "C 105.40 822.00 112.74 817.15 114.09 812.77 C 118.56 798.32 120.41 781.74 125.18 766.21 "
    "A 0.55 0.55 0.0 0 1 125.93 765.87 C 131.64 768.40 126.65 796.54 133.38 803.49 "
    "A 1.35 1.35 0.0 0 0 134.16 803.90 C 138.40 804.59 139.71 797.34 140.15 793.73 "
    "Q 141.74 780.80 142.58 767.76 Q 142.86 763.46 144.07 759.34 Q 150.39 737.64 154.77 715.46 "
    "Q 156.15 708.50 155.48 697.76 Q 154.48 681.63 161.99 665.46 Q 180.58 625.46 201.25 586.52 "
    "C 213.64 563.18 218.66 541.14 220.65 514.18 C 221.24 506.18 223.22 502.59 228.42 495.84 "
    "C 237.76 483.72 242.73 464.92 246.12 450.19 Q 246.24 449.64 246.75 449.42 L 250.30 447.82 "
    "A 0.49 0.49 0.0 0 1 250.99 448.23 Q 252.78 470.14 257.44 487.01 "
    "C 259.04 492.80 264.20 498.21 265.32 505.20 C 265.91 508.82 266.99 512.44 267.11 516.00 "
    "Q 267.57 529.33 266.95 540.50 C 265.58 565.32 263.85 592.20 259.98 619.13 "
    "C 258.39 630.19 253.14 640.55 250.52 651.43 Q 245.19 673.62 242.32 696.24 "
    "C 239.63 717.56 236.59 740.02 236.04 757.75 Q 234.98 791.48 237.98 842.55 "
    "Q 239.43 867.18 244.64 891.26 Q 247.76 905.70 255.88 917.90 Q 256.15 918.31 256.08 918.79 "
    "C 254.89 926.25 257.03 933.47 255.60 940.95 Q 252.28 958.32 251.77 975.98 "
    "C 251.55 983.43 252.85 991.28 253.67 998.93 Q 253.99 1001.95 253.29 1005.00 "
    "C 239.19 1067.03 246.93 1130.64 261.77 1190.07 C 266.01 1207.06 266.47 1222.37 264.71 1240.03 "
    "C 263.85 1248.62 262.10 1260.41 264.24 1268.75 C 266.05 1275.80 267.54 1287.46 261.78 1293.28 "
    "C 256.71 1298.39 242.40 1310.55 240.72 1316.98 C 239.19 1322.86 235.04 1332.26 242.29 1333.71 "
    "Q 242.69 1333.79 243.08 1333.66 L 244.23 1333.29 Q 245.05 1333.02 244.81 1333.85 "
    "C 242.95 1340.16 249.20 1340.52 253.77 1340.86 C 256.46 1341.06 257.37 1343.60 259.30 1344.71 "
    "Q 263.13 1346.91 267.14 1344.43 Q 267.59 1344.15 267.92 1344.56 Q 271.17 1348.61 276.21 1349.09 "
    "C 278.90 1349.35 281.27 1347.36 283.62 1346.09 Q 284.10 1345.82 284.44 1346.26 "
    "Q 288.33 1351.29 294.72 1351.38 C 295.77 1351.39 297.65 1351.62 298.54 1350.79 "
    "Q 301.20 1348.30 306.57 1341.58 C 312.04 1334.74 311.14 1328.85 310.29 1320.16 "
    "C 309.43 1311.33 311.17 1303.41 313.76 1295.20 C 315.84 1288.56 313.35 1280.06 314.07 1273.15 "
    "C 314.57 1268.39 315.80 1263.68 315.01 1259.02 C 314.06 1253.42 311.98 1247.60 311.31 1242.66 "
    "Q 309.57 1229.80 309.57 1219.75 Q 309.57 1192.29 313.54 1161.94 "
    "C 315.34 1148.21 319.24 1136.08 324.12 1123.46 Q 325.66 1119.48 326.10 1115.72 "
    "C 330.14 1081.34 326.20 1048.44 320.65 1013.26 C 319.84 1008.17 319.39 1002.54 321.72 997.72 "
    "C 328.03 984.68 329.28 969.38 329.07 954.15 C 329.01 949.50 327.95 944.55 327.58 939.63 "
    "C 327.13 933.64 329.28 925.78 330.82 919.80 C 334.72 904.69 337.76 888.96 341.43 874.30 "
    "Q 348.95 844.25 355.42 813.95 C 358.50 799.49 357.70 784.78 357.75 768.06 "
    "Q 357.78 756.80 356.36 748.81 Q 356.26 748.24 356.77 748.50 L 363.71 751.99 "
    "A 1.07 1.07 0.0 0 0 364.67 751.99 L 371.53 748.56 Q 372.07 748.29 371.98 748.89 "
    "C 369.47 765.94 370.28 783.04 371.30 800.17 Q 371.86 809.54 372.73 813.51 "
    "C 378.37 839.12 384.90 864.49 390.59 890.08 Q 394.83 909.20 399.51 928.22 "
    "C 400.58 932.58 401.13 937.66 400.58 941.57 C 398.11 958.92 398.53 982.22 407.11 998.54 "
    "C 408.41 1001.01 408.74 1005.35 408.31 1008.09 C 402.82 1043.75 398.07 1079.22 402.19 1115.33 "
    "Q 402.65 1119.34 404.21 1123.44 C 410.53 1140.06 413.55 1150.61 415.25 1164.75 "
    "C 418.31 1190.26 420.52 1218.43 416.79 1244.33 C 415.56 1252.86 411.78 1258.57 413.63 1267.80 "
    "Q 415.33 1276.21 414.16 1284.74 C 413.11 1292.39 415.65 1298.68 417.31 1305.89 "
    "C 419.02 1313.32 418.11 1320.99 417.47 1328.50 C 416.71 1337.55 423.74 1344.86 430.17 1350.90 "
    "A 1.48 1.46 -18.7 0 0 430.95 1351.28 Q 439.25 1352.41 444.03 1346.06 "
    "Q 444.40 1345.57 444.87 1345.96 Q 453.39 1352.89 460.49 1344.48 Q 460.81 1344.11 461.23 1344.37 "
    "C 469.09 1349.37 469.89 1340.80 474.98 1340.71 C 479.52 1340.64 485.21 1340.09 483.54 1333.77 "
    "Q 483.38 1333.17 483.97 1333.35 C 488.25 1334.67 490.66 1331.94 490.06 1327.75 "
    "C 489.09 1321.04 487.50 1314.41 483.44 1310.30 Q 474.77 1301.53 466.05 1292.83 "
    "C 461.19 1287.98 462.25 1276.40 463.74 1270.47 C 466.27 1260.35 464.49 1248.06 463.03 1236.25 "
    "C 461.04 1220.05 463.22 1204.28 467.41 1187.04 C 481.60 1128.60 488.89 1065.20 475.23 1006.07 "
    "C 473.92 1000.37 475.00 995.00 475.76 989.36 C 477.88 973.68 475.72 958.50 473.08 942.76 "
    "C 471.70 934.55 473.60 926.56 472.20 918.79 Q 472.11 918.30 472.39 917.89 "
    "C 483.07 902.63 486.53 880.99 488.49 863.25 C 492.12 830.38 492.47 797.34 492.26 764.31 "
    "C 492.11 741.56 488.80 719.07 486.12 696.53 C 484.30 681.19 480.76 664.32 477.47 649.99 "
    "C 474.89 638.73 469.69 628.87 468.04 617.25 C 465.37 598.45 464.19 580.92 462.40 556.31 "
    "Q 460.86 535.06 461.01 522.74 Q 461.13 512.05 463.22 504.00 "
    "C 464.54 498.90 468.30 493.91 469.91 489.46 C 474.50 476.74 476.10 461.71 477.56 448.28 "
    "Q 477.62 447.74 478.13 447.94 L 481.73 449.35 A 0.77 0.77 0.0 0 1 482.19 449.89 "
    "Q 486.03 466.84 492.52 482.96 C 494.16 487.04 496.63 491.75 500.12 495.79 "
    "C 505.75 502.32 507.17 507.95 508.00 517.24 C 509.72 536.47 512.15 552.06 518.89 569.24 "
    "Q 521.60 576.16 527.50 587.28 Q 543.57 617.60 558.56 648.47 "
    "C 566.04 663.89 571.90 675.54 572.85 690.59 Q 572.98 692.57 572.55 700.88 "
    "Q 572.12 709.31 573.99 718.25 Q 577.87 736.78 582.37 752.38 "
    "C 585.15 761.98 586.32 769.32 586.71 778.53 C 586.92 783.46 587.58 803.53 593.41 804.06 "
    "C 599.41 804.61 599.71 774.61 600.39 768.08 A 1.12 1.12 0.0 0 1 600.80 767.33 "
    "Q 601.30 766.93 601.62 766.30 A 1.39 1.00 59.0 0 1 603.70 767.19 "
    "C 607.27 782.50 609.43 797.55 614.25 812.25 C 615.52 816.12 618.33 820.08 622.81 817.38 "
    "A 1.18 1.17 -8.4 0 0 623.35 816.66 Q 624.98 810.32 624.13 803.72 "
    "Q 621.83 785.89 618.23 768.64 A 0.53 0.53 0.0 0 1 619.24 768.34 "
    "C 622.72 777.06 636.06 814.20 645.24 816.03 C 650.64 817.10 652.13 811.12 650.95 807.31 "
    "C 648.59 799.74 644.42 791.59 642.09 784.69 Q 638.29 773.46 635.22 761.98 "
    "A 0.15 0.14 -73.3 0 1 635.47 761.84 Q 640.35 767.61 644.90 773.66 "
    "C 649.45 779.70 653.60 787.18 658.03 793.93 Q 660.09 797.07 661.70 797.82 "
    "C 665.53 799.62 670.61 795.77 669.00 791.28 C 666.63 784.66 661.63 776.66 659.33 772.19 "
    "Q 654.22 762.29 648.82 752.53 C 645.43 746.40 644.71 741.93 646.89 735.59 "
    "Q 647.08 735.05 647.60 735.27 C 650.55 736.50 652.37 737.45 654.44 740.27 "
    "Q 661.27 749.61 673.53 749.92 C 681.25 750.12 680.47 740.89 676.20 738.28 "
    "C 671.33 735.31 664.61 731.14 661.97 725.94 C 657.98 718.11 654.62 711.26 649.21 707.28 "
    "Q 637.40 698.62 623.76 693.40 C 619.45 691.75 615.12 686.26 613.76 682.47 "
    "Q 608.42 667.65 602.70 641.81 Q 594.90 606.62 590.85 578.90 Q 588.46 562.58 587.74 559.15 "
    "C 582.02 531.75 569.74 509.81 552.98 487.61 C 551.81 486.06 551.91 485.12 551.97 483.26 "
    "Q 552.48 466.57 548.70 449.61 C 546.27 438.71 541.82 430.32 537.44 420.82 "
    "Q 537.22 420.36 537.28 419.85 C 539.40 398.94 540.83 377.68 539.05 356.70 "
    "C 537.31 336.13 521.34 317.28 504.86 306.23 C 494.75 299.45 485.77 296.97 473.93 298.16 "
    "Q 464.41 299.12 453.63 298.41 C 438.05 297.39 418.32 280.58 407.40 270.35 "
    "C 405.82 268.87 404.57 267.56 404.10 265.32 Q 401.24 251.68 401.26 237.76 "
    "Q 401.26 233.73 404.68 232.04 Q 405.14 231.82 405.39 231.38 "
    "C 409.76 223.86 408.77 215.16 408.75 206.85 A 0.38 0.38 0.0 0 1 409.48 206.69 "
    "C 410.36 208.62 412.01 211.62 414.22 208.45 C 421.05 198.67 427.45 183.93 425.97 172.00 "
    "C 425.49 168.15 422.83 165.91 418.91 167.68"
)

# ISAK skinfold dot positions for the 0 0 724 1448 viewBox.
# Subject's right side (viewer's left). Subject centre x≈362.
_SKINFOLD_SITE_POSITIONS: dict[str, dict[str, float]] = {
    "biceps":       {"cx": 215, "cy": 470},   # front of upper R arm
    "triceps":      {"cx": 178, "cy": 490},   # back of upper R arm (outboard)
    "subscapular":  {"cx": 258, "cy": 440},   # below R shoulder blade
    "supraspinale": {"cx": 268, "cy": 660},   # above R hip, slightly forward
    "iliac_crest":  {"cx": 240, "cy": 705},   # R hip / waist
    "abdominal":    {"cx": 312, "cy": 625},   # R of navel
    "front_thigh":  {"cx": 308, "cy": 920},   # mid R thigh (front)
    "medial_calf":  {"cx": 320, "cy": 1170},  # inner R calf (toward midline)
}


def _skinfold_value_to_color(value: float | None, max_value: float) -> str:
    """Blue (#3b82f6) → Amber (#f59e0b) linear interpolation by magnitude."""
    if value is None or max_value <= 0:
        return "#3b82f6"
    t = min(value / max_value, 1.0)
    r = round(59 + (245 - 59) * t)
    g = round(130 + (158 - 130) * t)
    b = round(246 + (11 - 246) * t)
    return f"rgb({r},{g},{b})"


def skinfold_silhouette_svg(sites: list[dict]) -> str:
    """Return raw SVG markup for the ISAK-site silhouette.

    Use this when you need to embed the SVG yourself (e.g. inside an
    HTML report, a custom iframe, or a Pandoc render). Otherwise prefer
    ``skinfold_silhouette`` which wraps it in a Dash component.

    Parameters
    ----------
    sites : list[dict]
        ``[{"key": "biceps", "label": "Biceps", "value": 6.2}, ...]``.
        Valid keys: biceps, triceps, subscapular, supraspinale,
        iliac_crest, abdominal, front_thigh, medial_calf. Unknown keys
        are silently skipped. ``value`` may be ``None`` for missing
        measurements — the dot still renders in base blue.

    Notes
    -----
    Distinct from ``aspire_dash.medical.body_silhouette`` (injury-region
    heatmap). This visual uses a different SVG outline (MIT, from
    react-native-body-highlighter) and overlays single-point ISAK dots
    rather than colourising body-map regions.
    """
    max_value = 0.0
    for s in sites:
        v = s.get("value")
        if v is not None and v > max_value:
            max_value = v

    # ViewBox extends slightly below the figure (1448 → 1500) to leave
    # room for the legend bar.
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 724 1500" '
        'preserveAspectRatio="xMidYMin meet" '
        'style="width:100%;max-width:260px;height:auto;'
        'font-family:Inter,system-ui,sans-serif;">',
        # Body outline — stroke-only, soft slate
        f'<path d="{_SKINFOLD_BODY_PATH}" fill="#f8fafc" stroke="#94a3b8" stroke-width="3" '
        'stroke-linecap="round" stroke-linejoin="round" vector-effect="non-scaling-stroke" />',
        # Gradient defs for legend
        '<defs><linearGradient id="sf-legend-grad" x1="0" y1="0" x2="1" y2="0">'
        '<stop offset="0%" stop-color="#3b82f6"/>'
        '<stop offset="100%" stop-color="#f59e0b"/>'
        '</linearGradient></defs>',
    ]

    # Site dots — radius scaled to the larger viewBox.
    for site in sites:
        pos = _SKINFOLD_SITE_POSITIONS.get(site["key"])
        if not pos:
            continue
        v = site.get("value")
        color = _skinfold_value_to_color(v, max_value)
        title = site["label"] + (f": {v:.1f} mm" if v is not None else "")
        parts.append(
            f'<circle cx="{pos["cx"]}" cy="{pos["cy"]}" r="22" fill="{color}" '
            f'stroke="white" stroke-width="6"><title>{title}</title></circle>'
        )

    # Legend bar (footer band, scaled to viewBox).
    parts += [
        '<text x="220" y="1483" font-size="30" fill="#94a3b8" text-anchor="end">Low</text>',
        '<rect x="232" y="1462" width="260" height="22" rx="11" fill="url(#sf-legend-grad)" />',
        '<text x="504" y="1483" font-size="30" fill="#94a3b8" text-anchor="start">High</text>',
        '</svg>',
    ]
    return "".join(parts)


def skinfold_silhouette(sites: list[dict]):
    """ISAK skinfold-site silhouette as a Dash component.

    Front-view male anatomical outline with 8 ISAK skinfold-site dots,
    each tinted blue→amber by the magnitude of the measurement
    (largest in the squad = full amber). Wrapped in an ``html.Iframe``
    so the inline SVG renders consistently on Posit Connect.

    Parameters
    ----------
    sites : list[dict]
        See ``skinfold_silhouette_svg``.

    Examples
    --------
    >>> from aspire_dash.anthropometric import skinfold_silhouette
    >>> skinfold_silhouette([
    ...     {"key": "biceps",      "label": "Biceps",       "value": 6.2},
    ...     {"key": "triceps",     "label": "Triceps",      "value": 9.8},
    ...     {"key": "front_thigh", "label": "Front Thigh",  "value": 12.4},
    ... ])

    Notes
    -----
    Complements ``aspire_dash.medical.body_silhouette`` (injury-region
    heatmap). Keep both addressable side-by-side — they're genuinely
    different visuals serving different domains.
    """
    svg = skinfold_silhouette_svg(sites)
    doc = (
        '<!doctype html><html><head><meta charset="utf-8">'
        '<style>html,body{margin:0;padding:0;background:transparent;'
        'display:flex;justify-content:center;align-items:flex-start;}</style>'
        '</head><body>' + svg + '</body></html>'
    )
    return html.Iframe(
        srcDoc=doc,
        style={"border": 0, "width": "100%", "maxWidth": 280, "height": 520,
               "background": "transparent"},
    )


# ── 6. Squad z-score heatmap (html.Table) ──────────────────────────────────

def _zscore_last_name(name: str) -> str:
    return name.split(" ")[-1] if name else name


def zscore_heatmap(athletes, measures, matrix, raw_values, stats):
    """Squad-vs-population z-score matrix as a Dash ``html.Table``.

    Renders a measure-by-athlete matrix with group banding, mean+SD
    columns, and a 7-bucket colour scale (deep red → near-white →
    deep green). Inverted measures (lower-is-better, e.g. skinfolds)
    flip automatically — high values render red.

    Parameters
    ----------
    athletes : list[dict]
        ``[{"id": ..., "name": ...}, ...]`` — one column per row.
    measures : list[dict]
        ``[{"key", "label", "unit", "group"}, ...]``. Group banding
        comes from the order of the list — keys with the same ``group``
        are clustered with a banner row. Use ``Z_SCORE_MEASURES`` for
        the default ISAK metadata.
    matrix : dict
        ``{athlete_id: {key: z | None}}`` — the z-score table. Typically
        the ``matrix`` key from ``compute_squad_z_scores``.
    raw_values : dict
        ``{athlete_id: {key: raw_value | None}}`` — the underlying
        measurements, shown in the hover tooltip.
    stats : dict
        ``{key: {"mean", "sd", "n"}}`` — the per-key summary. From
        ``compute_squad_z_scores`` ``stats`` key.

    Returns
    -------
    A ``html.Div`` containing a colour-key legend and the heatmap
    table, ready to drop in a page layout.
    """
    # Group rows
    group_order, grouped = [], {}
    for m in measures:
        g = m["group"]
        if g not in grouped:
            grouped[g] = []
            group_order.append(g)
        grouped[g].append(m)

    legend_stops = ["#991b1b", "#fee2e2", "#f8fafc", "#d1fae5", "#065f46"]
    legend = html.Div([
        html.Span("Below avg", className="zscore-heatmap__legend-label"),
        html.Div([html.Div(style={"backgroundColor": c}) for c in legend_stops],
                 className="zscore-heatmap__legend-bar"),
        html.Span("Above avg", className="zscore-heatmap__legend-label"),
        html.Span(" (inverted for skinfolds/fat)",
                  className="zscore-heatmap__legend-note"),
    ], className="zscore-heatmap__legend")

    # Header
    header_cells = [
        html.Th("Measure", className="zscore-table__measure-h"),
        html.Th("Mean", className="zscore-table__stat-h"),
        html.Th("SD", className="zscore-table__stat-h"),
    ]
    for a in athletes:
        header_cells.append(html.Th(_zscore_last_name(a["name"])))

    rows = [html.Tr(header_cells)]
    for grp in group_order:
        rows.append(html.Tr([html.Td(grp, colSpan=3 + len(athletes),
                                     className="zscore-table__group")]))
        for m in grouped[grp]:
            s = stats.get(m["key"], {})
            inv = is_inverted(m["key"])
            cells = [
                html.Td([m["label"],
                         html.Span(f" {m['unit']}", className="zscore-table__unit")],
                        className="zscore-table__measure"),
                html.Td(f"{s['mean']:.1f}" if s else "-",
                        className="zscore-table__stat is-mean"),
                html.Td(f"{s['sd']:.1f}" if s else "-",
                        className="zscore-table__stat is-sd"),
            ]
            for a in athletes:
                z = (matrix.get(a["id"]) or {}).get(m["key"])
                raw = (raw_values.get(a["id"]) or {}).get(m["key"])
                bg, text = z_score_color(z, inv)
                title = (f"{m['label']}: {raw:.1f} {m['unit']} (z={z:.2f})"
                         if z is not None and raw is not None
                         else f"{m['label']}: no data")
                cells.append(html.Td(
                    f"{z:.1f}" if z is not None else "--",
                    title=title,
                    className="zscore-table__cell",
                    # 7-bucket colour comes from z_score_color — stays inline
                    style={"backgroundColor": bg, "color": text},
                ))
            rows.append(html.Tr(cells))

    table = html.Table(rows, className="zscore-table")
    return html.Div([legend, html.Div(table, className="zscore-table-wrap")],
                    className="zscore-heatmap")


# ── 7. Per-athlete z-score radar (Plotly polar) ─────────────────────────────

def zscore_radar_figure(athlete_name: str, z_items):
    """Per-athlete z-score radar figure (Plotly polar).

    Closed polygon over up to ~20 measurement axes, clamped to
    ``[-3, +3]`` so an outlier doesn't blow out the scale. Designed to
    pair with ``zscore_heatmap`` — heatmap for the squad, radar to
    drill into one athlete.

    Parameters
    ----------
    athlete_name : str
        Used as plot title and hover label.
    z_items : list[dict]
        ``[{"key", "label", "z"}, ...]`` — already-computed z-scores.
        ``z`` may be ``None`` (treated as 0). Typically built from
        ``compute_squad_z_scores`` like::

            zr = compute_squad_z_scores(athletes, keys)
            z_items = [
                {"key": k, "label": label_map[k], "z": zr["matrix"][aid].get(k)}
                for k in keys
            ]

    Returns
    -------
    A ``plotly.graph_objects.Figure`` ready for ``dcc.Graph``.
    """
    labels = [it["label"] for it in z_items]
    values = [max(-3, min(3, it["z"])) if it["z"] is not None else 0 for it in z_items]

    # Close the loop
    labels_c = labels + [labels[0]]
    values_c = values + [values[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values_c, theta=labels_c,
        mode="lines+markers",
        fill="toself",
        line=dict(color="#3b82f6", width=2),
        fillcolor="rgba(59, 130, 246, 0.2)",
        marker=dict(size=5, color="#3b82f6", line=dict(color="white", width=1.5)),
        name=athlete_name, hoverinfo="text",
        text=[f"{l}: z={v:.2f}" for l, v in zip(labels, values)] + [None],
    ))
    fig.update_layout(
        title=dict(text=f"{athlete_name}<br><span style='font-size:11px;color:#94a3b8'>Z-Score Profile vs Squad Mean</span>",
                   font=dict(size=14, color="#001d3d")),
        polar=dict(
            radialaxis=dict(range=[-3, 3], tickfont=dict(size=9, color="#94a3b8"),
                            showline=False, gridcolor="#e2e8f0"),
            angularaxis=dict(tickfont=dict(size=10, color="#64748b"), gridcolor="#e2e8f0"),
            bgcolor="white",
        ),
        paper_bgcolor="white", showlegend=False,
        margin=dict(l=60, r=60, t=80, b=40),
        height=460,
        font=dict(family="Inter, system-ui, sans-serif"),
    )
    return fig
