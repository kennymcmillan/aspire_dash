"""v0.91 Asian Games design language (aspire_dash.asian_games).

Builders return the right Dash components and classes, the sort helper keeps
blanks at the bottom, and the stylesheet ships scoped under .ag-app with the
curve mask. Deterministic, no network, no Dash app needed."""
import os

import dash_bootstrap_components as dbc  # noqa: F401  (import order matches the app)
from dash import dcc, html

import aspire_dash.asian_games as ag

CSS = os.path.join(os.path.dirname(ag.__file__), "assets", "03_asian_games.css")


def _classes(component):
    return (getattr(component, "className", "") or "").split()


def _walk(c):
    yield c
    kids = getattr(c, "children", None)
    if kids is None:
        return
    for k in kids if isinstance(kids, (list, tuple)) else [kids]:
        if hasattr(k, "to_plotly_json"):
            yield from _walk(k)


def test_every_export_exists():
    for name in ag.__all__:
        assert hasattr(ag, name), name


def test_shell_wraps_hero_main_and_footer():
    page = ag.ag_shell(html.P("x"), nav_items=[{"label": "Home", "href": "/ag"}], active="/ag")
    assert "ag-app" in _classes(page)
    kinds = [type(k).__name__ for k in page.children if k is not None]
    assert kinds[:3] == ["Div", "Main", "Footer"]
    hero = page.children[0]
    assert "ag-hero--curve" in _classes(hero)
    # the rim (sweeping wave) and the masked gradient come first, then the nav
    assert _classes(hero.children[0]) == ["ag-hero__rim"]
    assert _classes(hero.children[1]) == ["ag-hero__mask"]
    assert "ag-topnav" in _classes(hero.children[2])


def test_active_nav_link_is_marked():
    nav = ag.ag_topnav([{"label": "Home", "href": "/ag"}, {"label": "Results", "href": "/ag/results"}],
                       "/ag/results")
    links = [c for c in _walk(nav) if isinstance(c, dcc.Link) and "ag-nav__link" in _classes(c)]
    assert [("is-active" in _classes(l)) for l in links] == [False, True]


def test_hero_variants():
    assert "ag-hero--rounded" in _classes(ag.ag_wave_hero([], variant="rounded"))
    assert "ag-hero--no-rim" in _classes(ag.ag_wave_hero([], rim=False))
    styled = ag.ag_wave_hero([], dip=120, curve_height=90)
    assert styled.style == {"--ag-hero-dip": "120px", "--ag-curve-h": "90px"}


def test_choice_group_has_store_and_one_active_button():
    tabs = ag.ag_pill_tabs("grp", ["A", "B", "C"], "B")
    store = tabs.children[0]
    assert isinstance(store, dcc.Store) and store.id == ag.ag_choice_id("grp") and store.data == "B"
    active = [b.id["value"] for b in tabs.children[1:] if "is-active" in _classes(b)]
    assert active == ["B"]


def test_date_strip_flags_medal_and_today():
    strip = ag.ag_date_strip("d", [{"value": "2026-09-23", "medal": True},
                                   {"value": "2026-09-24", "today": True}], "2026-09-24")
    first, second = strip.children[1:]
    assert "ag-day--medal" in _classes(first)
    assert {"ag-day--today", "is-active"} <= set(_classes(second))


def test_results_table_rows_medals_focus_and_empty():
    cols = [{"key": "rank", "kind": "rank"}, {"key": "surname", "kind": "athlete", "sortable": True},
            {"key": "mark", "kind": "mark"}]
    rows = [{"rank": 1, "surname": "A", "given": "x", "noc": "QAT", "athlete_id": "A1", "mark": 1.0,
             "medal": "gold", "records": ["GR"]},
            {"rank": 2, "surname": "B", "given": "y", "noc": "JPN", "mark": 2.0}]
    t = ag.ag_results_table(cols, rows, table_id="t", focus_noc="QAT", sort_state={"key": "surname"})
    head, r1, r2 = t.children
    assert "ag-rrow--head" in _classes(head)
    assert {"ag-rrow--medal-gold", "ag-rrow--focus"} <= set(_classes(r1))
    assert "ag-rrow--focus" not in _classes(r2)
    sort_btns = [c for c in _walk(head) if isinstance(getattr(c, "id", None), dict)]
    assert sort_btns[0].id == {"type": "ag-sort", "table": "t", "key": "surname", "d": False}
    assert "is-sorted" in _classes(sort_btns[0])
    empty = ag.ag_results_table(cols, [], empty_text="none")
    assert "ag-empty" in _classes(empty.children[1])


def test_sort_rows_sinks_blanks():
    rows = [{"k": 3}, {"k": None}, {"k": 1}, {"k": ""}]
    assert [r["k"] for r in ag.ag_sort_rows(rows, {"key": "k", "desc": False})][:2] == [1, 3]
    assert [r["k"] for r in ag.ag_sort_rows(rows, {"key": "k", "desc": True})][:2] == [3, 1]
    assert ag.ag_sort_rows(rows, None) == rows


def test_medal_table_totals_and_open_row():
    rows = [{"rank": 1, "noc": "QAT", "gold": 2, "silver": 1, "bronze": 0,
             "breakdown": [{"label": "Athletics", "icon": "fa-person-running", "gold": 2, "silver": 1,
                            "bronze": 0}]}]
    table = ag.ag_medal_table(rows, focus_noc="QAT", open_noc="QAT")
    row = table.children[1]
    assert isinstance(row, html.Details) and row.open is True
    assert "ag-mrow--focus" in _classes(row)
    totals = [c.children for c in _walk(row) if "t" in _classes(c) and "c" in _classes(c)]
    assert totals[0] == 3


def test_status_pill_and_profile():
    assert _classes(ag.ag_status_pill("live")) == ["ag-status", "ag-status--live"]
    prof = ag.ag_athlete_profile({"id": "A1", "surname": "DOE", "given": "Jo", "noc": "QAT",
                                  "sport": "Swimming", "gender": "Male", "age": 22,
                                  "events": [{"label": "100m Free", "rank": 1, "medal": "gold"}],
                                  "schedule": []})
    assert "ag-profile" in _classes(prof)


def test_stylesheet_is_scoped_and_ships_the_curve():
    css = open(CSS, encoding="utf-8").read()
    assert "M1920 0H0V186C0 186 344 278 960 278C1576 278 1920 186 1920 186V0Z" in css
    assert ".main-area:has(.ag-app) > .header" in css
    # no bare element selectors that could restyle the rest of an Aspire app
    for bad in ("\nbody {", "\nh1 {", "\n.card {", "\ntable {"):
        assert bad not in css


def test_default_palette_is_aspire_and_games_theme_is_opt_in():
    assert ag.AG_COLORS["primary"] == "#004185"
    assert ag.AG_COLORS_GAMES["primary"] == "#4f3b95"
    nav = [{"label": "Home", "href": "/ag"}]
    assert "ag-theme--games" not in _classes(ag.ag_shell(html.P(), nav_items=nav))
    assert "ag-theme--games" in _classes(ag.ag_shell(html.P(), nav_items=nav, theme="games"))
    css = open(CSS, encoding="utf-8").read()
    assert ".ag-app.ag-theme--games" in css
    # purple only lives inside the opt-in theme block
    default_block = css[:css.index(".ag-app.ag-theme--games")]
    assert "#4f3b95" not in default_block
