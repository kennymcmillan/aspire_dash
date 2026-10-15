"""v0.106.0: draw path, inline ranks, upset star, event pill, bare flags (promoted from Fencing Reports)."""
import json

from plotly.utils import PlotlyJSONEncoder

from aspire_dash.draw import (bye_step, draw_columns, draw_path, draw_rows, finish_step, lead_step, loss_step,
                              round_depth, short_round, win_step)
from aspire_dash.sports import country_flag, event_pill, rank_pill, rank_pills, upset_star


def _txt(c):
    return json.dumps(c, cls=PlotlyJSONEncoder)


def _classes(c, out=None):
    out = [] if out is None else out
    if c is None or isinstance(c, (str, int, float)):
        return out
    if isinstance(c, (list, tuple)):
        for x in c:
            _classes(x, out)
        return out
    cls = getattr(c, "className", None)
    if cls:
        out.append(cls)
    _classes(getattr(c, "children", None), out)
    return out


def test_short_round_and_depth_order():
    assert [short_round(x) for x in ("Table of 64", "Round of 32", "Quarter-finals", "Final", "Semi-final")] == \
        ["T64", "R32", "QF", "F", "SF"]
    assert sorted(["F", "QF", "T32", "T128", "SF", "T64"], key=round_depth) == ["T128", "T64", "T32", "QF", "SF", "F"]


def test_columns_align_rounds_across_athletes_lead_first_finish_last():
    a = [lead_step("POOLS", "5V / 6"), bye_step("Table of 128"), win_step("Table of 64", "15-10"), finish_step(32)]
    b = [lead_step("POOLS", "2V / 6"), loss_step("Table of 128", "8-15"), finish_step(100)]
    assert draw_columns([a, b]) == ["POOLS", "T128", "T64", "FINISH"]


def test_path_draws_pills_lines_rank_and_star():
    steps = [lead_step("POOLS", "5V / 6"), win_step("Table of 64", "15-10", opp="NOVAK", nation="CZE", rank=60,
                                                    star=True), loss_step("Table of 32", "12-15"), finish_step(17)]
    out = draw_path(steps)
    cls = _classes(out)
    assert "draw-pill draw-pill--lead" in cls and "draw-pill draw-pill--win" in cls and "draw-pill draw-pill--loss" in cls
    assert "draw-finish" in cls                                   # 17th: outlined, no medal class
    assert "draw-line draw-line--in draw-line--win" in cls and "draw-line draw-line--in draw-line--loss" in cls
    t = _txt(out)
    assert "#60" in t and "upset-star" in t and "NOVAK" in t and "17th" in t and "/cz.png" in t


def test_gap_column_gets_a_line_through_and_medal_finish():
    a = [win_step("Table of 64", "15-3"), win_step("Final", "15-14"), finish_step(1)]
    b = [win_step("Table of 64", "15-3"), win_step("Table of 32", "15-9")]
    cols = draw_columns([a, b])
    assert cols == ["T64", "T32", "F", "FINISH"]
    cls = _classes(draw_path(a, cols))
    # T32 is empty for `a`: its cell still carries the line in and out
    assert cls.count("draw-line draw-line--in draw-line--win") == 2
    assert "draw-finish draw-finish--1" in cls


def test_empty_inputs_render_nothing():
    assert draw_path([]) is None and draw_path([None]) is None
    assert draw_rows([("x", [])]) is None
    assert finish_step(None) is None


def test_rows_share_columns():
    out = draw_rows([("A", [win_step("Table of 32", "15-1")]), ("B", [loss_step("Table of 64", "1-15")])],
                    title="Path through the draw")
    t = _txt(out)
    assert t.count('"gridTemplateColumns": "repeat(2, minmax(84px, 1fr))"') == 2 and "Path through the draw" in t


def test_rank_pill_label_and_inline_variant():
    assert "EuroF cadet" in _txt(rank_pill(89, "EuroF cadet")) and "rank-other" in _txt(rank_pill(89, "EuroF cadet"))
    inline = rank_pill(89, "EuroF cadet", variant="inline")
    assert "#89" in _txt(inline) and "fa-ranking-star" in _txt(inline) and "rank-inline" in _txt(inline)
    assert rank_pill(None, variant="inline") is None
    assert "rank-na" in _txt(rank_pill(None))                        # default variant unchanged
    assert rank_pill(5).children == "5"                              # unchanged without a label


def test_rank_pills_skips_unranked():
    out = _txt(rank_pills([("EuroF cadet", 89), ("FIE", None), ("FIE junior", 120)]))
    assert "#89" in out and "#120" in out and out.count("rank-inline\"") == 2
    assert rank_pills([("FIE", None)]) is None and rank_pills(None) is None


def test_upset_star_and_event_pill():
    assert "upset-star" in upset_star().className
    assert "player" in upset_star("Win over a player ranked above").title
    ind, team = _txt(event_pill("individual")), _txt(event_pill("team"))
    assert "INDIVIDUAL EVENT" in ind and "event-pill--individual" in ind and "fa-user\"" in ind
    assert "TEAM EVENT" in team and "event-pill--team" in team and "fa-users" in team
    assert "TEAM EVENT" in _txt(event_pill(True))


def test_country_flag_bare_is_one_element():
    img = country_flag("qat", size="sm", bare=True, className="x")
    assert img.__class__.__name__ == "Img" and img.src.endswith("/qa.png") and "flag-img--sm" in img.className
    assert "x" in img.className.split()
    assert country_flag("", bare=True) is None and country_flag(None, bare=True) is None
    assert country_flag("AIN", bare=True).children == "AIN"
    # default unchanged: span wrapper, empty span for no code
    assert country_flag("QAT").className.startswith("flag-chip flag-chip--md")
    assert country_flag(None).__class__.__name__ == "Span"
