"""0.108: ladder + steps + season-by-season chart, promoted from High Management Overview (tests ported from
HMO tests/test_ladder.py). Fixtures use the API journey step shapes (brief?view=page). No network."""
from types import SimpleNamespace

from aspire_dash.components import ladder  # the module; the card is exported as ladder_card


def _rung(label, mark, value, state, stage, gap=None, won=None, holder=None, kind="rung"):
    return {"kind": kind, "label": label, "mark": mark, "value": value, "state": state, "stage": stage, "gap": gap,
            "won": won, "holder": holder, "cleared": state in ("cleared", "before", "youth", "pb", "now")}


ATHLETE = {
    "event": "400m Hurdles", "unit": "s", "lower": True, "rec": SimpleNamespace(name="Basil Hadley"),
    "level": {"now": "World final standard", "peak": None},
    "season_bests": [[2018, 49.59, "49.59"], [2019, 49.33, "49.33"], [2022, 48.67, "48.67"], [2023, 48.52, "48.52"],
                     [2025, 48.29, "48.29"], [2026, 47.56, "47.56"]],
    "corridor": [{"year": 2018, "age": 18, "p75": 53.2, "p90": 51.97, "p95": 51.209},
                 {"year": 2019, "age": 19, "p75": 52.398, "p90": 51.3, "p95": 50.59}],
    "champs": [{"year": 2018, "lane": "yth", "comp": "IAAF World U20 Championships", "mark": "49.59", "medal": 2},
               {"year": 2023, "lane": "reg", "comp": "Arab Championships", "mark": "48.79", "medal": 1},
               {"year": 2026, "lane": "ag", "comp": "20th Asian Games", "mark": "47.82", "medal": 1}],
    "climb": {"steps": [
        _rung("Top 5% for age", "49.59", None, "youth", "Youth", kind="pctl", won={"text": "At 18 (U20): 97th"}),
        _rung("World U20 champs", "49.59", None, "youth", "Youth", kind="youth", won={"medal": 2, "text": "Silver 2018"}),
        _rung("Asian Games medal", "48.95", 48.95, "cleared", "Asia", won={"medal": 1, "text": "Gold 2026"}),
        _rung("World Champs final", "48.39", 48.39, "cleared", "World", won={"round": "SF", "text": "Semi 2023, 2025"}),
        _rung("Best 2026", "47.56", 47.56, "pb", "World", kind="pb"),
        _rung("World Champs medal", "47.31", 47.31, "next", "Podium", gap="0.25"),
        _rung("Olympic medal", "46.99", 46.99, "ahead", "Podium", gap="0.57"),
        _rung("National & area record", "46.98", 46.98, "ahead", "Records", gap="0.58", holder="Area Holder"),
        _rung("Olympic record", "45.94", 45.94, "ahead", "Records", gap="1.62"),
        _rung("Area 4", "45.90", 45.90, "ahead", "Records", gap="1.66"),
        _rung("Area 5", "45.85", 45.85, "ahead", "Records", gap="1.71"),
        _rung("World record", "45.80", 45.80, "ahead", "Records", gap="1.76", holder="Record HOLDER"),
    ]},
}


def _walk(node):
    yield node
    kids = getattr(node, "children", None)
    for k in (kids if isinstance(kids, list) else [kids]):
        if k is not None and not isinstance(k, (str, int, float)):
            yield from _walk(k)


def _text(node):
    out = []
    for n in _walk(node):
        kids = getattr(n, "children", None)
        for k in (kids if isinstance(kids, list) else [kids]):
            if isinstance(k, (str, int, float)):
                out.append(str(k))
    return " ".join(out)


def _rows(sec):
    return [n for n in _walk(sec) if "ad-lj-ld-row" in (getattr(n, "className", "") or "")]


def test_first_beaten_reads_the_season_bests_in_the_right_direction():
    sbs = ATHLETE["season_bests"]
    assert ladder.first_beaten(48.95, sbs, lower=True) == 2022          # 48.67 is the first season under 48.95
    assert ladder.first_beaten(47.31, sbs, lower=True) is None
    assert ladder.first_beaten(2.32, [[2010, 2.31, ""], [2011, 2.35, ""]], lower=False) == 2011


def test_the_ladder_runs_hardest_first_and_marks_the_next_rung():
    sec = ladder.ladder(ATHLETE)
    rows = _rows(sec)
    labels = [_text(r).split(" 4")[0] for r in rows]
    assert "World record" in _text(rows[0])                              # the summit is the top row
    assert "Top 5% for age" in _text(rows[-1])                           # the junior rungs are the bottom rows
    nxt = [r for r in rows if "is-next" in r.className]
    assert len(nxt) == 1 and "0.25 s to go" in _text(nxt[0])
    assert any("is-youth" in r.className for r in rows) and labels


def test_far_rungs_fold_behind_a_button_but_the_summit_stays():
    sec = ladder.ladder(ATHLETE)
    far = [r for r in _rows(sec) if "is-far" in r.className]
    assert [("Area 5" in _text(r)) for r in far] == [True]               # next + 4 shown, summit kept, Area 5 folded
    assert "+1 more rung to the world record" in _text(sec)


def test_a_best_above_the_fold_never_folds_or_counts():
    """Barshim: the career best (2.43) sits above the next rung + 4; it stays shown and the button counts rungs only."""
    steps = [dict(s) for s in ATHLETE["climb"]["steps"]]
    best = steps.pop(4)                                                  # move "Best 2026" up among the far rungs
    steps.insert(10, {**best, "kind": "pb"})
    j = {**ATHLETE, "climb": {"steps": steps}}
    sec = ladder.ladder(j)
    far = [r for r in _rows(sec) if "is-far" in r.className]
    here = [n for n in _walk(sec) if "ad-lj-ld-here" in (getattr(n, "className", "") or "")]
    assert len(here) == 1 and all("47.56" not in _text(r) for r in far)
    assert f"+{len(far)} more rung" in _text(sec) if far else "more rung" not in _text(sec)


def test_the_climber_sits_on_the_best_and_starts_from_the_bottom():
    sec = ladder.ladder(ATHLETE)
    here = [n for n in _walk(sec) if "ad-lj-ld-here" in (getattr(n, "className", "") or "")]
    assert len(here) == 1 and "47.56" in _text(here[0]) and "HH" not in _text(here[0])
    climber = [n for n in _walk(here[0]) if "ad-lj-ld-climber" in (getattr(n, "className", "") or "")][0]
    assert climber.children == "BH" and climber.style["--from"] == f"{4 * ladder.ROW_PX}px"   # 4 rows below it


def test_medal_and_since_chips_come_from_the_record():
    t = _text(ladder.ladder(ATHLETE))
    assert "Gold 2026" in t and "since 2022" in t and "Semi 2023, 2025" in t and "0.57 s off" in t


def test_the_chart_draws_the_corridor_the_rungs_the_medals_and_the_gap():
    fig = ladder.chart_figure(ATHLETE)
    names = [t.name for t in fig.data]
    assert "Top 25% for age" in names and "Top 5% for age" in names and "Season best" in names
    med = [t for t in fig.data if t.name == "Championship medal"][0]
    assert list(med.x) == [2018, 2026]                                   # majors only: the Arab title is regional
    texts = " | ".join(a.text for a in fig.layout.annotations)
    assert "World Champs medal 47.31" in texts and "0.25 s" in texts
    solid = [s for s in fig.layout.shapes if s.line.dash in (None, "solid")]
    dashed = [s for s in fig.layout.shapes if s.line.dash == "dash"]
    assert solid and dashed                                              # beaten rungs solid, ones to beat dashed
    assert fig.layout.yaxis.range[0] > fig.layout.yaxis.range[1]         # hurdles: faster is higher


def test_the_story_reads_the_same_numbers():
    s = ladder.story(ATHLETE)
    assert "top 5% for age at 18 (U20): 97th" in s
    assert "Next: World Champs medal, 0.25 s from the latest season best." in s


def test_no_steps_no_ladder_and_one_season_no_chart():
    assert ladder.ladder({"climb": {"steps": []}}) is None
    assert ladder.season_section({"season_bests": [[2026, 47.56, "47.56"]]}) is None


def _steps(sec):
    return [n for n in _walk(sec) if "ad-lj-st-step" in (getattr(n, "className", "") or "")]


def test_steps_view_runs_easiest_left_with_every_rung_and_the_climber():
    """Kenny 2026-10-13: Steps on desktop (left to right), Ladder on phone; same rungs, same states."""
    sec = ladder.ladder(ATHLETE)
    st = _steps(sec)
    assert len(st) == len(ATHLETE["climb"]["steps"])                      # nothing folded in the steps view
    assert "Top 5% for age" in _text(st[0]) and "World record" in _text(st[-1])
    nxt = [s for s in st if "is-next" in s.className]
    assert len(nxt) == 1 and "0.25 s to go" in _text(nxt[0])
    here = [s for s in st if "is-here" in s.className]
    assert len(here) == 1 and "BH" in _text(here[0])
    heights = [int(s.children[1].style["height"].rstrip("px")) for s in st if "is-here" not in s.className]
    assert heights == sorted(heights)                                    # each step at least as high as the last


def test_class_name_hook_for_page_grids():
    assert ladder.ladder(ATHLETE, className="span-5").className == "ad-lj-card ad-lj-ladder-card span-5"
    assert ladder.season_section(ATHLETE).className == "ad-lj-card"


def test_exported_names_keep_the_module_reachable():
    import aspire_dash.components as c
    assert c.ladder_card is ladder.ladder and c.season_section is ladder.season_section
    assert c.ladder is ladder
