"""Navigation: top nav bar, sidebar, header — the app shell.

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


__all__ = ['topnav', 'register_topnav_active', 'sidebar', 'hamburger_button', 'register_sidebar_toggle', 'header']

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
        # get_relative_path so the link resolves correctly when the app
        # is mounted at a subpath (e.g. Posit Connect's /content/<GUID>/
        # root). Raw href="/skeletons" would bounce to the Connect root,
        # not the app — clicks would silently 404. Falls back to the raw
        # href when called outside a Dash app context (unit tests).
        try:
            link_href = dash.get_relative_path(item["href"])
        except Exception:
            link_href = item["href"]
        # Use html.A (plain anchor) instead of dcc.Link for sidebar nav.
        # dcc.Link does client-side routing via React Router, which has
        # had intermittent issues with Connect subpaths + SSO + scrollable
        # containers — sidebar items deep in the scroll area sometimes
        # don't navigate on click. html.A does a full-page nav (~200 ms
        # extra) but works in every Connect/proxy/SSO/cached-bundle
        # scenario. Topnav can stay on dcc.Link because it sits above the
        # fold and is always interactive.
        nav_children.append(
            html.A(
                [icon_el, item["label"]],
                href=link_href,
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


