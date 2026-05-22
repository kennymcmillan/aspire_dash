"""Firstbeat / HR-zone components — reusable across any training-load app.

Provides HR zone bars, ACWR badges, training effect displays, and session cards.
Uses standard Firstbeat zone colours (Blue/Teal/Green/Yellow/Red for Z1-Z5).
"""

from dash import html

from .theme import SLATE, SHADOW_SM, RADIUS_LG

# ── Zone Colour System ──────────────────────────────────────────────────────

ZONE_COLORS = {
    "zone1": "#60A5FA",  # Blue  — Recovery
    "zone2": "#2DD4BF",  # Teal  — Easy
    "zone3": "#4ADE80",  # Green — Aerobic
    "zone4": "#FACC15",  # Yellow — Threshold
    "zone5": "#F87171",  # Red   — Max
}

ZONE_CONFIG = [
    {"key": "zone1", "label": "Z1", "name": "Recovery",  "color": "#60A5FA"},
    {"key": "zone2", "label": "Z2", "name": "Easy",      "color": "#2DD4BF"},
    {"key": "zone3", "label": "Z3", "name": "Aerobic",   "color": "#4ADE80"},
    {"key": "zone4", "label": "Z4", "name": "Threshold", "color": "#FACC15"},
    {"key": "zone5", "label": "Z5", "name": "Max",       "color": "#F87171"},
]

# ── ACWR Status System ──────────────────────────────────────────────────────

ACWR_THRESHOLDS = {
    "detraining": {"max": 0.8,  "color": "#3b82f6", "bg": "#dbeafe", "text": "#1e40af", "label": "Detraining"},
    "optimal":    {"max": 1.3,  "color": "#22c55e", "bg": "#dcfce7", "text": "#166534", "label": "Optimal"},
    "caution":    {"max": 1.5,  "color": "#f59e0b", "bg": "#fef3c7", "text": "#92400e", "label": "Caution"},
    "danger":     {"max": 99.0, "color": "#ef4444", "bg": "#fee2e2", "text": "#991b1b", "label": "Danger"},
}


def get_acwr_status(acwr):
    """Return status dict for an ACWR value.

    Returns dict with keys: status, label, color, bg, text.
    """
    if acwr is None:
        return {"status": "unknown", "label": "Unknown", "color": "#9ca3af",
                "bg": "#f3f4f6", "text": "#6b7280"}

    for key, t in ACWR_THRESHOLDS.items():
        if acwr < t["max"]:
            return {"status": key, "label": t["label"], "color": t["color"],
                    "bg": t["bg"], "text": t["text"]}

    # Fallback (acwr >= 99)
    t = ACWR_THRESHOLDS["danger"]
    return {"status": "danger", "label": t["label"], "color": t["color"],
            "bg": t["bg"], "text": t["text"]}


# ── ACWR Badge ──────────────────────────────────────────────────────────────

def acwr_badge(acwr, show_value=True):
    """Pill badge showing ACWR status with optional numeric value.

    Parameters
    ----------
    acwr : float or None
        Acute-to-Chronic Workload Ratio.
    show_value : bool
        Show the numeric ACWR value alongside the label.
    """
    s = get_acwr_status(acwr)
    text = s["label"]
    if show_value and acwr is not None:
        text = f"{acwr:.2f} — {s['label']}"

    return html.Span(text, style={
        "display": "inline-flex", "alignItems": "center",
        "padding": "2px 10px", "borderRadius": "9999px",
        "fontSize": "11px", "fontWeight": "600",
        "background": s["bg"], "color": s["text"],
        "whiteSpace": "nowrap",
        # v0.32 — tabular-nums so "1.10" and "1.85" don't jitter width (#26)
        "fontVariantNumeric": "tabular-nums",
    })


# ── Zone Bars (Horizontal, stacked per-zone) ────────────────────────────────

def zone_bars(zones, show_labels=True, show_duration=True, bar_height=16):
    """Horizontal HR zone bars — one bar per zone, like the Firstbeat session card.

    Parameters
    ----------
    zones : dict
        {"zone1": float, "zone2": float, ...} — values in minutes.
    show_labels : bool
        Show "Z1", "Z2", etc. labels on the left.
    show_duration : bool
        Show duration text (e.g. "42.1m") on the right.
    bar_height : int
        Height of each bar in px.
    """
    zones = zones or {}
    max_val = max((zones.get(z["key"], 0) or 0 for z in ZONE_CONFIG), default=1)
    max_val = max(max_val, 0.1)  # avoid division by zero

    rows = []
    for z in ZONE_CONFIG:
        val = zones.get(z["key"], 0) or 0
        pct = max(2, (val / max_val) * 100) if val > 0 else 0

        row_children = []

        if show_labels:
            row_children.append(html.Span(z["label"], style={
                "fontSize": "11px", "fontWeight": "600", "color": SLATE["500"],
                "width": "24px", "flexShrink": "0", "textAlign": "center",
            }))

        # Bar background
        bar_fill = html.Div(style={
            "width": f"{pct:.1f}%", "height": "100%",
            "backgroundColor": z["color"], "borderRadius": f"{bar_height // 2}px",
            "transition": "width 0.3s ease",
            "minWidth": "2px" if val > 0 else "0",
        })
        row_children.append(html.Div([bar_fill], style={
            "flex": "1", "height": f"{bar_height}px",
            "backgroundColor": SLATE["100"], "borderRadius": f"{bar_height // 2}px",
            "overflow": "hidden",
        }))

        if show_duration:
            row_children.append(html.Span(
                f"{val:.0f}m" if val > 0 else "",
                style={
                    "fontSize": "10px", "color": SLATE["400"],
                    "width": "32px", "textAlign": "right", "flexShrink": "0",
                },
            ))

        rows.append(html.Div(row_children, style={
            "display": "flex", "alignItems": "center", "gap": "6px",
        }))

    return html.Div(rows, style={"display": "flex", "flexDirection": "column", "gap": "4px"})


# ── Zone Stacked Bar (Compact inline) ────────────────────────────────────────

def zone_stacked_bar(zones, width=120, height=16):
    """Compact inline stacked bar showing zone distribution.

    Parameters
    ----------
    zones : dict
        {"zone1": float, ...} — values in minutes.
    width : int
        Total bar width in px.
    height : int
        Bar height in px.
    """
    zones = zones or {}
    total = sum(zones.get(z["key"], 0) or 0 for z in ZONE_CONFIG)

    if total <= 0:
        return html.Div(style={
            "width": f"{width}px", "height": f"{height}px",
            "backgroundColor": SLATE["200"], "borderRadius": f"{height // 2}px",
        })

    segments = []
    for z in ZONE_CONFIG:
        val = zones.get(z["key"], 0) or 0
        if val <= 0:
            continue
        pct = (val / total) * 100
        segments.append(html.Div(style={
            "width": f"{max(pct, 1.5):.1f}%", "height": "100%",
            "backgroundColor": z["color"],
        }))

    tooltip = " | ".join(
        f"{z['label']}: {zones.get(z['key'], 0) or 0:.0f}m" for z in ZONE_CONFIG
    )

    return html.Div(segments, title=tooltip, style={
        "display": "flex", "width": f"{width}px", "height": f"{height}px",
        "borderRadius": f"{height // 2}px", "overflow": "hidden",
    })


# ── Metric Trio (HR / TE / TRIMP) ────────────────────────────────────────────

def metric_trio(hr_avg=None, hr_peak=None, aerobic_te=None, anaerobic_te=None,
                trimp=None, hr_avg_pct=None, hr_peak_pct=None):
    """3-column metric display — Heart Rate / Training Effect / TRIMP.

    Matches the Firstbeat session card metric grid pattern.
    """
    def _fmt(v, decimals=0):
        if v is None:
            return "-"
        return f"{v:.{decimals}f}"

    def _metric_cell(icon_class, icon_color, bg_color, values, sub_text):
        return html.Div([
            html.Div([
                html.I(className=icon_class, style={
                    "fontSize": "14px", "color": icon_color, "marginRight": "6px",
                }),
                html.Span(values, style={
                    "fontWeight": "700", "fontSize": "14px", "color": SLATE["800"],
                }),
            ], style={"display": "flex", "alignItems": "center"}),
            html.Div(sub_text, style={
                "fontSize": "10px", "color": SLATE["400"], "marginTop": "2px",
            }),
        ], style={
            "backgroundColor": bg_color, "borderRadius": "8px",
            "padding": "8px 12px",
        })

    # HR sub text
    if hr_avg_pct is not None and hr_peak_pct is not None:
        hr_sub = f"{_fmt(hr_avg_pct)}% / {_fmt(hr_peak_pct)}%"
    else:
        hr_sub = "avg / peak"

    return html.Div([
        _metric_cell(
            "fa-solid fa-heart", "#f87171", "#fef2f2",
            f"{_fmt(hr_avg)} / {_fmt(hr_peak)}",
            hr_sub,
        ),
        _metric_cell(
            "fa-solid fa-bolt", "#10b981", "#ecfdf5",
            f"{_fmt(aerobic_te, 1)} / {_fmt(anaerobic_te, 1)}",
            "aero / anaero",
        ),
        _metric_cell(
            "fa-solid fa-fire", "#f97316", "#fff7ed",
            _fmt(trimp),
            "TRIMP",
        ),
    ], style={
        "display": "grid", "gridTemplateColumns": "1fr 1fr 1fr", "gap": "8px",
    })


# ── Training Session Card ────────────────────────────────────────────────────

def training_card(
    athlete_name, sport, date_str, time_str=None,
    zones=None, hr_avg=None, hr_peak=None,
    aerobic_te=None, anaerobic_te=None, trimp=None,
    hr_avg_pct=None, hr_peak_pct=None,
    acwr=None, duration_min=None, title=None,
    on_click_id=None,
):
    """Complete training session card with zones, metrics, and ACWR badge.

    Parameters
    ----------
    athlete_name : str
    sport : str
    date_str : str
        Formatted date (e.g. "Jan 23, 2026").
    time_str : str or None
        Formatted time range.
    zones : dict or None
        {"zone1": float, ...} in minutes.
    hr_avg, hr_peak : float or None
    aerobic_te, anaerobic_te : float or None
    trimp : float or None
    acwr : float or None
    duration_min : float or None
    title : str or None
        Session title (e.g. "Fencing Training").
    on_click_id : str or None
        If set, makes the card a clickable link target.
    """
    # Header
    header_right = []
    if acwr is not None:
        header_right.append(acwr_badge(acwr))

    session_title = title or sport
    header_children = [
        html.Div([
            html.Div(athlete_name, style={
                "fontWeight": "700", "fontSize": "14px", "color": SLATE["800"],
                "overflow": "hidden", "textOverflow": "ellipsis", "whiteSpace": "nowrap",
            }),
            html.Div([
                html.Span(session_title, style={
                    "fontSize": "12px", "color": SLATE["500"],
                }),
                html.Span(f" - {date_str}", style={
                    "fontSize": "12px", "color": SLATE["400"],
                }),
                html.Span(f" {time_str}", style={
                    "fontSize": "11px", "color": SLATE["400"],
                }) if time_str else None,
            ]),
        ], style={"flex": "1", "minWidth": "0"}),
        html.Div(header_right, style={
            "display": "flex", "alignItems": "flex-start", "gap": "8px",
        }),
    ]

    # Duration badge
    if duration_min is not None:
        dur_text = f"{int(duration_min)}min"
        header_right.insert(0, html.Span(dur_text, style={
            "fontSize": "11px", "fontWeight": "500", "color": SLATE["500"],
            "backgroundColor": SLATE["100"], "padding": "2px 8px",
            "borderRadius": "9999px",
        }))

    children = [
        # Header row
        html.Div(header_children, style={
            "display": "flex", "justifyContent": "space-between",
            "alignItems": "flex-start", "marginBottom": "12px",
        }),
        # Zone bars
        html.Div([
            html.Div("HR ZONES", style={
                "fontSize": "10px", "fontWeight": "600", "color": SLATE["400"],
                "textTransform": "uppercase", "letterSpacing": "0.05em",
                "marginBottom": "6px",
            }),
            zone_bars(zones),
        ], style={"marginBottom": "12px"}),
        # Metrics
        metric_trio(
            hr_avg=hr_avg, hr_peak=hr_peak,
            aerobic_te=aerobic_te, anaerobic_te=anaerobic_te,
            trimp=trimp, hr_avg_pct=hr_avg_pct, hr_peak_pct=hr_peak_pct,
        ),
    ]

    card_style = {
        "background": "white",
        "border": f"1px solid {SLATE['200']}",
        "borderRadius": f"{RADIUS_LG}px",
        "padding": "16px",
        "boxShadow": SHADOW_SM,
        "transition": "box-shadow 0.2s, border-color 0.2s",
    }

    props = {"style": card_style}
    if on_click_id:
        props["id"] = on_click_id

    return html.Div(children, **props)


# ── ACWR Zone Reference Areas (for Plotly charts) ───────────────────────────

ACWR_ZONES = [
    {"y0": 0.0, "y1": 0.8, "color": "#DBEAFE", "label": "Detraining"},
    {"y0": 0.8, "y1": 1.3, "color": "#D1FAE5", "label": "Optimal"},
    {"y0": 1.3, "y1": 1.5, "color": "#FEF3C7", "label": "Caution"},
    {"y0": 1.5, "y1": 2.5, "color": "#FEE2E2", "label": "Danger"},
]


def add_acwr_zones(fig, opacity=0.5):
    """Add ACWR reference zone bands to a Plotly figure."""
    for z in ACWR_ZONES:
        fig.add_hrect(
            y0=z["y0"], y1=z["y1"],
            fillcolor=z["color"], opacity=opacity,
            line_width=0, layer="below",
        )
    return fig
