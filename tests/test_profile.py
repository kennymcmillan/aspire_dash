"""0.108: athlete profile components promoted from High Management Overview. Mock values only."""
from aspire_dash.components import form_from_results, form_strip, podium, profile_hero, profile_pill


def _walk(c):
    yield c
    kids = getattr(c, "children", None)
    if kids is None:
        return
    for k in (kids if isinstance(kids, (list, tuple)) else [kids]):
        if k is not None and not isinstance(k, (str, int, float)):
            yield from _walk(k)


def _classes(c):
    return [getattr(x, "className", "") or "" for x in _walk(c)]


def _texts(c):
    out = []
    for x in _walk(c):
        k = getattr(x, "children", None)
        if isinstance(k, (str, int, float)):
            out.append(str(k))
        elif isinstance(k, (list, tuple)):
            out += [str(i) for i in k if isinstance(i, (str, int, float))]
    return out


def _find(c, cls):
    return [x for x in _walk(c) if cls in (getattr(x, "className", "") or "").split()]


ITEMS = [{"name": "A One", "band": "world", "band_label": "World class", "value": "#6", "scope": "world", "href": "/a/1"},
         {"name": "B Two", "band": "gcc", "value": None},                       # no number: skipped
         {"name": "C Three", "band": "AG Medal", "value": "#45", "scope": "world", "sub": ["Squash", "PSA"]}]


def test_podium_skips_athletes_without_a_number_and_numbers_positions():
    p = podium(ITEMS)
    cards = _find(p, "ad-pod")
    assert len(cards) == 2
    assert [t for t in _texts(p) if t in ("1", "2", "3")] == ["1", "2"]
    assert "B Two" not in _texts(p)


def test_podium_band_key_is_slugged_onto_each_card():
    cls = [c.className for c in _find(podium(ITEMS), "ad-pod")]
    assert cls == ["ad-pod ad-band-world", "ad-pod ad-band-ag-medal"]


def test_podium_respects_n_and_returns_none_when_empty():
    assert len(_find(podium(ITEMS, n=1), "ad-pod")) == 1
    assert podium([{"name": "X", "value": None}]) is None
    assert podium([]) is None


def test_podium_card_is_a_link_only_when_href_given():
    from dash import dcc, html
    cards = _find(podium(ITEMS), "ad-pod")
    assert isinstance(cards[0], dcc.Link) and cards[0].href == "/a/1"
    assert isinstance(cards[1], html.Div)
    assert isinstance(_find(podium(ITEMS, link="a"), "ad-pod")[0], html.A)


def test_form_from_results_reads_wins_losses_and_places():
    rows = [["2026-10-01", "Open", "", "R1", "X", "Won 3-0"],
            ["2026-09-20", "Cup", "", "F", "Y", "Lost 1-3"],
            ["2026-09-01", "Champs", "400mH", "Final", "", "1st, 47.82"],
            ["2026-08-01", "Champs", "400mH", "Final", "", "3rd"],
            ["2026-07-01", "Meet", "400mH", "Heat", "", "11th"],
            ["2026-06-01", "Meet", "400mH", "Heat", "", "1st"]]       # 6th row: beyond n=5
    f = form_from_results(rows)
    assert [(x["text"], x["kind"]) for x in f] == [("W", "win"), ("L", "loss"), ("1", "gold"), ("3", "bronze"),
                                                   ("11", "place")]
    assert f[0]["title"] == "2026-10-01 · Open · R1 · v X · Won 3-0"


def test_form_from_results_skips_bad_rows():
    assert form_from_results([["a", "b"], None, ["d", "c", "e", "r", "o", "DNF"]]) == []
    assert form_from_results(None) == []


def test_form_strip_unknown_kind_falls_back_to_place_and_none_when_empty():
    s = form_strip([{"text": "W", "kind": "win"}, {"text": "4", "kind": "weird"}])
    assert [c.className for c in _find(s, "ad-form")] == ["ad-form is-win", "ad-form is-place"]
    assert form_strip([]) is None


def test_hero_big_number_scope_and_of():
    h = profile_hero("Zed", band="world", band_label="World class", value="#6", scope="World", of=812)
    assert h.className == "ad-ph ad-band-world"
    assert "#6" in _texts(h) and "World · of 812" in _texts(h)
    assert not _find(h, "is-empty")


def test_hero_without_value_says_so_and_never_shows_a_number():
    h = profile_hero("Zed", value=None)
    assert _find(h, "is-empty")
    assert "No ranking on file" in _texts(h)
    assert not _find(h, "ad-ph-num")


def test_hero_chips_capped_and_empty_chips_dropped():
    chips = [{"label": f"L{i}", "value": i} for i in range(8)] + [{"label": "none", "value": None}]
    h = profile_hero("Zed", value="#1", chips=chips)
    assert len(_find(h, "ad-ph-chip")) == 6
    assert len(_find(profile_hero("Zed", value="#1", chips=chips, max_chips=3), "ad-ph-chip")) == 3
    assert not _find(profile_hero("Zed", value="#1"), "ad-ph-chips")


def test_hero_optional_parts_only_when_given():
    bare = profile_hero("Zed", value="#1")
    for cls in ("ad-ph-pills", "ad-ph-headline", "ad-ph-form", "ad-ph-next", "ad-ph-medals", "ad-ph-tag"):
        assert not _find(bare, cls), cls
    full = profile_hero("Zed", value="#1", band_label="GCC class", pills=[profile_pill("Level", "level"), None],
                        headline="One line.", form=[{"text": "W", "kind": "win"}], next_step="5 places",
                        medals="tally", meta=["Squash", "", "Age 22"])
    for cls in ("ad-ph-pills", "ad-ph-headline", "ad-ph-form", "ad-ph-next", "ad-ph-medals", "ad-ph-tag"):
        assert _find(full, cls), cls
    assert "Squash · Age 22" in _texts(full)


def test_profile_pill_tones_and_none():
    assert profile_pill("x", "warn").className == "ad-ph-pill is-warn"
    assert profile_pill("x", "loud").className == "ad-ph-pill is-plain"
    assert profile_pill("") is None and profile_pill(None) is None
