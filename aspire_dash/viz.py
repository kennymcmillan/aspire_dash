"""Reusable custom SVG visualisations — rings, gauges, sparklines.

Generic versions of the WHOOP ring components, usable in any Aspire Dash app.
All colours default to the Aspire theme but can be overridden.
"""

import math
from typing import Tuple
from dash import html

try:
    import dash_svg as svg
    _HAS_SVG = True
except ImportError:
    _HAS_SVG = False

from .theme import SUCCESS, WARNING, DANGER, SLATE, ACCENT, GOLD


# ── Helpers ──────────────────────────────────────────────────────────────────

def _require_svg():
    if not _HAS_SVG:
        raise ImportError(
            "dash-svg is required for viz components. Install with: pip install dash-svg"
        )


def _svg_circle(cx, cy, r, stroke="#e2e8f0", stroke_width=5,
                dasharray=None, dashoffset=None, animated=False, fill="none"):
    """SVG circle element with optional dash animation."""
    props = dict(
        cx=str(cx), cy=str(cy), r=str(r),
        fill=fill, stroke=stroke, strokeWidth=str(stroke_width),
    )
    style = {"strokeLinecap": "round"}
    if dasharray is not None:
        props["strokeDasharray"] = str(dasharray)
    if dashoffset is not None:
        props["strokeDashoffset"] = str(dashoffset)
    if animated:
        style["transition"] = "all 0.5s ease-out"
    props["style"] = style
    return svg.Circle(**props)


# ── Ring / Donut Progress ────────────────────────────────────────────────────

def progress_ring(
    value,
    max_val=100,
    size=80,
    stroke_width=6,
    color=None,
    track_color="#e2e8f0",
    label=None,
    display=None,
    unit="",
    font_size=None,
    animated=True,
):
    """Circular progress ring — the building block for all ring variants.

    Parameters
    ----------
    value : float
        Current value (0 to max_val).
    max_val : float
        Maximum value (default 100).
    size : int
        Ring diameter in px (default 80).
    stroke_width : int
        Ring thickness in px (default 6).
    color : str or None
        Stroke colour. If None, uses ACCENT.
    track_color : str
        Background track colour.
    label : str or None
        Text below the ring.
    display : str or None
        Override text shown in centre. If None, shows rounded value.
    unit : str
        Small unit text after the value (e.g. "hrs", "%", "bpm").
    font_size : str or None
        Override centre text size. If None, auto-scales with ring size.
    animated : bool
        Enable smooth transition animation.
    """
    _require_svg()

    value = max(0, min(max_val, value or 0))
    pct = (value / max_val * 100) if max_val else 0
    color = color or ACCENT

    r = (size - stroke_width) / 2
    circ = 2 * math.pi * r
    offset = circ - (pct / 100) * circ
    cx = size / 2

    if font_size is None:
        font_size = f"{max(12, size // 4)}px"

    display_text = display if display is not None else str(round(value))

    centre_children = [
        html.Span(display_text, style={
            "fontWeight": "bold", "fontSize": font_size, "color": SLATE["800"],
            "lineHeight": "1",
        }),
    ]
    if unit:
        centre_children.append(
            html.Span(unit, style={
                "fontSize": f"{max(9, size // 10)}px", "color": SLATE["400"],
                "marginLeft": "1px",
            })
        )

    children = [
        html.Div([
            svg.Svg([
                _svg_circle(cx, cx, r, stroke=track_color, stroke_width=stroke_width),
                _svg_circle(cx, cx, r, stroke=color, stroke_width=stroke_width,
                            dasharray=circ, dashoffset=offset, animated=animated),
            ], width=str(size), height=str(size), style={"transform": "rotate(-90deg)"}),
            html.Div(
                centre_children,
                style={
                    "position": "absolute", "inset": "0",
                    "display": "flex", "flexDirection": "column",
                    "alignItems": "center", "justifyContent": "center",
                },
            ),
        ], style={"position": "relative", "width": f"{size}px", "height": f"{size}px"}),
    ]

    if label:
        children.append(html.Span(label, style={
            "marginTop": "4px", "fontSize": "11px", "fontWeight": "500",
            "textTransform": "uppercase", "letterSpacing": "0.05em",
            "color": SLATE["500"],
        }))

    return html.Div(children, style={
        "display": "flex", "flexDirection": "column", "alignItems": "center",
    })


def status_ring(
    value,
    max_val=100,
    thresholds=None,
    size=80,
    stroke_width=6,
    label=None,
    display=None,
    unit="",
):
    """Progress ring with auto colour based on value thresholds.

    Parameters
    ----------
    thresholds : dict or None
        {"green": 67, "yellow": 34} — value >= 67 is green, >= 34 yellow, else red.
        If None, uses default recovery-style thresholds.
    """
    thresholds = thresholds or {"green": 67, "yellow": 34}
    pct = (value / max_val * 100) if max_val and value else 0

    if pct >= thresholds.get("green", 67):
        color = SUCCESS
    elif pct >= thresholds.get("yellow", 34):
        color = WARNING
    else:
        color = DANGER

    return progress_ring(
        value, max_val=max_val, size=size, stroke_width=stroke_width,
        color=color, label=label, display=display, unit=unit,
    )


def ring_row(rings, gap="24px"):
    """Horizontal row of ring components with centered alignment."""
    return html.Div(rings, style={
        "display": "flex", "alignItems": "center", "justifyContent": "center",
        "gap": gap, "padding": "16px 0", "flexWrap": "wrap",
    })


# ── Sparkline ────────────────────────────────────────────────────────────────

def sparkline(values, color=None, width=120, height=32, stroke_width=2):
    """Inline SVG sparkline chart.

    Parameters
    ----------
    values : list[float]
        Data points to plot.
    color : str or None
        Line colour (default: ACCENT).
    width, height : int
        SVG dimensions in px.
    stroke_width : int
        Line thickness.
    """
    _require_svg()

    if not values or len(values) < 2:
        return html.Div(style={"width": f"{width}px", "height": f"{height}px"})

    color = color or ACCENT
    vmin, vmax = min(values), max(values)
    spread = vmax - vmin or 1
    pad = 2

    points = []
    for i, v in enumerate(values):
        x = pad + (i / (len(values) - 1)) * (width - 2 * pad)
        y = pad + (1 - (v - vmin) / spread) * (height - 2 * pad)
        points.append(f"{x:.1f},{y:.1f}")

    return html.Div(
        svg.Svg([
            svg.Polyline(
                points=" ".join(points),
                fill="none", stroke=color, strokeWidth=str(stroke_width),
                style={"strokeLinecap": "round", "strokeLinejoin": "round"},
            ),
        ], width=str(width), height=str(height)),
        style={"display": "inline-block"},
    )


# ── Horizontal Bar ───────────────────────────────────────────────────────────

def horizontal_bar(value, max_val=100, color=None, height=8, label=None, show_pct=False):
    """Simple horizontal progress bar.

    Parameters
    ----------
    value : float
        Current value.
    max_val : float
        Maximum value.
    color : str
        Bar fill colour (default: ACCENT).
    height : int
        Bar height in px.
    label : str or None
        Text label to the left.
    show_pct : bool
        Show percentage text to the right.
    """
    pct = min(100, (value / max_val * 100) if max_val else 0)
    color = color or ACCENT

    bar = html.Div([
        html.Div(style={
            "width": f"{pct:.1f}%", "height": "100%",
            "backgroundColor": color, "borderRadius": f"{height // 2}px",
            "transition": "width 0.3s ease",
        }),
    ], style={
        "flex": "1", "height": f"{height}px",
        "backgroundColor": SLATE["200"], "borderRadius": f"{height // 2}px",
        "overflow": "hidden",
    })

    children = []
    if label:
        children.append(html.Span(label, style={
            "fontSize": "12px", "fontWeight": "500", "color": SLATE["600"],
            "width": "80px", "flexShrink": "0",
        }))
    children.append(bar)
    if show_pct:
        children.append(html.Span(f"{pct:.0f}%", style={
            "fontSize": "12px", "fontWeight": "600", "color": SLATE["700"],
            "width": "40px", "textAlign": "right", "flexShrink": "0",
        }))

    return html.Div(children, style={
        "display": "flex", "alignItems": "center", "gap": "8px",
    })


# ── Status Dot ───────────────────────────────────────────────────────────────

def status_dot(status="green", size=8, pulse=False):
    """Coloured status indicator dot.

    Parameters
    ----------
    status : str
        "green", "yellow", "red", or a hex colour.
    size : int
        Dot diameter in px.
    pulse : bool
        Add pulse animation (requires aspire base CSS).
    """
    color_map = {"green": SUCCESS, "yellow": WARNING, "red": DANGER}
    color = color_map.get(status, status)

    style = {
        "width": f"{size}px", "height": f"{size}px",
        "borderRadius": "50%", "backgroundColor": color,
        "display": "inline-block", "flexShrink": "0",
    }

    cls = ""
    if pulse and status == "red":
        cls = "pulse-red"
    elif pulse:
        cls = "pulse-connected"

    return html.Span(className=cls, style=style)


# ── Metric Card with Sparkline ───────────────────────────────────────────────

def metric_spark(label, value, unit="", trend_values=None, color=None):
    """Compact metric display with optional inline sparkline.

    Parameters
    ----------
    label : str
        Metric name.
    value : str or number
        Current value to display.
    unit : str
        Unit suffix.
    trend_values : list[float] or None
        Data for sparkline. If None, no sparkline shown.
    color : str or None
        Sparkline colour (default: ACCENT).
    """
    right = None
    if trend_values and len(trend_values) >= 2:
        right = sparkline(trend_values, color=color, width=80, height=24, stroke_width=1.5)

    return html.Div([
        html.Div([
            html.Div(label, style={
                "fontSize": "11px", "fontWeight": "500", "color": SLATE["500"],
                "textTransform": "uppercase", "letterSpacing": "0.03em",
            }),
            html.Div([
                html.Span(str(value), style={
                    "fontSize": "20px", "fontWeight": "700", "color": SLATE["800"],
                    "fontVariantNumeric": "tabular-nums",
                }),
                html.Span(f" {unit}" if unit else "", style={
                    "fontSize": "12px", "color": SLATE["400"],
                }),
            ]),
        ]),
        right,
    ], style={
        "display": "flex", "alignItems": "center", "justifyContent": "space-between",
        "padding": "12px 16px", "background": "white",
        "borderRadius": "8px", "border": f"1px solid {SLATE['200']}",
        "boxShadow": "0 1px 2px rgba(0,0,0,0.04)",
    })


# ── Body Fat Gauge (semicircle, green→amber→red) ─────────────────────────────
#
# Pure SVG semicircle gauge with gradient arc, tick labels (5/10/15/20/25/30),
# zone labels (Athletic/Fit/Average/Above/High), needle dot, tabular numeric
# centre value. Ported byte-for-byte from the DASH_Anthro app so any Aspire
# anthro / body-comp dashboard can drop it in with no extra deps (no Plotly,
# no dash-svg — emits SVG markup inside an html.Iframe).

# Geometry constants — keep in sync with the source TSX gauge.
_BFG_CX = 100
_BFG_CY = 105
_BFG_R_OUTER = 80
_BFG_R_INNER = 64
_BFG_STROKE_W = _BFG_R_OUTER - _BFG_R_INNER
_BFG_R_MID = (_BFG_R_OUTER + _BFG_R_INNER) / 2
_BFG_MAX = 30

_BFG_ZONES = [
    {"start": 5,  "end": 10, "label": "Athletic"},
    {"start": 10, "end": 15, "label": "Fit"},
    {"start": 15, "end": 20, "label": "Average"},
    {"start": 20, "end": 25, "label": "Above"},
    {"start": 25, "end": 30, "label": "High"},
]

_BFG_TICKS = [5, 10, 15, 20, 25, 30]


def _bfg_to_angle(bf: float) -> float:
    return (max(0.0, min(bf, _BFG_MAX)) / _BFG_MAX) * 180.0


def _bfg_polar(angle_deg: float, r: float) -> Tuple[float, float]:
    rad = (180.0 - angle_deg) * math.pi / 180.0
    return _BFG_CX + r * math.cos(rad), _BFG_CY - r * math.sin(rad)


def _bfg_arc_path(start_deg: float, end_deg: float, r: float) -> str:
    if abs(end_deg - start_deg) < 0.1:
        return ""
    p1 = _bfg_polar(start_deg, r)
    p2 = _bfg_polar(end_deg, r)
    large = 1 if (end_deg - start_deg) > 180 else 0
    return f"M {p1[0]:.3f},{p1[1]:.3f} A {r},{r} 0 {large} 1 {p2[0]:.3f},{p2[1]:.3f}"


def body_fat_gauge_svg(value: float) -> str:
    """Return the raw SVG markup string for a body-fat semicircle gauge.

    Use this when you need to embed the SVG yourself (e.g. inside an HTML
    report, a custom iframe, or a Pandoc render). Otherwise prefer
    ``body_fat_gauge`` which wraps it in a Dash component.

    Parameters
    ----------
    value : float
        Body fat percentage. Clamped to ``[0, 30]``. ``None`` / falsy
        values render as 0.0% with no foreground arc.
    """
    target = _bfg_to_angle(float(value or 0))

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 130" '
        'style="width:100%;max-width:320px;height:auto;font-family:Inter,system-ui,sans-serif;">',
        '<defs><linearGradient id="bf-gauge-grad" x1="0" y1="0" x2="1" y2="0">'
        '<stop offset="0%" stop-color="#10b981"/>'
        '<stop offset="45%" stop-color="#f59e0b"/>'
        '<stop offset="100%" stop-color="#ef4444"/>'
        '</linearGradient></defs>',
        # Background arc
        f'<path d="{_bfg_arc_path(0, 180, _BFG_R_MID)}" fill="none" stroke="#e2e8f0" '
        f'stroke-width="{_BFG_STROKE_W}" stroke-linecap="round" />',
    ]

    # Foreground arc
    if target > 0.5:
        parts.append(
            f'<path d="{_bfg_arc_path(0, target, _BFG_R_MID)}" fill="none" '
            f'stroke="url(#bf-gauge-grad)" stroke-width="{_BFG_STROKE_W}" stroke-linecap="round" />'
        )

    # Ticks
    for tick in _BFG_TICKS:
        a = _bfg_to_angle(tick)
        ox, oy = _bfg_polar(a, _BFG_R_OUTER + 2)
        ix, iy = _bfg_polar(a, _BFG_R_OUTER + 8)
        lx, ly = _bfg_polar(a, _BFG_R_OUTER + 16)
        parts.append(
            f'<line x1="{ox:.2f}" y1="{oy:.2f}" x2="{ix:.2f}" y2="{iy:.2f}" '
            'stroke="#94a3b8" stroke-width="1" />'
        )
        parts.append(
            f'<text x="{lx:.2f}" y="{ly:.2f}" text-anchor="middle" '
            'dominant-baseline="central" font-size="8" fill="#94a3b8" font-weight="500">'
            f'{tick}</text>'
        )

    # Zone labels
    for z in _BFG_ZONES:
        mid_a = _bfg_to_angle((z["start"] + z["end"]) / 2)
        zx, zy = _bfg_polar(mid_a, _BFG_R_INNER - 12)
        parts.append(
            f'<text x="{zx:.2f}" y="{zy:.2f}" text-anchor="middle" '
            'dominant-baseline="central" font-size="7" fill="#94a3b8" font-weight="500">'
            f'{z["label"]}</text>'
        )

    # Needle indicator
    nx, ny = _bfg_polar(target, _BFG_R_INNER - 2)
    parts.append(
        f'<circle cx="{nx:.2f}" cy="{ny:.2f}" r="3" fill="#001d3d" '
        'stroke="white" stroke-width="1.5" />'
    )

    # Center value
    parts.append(
        f'<text x="{_BFG_CX}" y="{_BFG_CY - 6}" text-anchor="middle" font-size="26" '
        'font-weight="700" fill="#001d3d" style="font-variant-numeric:tabular-nums;">'
        f'{float(value or 0):.1f}</text>'
    )
    parts.append(
        f'<text x="{_BFG_CX}" y="{_BFG_CY + 10}" text-anchor="middle" font-size="9" '
        'fill="#94a3b8" font-weight="500">% Body Fat</text>'
    )
    parts.append('</svg>')
    return "".join(parts)


def body_fat_gauge(value: float):
    """Body-fat semicircle gauge as a Dash component.

    Wraps ``body_fat_gauge_svg`` in an ``html.Iframe`` so the inline SVG
    renders correctly on Posit Connect (where ``dcc.Markdown`` with
    ``dangerously_allow_html`` has been flaky for raw SVG). No extra
    Python deps beyond Dash.

    Parameters
    ----------
    value : float
        Body fat percentage. Clamped to ``[0, 30]``.

    Examples
    --------
    >>> from aspire_dash.viz import body_fat_gauge
    >>> body_fat_gauge(12.3)
    """
    svg = body_fat_gauge_svg(value)
    doc = (
        '<!doctype html><html><head><meta charset="utf-8">'
        '<style>html,body{margin:0;padding:0;background:transparent;'
        'display:flex;justify-content:center;align-items:center;}</style>'
        '</head><body>' + svg + '</body></html>'
    )
    return html.Iframe(
        srcDoc=doc,
        style={"border": 0, "width": "100%", "maxWidth": 340, "height": 220,
               "background": "transparent"},
    )
