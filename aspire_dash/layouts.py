"""Standard page layouts — sidebar + main area with sticky header."""

from dash import html, dcc, page_container
from .theme import SIDEBAR_WIDTH, SLATE


def page_layout(sidebar_el, header_el=None, use_pages=True):
    """Full app layout: sidebar + main area (with Dash Pages support).

    Parameters
    ----------
    sidebar_el : Component
        The sidebar component (from components.sidebar()).
    header_el : Component or None
        The header component (from components.header()).
        If None, only page_container is rendered.
    use_pages : bool
        If True, renders dash.page_container for multi-page routing.
        If False, renders an empty div with id="page-content" for manual routing.
    """
    main_children = []
    if header_el:
        main_children.append(header_el)

    if use_pages:
        main_children.append(
            html.Div(page_container, className="page-content", style={"padding": "24px"})
        )
    else:
        main_children.append(
            html.Div(id="page-content", className="page-content", style={"padding": "24px"})
        )

    return html.Div([
        dcc.Location(id="url", refresh=False),
        sidebar_el,
        html.Div(main_children, id="main-area", className="main-area", style={
            "marginLeft": f"{SIDEBAR_WIDTH}px",
            "backgroundColor": SLATE["100"],
            "flex": "1",
            "minHeight": "100vh",
            "transition": "margin-left 0.3s ease",
        }),
    ], className="app-container", style={
        "display": "flex",
        "minHeight": "100vh",
    })


def single_page_layout(children, max_width="1200px"):
    """Simple centered layout without sidebar (e.g. login, landing pages)."""
    return html.Div(
        html.Div(children, style={
            "maxWidth": max_width,
            "margin": "0 auto",
            "padding": "24px",
        }),
        style={
            "minHeight": "100vh",
            "backgroundColor": SLATE["100"],
        },
    )
