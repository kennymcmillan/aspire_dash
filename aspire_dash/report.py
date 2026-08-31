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
           "report_grid", "trend_rich", "combo_chart", "multiline_chart",
           "PHV_ZONES", "date_categories", "categorical_date_axis",
           "apply_break", "add_injury_markers",
           "COMBO_BAR_LABEL", "DATE_TICK_FORMAT"]


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
    hoverlabel=dict(bgcolor="white", font_size=12, font_color="#0f172a",
                    bordercolor="#e2e8f0", font_family="Poppins, sans-serif"),
)


# Maturation (PHV) bands for %-predicted-adult-height charts — shade + label.
PHV_ZONES = [
    {"y0": 0, "y1": 85, "label": "Pre-PHV", "color": "#3b82f6"},
    {"y0": 85, "y1": 90, "label": "Approaching", "color": "#f59e0b"},
    {"y0": 90, "y1": 95.1, "label": "Circa-PHV", "color": "#ef4444"},
    {"y0": 95.1, "y1": 100, "label": "Post-PHV", "color": "#16a34a"},
]


def trend_rich(dates, values, unit: str = "", *, color: str = "#004185",
               context: dict | None = None, reverse: bool = False,
               band_lines: list[tuple] | None = None, zones: list[dict] | None = None,
               pb_mask=None, height: int = 250, date_ticks: bool = True) -> go.Figure:
    """Spline trend with branded area fill + a RICH hover.

    context: {label: per-point-iterable} — each becomes a hover line (the PBI
        custom-tooltip pattern: value + athlete state at that moment).
    band_lines: [(y, label), ...] dotted reference lines.
    zones: [{y0,y1,label,color}, ...] shaded horizontal bands (e.g. PHV_ZONES,
        ACWR/ref-range zones) — the "wow" layer for maturation/load charts.
    pb_mask: per-point bool iterable — gold ★ markers on personal-best points.
    reverse: invert the y-axis for lower-is-better metrics (contact time).
    date_ticks: two-line month/year x-tick labels (DATE_TICK_FORMAT) so a long
        date range stays legible. Default True; set False for the bare axis.
    """
    d = pd.DataFrame({"x": pd.to_datetime(dates),
                      "y": pd.to_numeric(values, errors="coerce")})
    ctx_labels = list((context or {}).keys())
    for i, lab in enumerate(ctx_labels):
        d[f"_c{i}"] = list(context[lab])
    if pb_mask is not None:
        d["_pb"] = list(pb_mask)
    d = d.dropna(subset=["y"]).sort_values("x")

    hover = "<b>%{x|%d %b %Y}</b><br>%{y:.1f} " + unit
    for i, lab in enumerate(ctx_labels):
        hover += f"<br>{lab}: %{{customdata[{i}]}}"
    hover += "<extra></extra>"
    custom = d[[f"_c{i}" for i in range(len(ctx_labels))]].values if ctx_labels else None

    h = color.lstrip("#")
    fill = f"rgba({int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)},0.08)"

    fig = go.Figure()
    for z in (zones or []):
        zh = z["color"].lstrip("#")
        fig.add_hrect(y0=z["y0"], y1=z["y1"], line_width=0,
                      fillcolor=f"rgba({int(zh[0:2],16)},{int(zh[2:4],16)},{int(zh[4:6],16)},0.07)",
                      layer="below")
        # zone label OUTSIDE the plot, in the right margin (xref=paper > 1), at the
        # band midpoint, coloured by the zone — so it never overlaps the data.
        if z.get("label"):
            fig.add_annotation(xref="paper", x=1.01, xanchor="left",
                               yref="y", y=(z["y0"] + z["y1"]) / 2, yanchor="middle",
                               text=z["label"], showarrow=False,
                               font=dict(size=9, color=z["color"]))

    fig.add_trace(go.Scatter(
        x=d["x"], y=d["y"], mode="lines+markers",
        line=dict(color=color, width=2.5, shape="spline"),
        marker=dict(size=8, color=color, line=dict(width=2, color="white")),
        fill="tozeroy" if not zones else None, fillcolor=fill if not zones else None,
        customdata=custom, hovertemplate=hover))

    if pb_mask is not None and "_pb" in d:
        pb = d[d["_pb"].astype(bool)]
        if len(pb):
            fig.add_trace(go.Scatter(
                x=pb["x"], y=pb["y"], mode="markers",
                marker=dict(symbol="star", size=14, color="#fbb800",
                            line=dict(width=1, color="#b8860b")),
                hovertemplate="<b>PB</b> %{y:.1f} " + unit + "<extra></extra>"))

    for y, label in (band_lines or []):
        fig.add_hline(y=y, line_dash="dot", line_color="#cbd5e1",
                      annotation_text=label, annotation_font_size=9,
                      annotation_font_color="#94a3b8")

    layout = dict(_TREND_LAYOUT)
    if zones:  # make room in the right margin for the zone labels
        layout["margin"] = {**_TREND_LAYOUT["margin"], "r": 88}
    fig.update_layout(height=height, yaxis_title=unit, **layout)
    fig.update_xaxes(showgrid=False, linecolor="#e2e8f0")
    if date_ticks:
        fig.update_xaxes(tickformat=DATE_TICK_FORMAT)
    fig.update_yaxes(gridcolor="#f1f5f9", zeroline=False,
                     autorange="reversed" if reverse else True)
    return fig


# PBI combo/line charts — promoted from the Development Testing Dashboard port
# (the "Longitudinal Physical Data" page). Defaults match the PBI: teal columns,
# a gold secondary-axis line, navy data labels.
COMBO_COLUMN = "#01B8AA"   # primary grouped columns (teal)
COMBO_LINE = "#F2C80F"     # secondary-axis line (gold)
COMBO_LABEL = "#050574"    # data labels (navy)
COMBO_BAR_LABEL = "#004185"  # pop navy (brand primary) for value-above-bar labels

# Shared time-series x-axis default: two-line month-over-year ticks. A long date
# range on one line crowds; "Mar / 2026" over two lines stays legible.
DATE_TICK_FORMAT = "%b<br>%Y"

_BREAK_MUTED = "#94a3b8"   # slate-400 (axis-break "//" glyph)
_INJURY_RED = "#e74c3c"    # event-marker red (Circa-PHV / "Poor" in the palette)


def _point_labels(values, dp, mode):
    """Data-label text per `mode`: 'last' (only the latest point — declutters a long
    series), 'all', or 'none'. Hover always shows every point regardless."""
    vals = list(values)
    if mode == "none" or not vals:
        return None
    if mode == "all":
        return [f"{v:.{dp}f}" for v in vals]
    return ["" for _ in vals[:-1]] + [f"{vals[-1]:.{dp}f}"]  # 'last'


def combo_chart(bars, line, left_unit: str = "", right_unit: str = "", *,
                height: int = 320, line_color: str = COMBO_LINE,
                label_color: str = COMBO_LABEL, label_mode: str = "last",
                bar_labels: bool | None = None,
                bar_label_color: str = COMBO_BAR_LABEL,
                categorical_x: bool = False) -> go.Figure:
    """Dual-axis combo (PBI lineClusteredColumnComboChart): grouped columns on the
    primary y, a line on the secondary y — e.g. test values as columns with a paired
    index (RSI, power, F/BM) as the line.

    bars: ``[(name, x, y, colour, decimals), ...]`` — one grouped column series each.
    line: ``(name, x, y, decimals)`` — the secondary-axis line (gold by default).
    bar_labels: control the value labels ABOVE each column, independently of the
        line's ``label_mode``. ``None`` (default) keeps the legacy behaviour
        (columns labelled per ``label_mode`` in ``label_color``); ``True`` prints
        EVERY column's value above it in ``bar_label_color`` (pop navy #004185) and
        reserves top headroom so the labels are never clipped; ``False`` drops the
        column labels. The secondary-axis line labels always follow ``label_mode``.
    categorical_x: when ``True``, convert a datetime x-axis into evenly-spaced
        categories with two-line month/year labels (see ``categorical_date_axis``).
        Fixes the skinny-sliver look of clustered columns on unevenly spaced dates.
    """
    # Column value labels are resolved independently of the line's label_mode.
    if bar_labels is True:
        bar_mode, bar_col = "all", bar_label_color
    elif bar_labels is False:
        bar_mode, bar_col = "none", label_color
    else:
        bar_mode, bar_col = label_mode, label_color

    fig = go.Figure()
    for name, x, y, colour, dp in bars:
        fig.add_bar(x=list(x), y=list(y), name=name, marker_color=colour,
                    text=_point_labels(y, dp, bar_mode), textposition="outside",
                    textfont=dict(size=9, color=bar_col), cliponaxis=False)
    ln_name, lx, ly, ldp = line
    fig.add_trace(go.Scatter(
        x=list(lx), y=list(ly), name=ln_name, yaxis="y2",
        mode="lines+markers+text", line=dict(color=line_color, width=2.6),
        marker=dict(size=7, color=line_color, line=dict(color="white", width=1)),
        text=_point_labels(ly, ldp, label_mode), textposition="top center",
        textfont=dict(size=9, color=label_color)))
    layout = dict(_TREND_LAYOUT)
    layout.update(showlegend=True, margin=dict(l=54, r=54, t=10, b=38),
                  legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0,
                              font=dict(size=10)))
    fig.update_layout(height=height, barmode="group", **layout)
    fig.update_xaxes(showgrid=False, linecolor="#e2e8f0", tickfont=dict(size=10))
    fig.update_yaxes(title_text=left_unit, title_font={"size": 11}, title_standoff=4,
                     gridcolor="#f1f5f9", zeroline=False)
    fig.update_layout(yaxis2=dict(title=dict(text=right_unit, font={"size": 11}),
                                  overlaying="y", side="right", showgrid=False,
                                  zeroline=False, rangemode="tozero"))
    if categorical_x:
        categorical_date_axis(fig)
    if bar_labels is True:
        # Headroom so the outside value labels are not clipped at the plot top.
        fig.update_yaxes(automargin=True)
    return fig


def multiline_chart(series, unit: str = "", *, height: int = 320,
                    label_color: str = COMBO_LABEL, label_mode: str = "last",
                    date_ticks: bool = True) -> go.Figure:
    """Multi-series line chart (PBI lineChart): one line per series on a shared axis.

    series: ``[(name, x, y, colour, decimals), ...]``.
    date_ticks: two-line month/year x-tick labels (DATE_TICK_FORMAT) for a date
        x-axis. Default True; ignored by Plotly on a non-date (categorical) axis.
    """
    fig = go.Figure()
    for name, x, y, colour, dp in series:
        fig.add_trace(go.Scatter(
            x=list(x), y=list(y), name=name, mode="lines+markers+text",
            line=dict(color=colour, width=2.6),
            marker=dict(size=7, color=colour, line=dict(color="white", width=1)),
            text=_point_labels(y, dp, label_mode), textposition="top center",
            textfont=dict(size=9, color=label_color)))
    layout = dict(_TREND_LAYOUT)
    layout.update(showlegend=True,
                  legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0,
                              font=dict(size=10)))
    fig.update_layout(height=height, **layout)
    fig.update_xaxes(showgrid=False, linecolor="#e2e8f0", tickfont=dict(size=10))
    if date_ticks:
        fig.update_xaxes(tickformat=DATE_TICK_FORMAT)
    fig.update_yaxes(title_text=unit, title_font={"size": 11}, title_standoff=4,
                     gridcolor="#f1f5f9", zeroline=False)
    return fig


# ═════════════════════════════════════════════════════════════════════════════
# Chart primitives promoted from the Development Testing Dashboard (v0.73.0).
# Battle-tested in-app fixes lifted up so every report-port app inherits them.
# ═════════════════════════════════════════════════════════════════════════════


# ── Categorical date axis (clustered columns) ───────────────────────────────
def date_categories(stamps):
    """Ordered unique dates + a ``{Timestamp: two-line-label}`` map for a
    categorical date axis.

    Uses ``DATE_TICK_FORMAT`` ("%b<br>%Y"), dropping to "%d %b<br>%Y" when two
    dates would collapse to the same month label. Shared so event markers can
    snap to the SAME category labels the columns use.
    """
    order = sorted({pd.Timestamp(s) for s in stamps})
    fmt = DATE_TICK_FORMAT
    if len({d.strftime(fmt) for d in order}) != len(order):
        fmt = "%d %b<br>%Y"  # disambiguate two dates that share a month
    return order, {d: d.strftime(fmt) for d in order}


def categorical_date_axis(fig: go.Figure) -> go.Figure:
    """Turn a datetime x-axis into evenly-spaced categories with two-line
    month/year labels.

    On a datetime axis Plotly sizes every bar to the SMALLEST gap between dates,
    so unevenly spaced tests render as skinny slivers with big empty bays (the
    "bars look poor" trap). Categorical spacing gives confident, even columns,
    matching the original PBI clustered-column chart. No-op when the x values
    are not date-like, so it is safe to call unconditionally.
    """
    stamps = []
    for tr in fig.data:
        for x in (tr.x or []):
            try:
                stamps.append(pd.Timestamp(x))
            except (ValueError, TypeError):
                return fig  # not date-like -> leave the axis untouched
    if not stamps:
        return fig
    order, label = date_categories(stamps)
    for tr in fig.data:
        tr.x = [label[pd.Timestamp(x)] for x in tr.x]
    fig.update_xaxes(type="category", categoryorder="array",
                     categoryarray=[label[d] for d in order],
                     tickangle=0, tickfont=dict(size=9))
    return fig


# ── Growth-curve y-axis break ───────────────────────────────────────────────
def _add_break_glyph(fig: go.Figure) -> go.Figure:
    """Draw a small ``//`` axis-break glyph at the base of the y-axis.

    Plotly has no native broken axis, so we fake it in paper coordinates: a thin
    white rectangle "cuts" the gridlines at the bottom-left, then two short
    parallel slashes read as the break. Sits inside the plot (x>=0) so it never
    collides with the y-tick labels in the left margin.
    """
    fig.add_shape(type="rect", xref="paper", yref="paper",
                  x0=0.0, x1=0.028, y0=0.008, y1=0.060,
                  fillcolor="white", line_width=0, layer="above")
    for x0 in (0.002, 0.014):
        fig.add_shape(type="line", xref="paper", yref="paper",
                      x0=x0, y0=0.006, x1=x0 + 0.012, y1=0.062,
                      line=dict(color=_BREAK_MUTED, width=1.4), layer="above")
    return fig


def apply_break(fig: go.Figure, values, *, pad: float = 0.12) -> go.Figure:
    """Focus the y-axis on the DATA (not anchored at 0) + a ``//`` break glyph.

    Growth curves otherwise hug a near-zero baseline and waste vertical space.
    This pads the data min/max so the curve fills the plot, disables autorange
    (which would otherwise re-introduce 0 via an area fill), and stamps the break
    glyph at the base to signal that the axis does not start at zero.

    Degrades safely: 0 points -> unchanged; 1 point / all-equal -> a small
    symmetric band around the value (never a zero-width or zero-anchored range).
    """
    ys = pd.to_numeric(pd.Series(list(values)), errors="coerce").dropna()
    if len(ys) == 0:
        return fig  # nothing to range - leave the existing autorange alone
    lo, hi = float(ys.min()), float(ys.max())
    if hi <= lo:  # single point or all-equal -> sensible band around the value
        pad_abs = abs(lo) * 0.05 or 1.0
        lo, hi = lo - pad_abs, hi + pad_abs
    else:
        span = hi - lo
        lo -= span * pad
        hi += span * pad
    # autorange=False is REQUIRED: some builders set autorange=True explicitly,
    # which otherwise overrides a bare range= and snaps the axis back to 0.
    fig.update_yaxes(range=[lo, hi], autorange=False)
    _add_break_glyph(fig)
    return fig


# ── Event (injury) markers ──────────────────────────────────────────────────
def add_injury_markers(fig: go.Figure, dates, labels=None) -> go.Figure:
    """Draw a small red "X" just above the x-axis at each given date, with the
    event detail shown on hover.

    PRIMITIVE ONLY: the caller supplies the dates and a matching ``labels`` list
    (no data access happens here). The markers ride a hidden [0, 1] overlay axis
    pinned near the baseline, so they never disturb the primary y-range (or a
    secondary axis). On a categorical chart (see ``categorical_date_axis``) pass
    the matching category label as the x value.
    """
    dates = list(dates)
    if not dates:
        return fig
    labels = list(labels) if labels is not None else ["" for _ in dates]
    fig.add_trace(go.Scatter(
        x=dates, y=[0.04] * len(dates), mode="markers", yaxis="y99",
        name="Injury", showlegend=False, cliponaxis=False,
        marker=dict(symbol="x", size=9, color=_INJURY_RED,
                    line=dict(width=1, color="white")),
        customdata=list(labels),
        hovertemplate="<b>Injury</b><br>%{customdata}<extra></extra>"))
    fig.update_layout(yaxis99=dict(overlaying="y", range=[0, 1], visible=False,
                                   fixedrange=True))
    return fig
