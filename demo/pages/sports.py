"""Sports — country flags, IOC→ISO conversion, placement badges, rank arrows."""
import dash
from dash import html

from aspire_dash.sports import (
    country_flag, flag_with_name, placement_badge, rank_change,
    competition_badge, category_badge, format_season, gradient_stat_card,
    stat_card,
)

from ._shared import section, example

dash.register_page(__name__, path="/sports", title="Sports", name="Sports")


def layout():
    return html.Div([
        html.H1("Sports Components",
                style={"fontSize": "28px", "fontWeight": 700,
                       "marginBottom": "8px"}),
        html.P("Country flags, placement badges, rank-change arrows — for "
                "ranking-table type pages.",
                style={"color": "#64748b", "fontSize": "14px",
                       "marginBottom": "24px"}),

        section("country_flag",
                 "Flag SVG by IOC code (auto-converts to ISO)."),
        example("Flags",
                 html.Div([
                     country_flag("QAT", size="md"),
                     country_flag("EGY", size="md"),
                     country_flag("KSA", size="md"),
                     country_flag("UAE", size="md"),
                     country_flag("GBR", size="md"),
                 ], style={"display": "flex", "gap": "10px",
                            "alignItems": "center"}),
                 "country_flag('QAT', size='md')"),

        section("flag_with_name",
                 "Flag + athlete name — Qatar highlight by default."),
        example("Names",
                 html.Div([
                     flag_with_name("QAT", "Ali Turki Owaida",
                                     highlight_nation="QAT"),
                     flag_with_name("EGY", "Mohamed Hosny",
                                     highlight_nation="QAT"),
                 ], style={"display": "flex", "flexDirection": "column",
                            "gap": "8px"}),
                 "flag_with_name('QAT', 'Ali Turki', highlight_nation='QAT')"),

        section("placement_badge",
                 "Gold/silver/bronze badges + lower-place styling."),
        example("Placements",
                 html.Div([
                     placement_badge(1, size="md"),
                     placement_badge(2, size="md"),
                     placement_badge(3, size="md"),
                     placement_badge(4, size="md"),
                     placement_badge(10, size="md"),
                 ], style={"display": "flex", "gap": "8px",
                            "alignItems": "center"}),
                 "placement_badge(1, size='md')"),

        section("rank_change",
                 "Up / down / unchanged arrow w/ delta."),
        example("Rank deltas",
                 html.Div([
                     rank_change(5, 8),    # +3 — moved up
                     rank_change(12, 9),   # -3 — moved down
                     rank_change(7, 7),    #  0 — unchanged
                 ], style={"display": "flex", "gap": "14px",
                            "alignItems": "center"}),
                 "rank_change(current=5, previous=8)  # ▲ +3"),

        section("competition_badge",
                 "Competition tier (Olympic, WC, GP, etc.)."),
        example("Tiers",
                 html.Div([
                     competition_badge("Olympic"),
                     competition_badge("World Cup"),
                     competition_badge("Grand Prix"),
                     competition_badge("National"),
                 ], style={"display": "flex", "gap": "8px",
                            "alignItems": "center"}),
                 "competition_badge('Olympic')"),

        section("stat_card / gradient_stat_card",
                 "Sport-specific KPI tiles."),
        example("Stat cards",
                 html.Div([
                     stat_card("Medals", "47", sub="2026 season", icon="medal",
                                color="blue"),
                     gradient_stat_card("Top fencers", "12",
                                         emoji="🤺",
                                         bg="linear-gradient(135deg, #dbeafe, #bfdbfe)"),
                 ], style={"display": "flex", "gap": "12px"}),
                 "stat_card('Medals', '47', sub='2026 season', icon='medal')"),

        section("format_season",
                 "Season-string normaliser."),
        html.Pre(
            f"format_season('2025-26') → {format_season('2025-26')!r}\n"
            f"format_season('2026')    → {format_season('2026')!r}\n",
            style={"background": "#f1f5f9", "padding": "10px",
                    "borderRadius": "4px", "fontSize": "12px",
                    "fontFamily": "Fira Code, monospace"},
        ),
    ], style={"padding": "24px"})
