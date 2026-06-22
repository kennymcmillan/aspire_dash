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


def percentile_age_chart(bands, marks=None, *,
                         reference_lines=None, overlay=None,
                         pct=(10, 25, 50, 75, 90),
                         title=None, x_title="Age (years)", y_title="Mark",
                         band_color="#7f9bb8", mark_color=None,
                         height=460):
    """Athlete mark-vs-age plotted against shaded age-percentile bands.

    The canonical "how good is this for the athlete's age?" chart: a shaded
    normal-for-age corridor (outer + inner percentile bands and a median line)
    with the athlete's marks plotted over it, plus optional reference lines
    (records / qualifying standards) and an overlay curve (e.g. an elite
    athlete's progression at the same age).

    Parameters
    ----------
    bands : DataFrame | list[dict]
        One row per age step with an ``age`` column and percentile columns named
        ``p{n}`` for each ``n`` in ``pct`` (e.g. ``p10, p25, p50, p75, p90``).
    marks : DataFrame | list[dict] | None
        Athlete marks: ``age``, ``mark``, optional ``pb`` (bool) and ``label``.
        PB marks render as a star.
    reference_lines : list[dict] | None
        Horizontal references: ``{"y": float, "label": str, "color": str?}``.
    overlay : dict | None
        Comparison curve: ``{"name": str, "points": [{"age","mark"}...],
        "color": str?}`` — e.g. a record-holder's progression by age.
    pct : tuple[int, ...]
        Percentiles present in ``bands`` (ascending). Outer band = first/last,
        inner band = second/second-last, median = the middle value.
    """
    fig = go.Figure()
    rows = sorted(_records(bands), key=lambda r: r.get("age", 0))
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

    if overlay and overlay.get("points"):
        opts = sorted(_records(overlay["points"]), key=lambda r: r.get("age", 0))
        fig.add_trace(go.Scatter(
            x=[p.get("age") for p in opts], y=[p.get("mark") for p in opts],
            mode="lines+markers", name=overlay.get("name", "Overlay"),
            line=dict(color=overlay.get("color", "#8A1538"), width=2),
            marker=dict(size=5, color=overlay.get("color", "#8A1538")),
            hovertemplate=f"{overlay.get('name', 'Overlay')} · age %{{x}}: %{{y}}<extra></extra>"))

    mrows = _records(marks)
    non_pb = [m for m in mrows if not m.get("pb")]
    pb = [m for m in mrows if m.get("pb")]
    if non_pb:
        fig.add_trace(go.Scatter(
            x=[m["age"] for m in non_pb], y=[m["mark"] for m in non_pb],
            mode="markers", name="Mark",
            marker=dict(color=mark_color, size=10, line=dict(color="#8a6d00", width=1)),
            hovertemplate="%{y} at age %{x}<extra></extra>"))
    if pb:
        fig.add_trace(go.Scatter(
            x=[m["age"] for m in pb], y=[m["mark"] for m in pb],
            mode="markers+text", name="Personal best",
            marker=dict(color=mark_color, size=20, symbol="star",
                        line=dict(color="#8a6d00", width=1.5)),
            text=["PB"] * len(pb), textposition="top center",
            textfont=dict(color="#8a6d00", size=11),
            hovertemplate="PB %{y} at age %{x}<extra></extra>"))

    for ref in (reference_lines or []):
        col = ref.get("color", "#b3261e")
        fig.add_hline(y=ref["y"], line=dict(color=col, width=1.6, dash="dot"),
                      annotation_text=ref.get("label", ""),
                      annotation_position="top left",
                      annotation_font=dict(color=col, size=11))

    fig.update_layout(
        title=title, xaxis_title=x_title, yaxis_title=y_title, height=height,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=60, r=30, t=70 if title else 40, b=50))
    apply_template(fig)
    return fig
