"""Input controls: toggle_group, filter_bar, dark_mode_toggle, aspire_tabs.

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


__all__ = ['toggle_group', 'filter_bar', 'dark_mode_toggle', 'aspire_tabs']

# ── Toggle Group ─────────────────────────────────────────────────────────────

def toggle_group(toggle_id, options, value=None):
    """Segmented toggle button group (like WHOOP range/mode selector).

    Parameters
    ----------
    toggle_id : str
        Component ID.
    options : list[dict]
        Each dict: {"label": str, "value": str}.
    value : str or None
        Currently active value.
    """
    buttons = []
    for opt in options:
        is_active = opt["value"] == value
        buttons.append(html.Button(
            opt["label"],
            id={"type": f"{toggle_id}-btn", "index": opt["value"]},
            n_clicks=0,
            className=f"toggle-btn {'active' if is_active else ''}",
            style={
                "padding": "4px 10px", "borderRadius": "6px",
                "fontSize": "12px", "fontWeight": "600",
                "color": ACCENT if is_active else SLATE["500"],
                "background": "white" if is_active else "transparent",
                "border": "none", "cursor": "pointer",
                "boxShadow": SHADOW_SM if is_active else "none",
                "fontFamily": FONT_FAMILY,
                "transition": "background-color 150ms ease, color 150ms ease",
            },
        ))
    return html.Div(buttons, className="toggle-group", style={
        "display": "flex", "backgroundColor": SLATE["100"],
        "borderRadius": "8px", "padding": "2px",
    })



# ── Filter Bar ───────────────────────────────────────────────────────────────

def filter_bar(children):
    """White controls bar wrapping filter elements."""
    return html.Div(children, className="controls-bar", style={
        "display": "flex", "alignItems": "center", "gap": "12px",
        "padding": "12px", "background": "white",
        "borderRadius": f"{RADIUS_LG}px", "marginBottom": "12px",
        "boxShadow": SHADOW_SM, "flexWrap": "wrap",
    })



# ── Dark Mode Toggle ────────────────────────────────────────────────────────

def dark_mode_toggle():
    """Dark mode toggle button — place in header right_content.

    Requires dark_mode.js (copied by setup_app). Saves preference to localStorage.
    """
    return html.Button(
        html.I(className="fa-solid fa-moon", style={"fontSize": "14px", "color": SLATE["500"]}),
        id="dark-mode-toggle",
        n_clicks=0,
        style={
            "background": "none", "border": "none", "cursor": "pointer",
            "padding": "8px", "borderRadius": "8px",
            "display": "flex", "alignItems": "center", "justifyContent": "center",
        },
    )



# ── Aspire Tabs ────────────────────────────────────────────────────────────

#: Style dicts for un-selected dcc.Tab. Lift from aspire-budget-dashboard.
TAB_STYLE = {
    "padding": "10px 22px",
    "fontSize": "14px",
    "fontWeight": "500",
    "color": SLATE["500"],
    "background": "transparent",
    "border": "none",
    "borderBottom": "3px solid transparent",
    "transition": "color .15s ease, border-color .15s ease",
}
TAB_SELECTED_STYLE = {
    "padding": "10px 22px",
    "fontSize": "14px",
    "fontWeight": "700",
    "color": ACCENT,
    "background": "transparent",
    "border": "none",
    "borderBottom": f"3px solid {ACCENT}",
}
TABS_PARENT_STYLE = {
    "borderBottom": f"1px solid {SLATE['200']}",
    "marginTop": "8px",
}


def aspire_tabs(id: str, tabs: list[dict], value: str | None = None):
    """Branded ``dcc.Tabs`` with the Aspire-blue underline indicator.

    Replaces hand-rolled TAB_STYLE / TAB_SELECTED_STYLE dicts in every
    app that uses ``dcc.Tabs``. Same Aspire navy + gold accent applies
    via ``ACCENT`` from theme.

    Parameters
    ----------
    id : str
        Component id of the ``dcc.Tabs`` (callbacks read its ``value``).
    tabs : list of dict
        Each dict: ``{"label": str, "value": str}``. Optionally a
        ``"children"`` key for static tab content (otherwise feed
        ``dcc.Tabs`` output into your own router callback).
    value : str or None
        Initial active tab; defaults to first entry's value.
    """
    tab_children = []
    for t in tabs:
        kwargs = {
            "label": t["label"], "value": t["value"],
            "style": TAB_STYLE, "selected_style": TAB_SELECTED_STYLE,
        }
        if "children" in t:
            kwargs["children"] = t["children"]
        tab_children.append(dcc.Tab(**kwargs))
    return dcc.Tabs(
        id=id,
        value=value or (tabs[0]["value"] if tabs else None),
        children=tab_children,
        parent_style=TABS_PARENT_STYLE,
    )


