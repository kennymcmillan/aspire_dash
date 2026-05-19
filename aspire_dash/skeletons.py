"""Skeleton-shimmer placeholders for data-bound Dash UI.

Renders soft pulsing outlines while a callback is fetching the real
content. Friendlier than a spinner, gives the user a sense of the
shape of what's coming.

CSS is loaded from aspire_dash/assets/02_aspire_skeletons.css and
picked up automatically by any Dash app that uses
`aspire_dash.setup_app(app)`.

PUBLIC API
==========

Primitives (one-shape building blocks):

    skel_line(width="100%", lg=False, sm=False)   horizontal text-line bar
    skel_pill(width="80px")                        pill / badge
    skel_circle(size="40px")                       avatar / icon
    skel_card(height="120px")                      full card
    skel_tile(height="70px")                       short tile
    skel_row(height="38px")                        table-row bar

Composites (common layouts):

    skel_table_rows(n=5)                row-stack with decreasing widths
    skel_metric_tiles(n=4)              N-up metric tile row (kcal / mph / etc)
    skel_card_grid(n=6, cols=3)         responsive card grid
    skel_avatar_list(n=10)              avatar + 2-line list rows
    skel_kpi_strip(n=4)                 horizontal pill strip

Wrapper:

    skel_wrap(*children)                fade-in container
"""
from __future__ import annotations

from dash import html
import dash_bootstrap_components as dbc


# ---------- Primitives ----------

def skel_line(width: str | int = "100%", lg: bool = False, sm: bool = False,
              style: dict | None = None):
    """Single horizontal shimmer line for text placeholders."""
    cls = "skel-base skel-line-lg" if lg else (
        "skel-base skel-line-sm" if sm else "skel-base skel-line")
    final_style = {"width": width if isinstance(width, str) else f"{width}px"}
    if style:
        final_style.update(style)
    return html.Div(className=cls, style=final_style)


def skel_pill(width: str | int = "80px"):
    """Pill / badge placeholder."""
    return html.Div(
        className="skel-base skel-pill",
        style={"width": width if isinstance(width, str) else f"{width}px"},
    )


def skel_circle(size: str = "40px"):
    """Avatar / icon placeholder."""
    return html.Div(
        className="skel-base skel-circle",
        style={"width": size, "height": size, "display": "inline-block"},
    )


def skel_card(height: str = "120px"):
    """Full-card placeholder."""
    return html.Div(className="skel-base skel-card",
                    style={"height": height})


def skel_tile(height: str = "70px"):
    """Short tile placeholder (for KPI / metric tiles)."""
    return html.Div(className="skel-base skel-tile",
                    style={"height": height})


def skel_row(height: str = "38px"):
    """Single table-row bar."""
    return html.Div(className="skel-base skel-row",
                    style={"height": height})


def skel_wrap(*children):
    """Container that fades in so the shimmer doesn't pop on mount."""
    return html.Div(list(children), className="skel-wrap")


# ---------- Composites ----------

def skel_table_rows(n: int = 5):
    """Stack of n shimmer bars with decreasing widths — fallback for
    tabular data loads."""
    return skel_wrap(*[
        html.Div(className="skel-base skel-row",
                 style={"width": f"{100 - i*3}%"})
        for i in range(n)
    ])


def skel_metric_tiles(n: int = 4, size: str = "lg"):
    """N-up metric tile row geometry. `size='lg'` matches the
    standard Aspire 4-tile metric card (~80px high), `size='sm'`
    matches the inline live-preview row (~50px high)."""
    height = "80px" if size == "lg" else "50px"
    return dbc.Row([
        dbc.Col(html.Div([
            skel_line(width="60%", sm=True),
            skel_line(width="40%", lg=True),
            skel_line(width="50%", sm=True),
        ], style={"padding": "12px 16px" if size == "lg" else "8px 12px",
                  "background": "white",
                  "border": "1px solid #e2e8f0",
                  "borderRadius": "8px" if size == "lg" else "6px",
                  "height": height}),
                md=int(12 / n) if n else 3, className="mb-2")
        for _ in range(n)
    ], className="g-2")


def skel_card_grid(n: int = 6, cols: int = 3, height: str = "140px"):
    """Responsive card grid placeholder. Useful for: download tile
    grids, project tiles, dashboard widgets."""
    width = max(1, int(12 / cols))
    return dbc.Row([
        dbc.Col(html.Div([
            skel_line(width="40%", lg=True),
            skel_line(width="70%", sm=True),
            html.Div(className="skel-base skel-pill",
                     style={"width": "120px", "height": "32px",
                            "marginTop": "12px"}),
        ], style={"padding": "16px",
                  "background": "white",
                  "border": "1px solid #e2e8f0",
                  "borderRadius": "8px",
                  "height": height}),
                md=width, className="mb-3")
        for _ in range(n)
    ])


def skel_avatar_list(n: int = 10):
    """Avatar-plus-two-lines row stack. Athlete pickers, member lists,
    contact directories etc."""
    return skel_wrap(*[
        html.Div(
            dbc.Row([
                dbc.Col(skel_circle(size="36px"), width="auto"),
                dbc.Col([
                    skel_line(width="60%"),
                    skel_line(width="40%", sm=True),
                ]),
            ], className="g-2 align-items-center"),
            style={"padding": "8px 12px",
                   "borderBottom": "1px solid #f1f5f9"},
        )
        for _ in range(n)
    ])


def skel_kpi_strip(n: int = 4):
    """Inline pill strip — small KPIs in a header."""
    return html.Div([
        skel_pill(width=80) for _ in range(n)
    ], style={"display": "flex", "gap": "8px", "alignItems": "center"})
