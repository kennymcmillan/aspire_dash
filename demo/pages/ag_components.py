"""Asian Games design: component reference (every ag_* helper with its code)."""
import dash
from dash import dcc, html

from aspire_dash.asian_games import (
    AG_COLORS, AG_COLORS_GAMES, ag_athlete_card, ag_athlete_profile, ag_band, ag_button, ag_chip, ag_date_strip,
    ag_discipline_card, ag_empty, ag_event_capsule, ag_feature_banner, ag_field, ag_filter_panel,
    ag_gradient_title, ag_hero_heading, ag_hero_stats, ag_intro, ag_legend, ag_medal_chip,
    ag_medal_icon, ag_medal_stack, ag_medal_table, ag_medal_widget, ag_news_card, ag_noc,
    ag_page_title, ag_pill_tabs, ag_records_panel, ag_results_table, ag_schedule_unit,
    ag_section_title, ag_sport_tile, ag_stat, ag_status_pill, ag_subtab_links, ag_subtabs,
    ag_unit_strip, ag_wave_hero,
)

from ._ag_common import ag_page
from ._ag_data import ATHLETES, EVENTS, MEDAL_TABLE, NEWS, TODAY, days_strip, discipline_days
from ._shared import example

dash.register_page(__name__, path="/ag/components", title="AG · Components", name="AG Components")

_EV = EVENTS["SWM-W200IM"]
_ROWS = _EV["units"][-1]["rows"][:4]
_COLS = [
    {"key": "rank", "label": "Rank", "kind": "rank", "width": "56px", "sortable": True},
    {"key": "surname", "label": "Name", "kind": "athlete", "sortable": True},
    {"key": "mark", "label": "Result", "kind": "mark", "width": "140px", "align": "right", "sortable": True},
    {"key": "gap", "label": "Gap", "kind": "gap", "width": "70px", "align": "right"},
]


def _swatches(colors=AG_COLORS):
    return html.Div([
        html.Div([html.Div(style={"height": "44px", "borderRadius": "10px", "background": v,
                                  "border": "1px solid #e7e7e7"}),
                  html.Div(k, style={"fontSize": "12px", "fontWeight": 600, "marginTop": "4px"}),
                  html.Div(v, className="ag-muted", style={"fontSize": "11px"})])
        for k, v in colors.items()
    ], style={"display": "grid", "gridTemplateColumns": "repeat(auto-fill, minmax(110px, 1fr))", "gap": "12px"})


def layout(bio=None, **_):
    hero = ag_hero_heading("Component guide", eyebrow="aspire_dash.asian_games",
                           lead="Every building block in this section, live, with the call that makes it.")
    a = next(iter(ATHLETES.values()))
    body = [
        ag_page_title("Component guide"),
        html.P(["Import from ", html.Code("aspire_dash.asian_games"), ". Wrap each page in ",
                html.Code("ag_shell()"), " and it gets the nav, the wave hero and the footer. Styles are "
                "scoped to ", html.Code(".ag-app"), ", so nothing leaks into the rest of the app."],
               className="ag-muted"),

        ag_section_title("Foundations"),
        example("Palette (AG_COLORS)", _swatches(), "from aspire_dash.asian_games import AG_COLORS\nAG_COLORS['primary']  # '#004185' (Aspire blue)"),
        example("Original Aichi-Nagoya palette (theme='games')", _swatches(AG_COLORS_GAMES),
                'ag_shell(children, nav_items=NAV, theme="games")  # purple and gold instead of Aspire blue'),
        example("Headings", html.Div([ag_page_title("Swimming results"), ag_gradient_title("Competition"),
                                      ag_section_title("Final", aside="Official")]),
                'ag_page_title("Swimming results")\nag_gradient_title("Competition")\nag_section_title("Final", aside="Official")'),

        ag_section_title("Hero and navigation"),
        example("Curved wave hero (variant='curve')",
                ag_wave_hero([ag_band("Swimming", "fa-person-swimming",
                                      ag_subtab_links([{"label": "Schedule", "href": "/ag/schedule"},
                                                       {"label": "Results", "href": "/ag/results"},
                                                       {"label": "Medals", "href": "/ag/medals"}], "/ag/results")),
                              html.Div(ag_event_capsule("Women's 200m IM", "Final", status="official",
                                                        when="Sep 23, 19:52", venue="Aquatics Centre"),
                                       style={"padding": "20px 20px 0"})]),
                'ag_wave_hero([\n    ag_band("Swimming", "fa-person-swimming", ag_subtab_links(items, active)),\n'
                '    ag_event_capsule("Women\'s 200m IM", "Final", status="official",\n'
                '                     when="Sep 23, 19:52", venue="Aquatics Centre"),\n])'),
        example("Rounded hero (variant='rounded') with glass stats",
                ag_wave_hero(html.Div([ag_hero_heading("Medal standings", eyebrow="Medals"),
                                       ag_hero_stats([("16", "NOCs"), ("197", "Golds")])],
                                      style={"paddingTop": "24px"}), variant="rounded"),
                'ag_wave_hero(ag_hero_heading("Medal standings"), variant="rounded")\n'
                'ag_hero_stats([("16", "NOCs"), ("197", "Golds")])'),
        example("Value-driven sub-tabs (read Input(ag_choice_id('demo-sub'), 'data'))",
                html.Div(ag_subtabs("demo-sub", ["Entries", "Results", "Medals"], "Results"),
                         style={"background": "#001d3d", "borderRadius": "12px", "padding": "16px 12px 4px"}),
                'ag_subtabs("demo-sub", ["Entries", "Results", "Medals"], "Results")'),

        ag_section_title("Controls"),
        example("Pill tabs", html.Div([ag_pill_tabs("demo-pill", ["Start list", "Results", "Summary"], "Results"),
                                       html.Br(),
                                       ag_pill_tabs("demo-pill2", ["Medal standings", "Medallists"],
                                                    variant="outline")]),
                'ag_pill_tabs("res-mode", ["Start list", "Results", "Summary"], "Results")\n'
                'ag_pill_tabs("med-tab", [...], variant="outline")'),
        example("Heat strip", ag_unit_strip("demo-unit", _EV["units"]),
                'ag_unit_strip("res-unit", [{"value", "label", "when", "status"}, ...])'),
        example("Date strip (click a day: it lifts)", ag_date_strip("demo-day", days_strip()[:10], TODAY),
                'ag_date_strip("sch-day", [{"value": "2026-09-24", "medal": True, "today": True}, ...], value)'),
        example("Filter panel", ag_filter_panel([ag_field("Search", dcc.Input(className="ag-input", placeholder="Name"))],
                                                open=True, chips=[ag_chip("QAT", "purple"), ag_chip("Swimming", "purple")]),
                'ag_filter_panel([ag_field("NOC", dcc.Dropdown(..., className="ag-select"))], chips=[...])'),
        example("Buttons", html.Div([ag_button("Primary"), ag_button("Outline", variant="outline"),
                                     ag_button("Show filters", variant="ghost", icon="fa-sliders")],
                                    className="ag-row"),
                'ag_button("Primary")\nag_button("Outline", variant="outline")\nag_button("Show filters", variant="ghost", icon="fa-sliders")'),

        ag_section_title("Status, medals and chips"),
        example("Status pills", html.Div([ag_status_pill(s) for s in
                                          ("official", "live", "running", "delayed", "unofficial", "scheduled")],
                                         className="ag-row"),
                'ag_status_pill("official")  # live / running / delayed / unofficial / scheduled'),
        example("Medals", html.Div([ag_medal_icon("gold"), ag_medal_icon("silver"), ag_medal_icon("bronze"),
                                    ag_medal_chip("gold"), ag_medal_chip("silver"), ag_medal_chip("bronze"),
                                    ag_medal_stack()], className="ag-row", style={"alignItems": "center"}),
                'ag_medal_icon("gold")\nag_medal_chip("silver")\nag_medal_stack("Medal")'),
        example("NOC cell and legend", html.Div([ag_noc("QAT"), ag_noc("JPN"),
                                                 ag_legend([("Competition day", "outline"), ("Medal day", "gold"),
                                                            ("Live", "live")])], className="ag-row",
                                                style={"alignItems": "center"}),
                'ag_noc("QAT")\nag_legend([("Medal day", "gold"), ("Live", "live")])'),

        ag_section_title("Tables"),
        example("Row-card results table (sortable, Qatar highlighted)",
                ag_results_table(_COLS, _ROWS, focus_noc="QAT"),
                'ag_sort_store("res-table", "rank")\n'
                'ag_results_table(columns, ag_sort_rows(rows, state), table_id="res-table",\n'
                '                 sort_state=state, focus_noc="QAT")'),
        example("Expandable medal table", ag_medal_table(MEDAL_TABLE[:4], open_noc=MEDAL_TABLE[0]["noc"]),
                'ag_medal_table(rows, focus_noc="QAT", open_noc="QAT")'),
        example("Records panel", ag_records_panel(_EV["records"]), 'ag_records_panel(records)'),
        example("Empty state", ag_empty(), 'ag_empty("No results available")'),

        ag_section_title("Schedule"),
        example("Schedule rows", html.Div([
            ag_schedule_unit("19:30", "Men's 100m Freestyle", phase="Final", venue="Aquatics Centre",
                             status="live", icon="fa-person-swimming", medal=True),
            ag_schedule_unit("21:15", "Men's 100m", phase="Final", venue="Main Stadium",
                             status="scheduled", icon="fa-person-running", medal=True),
        ], className="ag-sunits"),
            'ag_schedule_unit("19:30", "Men\'s 100m Freestyle", phase="Final",\n'
            '                 venue="Aquatics Centre", status="live", icon="fa-person-swimming", medal=True)'),
        example("By-discipline card", html.Div(ag_discipline_card("Swimming", "fa-person-swimming",
                                                                  discipline_days()["SWM"], live=True),
                                               style={"maxWidth": "520px"}),
                'ag_discipline_card("Swimming", "fa-person-swimming", days, live=True)'),

        ag_section_title("Athletes"),
        example("Participant card (click opens the profile modal)",
                html.Div([ag_athlete_card(x) for x in list(ATHLETES.values())[:3]], className="ag-agrid"),
                'ag_athlete_card(athlete)  # fires {"type": "ag-athlete", "id": ...}'),
        example("Athlete profile", html.Div(ag_athlete_profile(a), style={"maxWidth": "560px"}),
                'ag_athlete_profile(athlete)'),

        ag_section_title("Org-site cards"),
        example("Page intro", ag_intro("News", "Latest stories", "Centred grey lead text.", pill_icon="fa-newspaper"),
                'ag_intro("News", "Latest stories", "Lead text", pill_icon="fa-newspaper")'),
        example("Sports tiles", html.Div([ag_sport_tile("Athletics", "fa-person-running"),
                                          ag_sport_tile("Swimming", "fa-person-swimming"),
                                          ag_sport_tile("Squash", "fa-table-tennis-paddle-ball"),
                                          ag_sport_tile("Fencing", "fa-shield-halved"),
                                          ag_sport_tile("Padel", "fa-baseball"),
                                          ag_sport_tile("Shooting", "fa-bullseye")], className="ag-tiles"),
                'ag_sport_tile("Athletics", "fa-person-running", href="/ag/results?disc=ATH")'),
        example("News cards", html.Div([ag_news_card(n["title"], n["text"], date=n["date"], tags=n["tags"],
                                                     icon=n["icon"], tone=n["tone"]) for n in NEWS],
                                       className="ag-news"),
                'ag_news_card(title, text, date="24 Sep 2026", tags=["Swimming"], tone="gold")'),
        example("Medal widget and stat tiles", html.Div([
            ag_medal_widget(MEDAL_TABLE, limit=5),
            html.Div([ag_stat("Golds", "58", "sample", gold=True), ag_stat("Athletes", str(len(ATHLETES)))],
                     className="ag-stats"),
        ], className="ag-split"), 'ag_medal_widget(rows, limit=5)\nag_stat("Golds", "58", gold=True)'),
        example("Feature banner", ag_feature_banner("Follow every final", "Two-column banner with a patterned panel.",
                                                    button=ag_button("Open", variant="light")),
                'ag_feature_banner(title, text, icon="fa-medal", button=ag_button("Open", variant="light"))'),
    ]
    return ag_page(body, active="/ag/components", hero=hero, hero_kwargs={"dip": 90}, bio=bio)
