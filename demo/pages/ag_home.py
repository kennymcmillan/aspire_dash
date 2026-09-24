"""Asian Games design: home page in the aichi-nagoya2026.org style."""
import datetime as dt

import dash
from dash import html

from aspire_dash.asian_games import (
    AG_DISCIPLINES, ag_button, ag_feature_banner, ag_hero_heading, ag_hero_stats, ag_intro,
    ag_medal_widget, ag_news_card, ag_results_table, ag_schedule_unit, ag_section_title,
    ag_sport_tile, ag_status_pill,
)

from ._ag_common import ag_page, sample_note
from ._ag_data import ATHLETES, EVENTS, GAMES_DAYS, MEDAL_TABLE, NEWS, SCHEDULE, TODAY

dash.register_page(__name__, path="/ag", title="AG · Home", name="AG Home")


def layout(bio=None, **_):
    day_no = GAMES_DAYS.index(TODAY) + 1
    today = SCHEDULE[TODAY]
    live = [u for u in today if u["status"] in ("live", "running")] or today[:4]
    latest = EVENTS["SWM-W200IM"]
    podium = [r for r in latest["units"][-1]["rows"] if r.get("rank") and r["rank"] <= 3]

    hero = ag_hero_heading(
        ["Asian Games ", html.Em("design"), " language"],
        eyebrow=["19 Sep to 4 Oct 2026 · Day ", str(day_no), " of 16"],
        lead="The layout, navigation and results patterns from the Aichi-Nagoya 2026 sites, "
             "rebuilt as aspire_dash components. Every page in this section uses the same shell.",
        actions=[ag_button("Live results", href="/ag/results", variant="light", icon="fa-circle-play"),
                 ag_button("Component guide", href="/ag/components", icon="fa-shapes")],
        children=ag_hero_stats([(str(day_no), "Competition day"), (str(len(ATHLETES)), "Sample athletes"),
                                (str(len(EVENTS)), "Events with results"),
                                (str(sum(r["gold"] for r in MEDAL_TABLE)), "Golds awarded")]),
    )

    body = [
        html.Div([
            html.Div([
                ag_section_title("Happening today", aside=dt.date.fromisoformat(TODAY).strftime("%A %d %B")),
                html.Div([ag_schedule_unit(u["time"], u["event"], phase=u["phase"], unit=u["unit"],
                                           venue=u["venue"], status=u["status"],
                                           icon=AG_DISCIPLINES[u["discipline"]][1], medal=u["medal"])
                          for u in live[:5]], className="ag-sunits"),
                ag_section_title("Latest final", aside=latest["name"]),
                ag_results_table([
                    {"key": "rank", "label": "Rank", "kind": "rank", "width": "56px"},
                    {"key": "surname", "label": "Name", "kind": "athlete"},
                    {"key": "mark", "label": "Result", "kind": "mark", "width": "140px", "align": "right"},
                ], podium),
            ]),
            html.Div([
                ag_section_title("Standings"),
                ag_medal_widget(MEDAL_TABLE, link="/ag/medals"),
            ]),
        ], className="ag-split"),

        ag_intro("Sports", "Pick a discipline",
                 "Tiles link to the results page for that discipline. Swimming and athletics carry sample "
                 "results; the rest show the empty state.", pill_icon="fa-medal"),
        html.Div([ag_sport_tile(label, icon, f"/ag/results?disc={code}")
                  for code, (label, icon) in list(AG_DISCIPLINES.items())[:12]], className="ag-tiles"),

        ag_intro("News", "Latest stories", pill_icon="fa-newspaper"),
        html.Div([ag_news_card(n["title"], n["text"], date=n["date"], tags=n["tags"], icon=n["icon"],
                               tone=n["tone"]) for n in NEWS], className="ag-news"),

        html.Div(ag_feature_banner(
            "Follow every final",
            "The schedule page marks medal days in gold and lifts the day you pick. Live units pulse red.",
            icon="fa-calendar-days",
            button=ag_button("Open schedule", href="/ag/schedule", variant="light")),
            style={"marginTop": "48px"}),
        html.Div([ag_status_pill("live"), html.Span(" Live units update in place", className="ag-muted")],
                 style={"marginTop": "18px"}),
        sample_note(),
    ]
    return ag_page(body, active="/ag", hero=hero, hero_kwargs={"dip": 120}, bio=bio)
