"""Sports — country flags, IOC→ISO conversion, placement badges, rank arrows."""
import dash
from dash import html

from aspire_dash.sports import (
    country_flag, flag_with_name, placement_badge, rank_change,
    competition_badge, category_badge, format_season, gradient_stat_card,
    stat_card, source_badge, competition_card, data_row, mini_stat,
    header_stat, trend_arrow,
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

        section("source_badge",
                 "Federation pill — colour auto-resolved per federation."),
        example("Federations",
                 html.Div([
                     source_badge("FIE", federation="fie"),
                     source_badge("PSA", federation="psa"),
                     source_badge("WTT", federation="wtt"),
                     source_badge("WA", federation="wa"),
                     source_badge("FIP", federation="fip"),
                 ], style={"display": "flex", "gap": "8px",
                            "alignItems": "center"}),
                 "source_badge('PSA', federation='psa')"),

        section("competition_card",
                 "Event card — federation / title / meta / result chain "
                 "(v0.45: hover lift + medal-toned placement)."),
        example("Events",
                 html.Div([
                     competition_card("Fencing Grand Prix Doha",
                                       date="2026-03-01", location="Doha",
                                       result="Gold medal", placement=1,
                                       federation="fie", category="Senior"),
                     competition_card("PSA World Championships",
                                       date="2026-05-12", location="Cairo",
                                       result="Quarter-final", placement=6,
                                       federation="psa"),
                 ], style={"display": "grid",
                            "gridTemplateColumns": "repeat(2, minmax(0, 280px))",
                            "gap": "12px"}),
                 "competition_card('GP Doha', placement=1, federation='fie')"),

        section("data_row + stats",
                 "Data grid rows (hover tint, header caps) + dense stats."),
        example("Rows",
                 html.Div([
                     data_row(["Rank", "Athlete", "Nation", "Points"],
                               header=True),
                     data_row(["1", "Ali Turki Owaida", "QAT", "152"],
                               highlight=True),
                     data_row(["2", "Mohamed Hosny", "EGY", "147"]),
                     data_row(["3", "Kim Min-jun", "KOR", "139"]),
                 ]),
                 "data_row([...], header=True) / data_row([...], highlight=True)"),
        example("Dense stats",
                 html.Div([
                     mini_stat("W/M", "4/6"),
                     mini_stat("Win%", "67%", color="#16a34a"),
                     header_stat("Competitions", 105),
                     header_stat("Pool Bouts", 174),
                     trend_arrow([42, 27, 11], label="World rank"),
                 ], style={"display": "flex", "gap": "24px",
                            "alignItems": "center"}),
                 "mini_stat('Win%', '67%') · header_stat('Bouts', 174) · trend_arrow([...])"),

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
