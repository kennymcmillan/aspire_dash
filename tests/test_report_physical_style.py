"""v0.97.0 promotions from the Development Testing Dashboard: the "physical"
combo style (boxed bar + line values, rounded bars, fixed headroom), fit_yaxis,
pad_date_xaxis, and the hover-card clamp asset. Deterministic, no network."""
import math
from pathlib import Path

import pandas as pd

from aspire_dash.report import (COMBO_BAR_LABEL, COMBO_LINE, combo_chart,
                                fit_yaxis, pad_date_xaxis, trend_rich)

DATES = ["2025-10-10", "2026-01-12", "2026-04-03", "2026-09-20"]
BARS = [("Contact", DATES, [150.0, 145.0, 148.0, 142.0], "#01B8AA", 0)]
LINE = ("Tf/Tc", DATES, [2.6, 2.8, 3.0, 3.1], 1)


def _physical(bars=BARS, line=LINE):
    return combo_chart(bars, line, "ms", "Tf/Tc", bar_labels=True, categorical_x=True,
                       boxed_labels=True, rounded_bars=True, headroom=0.15)


def _ann(fig, bg):
    return [a for a in fig.layout.annotations if a.bgcolor == bg]


def test_defaults_unchanged():
    """Opt-in only: an app that passes none of the new flags gets the old chart."""
    fig = combo_chart(BARS, LINE, "ms", "Tf/Tc")
    assert not fig.layout.annotations
    assert fig.layout.yaxis.range is None and fig.layout.yaxis2.range is None
    assert "text" in [t for t in fig.data if t.type == "scatter"][0].mode


def test_boxed_bar_values_inside_column_top():
    fig = _physical()
    boxes = _ann(fig, "white")
    assert [a.text for a in boxes] == ["<b>150</b>", "<b>145</b>", "<b>148</b>", "<b>142</b>"]
    assert all(a.yanchor == "top" and a.font.color == COMBO_BAR_LABEL for a in boxes)
    assert [t.textposition for t in fig.data if t.type == "bar"] == ["none"]


def test_boxed_line_values_above_each_point_black_on_line_colour():
    fig = _physical()
    gold = _ann(fig, COMBO_LINE)
    assert [a.text for a in gold] == ["<b>2.6</b>", "<b>2.8</b>", "<b>3.0</b>", "<b>3.1</b>"]
    assert all(a.yref == "y2" and a.yanchor == "bottom" and a.font.color == "#000000"
               for a in gold)
    assert "text" not in [t for t in fig.data if t.type == "scatter"][0].mode


def test_boxed_labels_skip_missing_points():
    fig = _physical(line=("Tf/Tc", DATES, [2.6, None, float("nan"), 3.1], 1))
    assert [a.text for a in _ann(fig, COMBO_LINE)] == ["<b>2.6</b>", "<b>3.1</b>"]


def test_grouped_bar_labels_sit_over_their_own_column():
    bars = [("a", DATES, [1, 2, 3, 4], "#01B8AA", 0), ("b", DATES, [5, 6, 7, 8], "#7DD3CC", 0)]
    fig = _physical(bars=bars)
    a, b = [t for t in fig.data if t.type == "bar"]
    xs = {an.text: an.x for an in _ann(fig, "white")}
    assert math.isclose(xs["<b>1</b>"], a.offset + a.width / 2)          # category 0
    assert math.isclose(xs["<b>8</b>"], 3 + b.offset + b.width / 2)      # category 3


def test_headroom_fixes_both_axes():
    fig = _physical()
    assert list(fig.layout.yaxis.range) == [0, 150 * 1.15]
    assert list(fig.layout.yaxis2.range) == [0, 3.1 * 1.15]
    assert fig.layout.yaxis.autorange is False and fig.layout.yaxis2.autorange is False


def test_headroom_with_empty_line():
    fig = combo_chart(BARS, ("F/BM", [], [], 1), "N", "N/kg", categorical_x=True,
                      boxed_labels=True, headroom=0.15)
    assert list(fig.layout.yaxis.range) == [0, 150 * 1.15]
    assert fig.layout.yaxis2.range is None


def test_rounded_bars():
    fig = _physical()
    assert [t.marker.cornerradius for t in fig.data if t.type == "bar"] == [4]
    assert fig.layout.bargap == 0.30


def test_fit_yaxis_centres_with_min_span_and_beats_autorange():
    fig = trend_rich(pd.to_datetime(DATES[:3]), [50.0, 51.0, 52.0], "kg")
    fit_yaxis(fig, [50.0, 51.0, 52.0], min_span=8.0)
    lo, hi = fig.layout.yaxis.range
    assert fig.layout.yaxis.autorange is False          # trend_rich turns it on
    assert (lo, hi) == (45, 57)
    assert hi - lo >= 8 and lo < 50 and hi > 52


def test_fit_yaxis_uses_real_span_when_bigger():
    fig = trend_rich(pd.to_datetime(DATES[:3]), [140.0, 150.0, 165.0], "cm")
    fit_yaxis(fig, [140.0, 150.0, 165.0], min_span=10.0)
    lo, hi = fig.layout.yaxis.range
    assert lo <= 135 and hi >= 170


def test_fit_yaxis_no_data_is_noop():
    fig = trend_rich(pd.to_datetime(DATES[:1]), [1.0], "u")
    before = fig.layout.yaxis.range
    fit_yaxis(fig, [None, float("nan")])
    assert fig.layout.yaxis.range == before


def test_pad_date_xaxis_iso_strings_around_the_data():
    fig = trend_rich(pd.to_datetime(DATES), [1, 2, 3, 4], "u")
    pad_date_xaxis(fig, DATES)
    lo, hi = fig.layout.xaxis.range
    assert isinstance(lo, str) and lo < "2025-10-10" and hi > "2026-09-20"
    assert fig.layout.xaxis.autorange is False
    fig.to_json()                                        # serialisable (kaleido/Dash)


def test_clamp_asset_ships_with_the_library():
    import aspire_dash
    js = Path(aspire_dash.__file__).parent / "assets" / "hovercard_clamp.js"
    src = js.read_text(encoding="utf-8")
    assert "hc-nudged" in src and "MutationObserver" in src
    css = (js.parent / "00_aspire_base.css").read_text(encoding="utf-8")
    assert ".hover.hc-nudged::before" in css
