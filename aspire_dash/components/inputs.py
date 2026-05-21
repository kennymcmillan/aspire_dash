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


__all__ = ['toggle_group', 'mode_toggle', 'filter_bar', 'dark_mode_toggle',
           'aspire_tabs', 'date_picker_single']

# ── Date picker ──────────────────────────────────────────────────────────────

def date_picker_single(picker_id, value=None, *,
                        display_format="D MMM YYYY",
                        width="140px",
                        **kwargs):
    """``dcc.DatePickerSingle`` with a known-good display format.

    ``"D MMM YYYY"`` renders ``19 May 2026``. We don't include ``ddd``
    (day-of-week) because dash's underlying picker silently misparses
    that token into ``dd`` + ``d``, producing ``Tu19 19 May 2026`` —
    a real-world bug we hit and fixed in the fencing planner.

    Parameters
    ----------
    picker_id : str
        Component id for callbacks.
    value : str or date or None
        Initial date — passes straight through to ``date`` prop.
    display_format : str
        Moment.js format string. Defaults to the safe ``D MMM YYYY``.
        Avoid ``ddd`` and ``dd`` tokens (rendering bug). Use ``dddd``
        (full weekday) if you really need a day name.
    width : str
        CSS width.
    **kwargs
        Forwarded to ``dcc.DatePickerSingle``.

    Returns
    -------
    ``dcc.DatePickerSingle``.
    """
    return dcc.DatePickerSingle(
        id=picker_id,
        date=value,
        display_format=display_format,
        style={"fontSize": "12px", "width": width, **kwargs.pop("style", {})},
        **kwargs,
    )


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



# ── Mode Toggle (mutually-exclusive analysis modes) ─────────────────────────

MODE_TOGGLE_COLORS = {
    "navy":    "mode-btn-active-navy",
    "blue":    "mode-btn-active-blue",
    "red":     "mode-btn-active-red",
    "emerald": "mode-btn-active-emerald",
}


def mode_toggle(id_prefix, options, default=None, register_callback=True):
    """Mutually-exclusive button group — exactly one mode active at all times.

    Generalises the SD/MA/Acute/Adaptive overlay toggle from DASH_VALD. Renders
    a row of ``html.Button`` elements plus a backing ``dcc.Store`` that holds
    the currently-active option's ``value``. Subscribe to ``f"{id_prefix}-store"``
    from your chart callback to switch overlays.

    Parameters
    ----------
    id_prefix : str
        Base id. Buttons get ``f"{id_prefix}-btn-{value}"``; store gets
        ``f"{id_prefix}-store"``.
    options : list of dict
        Each: ``{"label": str, "value": str, "color": "navy"|"blue"|"red"|"emerald"}``.
        ``color`` defaults to ``"navy"``.
    default : str or None
        Initial active ``value``. Defaults to the first option's value.
    register_callback : bool
        If True (default), registers the mutex clientside callback inline so the
        caller doesn't have to. Set False for layout-only smoke tests.
    """
    if not options:
        raise ValueError("mode_toggle requires at least one option")

    default = default or options[0]["value"]
    store_id = f"{id_prefix}-store"
    button_ids = [f"{id_prefix}-btn-{opt['value']}" for opt in options]

    buttons = []
    for opt, bid in zip(options, button_ids):
        is_active = opt["value"] == default
        active_class = MODE_TOGGLE_COLORS.get(opt.get("color", "navy"), "mode-btn-active-navy")
        cls = f"mode-btn {active_class}" if is_active else "mode-btn"
        buttons.append(html.Button(opt["label"], id=bid, n_clicks=0, className=cls))

    layout = html.Div([
        html.Div(buttons, className="mode-toggle-group"),
        dcc.Store(id=store_id, data=default),
    ])

    if register_callback:
        _register_mode_toggle_callback(id_prefix, options)

    return layout


def _register_mode_toggle_callback(id_prefix, options):
    """Wire the mutex clientside callback for a mode_toggle."""
    import json
    button_ids = [f"{id_prefix}-btn-{opt['value']}" for opt in options]
    store_id = f"{id_prefix}-store"
    values = [opt["value"] for opt in options]
    value_to_class = {
        opt["value"]: f"mode-btn {MODE_TOGGLE_COLORS.get(opt.get('color', 'navy'), 'mode-btn-active-navy')}"
        for opt in options
    }

    sig = ", ".join(f"c{i}" for i in range(len(options)))
    js = f"""
    function({sig}, currentValue) {{
        const ctx = dash_clientside.callback_context;
        const VALUES = {json.dumps(values)};
        const BUTTON_IDS = {json.dumps(button_ids)};
        const VALUE_TO_CLASS = {json.dumps(value_to_class)};

        let activeValue = currentValue || VALUES[0];
        if (ctx.triggered && ctx.triggered.length > 0) {{
            const tid = ctx.triggered[0].prop_id.split(".")[0];
            const idx = BUTTON_IDS.indexOf(tid);
            if (idx >= 0) activeValue = VALUES[idx];
        }}

        const classes = VALUES.map(v =>
            v === activeValue ? VALUE_TO_CLASS[v] : "mode-btn"
        );
        return [...classes, activeValue];
    }}
    """

    clientside_callback(
        js,
        [Output(bid, "className") for bid in button_ids] + [Output(store_id, "data")],
        [Input(bid, "n_clicks") for bid in button_ids],
        [State(store_id, "data")],
    )


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


