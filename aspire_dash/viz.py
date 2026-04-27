"""Reusable custom SVG visualisations — rings, gauges, sparklines.

Generic versions of the WHOOP ring components, usable in any Aspire Dash app.
All colours default to the Aspire theme but can be overridden.
"""

import math
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


def _svg_circle(cx, cy, r, stroke="#e5e7eb", stroke_width=5,
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
    track_color="#e5e7eb",
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
