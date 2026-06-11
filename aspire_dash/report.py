"""Report shell — PBI-style page chrome for report-port apps (v0.53.0).

Promoted from development_dashboard (the Power BI "Development Testing
Dashboard" port): a navy title band with the Aspire logo, an optional left
rail (athlete photo + pickers), PBI-style value cards, responsive card/chart
grids, and a rich-hover trend chart whose tooltip carries athlete context
(the PBI custom tooltips coaches valued).

All styling lives in 00_aspire_base.css (`.report-*` classes) — helpers emit
classNames only.

Usage::

    from aspire_dash.report import report_page, athlete_rail, report_card, report_grid

    layout = report_page(
        "Individual Growth & Maturation",
        rail=athlete_rail(photo_el, group_dd, athlete_dd),
        content=dcc.Loading(html.Div(id="content")),
    )
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

import dash
from dash import html

__all__ = ["report_band", "athlete_rail", "report_page", "report_card",
           "report_grid", "trend_rich"]


def report_band(title: str, subtitle: str = "", logo_src: str | None = None) -> html.Div:
    """Navy title band: page name left, Aspire logo right."""
    return html.Div([
        html.Div([
            html.H1(title),
            html.Div(subtitle, className="report-band-sub") if subtitle else None,
        ]),
        html.Img(src=logo_src or dash.get_asset_url("aspire-logo.png")),
    ], className="report-band")


def athlete_rail(photo_el, *controls, labels: list[str] | None = None) -> html.Div:
    """Left rail: photo on top, then labelled picker controls (PBI slicer column).

    labels defaults to ["Development Group", "Athlete", ...] positionally — pass
    your own list to override.
    """
    default = ["Development Group", "Athlete", "Filter", "Filter 2"]
    labels = labels or default
    children = [html.Div(photo_el, className="report-rail-photo")]
    for i, ctrl in enumerate(controls):
        children.append(html.Label(labels[i].upper() if i < len(labels) else "",
                                   className="control-label"))
        children.append(ctrl)
        children.append(html.Div(className="report-rail-gap"))
    return html.Div(children, className="report-rail")


def report_page(title: str, content, rail=None, subtitle: str = "") -> html.Div:
    """Full report page: title band, then [rail | content] (rail optional)."""
    body = [rail, html.Div(content, className="report-content")] if rail is not None \
        else [html.Div(content, className="report-content")]
    return html.Div([report_band(title, subtitle),
                     html.Div(body, className="report-body")])


def report_card(label: str, value, sub: str = "", accent: str | None = None) -> html.Div:
    """PBI value card: uppercase label, big value, optional sub line.
    accent (hex) recolours the top stripe + value via inline CSS variables only."""
    style = {"borderTopColor": accent} if accent else None
    vstyle = {"color": accent} if accent else None
    return html.Div([
        html.Div(label, className="report-card-label"),
        html.Div(value, className="report-card-value", style=vstyle),
        html.Div(sub, className="report-card-sub") if sub else None,
    ], className="card report-card", style=style)


def report_grid(items: list, cols: int = 3) -> html.Div:
    """Responsive grid (2/3/4/6 columns; collapses on tablet/mobile)."""
    cols = cols if cols in (2, 3, 4, 6) else 3
    return html.Div(items, className=f"report-grid report-grid-{cols}")


_TREND_LAYOUT = dict(
    margin=dict(l=44, r=16, t=10, b=34), showlegend=False,
    plot_bgcolor="white", paper_bgcolor="white",
    font=dict(family="Poppins, sans-serif", size=11, color="#334155"),
    hoverlabel=dict(bgcolor="white", font_size=12, bordercolor="#e2e8f0",
                    font_family="Poppins, sans-serif"),
)


def trend_rich(dates, values, unit: str = "", *, color: str = "#004185",
               context: dict | None = None, reverse: bool = False,
               band_lines: list[tuple] | None = None, height: int = 250) -> go.Figure:
    """Spline trend with branded area fill + a RICH hover.

    context: optional {label: per-point-iterable} — each entry becomes a hover
    line (e.g. {"Maturation": mat_series, "Height": heights}). This is the PBI
    custom-tooltip pattern: the value plus the athlete's state at that moment.
    band_lines: [(y, label), ...] dotted reference lines (e.g. PHV thresholds).
    reverse: invert the y-axis for lower-is-better metrics (contact time).
    """
    d = pd.DataFrame({"x": pd.to_datetime(dates),
                      "y": pd.to_numeric(values, errors="coerce")})
    ctx_labels = list((context or {}).keys())
    for i, lab in enumerate(ctx_labels):
        d[f"_c{i}"] = list(context[lab])
    d = d.dropna(subset=["y"]).sort_values("x")

    hover = "<b>%{x|%d %b %Y}</b><br>%{y:.1f} " + unit
    for i, lab in enumerate(ctx_labels):
        hover += f"<br>{lab}: %{{customdata[{i}]}}"
    hover += "<extra></extra>"
    custom = d[[f"_c{i}" for i in range(len(ctx_labels))]].values if ctx_labels else None

    h = color.lstrip("#")
    fill = f"rgba({int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)},0.08)"

    fig = go.Figure(go.Scatter(
        x=d["x"], y=d["y"], mode="lines+markers",
        line=dict(color=color, width=2.5, shape="spline"),
        marker=dict(size=8, color=color, line=dict(width=2, color="white")),
        fill="tozeroy", fillcolor=fill,
        customdata=custom, hovertemplate=hover))

    for y, label in (band_lines or []):
        fig.add_hline(y=y, line_dash="dot", line_color="#cbd5e1",
                      annotation_text=label, annotation_font_size=9,
                      annotation_font_color="#94a3b8")

    fig.update_layout(height=height, yaxis_title=unit, **_TREND_LAYOUT)
    fig.update_xaxes(showgrid=False, linecolor="#e2e8f0")
    fig.update_yaxes(gridcolor="#f1f5f9", zeroline=False,
                     autorange="reversed" if reverse else True)
    return fig
