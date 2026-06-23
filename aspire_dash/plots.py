"""Aspire-styled Plotly chart helpers — sport-dashboard collection.

12 helpers covering the patterns that appear repeatedly in athlete and
performance dashboards. All return a `plotly.graph_objects.Figure` with
the `aspire` template applied + tight margins + Aspire palette. Drop
into any `dcc.Graph(figure=...)` slot.

The set:
    boxplot_by_group, violin_by_group, ridge_chart
    sunburst, treemap
    calendar_heatmap
    waterfall, sankey
    radar, slope_chart, dumbbell
    percentile_age_chart

Designed for: sport rankings, athlete comparisons, load monitoring,
budget waterfalls, attendance heatmaps, transition flows.

(Module name is `plots` to avoid clashing with the existing `viz`
module which holds SVG rings/gauges/sparklines.)
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from .theme import CHART_COLORS, ASPIRE, SLATE, GOLD, ASPIRE_BLUE
from .charts import apply_template


# ── Distribution charts ────────────────────────────────────────────────────

def boxplot_by_group(df, value: str, group: str, *,
                      title: str | None = None,
                      orientation: str = "v",
                      height: int = 320):
    """Boxplot comparing a numeric distribution across categorical groups."""
    fig = go.Figure()
    groups = df[group].dropna().unique()
    for i, g in enumerate(groups):
        sub = df[df[group] == g][value].dropna()
        color = CHART_COLORS[i % len(CHART_COLORS)]
        if orientation == "h":
            fig.add_trace(go.Box(x=sub, name=str(g), marker_color=color,
                                  line=dict(width=1.5), boxmean="sd"))
        else:
            fig.add_trace(go.Box(y=sub, name=str(g), marker_color=color,
                                  line=dict(width=1.5), boxmean="sd"))
    fig.update_layout(title=title, height=height, showlegend=False)
    return apply_template(fig)


def violin_by_group(df, value: str, group: str, *,
                     title: str | None = None,
                     height: int = 340, show_box: bool = True):
    """Violin plot — distribution shape per group."""
    fig = go.Figure()
    groups = df[group].dropna().unique()
    for i, g in enumerate(groups):
        sub = df[df[group] == g][value].dropna()
        color = CHART_COLORS[i % len(CHART_COLORS)]
        fig.add_trace(go.Violin(y=sub, name=str(g),
                                 box_visible=show_box, meanline_visible=True,
                                 fillcolor=color, line_color=color,
                                 opacity=0.65, points=False))
    fig.update_layout(title=title, height=height, showlegend=False,
                       violingap=0.2)
    return apply_template(fig)


def ridge_chart(df, value: str, group: str, *,
                 title: str | None = None, height: int = 320):
    """Ridgeline — overlapping KDE distributions stacked vertically."""
    fig = go.Figure()
    groups = list(df[group].dropna().unique())
    for i, g in enumerate(groups):
        sub = df[df[group] == g][value].dropna()
        color = CHART_COLORS[i % len(CHART_COLORS)]
        fig.add_trace(go.Violin(
            x=sub, name=str(g), side="positive", orientation="h",
            fillcolor=color, line_color=color, opacity=0.65, points=False,
        ))
    fig.update_layout(title=title,
                       height=max(height, 50 + 40 * len(groups)),
                       showlegend=False,
                       violingap=0, violingroupgap=0.2)
    return apply_template(fig)


# ── Hierarchy / proportion ─────────────────────────────────────────────────

def sunburst(df, path: list[str], value: str, *,
              title: str | None = None, height: int = 420):
    """Sunburst — hierarchical proportion."""
    fig = px.sunburst(df, path=path, values=value,
                       color_discrete_sequence=CHART_COLORS)
    fig.update_traces(marker=dict(line=dict(color="white", width=2)))
    fig.update_layout(title=title, height=height,
                       margin=dict(t=24 if title else 8, b=8, l=8, r=8))
    return apply_template(fig)


def treemap(df, path: list[str], value: str, *,
             title: str | None = None, height: int = 420):
    """Treemap — proportional rectangles."""
    fig = px.treemap(df, path=path, values=value,
                      color_discrete_sequence=CHART_COLORS)
    fig.update_traces(marker=dict(line=dict(color="white", width=2)),
                       textfont=dict(size=12, color="white",
                                     family="Poppins"))
    fig.update_layout(title=title, height=height,
                       margin=dict(t=24 if title else 8, b=8, l=8, r=8))
    return apply_template(fig)


# ── Time-series specials ───────────────────────────────────────────────────

def calendar_heatmap(df, date_col: str, value_col: str, *,
                      year: int | None = None,
                      title: str | None = None, height: int = 200):
    """GitHub-style calendar heatmap. Sun first (Qatar week)."""
    d = df.copy()
    d[date_col] = pd.to_datetime(d[date_col])
    if year:
        d = d[d[date_col].dt.year == year]
    d["dow"] = d[date_col].dt.dayofweek
    d["week"] = d[date_col].dt.isocalendar().week
    pivot = d.pivot_table(index="dow", columns="week",
                           values=value_col, aggfunc="sum")
    if 6 in pivot.index:
        pivot = pivot.reindex([6, 0, 1, 2, 3, 4, 5])
    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=[f"W{c}" for c in pivot.columns],
        y=["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
        colorscale=[[0.0, "#f1f5f9"],
                     [0.5, ASPIRE["300"]],
                     [1.0, ASPIRE["700"]]],
        xgap=2, ygap=2, colorbar=dict(thickness=10),
    ))
    fig.update_layout(title=title, height=height,
                       margin=dict(t=24 if title else 8, b=24, l=40, r=8))
    return apply_template(fig)


# ── Financial / accumulation ───────────────────────────────────────────────

def waterfall(labels: list[str], values: list[float], *,
               title: str | None = None,
               total_label: str = "Total", height: int = 320):
    """Sequential additions/subtractions."""
    measure = ["relative"] * len(values) + ["total"]
    fig = go.Figure(go.Waterfall(
        orientation="v",
        measure=measure,
        x=list(labels) + [total_label],
        y=list(values) + [sum(values)],
        connector=dict(line=dict(color=SLATE["300"], width=1)),
        increasing=dict(marker=dict(color=ASPIRE["600"])),
        decreasing=dict(marker=dict(color="#dc2626")),
        totals=dict(marker=dict(color=SLATE["700"])),
    ))
    fig.update_layout(title=title, height=height, showlegend=False)
    return apply_template(fig)


# ── Flow ───────────────────────────────────────────────────────────────────

def sankey(source: list[int], target: list[int], value: list[float],
            labels: list[str], *,
            title: str | None = None, height: int = 380):
    """Sankey — flow between nodes."""
    n = len(labels)
    node_colors = [CHART_COLORS[i % len(CHART_COLORS)] for i in range(n)]
    # Convert each hex node colour to rgba for the link fill (Plotly
    # rejects 8-char hex; rgba() is the canonical alpha form).
    def _to_rgba(hex_, alpha=0.33):
        h = hex_.lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return f"rgba({r},{g},{b},{alpha})"
    link_colors = [_to_rgba(node_colors[s]) for s in source]
    fig = go.Figure(go.Sankey(
        node=dict(label=labels, pad=18, thickness=18,
                   line=dict(color="white", width=0.5),
                   color=node_colors),
        link=dict(source=source, target=target, value=value,
                   color=link_colors),
    ))
    fig.update_layout(title=title, height=height,
                       font=dict(family="Poppins", size=12,
                                 color=SLATE["700"]),
                       margin=dict(t=24 if title else 8, b=8, l=8, r=8))
    return apply_template(fig)


# ── Comparison ─────────────────────────────────────────────────────────────

def radar(categories: list[str], series: list[dict], *,
           title: str | None = None,
           height: int = 360, range_max: float | None = None):
    """Radar / polar — multi-dimensional profile.

    `series` items: `{'name': str, 'values': [..], 'color': optional}`.
    """
    def _to_rgba(hex_, alpha=0.2):
        h = hex_.lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return f"rgba({r},{g},{b},{alpha})"
    fig = go.Figure()
    for i, s in enumerate(series):
        color = s.get("color", CHART_COLORS[i % len(CHART_COLORS)])
        fig.add_trace(go.Scatterpolar(
            theta=categories + categories[:1],
            r=list(s["values"]) + [s["values"][0]],
            name=s["name"], line=dict(color=color, width=2),
            fillcolor=_to_rgba(color), fill="toself",
        ))
    max_v = range_max or max(max(s["values"]) for s in series) * 1.05
    fig.update_layout(
        title=title, height=height,
        polar=dict(radialaxis=dict(visible=True, range=[0, max_v],
                                    showline=False, gridcolor=SLATE["100"]),
                    angularaxis=dict(tickfont=dict(size=11),
                                     gridcolor=SLATE["100"])),
        legend=dict(orientation="h", y=-0.1, x=0,
                    font=dict(size=11, color=SLATE["600"])),
        margin=dict(t=24 if title else 8, b=40, l=24, r=24),
    )
    return fig


def slope_chart(df, x: str, y: str, group: str, *,
                 title: str | None = None, height: int = 360):
    """Slope chart — value at exactly two x points, per group."""
    fig = go.Figure()
    x_vals = list(df[x].drop_duplicates())
    if len(x_vals) != 2:
        raise ValueError(
            f"slope_chart needs exactly 2 distinct x values, got {x_vals}"
        )
    for i, g in enumerate(df[group].dropna().unique()):
        sub = df[df[group] == g]
        if len(sub) < 2: continue
        v0 = sub[sub[x] == x_vals[0]][y].iloc[0]
        v1 = sub[sub[x] == x_vals[1]][y].iloc[0]
        delta = v1 - v0
        color = "#16a34a" if delta > 0 else "#dc2626" if delta < 0 \
                else CHART_COLORS[i % len(CHART_COLORS)]
        fig.add_trace(go.Scatter(
            x=x_vals, y=[v0, v1], mode="lines+markers+text",
            text=[f"{g} {v0:g}", f"{v1:g} {g}"],
            textposition=["middle left", "middle right"],
            line=dict(color=color, width=2),
            marker=dict(size=8, color=color),
            name=str(g), hoverinfo="text+x+y",
        ))
    fig.update_layout(title=title, height=height, showlegend=False,
                       xaxis=dict(showgrid=False),
                       yaxis=dict(showgrid=True, gridcolor=SLATE["50"]),
                       margin=dict(t=24 if title else 8, b=32,
                                   l=80, r=80))
    return apply_template(fig)


def dumbbell(df, label: str, start: str, end: str, *,
              title: str | None = None, height: int = 360,
              start_label: str = "Before", end_label: str = "After"):
    """Dumbbell — two values per row, connected by a bar."""
    fig = go.Figure()
    for _, row in df.iterrows():
        delta = row[end] - row[start]
        color = "#16a34a" if delta > 0 else "#dc2626" if delta < 0 \
                else SLATE["400"]
        fig.add_trace(go.Scatter(
            x=[row[start], row[end]], y=[row[label], row[label]],
            mode="lines", line=dict(color=color, width=3),
            showlegend=False, hoverinfo="skip",
        ))
    fig.add_trace(go.Scatter(
        x=df[start], y=df[label], mode="markers", name=start_label,
        marker=dict(size=10, color=SLATE["400"],
                     line=dict(color="white", width=1)),
    ))
    fig.add_trace(go.Scatter(
        x=df[end], y=df[label], mode="markers", name=end_label,
        marker=dict(size=10, color=ASPIRE["600"],
                     line=dict(color="white", width=1)),
    ))
    fig.update_layout(title=title, height=height,
                       xaxis=dict(showgrid=True, gridcolor=SLATE["50"]),
                       yaxis=dict(showgrid=False, autorange="reversed"),
                       legend=dict(orientation="h", y=-0.12, x=0,
                                   font=dict(size=11)),
                       margin=dict(t=24 if title else 8, b=40,
                                   l=120, r=24))
    return apply_template(fig)


# ── VALD-style trend with adaptive reference band ──────────────────────────

def adaptive_trend(df, x: str, y: str, *,
                    window: int = 8, k: float = 1.0,
                    title: str | None = None, height: int = 280,
                    color: str | None = None,
                    band_label: str = "Adaptive range"):
    """Time-series line with rolling adaptive reference band (mean ± k·SD).

    Used by VALD jump-height trend, Whoop RHR baseline, endurance load.
    Pulls the math from :func:`aspire_dash.metrics.adaptive_range`.

        >>> adaptive_trend(df, x='date', y='jump_cm', window=8, k=1.0)
    """
    from .metrics import adaptive_range
    color = color or "#004185"
    band = adaptive_range(df[y], window=window, k=k)
    band = band.reset_index(drop=True)
    df2 = df.reset_index(drop=True)

    fig = go.Figure()
    # Band fill (upper - lower) — draw upper first, then lower w/ fill
    fig.add_trace(go.Scatter(
        x=df2[x], y=band["upper"], mode="lines",
        line=dict(color="rgba(0,0,0,0)"), showlegend=False,
        hoverinfo="skip",
    ))
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    fig.add_trace(go.Scatter(
        x=df2[x], y=band["lower"], mode="lines",
        line=dict(color="rgba(0,0,0,0)"),
        fill="tonexty", fillcolor=f"rgba({r},{g},{b},0.12)",
        name=band_label, hoverinfo="skip",
    ))
    # Rolling mean (dashed) + actual values
    fig.add_trace(go.Scatter(
        x=df2[x], y=band["mean"], mode="lines",
        line=dict(color=color, width=1.5, dash="dot"),
        name="Baseline", hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=df2[x], y=df2[y], mode="lines+markers",
        line=dict(color=color, width=2.5),
        marker=dict(size=6, color=color,
                     line=dict(color="white", width=1.5)),
        name=y,
    ))
    fig.update_layout(title=title, height=height,
                       legend=dict(orientation="h", y=-0.18, x=0,
                                   font=dict(size=11)))
    return apply_template(fig)


def sparkline_figure(values, dates=None, *, color=None, height=44, fill=True):
    """Axis-less inline sparkline figure (v0.45 — promoted from
    DASH_Anthro + endurance-dashboard, which each rebuilt it).

    The plotly complement to viz.sparkline (SVG): supports a date x-axis,
    tozeroy alpha fill, and auto y-padding around the data. Hover/toolbar
    off — pair with dcc.Graph(config={"displayModeBar": False}).
    """
    import plotly.graph_objects as go

    color = color or ASPIRE["600"]
    fig = go.Figure()
    xs = dates if dates is not None else list(range(len(values)))
    if fill:
        fig.add_trace(go.Scatter(
            x=xs, y=values, mode="lines",
            line=dict(color=color, width=1.8),
            fill="tozeroy", fillcolor=_rgba(color, 0.18),
            hoverinfo="skip", showlegend=False,
        ))
    else:
        fig.add_trace(go.Scatter(
            x=xs, y=values, mode="lines+markers",
            line=dict(color=color, width=1.8),
            marker=dict(size=4, color=color),
            hoverinfo="skip", showlegend=False,
        ))
    yvals = [v for v in values if v is not None]
    if yvals:
        ymin, ymax = min(yvals), max(yvals)
        pad = max(0.5, (ymax - ymin) * 0.4)
        fig.update_yaxes(range=[ymin - pad, ymax + pad])
    fig.update_layout(
        template=None,  # deliberately bare — no grid/legend at this size
        margin=dict(l=0, r=0, t=2, b=2), height=height,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        showlegend=False,
    )
    return fig


def _rgba(hexcol: str, a: float) -> str:
    h = str(hexcol).lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{a})"


# ── Development / benchmarking ──────────────────────────────────────────────

def _records(x):
    """Accept a DataFrame or a list of dicts; return a list of dicts."""
    if x is None:
        return []
    if hasattr(x, "to_dict"):
        return x.to_dict("records")
    return list(x)


def format_time(seconds):
    """Seconds -> athletics time string: 110.0 -> '1:50.00', 10.5 -> '10.50'."""
    if seconds is None:
        return ""
    s = float(seconds)
    sign = "-" if s < 0 else ""
    s = abs(s)
    if s >= 60:
        m = int(s // 60)
        return f"{sign}{m}:{s - m * 60:05.2f}"
    return f"{sign}{s:.2f}"


def _nice_ticks(lo, hi, target=7):
    """Round tick positions across [lo, hi] (so a time axis lands on 1:40, 1:50,
    2:00, not 1:46.52)."""
    import math
    span = hi - lo
    if span <= 0:
        return [lo]
    mag = 10 ** math.floor(math.log10(span / target))
    step = mag
    for m in (1, 2, 2.5, 5, 10):
        step = m * mag
        if span / step <= target * 1.4:
            break
    start = math.ceil(lo / step) * step
    ticks, v = [], start
    while v <= hi + step * 1e-6:
        ticks.append(round(v, 6))
        v += step
    return ticks or [lo, hi]


def _value_formatter(value_format):
    """None | 'time' | callable(value)->str  ->  formatter function or None."""
    if value_format is None:
        return None
    if callable(value_format):
        return value_format
    if value_format == "time":
        return format_time
    return None


def _norm_mark_series(marks, age_col, value_col, pb_col, default_mark_color,
                      pct_col="percentile"):
    """Normalise `marks` into series: [{name, line_color, mark_color, points}].
    Accepts a flat list/df of points (one athlete) OR a list of
    {name, data/points, color, *_col} series (compare multiple athletes).
    Each point also carries an optional `percentile` (read from `pct_col`)."""
    if marks is None:
        return []
    rows = _records(marks)
    if not rows:
        return []
    gold = default_mark_color or GOLD
    is_series = isinstance(rows[0], dict) and (("data" in rows[0]) or ("points" in rows[0]))
    if not is_series:
        pts = [{"age": r.get(age_col), "mark": r.get(value_col),
                "pb": r.get(pb_col), "label": r.get("label"),
                "percentile": r.get(pct_col)} for r in rows]
        return [{"name": "Athlete", "line_color": ASPIRE["600"],
                 "mark_color": gold, "points": pts}]
    out = []
    for k, s in enumerate(rows):
        col = s.get("color") or CHART_COLORS[k % len(CHART_COLORS)]
        a_c, v_c, p_c = s.get("age_col", age_col), s.get("value_col", value_col), s.get("pb_col", pb_col)
        pc = s.get("pct_col", pct_col)
        pts = [{"age": p.get(a_c), "mark": p.get(v_c), "pb": p.get(p_c),
                "label": p.get("label"), "percentile": p.get(pc)}
               for p in _records(s.get("data") or s.get("points") or [])]
        out.append({"name": s.get("name", f"Series {k + 1}"),
                    "line_color": col, "mark_color": col, "points": pts})
    return out


def _pct_suffix(p):
    """Hover suffix ' · 65th pct' when a point carries a percentile, else ''."""
    pct = p.get("percentile")
    return (" · %gth pct" % pct) if pct is not None else ""


def _star_size(p, base=19.0, lo=12.0, hi=24.0):
    """PB star size scaled by percentile (best-for-age = biggest star); the
    fixed `base` when the point has no percentile."""
    pct = p.get("percentile")
    if pct is None:
        return base
    frac = max(0.0, min(100.0, float(pct))) / 100.0
    return lo + frac * (hi - lo)


def percentile_age_chart(bands=None, marks=None, *,
                         reference_lines=None, overlay=None, overlays=None,
                         pct=(10, 25, 50, 75, 90), elite_line=100,
                         age_col="age", value_col="mark", pb_col="pb",
                         pct_col="percentile",
                         lower_is_better=False, value_format=None,
                         title=None, x_title="Age (years)", y_title="Mark",
                         band_color="#7f9bb8", mark_color=None,
                         x_range=None, height=460):
    """Athlete mark-vs-age plotted against shaded age-percentile bands.

    The canonical "how good is this for the athlete's age?" chart: a shaded
    normal-for-age corridor (outer + inner percentile bands and a median line)
    with the athlete's marks plotted over it, plus any number of reference lines
    (records / qualifying standards) and overlay curves (e.g. record-holder
    progressions). Built to be sport-agnostic and easy to connect data to:
    every input is optional and accepts a DataFrame or a list of dicts, and the
    mark columns are mappable so you do not have to rename your data.

    Parameters
    ----------
    bands : DataFrame | list[dict] | None
        One row per age step with an ``age`` column and percentile columns named
        ``p{n}`` for each ``n`` in ``pct`` (e.g. ``p10, p25, p50, p75, p90``).
        Build it from raw population marks with :func:`age_percentile_bands`.
        Omit it to plot marks + reference lines with no corridor.
    marks : DataFrame | list[dict] | None
        EITHER one athlete's points (``age``/``mark``/``pb``/``label``, column
        names overridable via ``age_col`` / ``value_col`` / ``pb_col``), OR a
        list of series to compare multiple athletes, each
        ``{"name": str, "data": [points...], "color": str?, "pb_col": str?}``.
        PB points render as a star.
    reference_lines : list[dict] | None
        Horizontal benchmark lines (qualifying standards, world / continental /
        championship records): ``{"y": float, "label": str, "color": str?}``.
        Any number; colours auto-cycle and labels alternate sides so close lines
        stay legible. Feed e.g. a row from the pinned U20 standards.
    overlay / overlays : dict | list[dict] | None
        One or many comparison curves:
        ``{"name": str, "points": [{"age","mark"}...], "color": str?}``.
    age_col, value_col, pb_col, pct_col : str
        Column/key names in ``marks`` (defaults ``age`` / ``mark`` / ``pb`` /
        ``percentile``). When a point carries a ``percentile`` (0..100, e.g. from
        ``aspire_data.benchmarks.best_pb_by_ageband(with_percentile=True)``), the
        PB star is sized by it (best-for-age = biggest star) and the hover shows
        it (``PB: 6.50 at age 17 · 65th pct``). Omit it for today's uniform star.
    lower_is_better : bool
        True for time events (faster = lower = better): the y-axis is reversed so
        better performances sit at the top. False (default) for jumps / throws /
        scores where higher is better. Build `bands` with the same flag.
    value_format : None | "time" | callable
        Formats the y-axis tick labels and hover values. "time" renders seconds
        as an athletics clock (110.0 -> "1:50.00", 10.5 -> "10.50"); pass a
        callable ``value -> str`` for other units. None leaves raw numbers.
    pct : tuple[int, ...]
        Percentiles used for the shaded corridor (ascending, symmetric around the
        median). Outer band = first/last, inner band = second/second-last,
        median = the middle value.
    elite_line : int | None
        Percentile to draw as a dashed "elite ceiling" line on top of the
        corridor (default ``100`` — the world-class best). Drawn only when the
        ``bands`` carry a ``p{elite_line}`` column, so it is safe to leave on for
        population-derived bands that stop at the 90th. Set ``None`` to hide it.
    """
    fig = go.Figure()
    rows = (sorted(_records(bands), key=lambda r: r.get("age", 0))
            if bands is not None else [])
    pcts = sorted(pct)
    mark_color = mark_color or GOLD

    if rows and len(pcts) >= 2:
        xs = [r.get("age") for r in rows]

        def yv(p):
            return [r.get(f"p{p}") for r in rows]

        lo_o, hi_o = pcts[0], pcts[-1]
        med = pcts[len(pcts) // 2]
        pairs = [(lo_o, hi_o, 0.12)]
        if len(pcts) >= 4:
            pairs.append((pcts[1], pcts[-2], 0.24))
        for lo, hi, alpha in pairs:
            fig.add_trace(go.Scatter(x=xs, y=yv(lo), mode="lines",
                                     line=dict(width=0), hoverinfo="skip",
                                     showlegend=False))
            fig.add_trace(go.Scatter(
                x=xs, y=yv(hi), mode="lines", name=f"{lo}th–{hi}th percentile",
                line=dict(width=0), fill="tonexty",
                fillcolor=_rgba(band_color, alpha),
                hovertemplate=f"{hi}th pct · age %{{x}}: %{{y}}<extra></extra>"))
        fig.add_trace(go.Scatter(
            x=xs, y=yv(med), mode="lines", name=f"{med}th percentile (median)",
            line=dict(color="#5a7799", width=2.2, dash="dash"),
            hovertemplate=f"{med}th pct · age %{{x}}: %{{y}}<extra></extra>"))

        # Elite ceiling: a dashed line at the top percentile (e.g. 100th) when the
        # bands carry it. Drawn in gold so it reads as the "world-class" target the
        # athlete's gold marks are chasing; silently skipped if absent.
        if elite_line is not None and f"p{elite_line}" in rows[0]:
            ev = yv(elite_line)
            if any(v is not None for v in ev):
                fig.add_trace(go.Scatter(
                    x=xs, y=ev, mode="lines",
                    name=f"{elite_line}th percentile (elite)",
                    line=dict(color=GOLD, width=2, dash="dash"),
                    hovertemplate=f"{elite_line}th pct · age %{{x}}: %{{y}}"
                                  "<extra></extra>"))

    ovs = list(overlays or [])
    if overlay:
        ovs.append(overlay)
    ov_cycle = ["#8A1538", ASPIRE_BLUE, SLATE["500"]]
    for j, ov in enumerate(ovs):
        if not ov.get("points"):
            continue
        opts = sorted(_records(ov["points"]), key=lambda r: r.get("age", 0))
        ocol = ov.get("color") or ov_cycle[j % len(ov_cycle)]
        fig.add_trace(go.Scatter(
            x=[p.get("age") for p in opts], y=[p.get("mark") for p in opts],
            mode="lines+markers", name=ov.get("name", "Overlay"),
            line=dict(color=ocol, width=2), marker=dict(size=5, color=ocol),
            hovertemplate=f"{ov.get('name', 'Overlay')} · age %{{x}}: %{{y}}<extra></extra>"))

    # Athlete marks: one or many series, each a connecting trajectory line (so the
    # eye reads improvement over age) with markers + PB stars on top.
    series = _norm_mark_series(marks, age_col, value_col, pb_col, mark_color, pct_col)
    multi = len(series) > 1
    for s in series:
        pts = sorted([p for p in s["points"]
                      if p.get("age") is not None and p.get("mark") is not None],
                     key=lambda p: p["age"])
        if not pts:
            continue
        if len(pts) >= 2:
            fig.add_trace(go.Scatter(
                x=[p["age"] for p in pts], y=[p["mark"] for p in pts],
                mode="lines", legendgroup=s["name"], showlegend=False,
                line=dict(color=s["line_color"], width=2.6, shape="spline",
                          smoothing=0.5), hoverinfo="skip"))
        non_pb = [p for p in pts if not p.get("pb")]
        pb = [p for p in pts if p.get("pb")]
        pre = (s["name"] + " ") if multi else ""
        if non_pb:
            fig.add_trace(go.Scatter(
                x=[p["age"] for p in non_pb], y=[p["mark"] for p in non_pb],
                mode="markers", name=s["name"] if multi else "Mark",
                legendgroup=s["name"], text=[_pct_suffix(p) for p in non_pb],
                marker=dict(color=s["mark_color"], size=11,
                            line=dict(color=ASPIRE["700"], width=1.5)),
                hovertemplate=pre + "%{y} at age %{x}%{text}<extra></extra>"))
        if pb:
            # Star size scales with each band-PB's percentile (best-for-age =
            # biggest star); a fixed size when no percentile is supplied so
            # existing callers are unchanged.
            has_pct = any(p.get("percentile") is not None for p in pb)
            star_size = [_star_size(p) for p in pb] if has_pct else 19
            fig.add_trace(go.Scatter(
                x=[p["age"] for p in pb], y=[p["mark"] for p in pb],
                mode="markers", name=(s["name"] + " PB") if multi else "Personal best",
                legendgroup=s["name"], text=[_pct_suffix(p) for p in pb],
                marker=dict(color=s["mark_color"], size=star_size, symbol="star",
                            line=dict(color=ASPIRE["700"], width=1.5)),
                hovertemplate=pre + "PB: %{y} at age %{x}%{text}<extra></extra>"))

    # Benchmark lines (qualifying standards, world / continental records, ...).
    # Distinct brand colours + a coloured label chip + alternating label side so
    # lines that sit close together stay legible.
    ref_cycle = [GOLD, ASPIRE_BLUE, "#8A1538", ASPIRE["600"], SLATE["500"]]
    refs = [r for r in (reference_lines or []) if r.get("y") is not None]
    for i, ref in enumerate(refs):
        col = ref.get("color") or ref_cycle[i % len(ref_cycle)]
        side = "right" if i % 2 == 0 else "left"
        fig.add_hline(
            y=ref["y"], line=dict(color=col, width=2),
            annotation_text=" " + str(ref.get("label", "")) + " ",
            annotation_position=f"top {side}",
            annotation_font=dict(color="#ffffff", size=11,
                                 family="Poppins, sans-serif"),
            annotation_bgcolor=col, annotation_borderpad=3)

    fig.update_layout(
        title=dict(text=title or "",
                   font=dict(family="Poppins, sans-serif", size=17,
                             color=ASPIRE["700"])),
        xaxis_title=x_title, yaxis_title=y_title, height=height,
        font=dict(family="Poppins, sans-serif", color=SLATE["700"]),
        hoverlabel=dict(font=dict(family="Poppins, sans-serif")),
        # Legend BELOW the plot — with up to 6 entries a top legend collides with
        # the title. Centred horizontal row under the x-axis label.
        legend=dict(orientation="h", yanchor="top", y=-0.16, xanchor="center",
                    x=0.5, font=dict(size=11)),
        margin=dict(l=64, r=30, t=52 if title else 24, b=92))
    if x_range:
        fig.update_xaxes(range=list(x_range))
    apply_template(fig)

    # Value formatting (e.g. running times as 1:50.00 on the axis + hover) and
    # the lower-is-better axis flip so elite always sits at the top.
    fmt = _value_formatter(value_format)
    ys = []
    if fmt:
        for tr in fig.data:
            yvals = list(getattr(tr, "y", []) or [])
            ys += [v for v in yvals if v is not None]
            htmpl = getattr(tr, "hovertemplate", None) or ""
            if yvals and "%{y}" in htmpl:
                tr.customdata = [[fmt(v)] if v is not None else [""] for v in yvals]
                tr.hovertemplate = htmpl.replace("%{y}", "%{customdata[0]}")
        ys += [r["y"] for r in refs]
    if fmt and ys:
        lo, hi = min(ys), max(ys)
        pad = (hi - lo) * 0.06 or 1.0
        r0, r1 = lo - pad, hi + pad
        ticks = _nice_ticks(r0, r1)
        fig.update_yaxes(tickmode="array", tickvals=ticks,
                         ticktext=[fmt(t) for t in ticks],
                         range=[r1, r0] if lower_is_better else [r0, r1])
    elif lower_is_better:
        fig.update_yaxes(autorange="reversed")
    return fig


def age_percentile_bands(population, *, age_col="age", value_col="value",
                         pct=(10, 25, 50, 75, 90), age_step=1.0, min_n=3,
                         lower_is_better=False):
    """Build the ``bands`` DataFrame (``age`` + ``p{n}`` columns) that
    :func:`percentile_age_chart` needs, from RAW population marks of any sport or
    event. Ages are binned to ``age_step`` and percentiles taken per bin; bins
    with fewer than ``min_n`` samples are dropped.

    The ``p{n}`` columns are PERFORMANCE percentiles: ``p90`` is the mark better
    than 90% of the population. For a time event (``lower_is_better=True``) that
    is the faster, lower value, so set the same ``lower_is_better`` on the chart
    and elite always sits at the top of the corridor. Returns an empty DataFrame
    on no usable input.
    """
    import numpy as np
    rows = _records(population)
    pts = [(r.get(age_col), r.get(value_col)) for r in rows
           if r.get(age_col) is not None and r.get(value_col) is not None]
    if not pts:
        return pd.DataFrame()
    df = pd.DataFrame(pts, columns=["age", "value"])
    df["bin"] = (df["age"] / age_step).round() * age_step
    out = []
    for b, g in df.groupby("bin"):
        if len(g) < min_n:
            continue
        row = {"age": float(b)}
        for p in pct:
            q = (100 - p) if lower_is_better else p
            row[f"p{p}"] = float(np.percentile(g["value"], q))
        out.append(row)
    return pd.DataFrame(out).sort_values("age").reset_index(drop=True) if out \
        else pd.DataFrame()
