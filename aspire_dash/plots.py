"""Aspire-styled Plotly chart helpers — sport-dashboard collection.

11 helpers covering the patterns that appear repeatedly in athlete and
performance dashboards. All return a `plotly.graph_objects.Figure` with
the `aspire` template applied + tight margins + Aspire palette. Drop
into any `dcc.Graph(figure=...)` slot.

The set:
    boxplot_by_group, violin_by_group, ridge_chart
    sunburst, treemap
    calendar_heatmap
    waterfall, sankey
    radar, slope_chart, dumbbell

Designed for: sport rankings, athlete comparisons, load monitoring,
budget waterfalls, attendance heatmaps, transition flows.

(Module name is `plots` to avoid clashing with the existing `viz`
module which holds SVG rings/gauges/sparklines.)
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from .theme import CHART_COLORS, ASPIRE, SLATE
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
