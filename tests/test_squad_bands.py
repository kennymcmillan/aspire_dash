"""0.107: band components + squad overview (promoted from endurance-dashboard).
Mock values only."""
import dash
from dash import dcc, html

from aspire_dash.components import (
    aspire_tabs, asymmetry_card, band_gauge, band_gauge_card, band_index, band_position,
    band_profile, band_radar, gap_to_next, panel_status, percentile_ring, register_spotlight,
    spotlight, spotlight_hero, spotlight_thumb, stat_chip, metric_panel, tier_card, view_switch)

UP = [("Development", None, 30), ("Typical-Good", 30, 40), ("Strong", 40, 45),
      ("Very strong", 45, None)]
# lower is better (contact time, s): listed worst -> best, high -> low
DOWN = [("Development", 0.220, None), ("Typical-Good", 0.180, 0.220),
        ("Strong", 0.165, 0.180), ("Very strong", None, 0.165)]


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
    return out


# ---- band maths -------------------------------------------------------------
def test_band_index_both_directions():
    assert [band_index(v, UP) for v in (10, 30, 42, 60)] == [0, 1, 2, 3]
    assert [band_index(v, DOWN) for v in (0.25, 0.20, 0.17, 0.15)] == [0, 1, 2, 3]


def test_band_position_inside_own_segment_and_monotone():
    p = [band_position(v, UP) for v in (20, 35, 42.5, 50)]
    assert p == sorted(p)
    assert 25 < band_position(35, UP) < 50          # Typical-Good = 2nd quarter
    assert band_position(35, UP) == 37.5            # midpoint of 30..40
    # faster contact = further right
    assert band_position(0.15, DOWN) > band_position(0.20, DOWN)
    assert 75 < band_position(0.15, DOWN) <= 100


def test_gap_to_next():
    assert gap_to_next(42, UP, "cm") == "3.0 cm to Very strong (+7.1%)"
    assert gap_to_next(50, UP, "cm") == "top band"
    assert gap_to_next(0.19, DOWN, "s").startswith("0.010 s to Strong (-5.3%)")


# ---- gauge + card -----------------------------------------------------------
def test_gauge_marks_current_band_and_cutoffs():
    g = band_gauge(42, UP)
    cur = [x for x in _walk(g) if "ad-gauge-name is-cur" in (getattr(x, "className", "") or "")]
    assert [x.children for x in cur] == ["Strong"]
    marker = [x for x in _walk(g) if getattr(x, "className", "") == "ad-gauge-marker"][0]
    assert marker.style["left"] == f"{band_position(42, UP):.1f}%"
    cuts = [x.children for x in _walk(g) if getattr(x, "className", "") == "ad-gauge-cut"]
    assert cuts == ["30", "40", "45"]


def test_gauge_card_change_and_empty():
    c = band_gauge_card("CMJ Jump Height", 42.0, "cm", UP, date="01-Oct-2026", delta=4.0, prev=38.0)
    t = " ".join(_texts(c))
    assert "+4.00 cm (+10.5%)" in t and "3.0 cm to Very strong" in t and "01-Oct-2026" in t
    assert "first test" in " ".join(_texts(band_gauge_card("X", 42.0, "cm", UP)))
    e = band_gauge_card("X", None, "cm", UP)
    assert "is-empty" in e.className and "no data" in _texts(e)
    assert "no reference band" in _texts(band_gauge_card("X", 2873.0, "N"))


def test_radar_traces_and_scale():
    rows = [{"label": "A", "value": 42, "prev": 35, "bands": UP, "unit": "cm"},
            {"label": "B", "value": 0.15, "bands": DOWN, "unit": "s"},
            {"label": "C", "value": 20, "prev": 25, "bands": UP}]
    fig = band_radar(rows)
    names = [t.name for t in fig.data]
    assert names[:4] == ["band 4", "band 3", "band 2", "band 1"]
    assert "Previous" in names and names[-1] == "Latest"
    latest = fig.data[-1]
    assert list(latest.r)[:3] == [band_position(42, UP) * 4 / 100, band_position(0.15, DOWN) * 4 / 100,
                                  band_position(20, UP) * 4 / 100]
    assert list(latest.r)[-1] == list(latest.r)[0]          # closed shape
    assert fig.layout.polar.radialaxis.range == (0, 4)
    no_prev = band_radar([{"label": "A", "value": 42, "bands": UP}])
    assert "Previous" not in [t.name for t in no_prev.data]


def test_profile_radar_flag_keeps_row_in_list():
    rows = [{"label": "A", "value": 42, "bands": UP}, {"label": "B", "value": 0.2, "bands": DOWN, "radar": False},
            {"label": "C", "value": None, "bands": UP}]
    p = band_profile(rows, ring_names=["D", "T", "S", "V"])
    g = [x for x in _walk(p) if isinstance(x, dcc.Graph)][0]
    assert list(g.figure.data[-1].theta) == ["A", "A"]      # B off the radar
    names = [x.children for x in _walk(p) if getattr(x, "className", "") == "ad-prof-name"]
    assert names == ["A", "B"]                                # C (no value) dropped
    assert "No banded tests" in band_profile([]).children


def test_panel_status_and_panel():
    assert panel_status([(1, False), (-0.01, True), (-2, False)]) == ("2 of 3 improved", "up")
    assert panel_status([(None, False)]) == (None, "")
    assert panel_status([(1, False), (-1, False)])[1] == ""
    p = metric_panel("CMJ", [html.Div("c")], subtitle="lower-body power", icon="fa-dumbbell",
                   family="force", date="01-Oct-2026", status=("1 of 1 improved", "up"), span=2, cols=4)
    assert p.className == "ad-panel fam-force span-2"
    cls = _classes(p)
    assert "ad-chip up" in cls and "ad-panel-cards cols-4" in cls and "ad-panel-icon" in cls


def test_asymmetry():
    a = asymmetry_card(600, 400, left_date="d1", right_date="d1")
    t = _texts(a)
    assert "17% Left" not in t and "33% Left" in t and "L 60%" in t and "R 40%" in t
    assert "latest d1" in t
    assert "Even" in _texts(asymmetry_card(500, 498))
    assert "L a · R b" in _texts(asymmetry_card(1, 2, left_date="a", right_date="b"))
    assert "no data" in _texts(asymmetry_card(None, 2))


# ---- squad ------------------------------------------------------------------
def test_ring():
    r = percentile_ring(73.4, "target")
    assert "ad-band-target" in r.className and "73.4%" in r.style["background"]
    assert "P73" in _texts(r)
    e = percentile_ring(None)
    assert "is-empty" in e.className and _texts(e) == ["–"]
    assert "P100" in _texts(percentile_ring(140))


def test_tier_card_band_is_data_and_optionals_absent():
    c = tier_card("Athlete A", band="AG Medal", band_label="AG medal contender", value="#6", scope="world")
    card = c
    assert "ad-band-ag-medal" in card.className
    t = _texts(card)
    assert "AG MEDAL CONTENDER" in t and "#6" in t and " world" in t
    cls = _classes(card)
    for absent in ("ad-ring", "ad-status", "ad-att-wrap", "ad-pos", "ad-card-foot"):
        assert not any(x.split(" ")[0] == absent for x in cls), absent
    q = tier_card("Athlete B")
    assert "–" in _texts(q) and "ad-band-squad" in q.className


def test_tier_card_full():
    c = tier_card("Athlete C", band="target", band_label="Target", corner="Grade 3",
                  sub=["QAT", "16.7y", "U18"], value_label="800m PB", value="1:52.40", pct=81,
                  position=1, status=("Available", "ok"), attendance=(100, 93),
                  footer=html.Div("next step", className="x-foot"),
                  href="/competition?id=1", data={"band": "U18", "skip": None})
    assert isinstance(c, html.A) and c.href == "/competition?id=1"
    assert getattr(c, "data-band") == "U18" and not hasattr(c, "data-skip")
    cls = _classes(c)
    for present in ("ad-ring ad-ring-md ad-band-target", "ad-status", "ad-pos ad-pos-1",
                    "ad-att-fill is-mid", "x-foot", "ad-card-foot"):
        assert present in cls, present
    t = _texts(c)
    assert "Grade 3" in t and "93%" in t and "QAT" in t
    d = tier_card("Athlete D", href="/x", link="dcc")
    assert isinstance(d.children, dcc.Link)
    assert "ad-ring" in " ".join(_classes(tier_card("E", ring=True)))


def test_spotlight_shell_and_heroes():
    heroes = [spotlight_hero(i, f"Athlete {c}", band="future", value="4:01", pct=None,
                             bars=[("2025", 60), ("2026", 72)],
                             rows=[{"date": "01 Oct", "title": "Meet", "result": "4:05", "pos": "1"}],
                             data={"band": "U20"}) for i, c in enumerate("AB")]
    assert heroes[0].style is None and heroes[1].style == {"display": "none"}
    assert getattr(heroes[1], "data-spot") == "1" and getattr(heroes[1], "data-band") == "U20"
    cls = _classes(heroes[0])
    assert "ad-row-pos is-win" in cls and cls.count("ad-bar-col") == 2
    plain = spotlight_hero(0, "Athlete Z")
    assert "ad-bars" not in _classes(plain) and "ad-row" not in _classes(plain)
    thumbs = [spotlight_thumb(i, f"Athlete {c}", id="sq") for i, c in enumerate("AB")]
    assert thumbs[0].id == {"type": "sq-thumb", "index": 0} and "is-active" in thumbs[0].className
    s = spotlight(heroes, thumbs, id="sq")
    ids = [getattr(x, "id", None) for x in _walk(s)]
    for i in ("sq-root", "sq-prev", "sq-next", "sq-pos", "sq-idx"):
        assert i in ids
    pos = [x for x in _walk(s) if getattr(x, "id", None) == "sq-pos"][0]
    assert pos.children == "1 / 2"


def _registered(output_fragment):
    from dash._callback import GLOBAL_CALLBACK_LIST
    return [c for c in GLOBAL_CALLBACK_LIST if output_fragment in str(c.get("output"))]


def test_register_spotlight_and_view_switch():
    register_spotlight("tsq", filter_id="tsq-filter")
    cb = _registered("tsq-idx.data")
    assert cb and any("tsq-filter" in str(c["inputs"]) for c in cb)
    fn = cb[-1]["clientside_function"]["function_name"]
    assert fn
    register_spotlight("tsq2")
    assert not any("filter" in str(c["inputs"]) for c in _registered("tsq2-idx.data"))
    view_switch("tview", {"cards": "tview-a", "spot": "tview-b"})
    vb = _registered("tview-a.style")
    assert vb and "tview-b.style" in str(vb[-1]["output"])


def test_aspire_tabs_keep_row_and_persistence():
    t = aspire_tabs("t", [{"label": "A", "value": "a"}], keep_row=True, persistence="session")
    assert t.mobile_breakpoint == 0 and t.persistence is True and t.persistence_type == "session"
    plain = aspire_tabs("t2", [{"label": "A", "value": "a"}])
    assert getattr(plain, "mobile_breakpoint", None) != 0
    assert not getattr(plain, "persistence", False)


def test_stat_chip():
    s = stat_chip(12, "Squad", "#0f7b3f")
    assert _texts(s) == ["12", "Squad"] and s.children[0].style["color"] == "#0f7b3f"


def test_css_ships_every_class_used():
    import re
    from pathlib import Path
    import aspire_dash
    css = (Path(aspire_dash.__file__).parent / "assets" / "07_squad_bands.css").read_text(encoding="utf-8")
    for k in ("ad-band-target", "ad-band-future", "ad-tier-card", "ad-gauge-marker", "ad-hero-left",
              "ad-panel", "ad-prof-row", "ad-thumb", "ad-pos-1", "ad-att-fill"):
        assert re.search(r"\." + re.escape(k) + r"\b", css), k


def test_band_position_descending_exact():
    # 0.170 s sits 2/3 of the way from the Strong band's slow edge (0.180) to its fast edge (0.165)
    assert round(band_position(0.170, DOWN), 2) == round((2 + 2 / 3) / 4 * 100, 2)
    assert band_position(0.168, DOWN) > band_position(0.175, DOWN)


def test_radar_ring_count_sets_scale():
    fig = band_radar([{"label": "A", "value": 42, "bands": UP}], rings=5)
    assert fig.layout.polar.radialaxis.range == (0, 5)
    assert [t.name for t in fig.data][:5] == ["band 5", "band 4", "band 3", "band 2", "band 1"]
    assert fig.data[-1].r[0] == band_position(42, UP) * 5 / 100


def test_tier_card_without_link_keeps_data_attrs():
    c = tier_card("Athlete F", data={"band": "U18"})
    assert getattr(c, "data-band") == "U18" and c.className == "ad-tier-cell"
    assert "ad-tier-card" in c.children.className


def test_only_first_place_gets_the_win_chip():
    rows = [{"date": "d", "title": "t", "result": "r", "pos": p} for p in ("1st", "10th", "11", "1", "2nd")]
    h = spotlight_hero(0, "Athlete W", rows=rows)
    pos = [x.className for x in _walk(h) if (getattr(x, "className", "") or "").startswith("ad-row-pos")]
    assert pos == ["ad-row-pos is-win", "ad-row-pos", "ad-row-pos", "ad-row-pos is-win", "ad-row-pos"]


def test_avatar_photo_alt_text_never_spills():
    from aspire_dash.athlete import athlete_avatar
    img = athlete_avatar("https://example.invalid/x.jpg", "Athlete Q", size=44)
    node = next(x for x in _walk(img) if getattr(x, "style", None) and "objectFit" in x.style)
    assert node.style["color"] == "transparent" and node.style["fontSize"] == "0"


# ---- photo card (0.109) ------------------------------------------------------
def test_photo_card_full():
    from aspire_dash.components import photo_card
    c = photo_card("Athlete Middle Alpha", photo="https://example.invalid/p.jpg", band="target",
                   tab_caption="Target · 800m PB", tab_value="1:50.85", pct=90,
                   injury=("Calf", "bad"), recovery=72, flag=("Load 1.6", "bad"),
                   meta=["QAT", "U20"], chip="GCC class", stats=[("800m PB", "1:50.85"), ("1500m PB", None)],
                   last={"title": "Mock Meet", "result": "1st · 1:51.20", "ago": "3w ago", "win": True},
                   attendance=93, hover="Short summary.", href="/competition?id=1", data={"band": "U20"})
    assert isinstance(c, html.A) and c.title == "Short summary." and getattr(c, "data-band") == "U20"
    t = _texts(c)
    assert "ALPHA" in t and "Athlete Middle" in t and "1:50.85" in t and "P90" in t
    assert "Calf" in t and "72" in t and "Load 1.6" in t and "GCC class" in t and "–" in t
    cls = _classes(c)
    for k in ("ad-pc ad-band-target", "ad-pc-pill is-bad", "ad-pc-dot is-win", "ad-att-fill is-mid",
              "ad-pc-ring", "ad-pc-chip", "ad-pc-img"):
        assert k in cls, k
    rec = next(x for x in _walk(c) if getattr(x, "className", "") == "ad-pc-rec")
    assert "#16a34a 0 72.0%" in rec.style["background"]


def test_photo_card_minimal_leaves_parts_out():
    from aspire_dash.components import photo_card
    c = photo_card("Solo")
    cls = _classes(c)
    for absent in ("ad-pc-tab", "ad-pc-status", "ad-pc-ring", "ad-pc-meta", "ad-pc-stats",
                   "ad-pc-lastrow", "ad-pc-att"):
        assert not any(x.split(" ")[0] == absent for x in cls), absent
    assert "SOLO" in _texts(c) and "ad-pc-img is-initials" in cls
    assert c.className == "ad-tier-cell" and not hasattr(c, "title")


def test_photo_card_recovery_zones_and_warn_flag():
    from aspire_dash.components import photo_card
    def rec_bg(v):
        c = photo_card("A B", recovery=v)
        return next(x for x in _walk(c) if getattr(x, "className", "") == "ad-pc-rec").style["background"]
    assert "#ca8a04" in rec_bg(50) and "#dc2626" in rec_bg(20) and "#16a34a" in rec_bg(67)
    assert "ad-pc-pill is-warn" in _classes(photo_card("A B", flag=("Load 1.4", "warn")))
    assert "ad-pc-pill is-warn" in _classes(photo_card("A B", injury=("Knee", "warn")))
