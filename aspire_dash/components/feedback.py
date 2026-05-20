"""Feedback UI: toast, badge, empty_state, loading_overlay, status_pill, freshness_banner, confirm_modal.

Auto-split from the legacy single-file components.py during the
0.8 → 1.0 refactor. Backwards-compatible: `from aspire_dash.components
import X` keeps working via the package __init__.
"""
import dash
from dash import html, dcc, clientside_callback, Input, Output, State
import dash_bootstrap_components as dbc

from ..theme import (
    SIDEBAR_WIDTH, SIDEBAR_BG, SIDEBAR_BORDER, SIDEBAR_LINK_COLOR,
    SIDEBAR_LINK_HOVER_BG, SIDEBAR_LINK_ACTIVE_BG,
    FONT_FAMILY, ACCENT, ACCENT_HOVER,
    LOGO_FILENAME, LOGO_ALT, SLATE, ASPIRE,
    SHADOW_SM, SHADOW_MD, RADIUS_LG, RADIUS_FULL,
)


__all__ = ['toast', 'badge', 'empty_state', 'loading_overlay', 'status_pill',
            'freshness_banner', 'confirm_modal', 'rate_limit_banner']

# ── Toast ────────────────────────────────────────────────────────────────────

TOAST_STYLE = {"position": "fixed", "top": 66, "right": 10, "width": 350, "zIndex": 9999}


def toast(toast_id: str):
    """Standard toast notification — fixed top-right."""
    return dbc.Toast(
        id=toast_id, header="", is_open=False, dismissable=True,
        duration=3000, style=TOAST_STYLE,
    )



# ── Badge ────────────────────────────────────────────────────────────────────

def badge(text, color="gray", pill=True):
    """Pill badge with semantic colour."""
    color_map = {
        "gray": {"bg": "#f3f4f6", "color": "#475569"},
        "blue": {"bg": "#dbeafe", "color": "#1e40af"},
        "green": {"bg": "#dcfce7", "color": "#166534"},
        "red": {"bg": "#fee2e2", "color": "#991b1b"},
        "amber": {"bg": "#fef3c7", "color": "#92400e"},
        "teal": {"bg": "#ccfbf1", "color": "#115e59"},
    }
    c = color_map.get(color, color_map["gray"])
    return html.Span(text, style={
        "display": "inline-flex", "alignItems": "center",
        "padding": "2px 10px",
        "borderRadius": f"{RADIUS_FULL}px" if pill else "6px",
        "fontSize": "11px", "fontWeight": "600",
        "background": c["bg"], "color": c["color"],
    })



# ── Empty State ──────────────────────────────────────────────────────────────

def empty_state(icon="fa-solid fa-inbox", text="No data found", hint=""):
    """Centered empty state with icon, text, and hint."""
    return html.Div([
        html.Div(html.I(className=icon), className="empty-state-icon",
                 style={"fontSize": "48px", "marginBottom": "12px", "opacity": "0.5"}),
        html.Div(text, style={"fontSize": "15px", "fontWeight": "500"}),
        html.Div(hint, style={"fontSize": "13px", "color": "#d1d5db", "marginTop": "4px"}) if hint else None,
    ], className="empty-state", style={
        "display": "flex", "flexDirection": "column",
        "alignItems": "center", "justifyContent": "center",
        "padding": "60px 24px", "color": "#9ca3af", "textAlign": "center",
    })



# ── Loading overlay ─────────────────────────────────────────────────────────

def loading_overlay(children, color: str = "#004185", overlay_opacity: float = 0.4,
                    z_index: int = 999):
    """Aspire-branded centered spinner overlay.

    Wraps `children` in a `dcc.Loading` configured to match the SAMS Attendance
    Dashboard pattern: centered fixed spinner over a translucent white scrim,
    aspire-blue stroke. Use this around `dcc.Store` + `page_container` so the
    spinner shows during slow data fetches, not just page renders.

    Example::

        from aspire_dash.components import loading_overlay
        app.layout = html.Div([
            ...
            loading_overlay([
                dcc.Store(id='my-data'),
                page_container,
            ]),
        ])

    Why wrap the Store inside? `dcc.Loading` only triggers on Outputs *inside*
    its children. If your slow callback's Output is a `dcc.Store` outside the
    Loading, the spinner doesn't show during the fetch — only during the
    downstream render. Putting the Store inside fixes that.
    """
    return dcc.Loading(
        children,
        type="circle",
        color=color,
        style={"position": "fixed", "top": "50%", "left": "50%",
               "transform": "translate(-50%, -50%)", "zIndex": str(z_index)},
        overlay_style={"visibility": "visible", "opacity": overlay_opacity,
                       "backgroundColor": "white"},
    )



# ── Status Pill ─────────────────────────────────────────────────────────────

#: Status → (background, foreground) palette using Aspire tokens.
#: Lifted from sams-attendance-dashboard and medical-dashboard, where
#: every page reimplemented its own Active/Inactive/Injured pill.
STATUS_PILL_PALETTE = {
    "current":    ("#dcfce7", "#166534"),  # green — fresh / available / present
    "active":     ("#dcfce7", "#166534"),
    "available":  ("#dcfce7", "#166534"),
    "present":    ("#dcfce7", "#166534"),
    "ok":         ("#dcfce7", "#166534"),
    "stale":      ("#fef3c7", "#92400e"),  # amber — warn / pending / on leave
    "warning":    ("#fef3c7", "#92400e"),
    "pending":    ("#fef3c7", "#92400e"),
    "on_leave":   ("#fef3c7", "#92400e"),
    "absent":     ("#fee2e2", "#991b1b"),  # red — silent / injured / risk
    "silent":     ("#fee2e2", "#991b1b"),
    "injured":    ("#fee2e2", "#991b1b"),
    "sidelined":  ("#fee2e2", "#991b1b"),
    "high_risk":  ("#fee2e2", "#991b1b"),
    "inactive":   ("#f1f5f9", "#475569"),  # slate — neutral / retired / archived
    "neutral":    ("#f1f5f9", "#475569"),
    "retired":    ("#f1f5f9", "#475569"),
    "archived":   ("#f1f5f9", "#475569"),
}


def status_pill(
    status: str | None,
    label: str | None = None,
    palette: dict | None = None,
    size: str = "md",
):
    """Coloured pill for state values (Active / Injured / Sidelined / ...).

    Parameters
    ----------
    status : str or None
        Status key — looked up in ``palette`` (defaults to
        ``STATUS_PILL_PALETTE``). Case-insensitive; spaces and dashes
        treated as underscores. Unknown values fall back to neutral slate.
    label : str or None
        Visible text. Defaults to a Title-Cased ``status``.
    palette : dict or None
        Override palette mapping ``key → (bg_hex, fg_hex)``. Useful for
        domain-specific colours (e.g. injury severity bands).
    size : "sm" | "md" | "lg"
        Visual density.

    Example::

        status_pill("active")        # green pill "Active"
        status_pill("on_leave")      # amber pill "On Leave"
        status_pill("injured", "Injured · 14d")  # red pill, custom label
    """
    key = (status or "").strip().lower().replace(" ", "_").replace("-", "_")
    pal = palette or STATUS_PILL_PALETTE
    bg, fg = pal.get(key, ("#f1f5f9", "#475569"))
    text = label if label is not None else (status or "—").replace("_", " ").title()
    size_map = {
        "sm": ("10px", "2px 8px"),
        "md": ("11px", "3px 10px"),
        "lg": ("13px", "5px 14px"),
    }
    font_size, padding = size_map.get(size, size_map["md"])
    return html.Span(
        text,
        style={
            "display": "inline-flex", "alignItems": "center",
            "background": bg, "color": fg,
            "padding": padding,
            "borderRadius": "999px",
            "fontSize": font_size, "fontWeight": "600",
            "fontVariantNumeric": "tabular-nums",
            "lineHeight": "1.2",
            "whiteSpace": "nowrap",
        },
    )



# ── Freshness Banner ────────────────────────────────────────────────────────

#: Default thresholds (in days) for the freshness classifier.
FRESHNESS_THRESHOLDS = {"fresh": 7, "stale": 30}


def _freshness_status(days: int | float | None) -> str:
    """Classify days-since-last-log into 'current' / 'stale' / 'silent'."""
    if days is None or days >= 9999:
        return "silent"
    try:
        d = float(days)
    except (TypeError, ValueError):
        return "silent"
    if d <= FRESHNESS_THRESHOLDS["fresh"]:
        return "current"
    if d <= FRESHNESS_THRESHOLDS["stale"]:
        return "stale"
    return "silent"


def freshness_banner(
    rows,
    label: str = "Data freshness",
    sort: str = "worst_first",
    empty_text: str = "No data available",
):
    """One-line banner with one chip per source, coloured by recency.

    Lifted from medical-dashboard. The same pattern fits nutrition's
    multi-sport diary freshness, training plan freshness, scraper
    freshness — anywhere a dashboard needs a visible "logging is
    healthy" signal.

    Parameters
    ----------
    rows : iterable of dict
        Each row: ``{"label": str, "days": int | None, "status": str | None}``.
        - ``label``: the chip text prefix (sport, scraper name, etc.)
        - ``days``: days since last update (None / 9999 = never)
        - ``status``: optional manual override; if omitted, derived from days
    label : str
        Eyebrow text on the left.
    sort : "worst_first" | "best_first" | "as_is"
        Chip ordering. Default sorts staler items left.
    empty_text : str
        Shown when ``rows`` is empty.
    """
    rows = list(rows or [])
    if not rows:
        chips = [html.Span(empty_text, style={"color": SLATE["500"]})]
    else:
        if sort == "worst_first":
            rows = sorted(rows, key=lambda r: -(r.get("days") or 0))
        elif sort == "best_first":
            rows = sorted(rows, key=lambda r: (r.get("days") or 0))
        chips = []
        for r in rows:
            days = r.get("days")
            status = r.get("status") or _freshness_status(days)
            bg, fg = STATUS_PILL_PALETTE.get(status, ("#e2e8f0", "#334155"))
            if days is None or days >= 9999:
                txt = f"{r.get('label', '—')} · never"
            else:
                txt = f"{r.get('label', '—')} · {int(days)}d ago"
            chips.append(html.Div(txt, style={
                "background": bg, "color": fg,
                "padding": "4px 10px", "borderRadius": "999px",
                "fontSize": "12px", "fontWeight": "600",
                "marginRight": "8px", "display": "inline-block",
                "fontVariantNumeric": "tabular-nums",
            }))

    return html.Div([
        html.Span(label.upper(), style={
            "fontSize": "11px", "fontWeight": "700",
            "color": SLATE["500"], "letterSpacing": "0.4px",
            "marginRight": "12px",
        }),
        *chips,
    ], style={
        "background": "white",
        "border": f"1px solid {SLATE['200']}",
        "borderRadius": f"{RADIUS_LG}px",
        "padding": "10px 16px",
        "marginBottom": "16px",
        "display": "flex", "alignItems": "center", "flexWrap": "wrap",
        "boxShadow": SHADOW_SM,
    })



# ── Confirm modal ──────────────────────────────────────────────────────────

def confirm_modal(
    id: str,
    title: str = "Confirm action",
    body: object = "Are you sure?",
    confirm_label: str = "Confirm",
    cancel_label: str = "Cancel",
    confirm_color: str = "danger",
    icon: str = "fa-solid fa-triangle-exclamation",
):
    """Standard confirm/cancel modal used by delete + destructive flows.

    Renders a ``dbc.Modal`` with ID ``id`` and two buttons:
    - ``{id}-confirm`` — the destructive button (Input this in your callback)
    - ``{id}-cancel`` — closes the modal

    Toggle ``is_open`` from your own callback when the trigger fires.

    Example::

        # Layout
        confirm_modal("delete-diary", title="Delete diary?",
                      body="This will soft-delete every row from 12 May.",
                      confirm_label="Delete")

        # Callback
        @callback(Output("delete-diary", "is_open"),
                  Input("row-delete-btn", "n_clicks"),
                  Input("delete-diary-confirm", "n_clicks"),
                  Input("delete-diary-cancel", "n_clicks"),
                  State("delete-diary", "is_open"),
                  prevent_initial_call=True)
        def _toggle(open_n, confirm_n, cancel_n, is_open):
            return not is_open
    """
    header_el = html.Div([
        html.I(className=icon, style={
            "color": "#d97706" if confirm_color in ("warning", "danger") else ASPIRE["600"],
            "marginRight": "10px",
        }),
        html.Strong(title),
    ], style={"display": "flex", "alignItems": "center"})

    return dbc.Modal([
        dbc.ModalHeader(header_el, close_button=True),
        dbc.ModalBody(body),
        dbc.ModalFooter([
            dbc.Button(cancel_label, id=f"{id}-cancel", color="light", n_clicks=0),
            dbc.Button(confirm_label, id=f"{id}-confirm",
                       color=confirm_color, n_clicks=0,
                       style={"marginLeft": "8px"}),
        ]),
    ], id=id, is_open=False, centered=True, backdrop="static")




# ── Rate-limit banner ────────────────────────────────────────────────────────

def rate_limit_banner(
    banner_id: str = "rate-limit-banner",
    visible: bool = False,
    message: str = "API rate limit reached — some data may be delayed.",
):
    """Sticky-top amber banner shown when a backend API rate-limits us.

    Wire to `aspire_dash.observability.get_metrics()` counter on a polling
    callback (or update `is_open` from the callback that catches the 429)::

        from aspire_dash.observability import get_metrics

        @callback(Output("rate-limit-banner", "style"),
                  Input("rate-limit-tick", "n_intervals"))
        def _show_banner(_):
            recent_429s = get_metrics().get("vald.429", 0)
            return {"display": "flex"} if recent_429s else {"display": "none"}

    Args:
        banner_id: component id so callbacks can toggle visibility.
        visible:   initial show state (default False).
        message:   text content; override per-app to match the upstream.
    """
    return html.Div(
        [
            html.I(className="fa-solid fa-triangle-exclamation",
                    style={"marginRight": "6px"}),
            html.Span(message),
        ],
        id=banner_id,
        className="rate-limit-banner",
        style={
            "display": "flex" if visible else "none",
            "alignItems": "center", "justifyContent": "center",
            "background": "#fef3c7", "color": "#92400e",
            "borderBottom": "1px solid #fbbf24",
            "padding": "8px 16px", "fontSize": "13px", "fontWeight": "500",
            "position": "sticky", "top": "0", "zIndex": "60", "gap": "8px",
        },
    )
