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
