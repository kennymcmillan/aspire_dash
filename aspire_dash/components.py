"""Reusable Dash components — sidebar, topnav, header, cards, toast, badges."""

import dash
from dash import html, dcc, clientside_callback, Input, Output, State
import dash_bootstrap_components as dbc
from .theme import (
    SIDEBAR_WIDTH, SIDEBAR_BG, SIDEBAR_BORDER, SIDEBAR_LINK_COLOR,
    SIDEBAR_LINK_HOVER_BG, SIDEBAR_LINK_ACTIVE_BG,
    FONT_FAMILY, ACCENT, ACCENT_HOVER,
    LOGO_FILENAME, LOGO_ALT, SLATE, ASPIRE,
    SHADOW_SM, SHADOW_MD, RADIUS_LG, RADIUS_FULL,
)


# ── Top Nav ──────────────────────────────────────────────────────────────────

def topnav(
    nav_items: list[dict],
    title: str = "",
    logo_src: str | None = None,
    right_content=None,
):
    """Horizontal sticky top-navigation bar — alternative to sidebar() for full-width layouts.

    Parameters
    ----------
    nav_items : list[dict]
        Each dict: ``{"label": str, "href": str, "icon": str (FA class), "id": str}``.
        ``id`` is used by ``register_topnav_active`` to set the active class.
    title : str
        App name shown right of the logo.
    logo_src : str or None
        Logo image src.  Use ``dash.get_relative_path("/assets/aspire_logo.png")``
        so the path resolves correctly on Posit Connect (app runs under a URL prefix).
    right_content : Component or None
        Optional element placed at the far right (e.g. a date badge).

    CSS
    ---
    Add the topnav CSS to your app's ``assets/overrides.css``::

        .topnav-link { ... }
        .topnav-link:hover { ... }
        .topnav-link.active { background: #004185; color: white; }

    Or install the aspire_dash base CSS (via ``setup_app``) — it includes
    ``.topnav-link`` rules automatically from v0.2.0 onwards.

    Pair with ``register_topnav_active(app, nav_items)`` to highlight the
    active page link on navigation.
    """
    nav_links = []
    for item in nav_items:
        nav_links.append(
            dcc.Link(
                html.Div(
                    [
                        html.I(className=item.get("icon", ""),
                               style={"marginRight": "6px", "fontSize": "12px"}),
                        html.Span(item["label"]),
                    ],
                    className="topnav-link",
                    id=item.get("id", ""),
                ),
                href=dash.get_relative_path(item["href"]),
                style={"textDecoration": "none"},
            )
        )

    left = html.Div(
        [
            html.Img(src=logo_src, style={"height": "30px", "width": "auto"}) if logo_src else None,
            html.Span(title, style={
                "fontWeight": "700", "fontSize": "15px",
                "color": "#1e293b", "marginLeft": "10px" if logo_src else "0",
            }) if title else None,
        ],
        style={"display": "flex", "alignItems": "center", "flexShrink": "0"},
    )

    centre = html.Div(nav_links,
                      style={"display": "flex", "gap": "4px", "alignItems": "center"})

    right = html.Div(
        right_content,
        style={"flexShrink": "0"},
    ) if right_content else html.Div(style={"flexShrink": "0"})

    return html.Div(
        [left, centre, right],
        style={
            "display": "flex", "justifyContent": "space-between",
            "alignItems": "center", "padding": "10px 24px",
            "borderBottom": "1px solid #dbeafe", "background": "#f5f9ff",
            "gap": "24px",
        },
    )


def register_topnav_active(app, nav_items: list[dict], url_id: str = "url"):
    """Register the clientside callback that highlights the active topnav link.

    Parameters
    ----------
    app : Dash
        The Dash app instance.
    nav_items : list[dict]
        Same list passed to ``topnav()`` — must include ``"href"`` and ``"id"`` keys.
    url_id : str
        ID of the ``dcc.Location`` component (default ``"url"``).

    Usage
    -----
    Call once in your ``create_app()`` after ``_register_callbacks``::

        from aspire_dash.components import topnav, register_topnav_active

        register_topnav_active(app, NAV_ITEMS)
    """
    link_ids = [item["id"] for item in nav_items]
    path_map  = {item["href"]: item["id"] for item in nav_items}
    url_prefix = dash.get_relative_path("/")

    clientside_callback(
        """
        function(pathname) {
            const linkMap = """ + str(path_map).replace("'", '"') + """;
            const allIds  = """ + str(link_ids).replace("'", '"') + """;
            const prefix  = """ + '"' + url_prefix + '"' + """;
            let relPath = pathname;
            if (prefix !== "/" && pathname.startsWith(prefix)) {
                relPath = "/" + pathname.slice(prefix.length);
            }
            let activeId = linkMap[relPath] || null;
            if (!activeId) {
                for (const [path, id] of Object.entries(linkMap)) {
                    if (path !== "/" && relPath.startsWith(path)) { activeId = id; break; }
                }
            }
            allIds.forEach(id => {
                const el = document.getElementById(id);
                if (!el) return;
                el.className = (id === activeId) ? "topnav-link active" : "topnav-link";
            });
            return window.dash_clientside.no_update;
        }
        """,
        Output(url_id, "search"),
        Input(url_id, "pathname"),
    )


# ── Sidebar ──────────────────────────────────────────────────────────────────

def sidebar(
    title: str,
    subtitle: str = "Aspire Academy",
    nav_items: list[dict] | None = None,
    logo_gradient: tuple[str, str] = ("#004185", "#0059b3"),
    footer: object = None,
    logo_src: str | None = None,
):
    """Collapsible sidebar with hamburger toggle (standard for all apps).

    Parameters
    ----------
    title : str
        App name shown in the logo section.
    subtitle : str
        Shown below the title (default: "Aspire Academy").
    nav_items : list[dict]
        Each dict: {"label": str, "href": str, "icon": str (FA class), "section": str (optional)}.
        When "section" changes, a divider + section label is inserted.
    logo_gradient : tuple
        Two hex colours for the gradient icon box.
    footer : Component or None
        Optional footer element at bottom of sidebar.
    logo_src : str | None
        Logo image src. When deploying to Posit Connect, callers should
        pass ``dash.get_relative_path("/assets/aspire-logo.png")`` so the
        path is prefixed with the Connect content GUID. Defaults to the
        absolute ``/assets/<LOGO_FILENAME>`` for back-compat with apps
        that haven't migrated yet (works locally, breaks on Connect).
    """
    nav_items = nav_items or []

    # Build navigation links
    nav_children = []
    current_section = None
    for item in nav_items:
        section = item.get("section")
        if section and section != current_section:
            if current_section is not None:
                nav_children.append(html.Div(className="sidebar-divider"))
            nav_children.append(
                html.Div(section, className="sidebar-section-label")
            )
            current_section = section

        icon_el = html.I(className=item.get("icon", "fa-solid fa-circle"), style={
            "width": "16px", "textAlign": "center", "fontSize": "13px", "marginRight": "10px",
        })
        nav_children.append(
            dcc.Link(
                [icon_el, item["label"]],
                href=item["href"],
                className="sidebar-link",
            )
        )

    sidebar_el = html.Div([
        # Logo
        html.Div([
            html.Div([
                html.Img(
                    src=logo_src or f"/assets/{LOGO_FILENAME}",
                    style={"height": "32px", "width": "auto"},
                ),
            ], style={
                "background": f"linear-gradient(to bottom right, {logo_gradient[0]}, {logo_gradient[1]})",
                "padding": "8px", "borderRadius": "8px",
                "display": "flex", "alignItems": "center", "justifyContent": "center",
            }),
            html.Div([
                html.Div(title, className="sidebar-logo-title", style={
                    "fontSize": "18px", "fontWeight": "700", "color": "white", "lineHeight": "1.2",
                }),
                html.Div(subtitle, style={
                    "fontSize": "13px", "color": "rgba(255,255,255,0.7)", "fontWeight": "400",
                }),
            ]),
        ], className="sidebar-logo", style={
            "padding": "16px", "borderBottom": f"1px solid {SIDEBAR_BORDER}",
            "display": "flex", "alignItems": "center", "gap": "12px",
        }),

        # Navigation
        html.Div(nav_children, className="sidebar-nav", style={
            "flex": "1", "overflowY": "auto", "padding": "16px",
        }),

        # Footer
        html.Div(footer, style={
            "padding": "12px 16px", "borderTop": f"1px solid {SIDEBAR_BORDER}",
            "marginTop": "auto",
        }) if footer else None,
    ], id="sidebar", className="sidebar")

    return sidebar_el


def hamburger_button():
    """Hamburger toggle button — place in the header."""
    return html.Button(
        html.I(className="fa-solid fa-bars", style={"fontSize": "16px", "color": SLATE["600"]}),
        id="sidebar-toggle",
        n_clicks=0,
        style={
            "background": "none", "border": "none", "cursor": "pointer",
            "padding": "8px", "borderRadius": "8px",
            "display": "flex", "alignItems": "center", "justifyContent": "center",
        },
    )


def register_sidebar_toggle(app):
    """Register the clientside callback for sidebar collapse. Call once in app.py."""
    clientside_callback(
        """
        function(n) {
            const sidebar = document.getElementById('sidebar');
            const main = document.getElementById('main-area');
            if (!sidebar || !main) return window.dash_clientside.no_update;
            sidebar.classList.toggle('sidebar-collapsed');
            main.classList.toggle('main-area-expanded');
            return window.dash_clientside.no_update;
        }
        """,
        Output("sidebar-toggle-dummy", "children"),
        Input("sidebar-toggle", "n_clicks"),
        prevent_initial_call=True,
    )


# ── Header ───────────────────────────────────────────────────────────────────

def header(title: str = "", subtitle: str = "", right_content=None):
    """Sticky header with backdrop blur. Include hamburger_button() in left content."""
    left = html.Div([
        hamburger_button(),
        html.Div([
            html.Div(title, style={
                "fontSize": "18px", "fontWeight": "600", "color": SLATE["800"],
            }) if title else None,
            html.Div(subtitle, style={
                "fontSize": "12px", "color": SLATE["400"], "marginTop": "1px",
            }) if subtitle else None,
        ]),
    ], style={"display": "flex", "alignItems": "center", "gap": "12px"})

    return html.Div([
        left,
        html.Div(right_content) if right_content else html.Div(),
    ], className="header", style={
        "display": "flex", "alignItems": "center", "justifyContent": "space-between",
        "padding": "12px 24px",
        "background": "rgba(255,255,255,0.95)",
        "borderBottom": f"1px solid {SLATE['100']}",
        "position": "sticky", "top": "0", "zIndex": "50",
        "backdropFilter": "blur(8px)", "WebkitBackdropFilter": "blur(8px)",
    })


# ── Cards ────────────────────────────────────────────────────────────────────

def card(children, className="", style=None, **kwargs):
    """Standard white card — 12px radius, shadow-sm."""
    base_style = {
        "background": "white",
        "borderRadius": f"{RADIUS_LG}px",
        "padding": "16px",
        "marginBottom": "24px",
        "boxShadow": SHADOW_SM,
    }
    if style:
        base_style.update(style)
    return html.Div(children, className=f"card {className}".strip(), style=base_style, **kwargs)


def summary_card(label, value, sub=None, icon=None, color_class=""):
    """KPI summary card (label + big value + optional subtitle)."""
    icon_el = html.I(className=icon, style={
        "fontSize": "12px", "marginRight": "4px",
    }) if icon else None

    return html.Div([
        html.Div([icon_el, label] if icon_el else label, className="card-label", style={
            "fontSize": "12px", "fontWeight": "500", "textTransform": "uppercase",
            "letterSpacing": "0.3px", "color": SLATE["500"], "marginBottom": "4px",
            "display": "flex", "alignItems": "center", "gap": "4px",
        }),
        html.Div(str(value), className="card-value", style={
            "fontSize": "22px", "fontWeight": "700", "color": SLATE["800"],
            "letterSpacing": "-0.02em", "fontVariantNumeric": "tabular-nums",
        }),
        html.Div(sub, className="card-sub", style={
            "fontSize": "12px", "color": SLATE["400"], "marginTop": "2px",
        }) if sub else None,
    ], className=f"budget-card {color_class}".strip(), style={
        "background": "white",
        "border": f"1px solid {SLATE['200']}",
        "borderRadius": "8px",
        "padding": "16px 20px",
        "boxShadow": "0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.03)",
        "transition": "box-shadow 0.2s",
    })


# ── KPI Tile ────────────────────────────────────────────────────────────────

def kpi_tile(label, value, unit="", color=None, target=None, size="lg",
             md_col=3, className="mb-2"):
    """KPI tile: uppercase label · big value · unit subtitle · optional
    vs-target progress bar with band coloring.

    Used for metric strips (calories / mph / kg / pct), dashboard KPI
    rows, and the macro-totals card on data-bound pages.

    Parameters
    ----------
    label : str
        Uppercase title (e.g. "Energy", "Protein").
    value : float | int | None
        The big number. None renders as "—".
    unit : str
        Right of the number (e.g. "kcal", "g", "mg"). Also shown in
        the target-comparison subtitle when target is provided.
    color : str
        Hex/CSS color for the left-stripe accent + value text. Falls
        back to ASPIRE_BLUE if not supplied.
    target : dict | None
        Optional vs-target context. Shape:
            {target_value | target_resolved_target,  # absolute target
             pct_of_target,                          # already-computed %
             band: "in" | "below" | "above"}
        When present, the tile gets a progress bar + a "X% of target"
        subtitle colored by band_color(band).
    size : "lg" | "sm"
        Visual density. lg = 1.8rem value, sm = 1.4rem value.
    md_col : int
        Bootstrap col width within a dbc.Row (1-12). Default 3 = 4-up.
    className : str
        Extra classes on the wrapping Col.

    Returns a dbc.Col so the tiles slot into a dbc.Row directly.
    """
    from aspire_dash.theme import band_color, ASPIRE_BLUE  # local — avoid cycle

    accent = color or ASPIRE_BLUE
    value_text_size = "1.8rem" if size == "lg" else "1.4rem"
    label_text_size = "0.7rem" if size == "lg" else "0.65rem"
    padding         = "12px 16px" if size == "lg" else "8px 12px"
    border_width    = "4px" if size == "lg" else "3px"
    border_radius   = "8px" if size == "lg" else "6px"

    bar = None
    sub = html.Div(unit, className="text-muted small",
                   style={"fontSize": label_text_size})

    has_target = bool(target) and (target.get("target_resolved_target")
                                   or target.get("target_value"))
    if has_target and value:
        tgt_val = (target.get("target_resolved_target")
                   or target.get("target_value"))
        band = (target.get("band") or "").lower()
        pct = target.get("pct_of_target")
        bc_hex = band_color(band, as_hex=True)
        bc_bs  = band_color(band)
        bar = dbc.Progress(
            value=min(100, (value / tgt_val) * 100) if tgt_val else 0,
            style={"height": "5px", "marginTop": "6px"},
            color=bc_bs,
        )
        pct_txt = (f"{pct:.0f}% of target" if pct is not None
                   else f"{value/tgt_val*100:.0f}% of {tgt_val:,.0f}{unit}")
        sub = html.Div([
            html.Span(unit), html.Span(" · "),
            html.Span(pct_txt, style={"color": bc_hex, "fontWeight": "600"}),
        ], className="text-muted small")

    return dbc.Col(html.Div([
        html.Div(label, className="text-muted small",
                 style={"textTransform": "uppercase",
                        "letterSpacing": "0.5px",
                        "fontSize": label_text_size}),
        html.Div(f"{value:,.0f}" if value else "—",
                 style={"fontSize": value_text_size,
                        "fontWeight": "700",
                        "color": accent, "lineHeight": "1.1"}),
        sub,
        bar,
    ], style={"padding": padding,
              "background": "white",
              "border": f"1px solid {SLATE['200']}",
              "borderRadius": border_radius,
              "borderLeft": f"{border_width} solid {accent}",
              "height": "100%"}),
        md=md_col, className=className)


def kpi_strip(metrics, *, size="lg", colors=None):
    """One-line convenience for a KPI row from a plain dict.

    Each entry in `metrics` is one of:
        {"label": "Energy", "value": 1971, "unit": "kcal"}            # 3-key
        ("Energy", 1971, "kcal")                                       # tuple

    `colors` is an optional dict mapping label.lower() -> color hex.
    Defaults to ASPIRE_BLUE for every tile.

    Example:
        kpi_strip([
            {"label": "Athletes", "value": 142,  "unit": ""},
            {"label": "Sports",   "value": 7,    "unit": ""},
            {"label": "Diaries",  "value": 1042, "unit": "this year"},
            {"label": "Avg kcal", "value": 2104, "unit": "kcal/day"},
        ])
    """
    from aspire_dash.theme import ASPIRE_BLUE
    colors = colors or {}
    specs = []
    for m in metrics:
        if isinstance(m, dict):
            label = m["label"]
            value = m.get("value")
            unit = m.get("unit", "")
        elif isinstance(m, tuple):
            if len(m) == 3:
                label, value, unit = m
            elif len(m) == 2:
                label, value = m
                unit = ""
            else:
                raise ValueError(f"kpi_strip tuple must be (label, value[, unit]): {m!r}")
        else:
            raise ValueError(f"kpi_strip entry must be dict or tuple: {m!r}")
        color = colors.get(label.lower(), ASPIRE_BLUE)
        specs.append((label, value, unit, color))
    return kpi_tile_row(specs, size=size)


def kpi_tile_row(specs, target_by_key=None, size="lg", className="g-2"):
    """Render a row of kpi_tile() components from a spec list.

    Each spec is a tuple:
        (label, key, value, unit, color)        # 5-tuple, with target lookup
        (label, value, unit, color)             # 4-tuple, no target lookup

    target_by_key : dict[str, dict] | None
        Maps key -> target dict (see kpi_tile docstring). Only used
        for 5-tuple specs.
    """
    by_key = target_by_key or {}
    cols = []
    for spec in specs:
        if len(spec) == 5:
            label, key, value, unit, color = spec
        elif len(spec) == 4:
            label, value, unit, color = spec
            key = None
        else:
            raise ValueError(f"kpi_tile_row spec must be 4 or 5 elements: {spec!r}")
        target = by_key.get((key or "").lower()) if key else None
        cols.append(kpi_tile(label, value, unit, color, target=target, size=size))
    return dbc.Row(cols, className=className)


# ── Graph Card ──────────────────────────────────────────────────────────────

def graph_card(figure, config=None, title=None, style=None, **graph_kwargs):
    """Wrap a dcc.Graph in a card with rounded corners, border, and shadow.

    Parameters
    ----------
    figure : plotly.graph_objects.Figure
        The Plotly figure to render.
    config : dict or None
        dcc.Graph config (modebar settings, etc.).
    title : str or None
        Optional title above the chart.
    style : dict or None
        Extra style overrides for the card container.
    **graph_kwargs
        Additional kwargs passed to dcc.Graph (e.g. id, className).
    """
    card_style = {
        "background": "white",
        "borderRadius": f"{RADIUS_LG}px",
        "border": f"1px solid {SLATE['200']}",
        "boxShadow": SHADOW_MD,
        "padding": "12px",
        "marginBottom": "16px",
        "overflow": "hidden",
    }
    if style:
        card_style.update(style)

    children = []
    if title:
        children.append(html.Div(title, style={
            "fontSize": "14px", "fontWeight": "600", "color": SLATE["700"],
            "padding": "4px 4px 8px",
        }))
    children.append(dcc.Graph(figure=figure, config=config or {}, **graph_kwargs))

    return html.Div(children, style=card_style)


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


# ── Info Box ─────────────────────────────────────────────────────────────────

def info_box(title, children, icon="fa-solid fa-circle-info"):
    """Blue info/tip box (like the Budget app status guide)."""
    return html.Div([
        html.Div([
            html.I(className=icon, style={"color": "#3b82f6", "marginRight": "8px"}),
            html.Strong(title, style={"color": "#1e40af"}),
        ], style={"display": "flex", "alignItems": "center", "marginBottom": "8px"}),
        html.Div(children),
    ], style={
        "background": "#eff6ff", "border": "1px solid #bfdbfe",
        "borderRadius": "8px", "padding": "12px 16px", "marginBottom": "16px",
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


# ── Print Header/Footer ─────────────────────────────────────────────────────

def print_header(title="", subtitle="", logo_src="/assets/aspire-logo.png"):
    """Header shown only when printing — hidden on screen."""
    return html.Div([
        html.Div([
            html.Img(src=logo_src, style={"height": "24px"}),
            html.Span(title, style={"fontWeight": "700", "fontSize": "14px", "marginLeft": "8px"}),
        ], style={"display": "flex", "alignItems": "center"}),
        html.Span(subtitle, style={"fontSize": "11px", "color": SLATE["500"]}),
    ], className="print-header")


def print_footer(text="Aspire Academy — Confidential"):
    """Footer shown only when printing — hidden on screen."""
    return html.Div(text, className="print-footer")


# ── Export Buttons ──────────────────────────────────────────────────────────

def export_buttons(export_id="data-export", csv=True, excel=True, style=None):
    """CSV/Excel export buttons with a shared dcc.Download.

    Parameters
    ----------
    export_id : str
        Base ID. Buttons get ``{export_id}-csv`` and ``{export_id}-xlsx``;
        the Download component gets ``{export_id}-download``.
    csv : bool
        Show the CSV button (default True).
    excel : bool
        Show the Excel button (default True).
    style : dict or None
        Extra style for the container div.

    Returns
    -------
    html.Div containing the buttons and a dcc.Download.

    Usage
    -----
    Layout::

        from aspire_dash.components import export_buttons, register_export_callback

        html.Div([
            html.H3("My Table"),
            export_buttons("my-export"),
        ])

    Then in your callbacks module::

        register_export_callback("my-export", app)

    And define a callback that builds the DataFrame::

        @callback(
            Output("my-export-download", "data"),
            Input("my-export-csv", "n_clicks"),
            Input("my-export-xlsx", "n_clicks"),
            ...
        )
        def do_export(csv_clicks, xlsx_clicks, ...):
            return send_export(ctx.triggered_id, df, "filename")
    """
    container_style = {"display": "flex", "gap": "8px"}
    if style:
        container_style.update(style)

    children = []
    if csv:
        children.append(html.Button(
            [html.I(className="fa-solid fa-file-csv", style={"marginRight": "6px"}), "CSV"],
            id=f"{export_id}-csv", className="btn-outline", n_clicks=0,
            style={"fontSize": "12px", "padding": "4px 12px"},
        ))
    if excel:
        children.append(html.Button(
            [html.I(className="fa-solid fa-file-excel", style={"marginRight": "6px"}), "Excel"],
            id=f"{export_id}-xlsx", className="btn-outline", n_clicks=0,
            style={"fontSize": "12px", "padding": "4px 12px"},
        ))
    children.append(dcc.Download(id=f"{export_id}-download"))

    return html.Div(children, style=container_style)


def send_export(triggered_id, df, filename_base, sheet_name="Sheet1"):
    """Build a dcc.Download-compatible dict for CSV or Excel.

    Parameters
    ----------
    triggered_id : str
        The ``ctx.triggered_id`` — must end with ``-csv`` or ``-xlsx``.
    df : pandas.DataFrame
        Data to export.
    filename_base : str
        Filename without extension (e.g. ``"cpet_data_time"``).
    sheet_name : str
        Excel sheet name (default ``"Sheet1"``).

    Returns
    -------
    dict suitable for assigning to ``dcc.Download.data``.
    """
    if triggered_id and triggered_id.endswith("-csv"):
        return dict(content=df.to_csv(index=False), filename=f"{filename_base}.csv")

    # Excel
    import io
    import base64
    buf = io.BytesIO()
    df.to_excel(buf, index=False, sheet_name=sheet_name)
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode()
    return dict(content=encoded, filename=f"{filename_base}.xlsx", base64=True)


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


# ── KPI Stat (vertical label/value/sub) ────────────────────────────────────

def kpi_stat(label, value, sub: str = "", color: str | None = None, icon: str | None = None):
    """Vertical KPI tile — uppercase label · big value · optional subtitle.

    Distinct from ``summary_card`` (denser layout, white-on-white) and
    ``kpi_tile`` (vs-target progress bar). This one is the bare KPI used
    in medical-dashboard squad cards and the budget app's variance row.

    Use directly inside a flex/grid or wrap in ``dbc.Col``.

    Parameters
    ----------
    label : str
        Uppercase eyebrow (e.g. "Days lost", "Budget").
    value : str | int | float
        Big number — pre-format thousands / currency / pct before passing in.
    sub : str
        Optional subtitle (e.g. "vs target", "138/174").
    color : str or None
        Hex for the value text. Defaults to Aspire blue.
    icon : str or None
        FontAwesome class for an inline label icon.
    """
    val_color = color or ASPIRE["600"]
    icon_el = html.I(className=icon, style={
        "fontSize": "10px", "marginRight": "6px", "color": SLATE["400"],
    }) if icon else None
    return html.Div([
        html.Div(
            [icon_el, label] if icon_el else label,
            style={
                "fontSize": "11px", "fontWeight": "600",
                "color": SLATE["500"], "textTransform": "uppercase",
                "letterSpacing": "0.4px",
                "display": "flex", "alignItems": "center",
            },
        ),
        html.Div(str(value), style={
            "fontSize": "26px", "fontWeight": "700", "color": val_color,
            "marginTop": "4px", "fontVariantNumeric": "tabular-nums",
            "lineHeight": "1.15",
        }),
        html.Div(sub, style={
            "fontSize": "12px", "color": SLATE["400"], "marginTop": "2px",
        }) if sub else None,
    ], style={
        "background": "white",
        "border": f"1px solid {SLATE['200']}",
        "borderRadius": f"{RADIUS_LG}px",
        "padding": "14px 16px",
        "boxShadow": SHADOW_SM,
    })


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
