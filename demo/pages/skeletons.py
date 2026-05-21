"""Skeletons — loading placeholders with shimmer animation."""
import dash
from dash import html

from aspire_dash.skeletons import (
    skel_line, skel_pill, skel_circle, skel_card, skel_tile, skel_row,
    skel_table_rows, skel_metric_tiles, skel_card_grid,
    skel_avatar_list, skel_kpi_strip, skel_sync_overlay,
)

from ._shared import section, example

dash.register_page(__name__, path="/skeletons", title="Skeletons",
                    name="Skeletons")


def layout():
    return html.Div([
        html.H1("Skeleton Loaders",
                style={"fontSize": "28px", "fontWeight": 700,
                       "marginBottom": "8px"}),
        html.P("Pure-CSS shimmer animations that mimic the shape of the "
                "real content while data is loading.",
                style={"color": "#64748b", "fontSize": "14px",
                       "marginBottom": "24px"}),

        section("skel_sync_overlay (v0.10.0 ✨)",
                 "Full-grid initial-load skeleton with spinning icon + caption. "
                 "Pair with a sibling Div that holds the real component "
                 "(display:none → revealed by callback)."),
        example(
            "SAMS sync overlay",
            skel_sync_overlay("Syncing Athlete Management System data",
                               rows=4, height="180px",
                               overlay_id="demo-sync-overlay-1"),
            "from aspire_dash.skeletons import skel_sync_overlay\n\n"
            "# In layout\n"
            'skel_sync_overlay("Syncing SAMS data", rows=8)\n\n'
            "# In callbacks — hide the overlay when sync resolves\n"
            "@callback(Output('sync-overlay', 'style'),\n"
            "          Input('sync-result', 'data'))\n"
            "def _hide(result):\n"
            "    return {'display': 'none'} if result else dash.no_update",
        ),

        section("skel_metric_tiles",
                 "Placeholder for a KPI strip / kpi_tile_row."),
        example("4 metric tiles",
                 skel_metric_tiles(n=4),
                 "skel_metric_tiles(n=4)"),

        section("skel_kpi_strip",
                 "Inline pills — same vibe but smaller."),
        example("4 pills",
                 skel_kpi_strip(n=4),
                 "skel_kpi_strip(n=4)"),

        section("skel_card_grid",
                 "Card placeholder grid — for fencer roster, athlete list, etc."),
        example("6 cards / 3 cols",
                 skel_card_grid(n=6, cols=3, height="80px"),
                 "skel_card_grid(n=6, cols=3, height='140px')"),

        section("skel_table_rows",
                 "Single-table placeholder."),
        example("5 rows",
                 skel_table_rows(n=5),
                 "skel_table_rows(n=5)"),

        section("skel_avatar_list",
                 "Avatar + name combo — fencer/athlete picker."),
        example("4 avatars",
                 skel_avatar_list(n=4),
                 "skel_avatar_list(n=4)"),

        section("Atomic placeholders",
                 "Building blocks for custom shapes."),
        example("Pill / line / circle",
                 html.Div([
                     skel_pill(width="80px"),
                     skel_line(width="60%"),
                     skel_circle(size="40px"),
                 ], style={"display": "flex", "gap": "12px",
                            "alignItems": "center"}),
                 "skel_pill() · skel_line() · skel_circle()"),
        example("Card",
                 skel_card(height="80px"),
                 "skel_card(height='120px')"),
    ], style={"padding": "24px"})
