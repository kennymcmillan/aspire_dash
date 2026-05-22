"""Brand assets — federation logos + sport heroes shipped with aspire_dash."""
import dash
from dash import html

from aspire_dash.brand_logos import (
    PARTNER_LOGOS, SPORT_HEROES,
    partner_logo, partner_logo_img, partners_strip,
    sport_hero_img,
)

from ._shared import section, code_block

dash.register_page(__name__, path="/brand", title="Brand",
                    name="Brand assets")


def layout():
    # Group logos by category
    by_cat = {}
    for slug, meta in PARTNER_LOGOS.items():
        by_cat.setdefault(meta["category"], []).append((slug, meta))

    return html.Div([
        html.H1("Brand assets",
                style={"fontSize": "28px", "fontWeight": 700,
                       "marginBottom": "8px"}),
        html.P("Aspire mark, Qatar federation logos, ministries, "
                "international partners + per-sport hero shots. "
                "All sniffed from aspire.qa and bundled in "
                "aspire_dash/assets/brand/. Football intentionally excluded.",
                style={"color": "#64748b", "fontSize": "14px",
                       "marginBottom": "24px"}),

        # Aspire mark
        section("Aspire Academy mark"),
        html.Div([
            partner_logo_img("aspire", height=80),
        ], className="card", style={"padding": "24px",
                                       "textAlign": "center"}),
        code_block(
            "from aspire_dash.brand_logos import partner_logo_img\n\n"
            "partner_logo_img('aspire', height=80)\n"
            "# returns html.Img with src auto-prefixed for Connect"
        ),

        # Per-sport federations
        section(f"Qatar federations ({len(by_cat.get('federation', []))})"),
        html.Div(
            [_logo_card(slug, meta)
             for slug, meta in by_cat.get("federation", [])],
            style={"display": "grid",
                    "gridTemplateColumns": "repeat(auto-fill, minmax(180px, 1fr))",
                    "gap": "12px"},
        ),

        # Ministries + multi-sport
        section("Ministries + multi-sport bodies"),
        html.Div(
            [_logo_card(slug, meta)
             for slug, meta in (by_cat.get("ministry", [])
                                 + by_cat.get("multi-sport", []))],
            style={"display": "grid",
                    "gridTemplateColumns": "repeat(auto-fill, minmax(180px, 1fr))",
                    "gap": "12px"},
        ),

        # International partners
        section("International partners + awards"),
        html.Div(
            [_logo_card(slug, meta)
             for slug, meta in (by_cat.get("international", [])
                                 + by_cat.get("award", []))],
            style={"display": "grid",
                    "gridTemplateColumns": "repeat(auto-fill, minmax(220px, 1fr))",
                    "gap": "12px"},
        ),

        # Sport hero shots
        section("Sport hero shots (page banners)"),
        html.Div(
            [html.Div([
                html.Div(sport.replace("_", " ").title(),
                          style={"fontSize": "11px", "fontWeight": 600,
                                  "textTransform": "uppercase",
                                  "letterSpacing": "0.5px",
                                  "color": "#64748b",
                                  "marginBottom": "6px"}),
                sport_hero_img(sport, 0, height=180,
                                width="100%"),
            ], style={"borderRadius": "8px", "overflow": "hidden"})
             for sport in SPORT_HEROES.keys()],
            style={"display": "grid",
                    "gridTemplateColumns": "repeat(auto-fill, minmax(240px, 1fr))",
                    "gap": "16px"},
        ),
        code_block(
            "from aspire_dash.brand_logos import sport_hero_img\n\n"
            "# Use as page banner\n"
            "sport_hero_img('fencing', 0, height=240)\n"
            "sport_hero_img('athletics', 1, height=240)"
        ),

        # Partners strip
        section("partners_strip — footer / about-page convenience"),
        html.Div([
            partners_strip(),
        ], className="card"),
        code_block(
            "from aspire_dash.brand_logos import partners_strip\n\n"
            "# All federations + ministries + Olympic in one strip\n"
            "partners_strip(height=48)\n\n"
            "# Or just the ones you want\n"
            "partners_strip(['fencing', 'swimming', 'athletics'],\n"
            "                height=60)"
        ),

    ], style={"padding": "24px"})


def _logo_card(slug, meta):
    return html.Div([
        html.Div([
            partner_logo_img(slug, height=56),
        ], style={"display": "flex", "alignItems": "center",
                   "justifyContent": "center",
                   "height": "80px",
                   "background": "white"}),
        html.Div(meta["name"], style={
            "fontSize": "11px", "fontWeight": 600,
            "color": "#475569",
            "textAlign": "center", "padding": "8px",
            "borderTop": "1px solid #e2e8f0",
        }),
        html.Div(f"slug: {slug!r}",
                  style={"fontSize": "10px",
                          "fontFamily": "monospace",
                          "color": "#94a3b8",
                          "textAlign": "center",
                          "padding": "0 8px 8px"}),
    ], className="card", style={"padding": "0", "overflow": "hidden"})
