"""v0.76: help drawer / button / welcome + register_help, search box + hits, viewstate token."""
from __future__ import annotations

import json

import dash
from dash import html

from aspire_dash import viewstate
from aspire_dash.components import (help_drawer, help_button, welcome_modal, register_help,
                                    search_box, search_hit, search_hit_id, hit_list)


def _ids(c, out=None):
    out = [] if out is None else out
    i = getattr(c, "id", None)
    if i is not None:
        out.append(i)
    ch = getattr(c, "children", None)
    for x in (ch if isinstance(ch, list) else [ch]):
        if x is not None and not isinstance(x, (str, int, float)):
            _ids(x, out)
    return out


def test_help_builders_use_the_prefix_and_group_examples():
    d = help_drawer([("Find", "Type a word")], [("Squash", "Top 30", "datasets?ds=x"), ("Squash", "Women", "datasets?ds=y"),
                                                ("Padel", "Top 50", "datasets?ds=z")], contact="a@b.qa", id_prefix="hp")
    assert d.id == "hp-drawer" and d.backdrop is False and d.placement == "end"
    s = json.dumps(d.to_plotly_json(), default=str)
    assert s.index("Squash") < s.index("Padel") and "mailto:a@b.qa" in s and "datasets?ds=z" in s
    assert help_button("hp").id == "hp-open"
    w = welcome_modal("Hi", "Intro", ["one", "two"], id_prefix="hp")
    assert {"hp-welcome-seen", "hp-welcome", "hp-welcome-close"} <= set(_ids(w))


def test_register_help_registers_two_callbacks():
    app = dash.Dash(__name__)
    app.layout = html.Div([help_button("hp"), help_drawer([("q", "a")], id_prefix="hp"), welcome_modal("t", "i", ["s"], id_prefix="hp")])
    before = len(app.callback_map)
    register_help(app, "hp")
    assert len(app.callback_map) == before + 2
    app.layout = html.Div([help_button("h2"), help_drawer([("q", "a")], id_prefix="h2")])
    register_help(app, "h2", welcome=False)
    assert len(app.callback_map) == before + 3


def test_search_hit_pattern_id_and_list():
    box = search_box("ds", "Search…")
    assert {"ds-search", "ds-search-results"} <= set(_ids(box))
    h = search_hit("ds", "k1", "PSA men", badges=[("Squash", "light"), ("Public", "success")], why="column: dob")
    assert h.id == {"type": "ds-hit", "key": "k1"} and h.n_clicks == 0
    assert search_hit_id("ds")["type"] == "ds-hit"
    assert hit_list([]) == "" and hit_list([], empty_text="none").children == "none"
    assert hit_list([h]).children == [h]


def test_viewstate_round_trip_and_tolerance():
    fm = {"Country": {"filterType": "text", "type": "equals", "filter": "EGY"}}
    tok = viewstate.encode(fm, {"Name": ["x"]}, "World_Ranking", True)
    st = viewstate.decode(tok)
    assert st["filter_model"] == fm and st["picks"] == {"Name": ["x"]} and st["sort_col"] == "World_Ranking" and st["sort_desc"]
    assert viewstate.column_state("World_Ranking", True) == [{"colId": "World_Ranking", "sort": "desc", "sortIndex": 0}]
    assert viewstate.encode({}, {}) == "" and viewstate.decode("junk!") is None and viewstate.decode(None) is None
