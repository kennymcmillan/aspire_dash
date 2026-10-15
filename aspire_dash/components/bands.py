"""Performance-band components (v0.107, promoted from endurance-dashboard Strength).

Every piece takes bands in the same shape ``history_figure(bands=...)`` already uses:
``[(name, low, high[, fill]), ...]`` listed WORST -> BEST, ``None`` = open end. A
lower-is-better metric (contact time) lists its bands high -> low; the helpers detect
that and still read left = worst, right = best.

    band_gauge(value, bands)                  equal-width band bar + gold marker
    band_gauge_card(label, value, ...)        card face: big value, gauge, change vs last
    band_radar(rows)                          every banded test on one 0..N band scale
    band_profile(rows)                        radar + a list of absolute values
    metric_panel(title, cards, ...)             tinted container per test (icon, status chip)
    metric_panels(panels)                       4-column grid of panels, 1 column on phones
    asymmetry_card(left, right)               left/right split bar
    panel_status(changes)                     ('2 of 3 improved', 'up'|'down'|'')

Styling lives in ``assets/07_squad_bands.css`` (copied by ``setup_app``); classes
start ``ad-``.
"""
from __future__ import annotations

import math

import plotly.graph_objects as go
from dash import dcc, html

from ..charts import _delta_dp, _hist_fmt_delta

GAUGE_FILLS = ["#cbd5e1", "#93b4dc", "#3f78bd", "#004185", "#002a5c"]
RING_FILLS = ["#eef2f7", "#e1e9f3", "#cfdcee", "#b9cde6", "#a3bedd"]
MARKER_GOLD = "#f2b705"
GOOD, BAD, FLAT = "#27AE60", "#E74C3C", "#111827"
_SEP_STYLE = {"color": "#94a3b8"}

__all__ = [
    "band_descending", "band_index", "band_position", "gap_to_next", "fmt_value",
    "change_text", "band_gauge", "band_gauge_card", "band_radar", "band_profile_list",
    "band_profile", "metric_panel", "metric_panels", "asymmetry_card", "panel_status",
]


def _missing(v) -> bool:
    return v is None or (isinstance(v, float) and math.isnan(v))


def fmt_value(v, unit: str = "") -> str:
    """'45.2 cm', '0.172 s', '2873 N', ratios '2.66'. '--' when missing."""
    if _missing(v):
        return "--"
    if unit == "s":
        s = f"{v:.3f}"
    elif abs(v) >= 100:
        s = f"{v:.0f}"
    elif not unit:
        s = f"{v:.2f}"
    else:
        s = f"{v:.1f}"
    return f"{s} {unit}".strip()


def change_text(delta, prev=None, unit: str = "") -> str:
    """Absolute AND % change vs the previous test: '+4.19 cm (+11.1%)'."""
    return _hist_fmt_delta(delta, unit, prev, dp=_delta_dp(prev, unit))


def _delta_color(delta, lower_is_better=False):
    if _missing(delta) or abs(delta) <= 1e-9:
        return FLAT
    return GOOD if ((delta < 0) if lower_is_better else (delta > 0)) else BAD


# --------------------------------------------------------------------------- #
# band maths
# --------------------------------------------------------------------------- #
def band_descending(bands) -> bool:
    """True when bands run high -> low (lower is better)."""
    first = bands[0][1] if bands[0][1] is not None else bands[0][2]
    last = bands[-1][2] if bands[-1][2] is not None else bands[-1][1]
    return first > last


def band_index(v, bands) -> int:
    """Index (0 = worst) of the band holding `v`."""
    for i, b in enumerate(bands):
        lo, hi = b[1], b[2]
        if (lo is None or v >= lo) and (hi is None or v < hi):
            return i
    top = max(e for b in bands for e in b[1:3] if e is not None)
    return len(bands) - 1 if v >= top else 0


def _band_span(bands, i):
    # Open-ended bands borrow the typical band width so the marker still moves.
    widths = sorted(b[2] - b[1] for b in bands if b[1] is not None and b[2] is not None)
    w = widths[len(widths) // 2] if widths else 1.0
    lo, hi = bands[i][1], bands[i][2]
    return (hi - w if lo is None else lo), (lo + w if hi is None else hi)


def band_position(v, bands) -> float:
    """Marker position 0-100 across EQUAL-width segments (worst left, best right)."""
    i = band_index(v, bands)
    lo, hi = _band_span(bands, i)
    frac = (hi - v) / (hi - lo) if band_descending(bands) else (v - lo) / (hi - lo)
    frac = min(max(frac, 0.03), 0.97)
    return (i + frac) / len(bands) * 100


def gap_to_next(v, bands, unit: str = "") -> str:
    """'2.9 cm to Very strong (+6.9%)', or 'top band'."""
    i = band_index(v, bands)
    if i >= len(bands) - 1:
        return "top band"
    nxt = bands[i + 1]
    edge = nxt[2] if band_descending(bands) else nxt[1]
    gap = edge - v
    dp = 3 if unit == "s" else (0 if abs(v) >= 100 else 1)
    return f"{abs(gap):.{dp}f} {unit} to {nxt[0]} ({gap / abs(v) * 100:+.1f}%)".replace("  ", " ")


# --------------------------------------------------------------------------- #
# gauge + card
# --------------------------------------------------------------------------- #
def band_gauge(value, bands):
    """Equal segments (current one solid), a gold marker, band names, cut-offs."""
    n = len(bands)
    fills = GAUGE_FILLS[-n:] if n <= len(GAUGE_FILLS) else GAUGE_FILLS
    cur = band_index(value, bands)
    desc = band_descending(bands)
    segs = [html.Div(className="ad-gauge-seg" + (" is-cur" if i == cur else ""),
                     style={"background": fills[i % len(fills)]}) for i in range(n)]
    marker = html.Div(className="ad-gauge-marker",
                      style={"left": f"{band_position(value, bands):.1f}%"})
    names = [html.Div(b[0], className="ad-gauge-name" + (" is-cur" if i == cur else ""))
             for i, b in enumerate(bands)]
    cuts = []
    for i in range(1, n):
        e = bands[i][2] if desc else bands[i][1]
        if e is None:
            e = bands[i - 1][1] if desc else bands[i - 1][2]
        cuts.append(html.Span(f"{e:g}", className="ad-gauge-cut",
                              style={"left": f"{i / n * 100:.2f}%"}))
    return html.Div(className="ad-gauge", role="img",
                    **{"aria-label": f"{fmt_value(value)} in band {bands[cur][0]}"}, children=[
        html.Div([html.Div(segs, className="ad-gauge-bar"), marker], className="ad-gauge-track"),
        html.Div(names, className="ad-gauge-names"),
        html.Div(cuts, className="ad-gauge-cuts"),
    ])


def _change_line(delta, prev, unit, lower_is_better):
    if _missing(delta):
        return html.Span("first test", className="ad-muted")
    return html.Span(["vs last ", html.B(change_text(delta, prev, unit),
                                         style={"color": _delta_color(delta, lower_is_better)})])


def band_gauge_card(label, value, unit: str = "", bands=None, *, date=None, delta=None,
                    prev=None, lower_is_better: bool = False, value_color: str = "#004185",
                    id=None, className: str = ""):
    """Card face: label + date, one big value, the band gauge (or 'no reference band'),
    one line with the change vs last (absolute and %) and the gap to the next band.
    `value=None` renders a quiet '--' / 'no data' card. Wrap it in
    ``history_trigger(card_id, card)`` to open a history chart on click."""
    kw = {"id": id} if id is not None else {}
    if _missing(value):
        return html.Div(className=f"ad-band-card is-empty {className}".strip(), **kw, children=[
            html.Div(label, className="ad-band-card-label"),
            html.Div("--", className="ad-band-card-value", style={"color": value_color}),
            html.Div("no data", className="ad-muted ad-small")])
    num, _, u = fmt_value(value, unit).partition(" ")
    foot = [_change_line(delta, prev, unit, lower_is_better)]
    if bands:
        foot += [html.Span(" · ", style=_SEP_STYLE),
                 html.Span(gap_to_next(value, bands, unit), className="ad-muted")]
    return html.Div(className=f"ad-band-card {className}".strip(), **kw, children=[
        html.Div([html.Span(label, className="ad-band-card-label"),
                  html.Span(str(date) if date else "", className="ad-band-card-date")],
                 className="ad-band-card-head"),
        html.Div([num, html.Small(f" {u}" if u else "")], className="ad-band-card-value",
                 style={"color": value_color}),
        band_gauge(value, bands) if bands else html.Div("no reference band",
                                                        className="ad-muted ad-small ad-gap"),
        html.Div(foot, className="ad-band-card-foot"),
    ])


# --------------------------------------------------------------------------- #
# radar + profile list
# --------------------------------------------------------------------------- #
def band_radar(rows, *, rings: int = 4, height: int = 460):
    """Radar of banded tests on one scale: centre = worst band, edge = best.

    rows: ``[{"label", "value", "bands", "unit"?, "prev"?}]``. The latest shape is
    filled navy with gold markers (hover: value + band); a dashed line shows the
    previous test where one exists. `rings` shaded rings sit behind it."""
    theta = [r["label"] for r in rows]
    closed = theta + theta[:1]
    fig = go.Figure()
    for k in range(rings, 0, -1):      # outer first so inner rings paint over it
        fig.add_trace(go.Scatterpolar(r=[k] * len(closed), theta=closed, mode="lines",
                                      fill="toself", fillcolor=RING_FILLS[(k - 1) % len(RING_FILLS)],
                                      line=dict(color="#ffffff", width=1),
                                      hoverinfo="skip", showlegend=False, name=f"band {k}"))
    scale = rings / 100
    prev = [(band_position(r["prev"], r["bands"]) * scale if not _missing(r.get("prev")) else None)
            for r in rows]
    if any(p is not None for p in prev):
        fig.add_trace(go.Scatterpolar(r=prev + prev[:1], theta=closed, mode="lines",
                                      name="Previous", connectgaps=True, hoverinfo="skip",
                                      line=dict(color="#64748b", width=1.5, dash="dash")))
    cur = [band_position(r["value"], r["bands"]) * scale for r in rows]
    hover = [f"{fmt_value(r['value'], r.get('unit', ''))} · "
             f"{r['bands'][band_index(r['value'], r['bands'])][0]}" for r in rows]
    fig.add_trace(go.Scatterpolar(
        r=cur + cur[:1], theta=closed, mode="lines+markers", name="Latest",
        fill="toself", fillcolor="rgba(0,65,133,0.22)", line=dict(color="#004185", width=2.5),
        marker=dict(size=9, color=MARKER_GOLD, line=dict(color="#004185", width=1.5)),
        customdata=hover + hover[:1],
        hovertemplate="<b>%{theta}</b><br>%{customdata}<extra></extra>"))
    fig.update_layout(
        template="plotly_white", height=height, margin=dict(l=70, r=70, t=30, b=30),
        showlegend=True, legend=dict(orientation="h", y=-0.06, x=0.5, xanchor="center"),
        polar=dict(bgcolor="rgba(0,0,0,0)",
                   radialaxis=dict(range=[0, rings], showticklabels=False, ticks="",
                                   showline=False, gridcolor="rgba(0,0,0,0)"),
                   angularaxis=dict(rotation=90, direction="clockwise",
                                    tickfont=dict(size=11, color="#1e293b"),
                                    gridcolor="#ffffff")))
    return fig


def band_profile_list(rows):
    """One line per test: name + band chip, absolute value, change vs last, gap, date.

    rows: ``[{"label", "value", "bands", "unit"?, "delta"?, "prev"?, "date"?,
    "lower_is_better"?}]``."""
    items = []
    for r in rows:
        v, bands, unit = r["value"], r["bands"], r.get("unit", "")
        bi = band_index(v, bands)
        num, _, u = fmt_value(v, unit).partition(" ")
        items.append(html.Div(className="ad-prof-row", children=[
            html.Div([html.Span(r["label"], className="ad-prof-name"),
                      html.Span(bands[bi][0],
                                className=f"ad-prof-band b{round(bi * 3 / max(len(bands) - 1, 1))}")],
                     className="ad-prof-top"),
            html.Div([html.Span(num, className="ad-prof-val"), html.Small(f" {u}" if u else "")]),
            html.Div([_change_line(r.get("delta"), r.get("prev"), unit, r.get("lower_is_better", False)),
                      html.Span(" · ", style=_SEP_STYLE), html.Span(gap_to_next(v, bands, unit))],
                     className="ad-prof-sub"),
            html.Div(str(r.get("date") or ""), className="ad-prof-date"),
        ]))
    return html.Div(items, className="ad-prof-list")


def band_profile(rows, *, ring_names=None, note=None, empty="No banded tests on file"):
    """Radar (rows with ``radar`` not False) beside the full absolute-value list.
    `ring_names` labels the ring colour key (inner -> outer); its length sets the
    ring count (default 4, unnamed)."""
    rows = [r for r in rows if not _missing(r.get("value")) and r.get("bands")]
    if not rows:
        return html.Div(empty, className="ad-empty-line")
    rings = len(ring_names) if ring_names else 4
    chart = [dcc.Graph(figure=band_radar([r for r in rows if r.get("radar", True)], rings=rings),
                       config={"displayModeBar": False})]
    if ring_names:
        chart.append(html.Div([html.Span([html.I(style={"background": RING_FILLS[i % len(RING_FILLS)]}), n],
                                         className="ad-ring-key")
                               for i, n in enumerate(ring_names)], className="ad-ring-keys"))
    if note:
        chart.append(html.Div(note, className="ad-prof-note"))
    return html.Div([html.Div(chart, className="ad-prof-chart"), band_profile_list(rows)],
                    className="ad-prof")


# --------------------------------------------------------------------------- #
# test panels + asymmetry
# --------------------------------------------------------------------------- #
def panel_status(changes):
    """changes: ``[(delta, lower_is_better), ...]`` -> ('2 of 3 improved', tone)."""
    moves = [(d, lib) for d, lib in changes if not _missing(d)]
    if not moves:
        return None, ""
    up = sum(1 for d, lib in moves if (d < 0 if lib else d > 0))
    tone = "up" if up * 2 > len(moves) else ("down" if up * 2 < len(moves) else "")
    return f"{up} of {len(moves)} improved", tone


def metric_panel(title, cards, *, subtitle=None, icon=None, family: str = "jump",
               date=None, status=None, span: int = 1, cols: int | None = None, raw: bool = False):
    """One tinted container per test. `family` sets the accent: 'jump' (navy),
    'force' (teal), 'speed' (gold); add your own with ``.ad-panel.fam-<x>{--acc:..}``.
    `status` = (text, 'up'|'down'|'') chip, e.g. from ``panel_status``. `span` = grid
    columns taken in ``metric_panels`` (1-4). `cols` forces that many cards per row
    (4 -> 2 on tablets, 1 on phones). `raw=True` puts `cards` in as-is (your own rows)."""
    meta = []
    if date:
        meta.append(html.Span(f"Tested {date}"))
    if status and status[0]:
        meta.append(html.Span(status[0], className=f"ad-chip {status[1]}".strip()))
    head = [html.Span(html.I(className=f"fa-solid {icon}"), className="ad-panel-icon",
                      **{"aria-hidden": "true"})] if icon else []
    head += [html.Div(title, className="ad-panel-title")]
    if subtitle:
        head.append(html.Div(subtitle, className="ad-panel-sub"))
    head.append(html.Div(meta, className="ad-panel-meta"))
    body = cards if raw else [html.Div(cards, className="ad-panel-cards" + (f" cols-{cols}" if cols else ""))]
    return html.Div([html.Div(head, className="ad-panel-head"), *body],
                    className=f"ad-panel fam-{family} span-{span}")


def metric_panels(panels):
    """4-column grid of ``metric_panel``s; 2 columns under 1100px, 1 on phones."""
    return html.Div(panels, className="ad-panels")


def asymmetry_card(left, right, *, left_date=None, right_date=None, title: str = "Asymmetry",
                   left_color: str = "#004185", right_color: str = "#dc2626"):
    """Split bar of each side's share of L+R. Asymmetry % = |L-R| / max(L, R), named
    for the stronger side ('12% Left', 'Even' under 0.5%). Dates show when they differ."""
    if _missing(left) or _missing(right) or not left or not right or left + right <= 0:
        return html.Div([html.Div(title, className="ad-band-card-label"),
                         html.Div("--", className="ad-asym-big"),
                         html.Div("no data", className="ad-muted ad-small")],
                        className="ad-band-card ad-asym")
    lp = round(left / (left + right) * 100, 1)
    rp = round(100 - lp, 1)
    asym = abs(left - right) / max(left, right) * 100
    side = "Left" if left > right else "Right"
    head = "Even" if round(asym) == 0 else f"{asym:.0f}% {side}"
    when = ("" if not (left_date or right_date) else
            f"latest {left_date}" if left_date == right_date else f"L {left_date} · R {right_date}")
    return html.Div(className="ad-band-card ad-asym", children=[
        html.Div(title, className="ad-band-card-label"),
        html.Div(head, className="ad-asym-big",
                 style={"color": FLAT if head == "Even" else (left_color if side == "Left" else right_color)}),
        html.Div(when, className="ad-muted ad-small"),
        html.Div(className="ad-asym-bar", role="img",
                 **{"aria-label": f"Left {lp:g}%, right {rp:g}%"}, children=[
            html.Div(style={"width": f"{lp:g}%", "background": left_color}),
            html.Div(style={"width": f"{rp:g}%", "background": right_color})]),
        html.Div([html.Span(f"L {lp:g}%", style={"color": left_color}),
                  html.Span(f"R {rp:g}%", style={"color": right_color})], className="ad-asym-legend"),
    ])
