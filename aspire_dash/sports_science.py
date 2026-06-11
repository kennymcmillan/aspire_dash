"""Sports-science chart helpers — Aspire-branded Plotly compositions.

Five domain-specific visuals coaches & S&C actually ask for:

- ``force_velocity_scatter`` — VALD ForceDecks FV profile + best-fit + Pmax
- ``lactate_curve``          — step-test lactate vs speed + HR (dual axis), per date
- ``acwr_chart``             — Acute:Chronic workload with shaded zones
- ``hr_zone_distribution``   — Z1–Z5 stacked bar (session or season)
- ``bullet_chart``           — Target vs actual w/ qualitative ranges
- ``session_load_bubble``    — sRPE × duration training-load map

All return ``dcc.Graph`` ready to drop into a layout. Branded via the
Aspire Plotly template (auto-applied) + token palette.
"""
from __future__ import annotations
import plotly.graph_objects as go
from dash import dcc

from .theme import (
    ASPIRE, ASPIRE_BLUE, SECONDARY, SLATE, SUCCESS, WARNING, DANGER, GOLD,
    FONT_DATA, FONT_HEADING, CHART_COLORS,
)
from .charts import GRAPH_CONFIG


# ─────────────────────────────────────────────────────────────────────────
# 1. Force-Velocity Profile (VALD ForceDecks style)
# ─────────────────────────────────────────────────────────────────────────


def _linfit(xs, ys):
    """Tiny least-squares (slope, intercept) without numpy."""
    n = len(xs)
    if n < 2:
        return 0.0, 0.0
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = sum((x - mx) ** 2 for x in xs)
    slope = num / den if den else 0.0
    intercept = my - slope * mx
    return slope, intercept


def force_velocity_scatter(
    samples: list[dict],
    *,
    title: str = "Force-Velocity Profile",
    height: int = 360,
    show_pmax: bool = True,
):
    """Scatter of (velocity, force) samples + linear FV regression + Pmax.

    `samples` = list of `{velocity, force, label?}` dicts. Velocity in
    m/s on x-axis, force in N (or N/kg) on y-axis. The FV line is the
    classic Samozino/Morin linear fit; Pmax (peak power) is the apex of
    F·v along that line — used to set sprint vs strength training emphasis.

    >>> force_velocity_scatter([
    ...     {"velocity": 0.3, "force": 1850, "label": "Squat"},
    ...     {"velocity": 1.1, "force": 1620, "label": "Jump squat"},
    ...     {"velocity": 2.4, "force": 1240, "label": "Loaded jump"},
    ...     {"velocity": 4.6, "force":  720, "label": "Sprint 0-5 m"},
    ... ])
    """
    xs = [s["velocity"] for s in samples]
    ys = [s["force"]    for s in samples]
    labels = [s.get("label", "") for s in samples]

    slope, intercept = _linfit(xs, ys)
    # F0 (force at v=0) = intercept; v0 (velocity at F=0) = -intercept / slope
    f0 = intercept
    v0 = (-intercept / slope) if slope else max(xs) * 1.1

    # Pmax = F0 * v0 / 4 (peak of inverted parabola P(v) = v · (F0 - slope·v))
    v_pmax = v0 / 2
    f_pmax = f0 / 2
    p_max = f_pmax * v_pmax     # watts (or W/kg if force was N/kg)

    # FV line
    xline = [0, v0]
    yline = [f0, 0]

    fig = go.Figure()
    # Samples
    fig.add_trace(go.Scatter(
        x=xs, y=ys, mode="markers+text",
        marker=dict(size=14, color=ASPIRE["600"],
                     line=dict(color="white", width=2)),
        text=labels, textposition="top center",
        textfont=dict(size=10, color=SLATE["600"], family=FONT_DATA),
        name="Samples",
        hovertemplate="<b>%{text}</b><br>v = %{x:.2f} m/s<br>F = %{y:.0f}<extra></extra>",
    ))
    # FV line
    fig.add_trace(go.Scatter(
        x=xline, y=yline, mode="lines",
        line=dict(color=SLATE["400"], width=2, dash="dash"),
        name="FV line", hoverinfo="skip",
    ))
    # Pmax point
    if show_pmax:
        fig.add_trace(go.Scatter(
            x=[v_pmax], y=[f_pmax], mode="markers+text",
            marker=dict(size=18, color=GOLD,
                         line=dict(color="white", width=3),
                         symbol="star"),
            text=[f"Pmax {p_max:,.0f}"], textposition="bottom center",
            textfont=dict(size=11, color=SLATE["800"], family=FONT_HEADING,
                          weight=600),
            name="Pmax",
            hovertemplate=(
                f"<b>Pmax</b><br>"
                f"v = {v_pmax:.2f} m/s<br>"
                f"F = {f_pmax:,.0f}<br>"
                f"P = {p_max:,.0f}<extra></extra>"
            ),
        ))

    fig.update_layout(
        title=title, height=height,
        xaxis=dict(title="Velocity (m/s)", rangemode="tozero"),
        yaxis=dict(title="Force (N)",      rangemode="tozero"),
        showlegend=False,
        margin=dict(l=50, r=20, t=40, b=40),
    )
    return dcc.Graph(figure=fig, config=GRAPH_CONFIG,
                      style={"height": f"{height}px"})


# ─────────────────────────────────────────────────────────────────────────
# 2. Acute:Chronic Workload Ratio (ACWR) chart
# ─────────────────────────────────────────────────────────────────────────


# Vibrant per-curve palette — gold / teal / amber / green / violet, with the
# latest test in Aspire blue. No greys: every test reads as its own colour.
_LACTATE_PALETTE = ["#fbb800", "#1876ab", "#e8833a", "#16a34a", "#8b5cf6", "#e11d8f"]


def lactate_curve(
    curves: dict,
    *,
    hr: bool = True,
    lt2_mmol: float = 4.0,
    lt1_mmol: float = 2.0,
    marker_size: int = 9,
    title: str = "Lactate Curves",
    height: int = 460,
    as_graph: bool = True,
):
    """Classic incremental step-test chart: speed (x) vs blood lactate (left y)
    and heart rate (right y, dashed). One curve per test date — click a date in
    the legend to toggle both its lactate + HR lines (shared legendgroup). The
    latest test is drawn boldest in Aspire blue with a soft fill; older tests
    each get a distinct vibrant colour (gold, teal, amber, green, violet — no
    greys). No zone shading — points are uniform filled circles so individual
    readings stay legible; the LT2 (4 mmol) guide line is emphasised.

    ``curves``: ordered ``{date_label: rows}`` (oldest → newest). Each ``rows``
    is anything with ``speed`` / ``la`` / ``hr`` sequences — a pandas DataFrame
    (columns) or a dict of lists. Sort by speed before passing for a clean line.

    >>> lactate_curve({"14 Sep 2022": df_old, "02 Oct 2025": df_new})
    """
    from plotly.subplots import make_subplots

    def _col(rows, name):
        try:                       # DataFrame
            return list(rows[name])
        except Exception:
            return list((rows or {}).get(name, []))

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    dates = list(curves.keys())
    n = len(dates)
    for i, d in enumerate(dates):
        rows = curves[d]
        speed, la, hrv = _col(rows, "speed"), _col(rows, "la"), _col(rows, "hr")
        is_latest = (i == n - 1)
        # latest = Aspire blue + bold + fill; older = a distinct vibrant colour
        colr = ASPIRE_BLUE if is_latest else _LACTATE_PALETTE[i % len(_LACTATE_PALETTE)]
        width = 4 if is_latest else 2.5
        fig.add_trace(go.Scatter(
            x=speed, y=la, mode="lines+markers", name=str(d), legendgroup=str(d),
            line=dict(color=colr, width=width, shape="spline"),
            marker=dict(size=marker_size, color=colr, symbol="circle",
                        line=dict(color="white", width=1.5)),
            # soft fill only under the latest curve
            fill="tozeroy" if is_latest else None,
            fillcolor="rgba(0,65,133,0.07)" if is_latest else None,
            hovertemplate="%{x:.1f} km/h<br>%{y:.2f} mmol/L<extra>" + str(d) + "</extra>",
        ), secondary_y=False)
        if hr and any(v is not None for v in hrv):
            fig.add_trace(go.Scatter(
                x=speed, y=hrv, mode="lines+markers", name=f"{d} HR",
                legendgroup=str(d), showlegend=False, opacity=0.6,
                line=dict(color=colr, width=1.5, dash="dot"),
                marker=dict(size=max(4, marker_size - 4), color=colr, symbol="circle"),
                hovertemplate="%{x:.1f} km/h<br>%{y:.0f} bpm<extra>" + str(d) + " HR</extra>",
            ), secondary_y=True)

    # LT2 (4 mmol) — emphasised; LT1 (2 mmol) — light guide
    fig.add_hline(y=lt2_mmol, line=dict(color=ASPIRE_BLUE, width=2, dash="dash"),
                  annotation_text=f"LT2 · {lt2_mmol:g} mmol",
                  annotation_position="top left",
                  annotation_font=dict(size=11, color=ASPIRE_BLUE, family=FONT_HEADING),
                  secondary_y=False)
    fig.add_hline(y=lt1_mmol, line=dict(color=SLATE["300"], width=1, dash="dot"),
                  annotation_text=f"LT1 · {lt1_mmol:g} mmol",
                  annotation_position="bottom left",
                  annotation_font=dict(size=10, color=SLATE["400"]),
                  secondary_y=False)

    fig.update_xaxes(title_text="Speed (km/h)", showgrid=True, gridcolor=SLATE["100"])
    fig.update_yaxes(title_text="Blood lactate (mmol/L)", secondary_y=False,
                     showgrid=True, gridcolor=SLATE["100"], rangemode="tozero")
    fig.update_yaxes(title_text="Heart rate (bpm)", secondary_y=True,
                     showgrid=False, rangemode="tozero")
    fig.update_layout(
        template="plotly_white", height=height,
        margin=dict(l=60, r=60, t=10, b=50),
        legend=dict(orientation="h", y=-0.18, x=0.5, xanchor="center", title_text=""),
        hovermode="closest", font=dict(family=FONT_DATA),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    )
    return dcc.Graph(figure=fig, config=GRAPH_CONFIG) if as_graph else fig


def acwr_chart(
    dates: list,
    daily_loads: list[float],
    *,
    acute_days: int = 7,
    chronic_days: int = 28,
    title: str = "Acute:Chronic Workload Ratio",
    height: int = 320,
):
    """Daily-load → rolling acute (7-d) & chronic (28-d) → ACWR line
    with shaded danger zones.

    Zones (Gabbett/Banister convention):
      - 0.8 – 1.3   sweet spot (green band)
      - 1.3 – 1.5   caution    (amber)
      - 1.5 +       danger     (red)
      - below 0.8   undertraining (slate)

    >>> acwr_chart(dates=[…], daily_loads=[…])
    """
    def _rolling(series, window):
        out = []
        for i in range(len(series)):
            start = max(0, i - window + 1)
            chunk = series[start:i + 1]
            out.append(sum(chunk) / len(chunk) if chunk else 0)
        return out

    acute   = _rolling(daily_loads, acute_days)
    chronic = _rolling(daily_loads, chronic_days)
    acwr    = [a / c if c else 0 for a, c in zip(acute, chronic)]

    fig = go.Figure()
    # Shaded zones — full chart width
    fig.add_hrect(y0=0.8, y1=1.3,
                   fillcolor="rgba(22,163,74,0.10)", line_width=0,
                   annotation_text="Sweet spot", annotation_position="top left",
                   annotation=dict(font=dict(size=10, color=SUCCESS)))
    fig.add_hrect(y0=1.3, y1=1.5,
                   fillcolor="rgba(217,119,6,0.12)", line_width=0,
                   annotation_text="Caution", annotation_position="top left",
                   annotation=dict(font=dict(size=10, color=WARNING)))
    fig.add_hrect(y0=1.5, y1=2.5,
                   fillcolor="rgba(220,38,38,0.10)", line_width=0,
                   annotation_text="Danger", annotation_position="top left",
                   annotation=dict(font=dict(size=10, color=DANGER)))
    # ACWR line
    fig.add_trace(go.Scatter(
        x=dates, y=acwr, mode="lines",
        line=dict(color=ASPIRE["600"], width=2.5),
        name="ACWR",
        hovertemplate="<b>%{x}</b><br>ACWR: %{y:.2f}<extra></extra>",
    ))
    # Reference line at 1.0 (acute = chronic)
    fig.add_hline(y=1.0, line=dict(color=SLATE["400"], width=1, dash="dot"))

    fig.update_layout(
        title=title, height=height,
        xaxis=dict(title=None),
        yaxis=dict(title="ACWR", range=[0, max(2.5, max(acwr) * 1.1 if acwr else 2.0)]),
        showlegend=False,
        margin=dict(l=40, r=20, t=40, b=40),
    )
    return dcc.Graph(figure=fig, config=GRAPH_CONFIG,
                      style={"height": f"{height}px"})


# ─────────────────────────────────────────────────────────────────────────
# 3. HR zone distribution (Z1-Z5 stacked bar)
# ─────────────────────────────────────────────────────────────────────────


_HR_ZONE_COLORS = {
    "Z1": "#94a3b8",   # slate (recovery)
    "Z2": "#16a34a",   # green (aerobic base)
    "Z3": "#fbb800",   # gold  (tempo)
    "Z4": "#d97706",   # amber (threshold)
    "Z5": "#dc2626",   # red   (VO2max+)
}


def hr_zone_distribution(
    sessions: list[dict],
    *,
    mode: str = "session",       # 'session' (one bar per session) | 'season' (one aggregated bar)
    title: str = "HR Zone Distribution",
    height: int = 280,
):
    """Stacked-bar HR zone time distribution.

    Each session dict: `{label, Z1, Z2, Z3, Z4, Z5}` — minutes per zone.

    `mode='session'`: one horizontal bar per session, stacked Z1→Z5.
    `mode='season'`: single bar showing total minutes-per-zone across all sessions.

    >>> hr_zone_distribution([
    ...     {"label": "Mon 09:00", "Z1": 5, "Z2": 25, "Z3": 18, "Z4": 8, "Z5": 4},
    ...     {"label": "Wed 17:00", "Z1": 8, "Z2": 35, "Z3": 10, "Z4": 5, "Z5": 2},
    ... ])
    """
    zones = ["Z1", "Z2", "Z3", "Z4", "Z5"]

    if mode == "season":
        totals = {z: sum(s.get(z, 0) for s in sessions) for z in zones}
        fig = go.Figure()
        for z in zones:
            fig.add_trace(go.Bar(
                x=[totals[z]], y=["Season"],
                orientation="h", name=z,
                marker=dict(color=_HR_ZONE_COLORS[z]),
                hovertemplate=f"<b>{z}</b>: %{{x:.0f}} min<extra></extra>",
            ))
    else:
        labels = [s.get("label", f"Session {i+1}") for i, s in enumerate(sessions)]
        fig = go.Figure()
        for z in zones:
            fig.add_trace(go.Bar(
                x=labels, y=[s.get(z, 0) for s in sessions],
                name=z, marker=dict(color=_HR_ZONE_COLORS[z]),
                hovertemplate=f"<b>{z}</b><br>%{{x}}: %{{y:.0f}} min<extra></extra>",
            ))

    fig.update_layout(
        barmode="stack",
        title=title, height=height,
        showlegend=True,
        legend=dict(orientation="h", y=-0.15, x=0, yanchor="top"),
        margin=dict(l=40, r=20, t=40, b=60),
    )
    if mode == "session":
        fig.update_yaxes(title="Minutes")
    return dcc.Graph(figure=fig, config=GRAPH_CONFIG,
                      style={"height": f"{height}px"})


# ─────────────────────────────────────────────────────────────────────────
# 4. Bullet chart (target vs actual)
# ─────────────────────────────────────────────────────────────────────────


def bullet_chart(
    value: float,
    target: float,
    *,
    ranges: tuple[float, float, float] = None,    # (poor, ok, good) thresholds
    label: str = "",
    sub: str | None = None,
    unit: str = "",
    height: int = 70,
):
    """Tactical bullet chart — value bar overlaid on qualitative-range bg
    with a target marker line.

    `ranges = (poor_max, ok_max, good_max)` defines the three bands.
    Defaults to `(target*0.6, target*0.9, target*1.1)` if omitted.

    >>> bullet_chart(value=42, target=40, ranges=(20, 35, 45),
    ...              label="Medals", unit="")
    """
    if ranges is None:
        ranges = (target * 0.6, target * 0.9, target * 1.1)
    poor, ok_max, good_max = ranges
    axis_max = max(good_max, value, target) * 1.1

    fig = go.Figure(go.Indicator(
        mode="number+gauge+delta",
        value=value,
        delta=dict(reference=target,
                    increasing=dict(color=SUCCESS),
                    decreasing=dict(color=DANGER),
                    font=dict(size=14)),
        number=dict(font=dict(size=18, family=FONT_HEADING),
                     suffix=unit),
        title=dict(text=f"<b>{label}</b><br><span style='font-size:11px;color:{SLATE['500']}'>{sub or ''}</span>",
                    font=dict(size=12, family=FONT_HEADING)),
        gauge=dict(
            shape="bullet",
            axis=dict(range=[0, axis_max],
                       tickfont=dict(size=10, color=SLATE["500"])),
            threshold=dict(
                line=dict(color=SLATE["900"], width=3),
                thickness=0.85, value=target,
            ),
            steps=[
                dict(range=[0, poor],          color="rgba(220,38,38,0.18)"),
                dict(range=[poor, ok_max],     color="rgba(217,119,6,0.18)"),
                dict(range=[ok_max, good_max], color="rgba(22,163,74,0.18)"),
                dict(range=[good_max, axis_max], color="rgba(0,65,133,0.10)"),
            ],
            bar=dict(color=ASPIRE["600"], thickness=0.5),
        ),
    ))
    fig.update_layout(
        height=height, margin=dict(l=130, r=20, t=10, b=10),
    )
    return dcc.Graph(figure=fig, config=GRAPH_CONFIG,
                      style={"height": f"{height}px"})


# ─────────────────────────────────────────────────────────────────────────
# 5. Session-load bubble chart (sRPE × duration)
# ─────────────────────────────────────────────────────────────────────────


def session_load_bubble(
    sessions: list[dict],
    *,
    title: str = "Session Load Map",
    height: int = 360,
):
    """sRPE × duration 2-D session-load map.

    Each session dict: `{date, rpe, duration_min, label?}`. Bubble size
    = total session-RPE load (rpe × duration). Colour by rpe band:
    green ≤4, gold 5-7, red ≥8.

    >>> session_load_bubble([
    ...     {"date": "2026-04-22", "rpe": 6, "duration_min": 75,
    ...      "label": "Tempo run"},
    ...     ...
    ... ])
    """
    dates    = [s["date"]         for s in sessions]
    rpes     = [s["rpe"]          for s in sessions]
    durs     = [s["duration_min"] for s in sessions]
    labels   = [s.get("label", "") for s in sessions]
    loads    = [r * d for r, d in zip(rpes, durs)]

    def _color(rpe):
        if rpe <= 4: return SUCCESS
        if rpe <= 7: return GOLD
        return DANGER

    colors = [_color(r) for r in rpes]
    # Size scaled — Plotly sizeref formula
    sizeref = 2.0 * max(loads) / (40 ** 2) if loads else 1

    fig = go.Figure(go.Scatter(
        x=dates, y=rpes,
        mode="markers",
        marker=dict(
            size=loads, sizeref=sizeref, sizemode="area",
            color=colors,
            line=dict(color="white", width=2),
            opacity=0.85,
        ),
        text=labels, customdata=durs,
        hovertemplate=(
            "<b>%{x}</b><br>"
            "%{text}<br>"
            "RPE %{y}<br>"
            "%{customdata} min<extra></extra>"
        ),
    ))

    # Reference bands
    fig.add_hrect(y0=0.5, y1=4.5,
                   fillcolor="rgba(22,163,74,0.05)", line_width=0)
    fig.add_hrect(y0=4.5, y1=7.5,
                   fillcolor="rgba(251,184,0,0.05)", line_width=0)
    fig.add_hrect(y0=7.5, y1=10.5,
                   fillcolor="rgba(220,38,38,0.05)", line_width=0)

    fig.update_layout(
        title=title, height=height,
        xaxis=dict(title=None),
        yaxis=dict(title="RPE", range=[0.5, 10.5], dtick=1),
        showlegend=False,
        margin=dict(l=40, r=20, t=40, b=40),
    )
    return dcc.Graph(figure=fig, config=GRAPH_CONFIG,
                      style={"height": f"{height}px"})


__all__ = [
    "force_velocity_scatter",
    "acwr_chart",
    "hr_zone_distribution",
    "bullet_chart",
    "session_load_bubble",
]
