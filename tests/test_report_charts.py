"""v0.72.0 chart promotions from the Development Testing Dashboard:
bar value labels, categorical-date x-axis, two-line month/year ticks,
apply_break, add_injury_markers. Deterministic, no network."""
import pandas as pd
import plotly.graph_objects as go

from aspire_dash.report import (
    combo_chart, trend_rich, multiline_chart,
    date_categories, categorical_date_axis, apply_break, add_injury_markers,
    COMBO_BAR_LABEL, DATE_TICK_FORMAT,
)

DATES = ["2026-01-15", "2026-03-20", "2026-06-05"]


def _bars_and_line():
    bars = [("CMJ", DATES, [30.0, 32.0, 35.0], "#01B8AA", 1)]
    line = ("RSI", DATES, [1.1, 1.2, 1.3], 2)
    return bars, line


def _bar_traces(fig):
    return [t for t in fig.data if t.type == "bar"]


# ── 1. Bar value labels ──────────────────────────────────────────────────────

def test_combo_chart_bar_labels_none_is_legacy():
    """Default (bar_labels=None) keeps the pre-0.72 behaviour: columns labelled
    per label_mode='last' (only the final column carries text)."""
    bars, line = _bars_and_line()
    fig = combo_chart(bars, line)
    bar = _bar_traces(fig)[0]
    assert list(bar.text) == ["", "", "35.0"]           # only last labelled
    assert fig.layout.yaxis.automargin is None            # no headroom forced


def test_combo_chart_bar_labels_true_labels_all_in_pop_navy():
    bars, line = _bars_and_line()
    fig = combo_chart(bars, line, bar_labels=True)
    bar = _bar_traces(fig)[0]
    assert list(bar.text) == ["30.0", "32.0", "35.0"]     # every column labelled
    assert bar.textfont.color == COMBO_BAR_LABEL == "#004185"
    assert bar.textposition == "outside"
    assert fig.layout.yaxis.automargin is True            # headroom reserved


def test_combo_chart_bar_labels_false_drops_bar_text():
    bars, line = _bars_and_line()
    fig = combo_chart(bars, line, bar_labels=False)
    bar = _bar_traces(fig)[0]
    assert bar.text is None
    # the secondary-axis line is unaffected by bar_labels (still per label_mode)
    line_tr = [t for t in fig.data if t.type == "scatter"][0]
    assert list(line_tr.text) == ["", "", "1.30"]


def test_combo_chart_bar_label_color_override():
    bars, line = _bars_and_line()
    fig = combo_chart(bars, line, bar_labels=True, bar_label_color="#050574")
    assert _bar_traces(fig)[0].textfont.color == "#050574"


# ── 2. Categorical date axis ─────────────────────────────────────────────────

def test_combo_chart_categorical_x_converts_dates():
    bars, line = _bars_and_line()
    fig = combo_chart(bars, line, categorical_x=True)
    assert fig.layout.xaxis.type == "category"
    assert fig.layout.xaxis.categoryorder == "array"
    # each tick label is a two-line month/year string
    for lab in fig.layout.xaxis.categoryarray:
        assert "<br>" in lab
    # bar + line x values are now the category labels (strings), not timestamps
    for tr in fig.data:
        assert all(isinstance(x, str) and "<br>" in x for x in tr.x)


def test_combo_chart_default_x_is_not_categorical():
    """Opt-in only: without categorical_x the axis stays a real date axis."""
    bars, line = _bars_and_line()
    fig = combo_chart(bars, line)
    assert fig.layout.xaxis.type != "category"


def test_date_categories_disambiguates_same_month():
    order, label = date_categories(["2026-01-05", "2026-01-20", "2026-02-10"])
    assert len(order) == 3
    # two dates share Jan -> fall back to day-level labels for the whole set
    assert label[pd.Timestamp("2026-01-05")] == "05 Jan<br>2026"
    assert label[pd.Timestamp("2026-01-20")] == "20 Jan<br>2026"


def test_date_categories_month_year_when_unique():
    _order, label = date_categories(DATES)
    assert label[pd.Timestamp("2026-01-15")] == "Jan<br>2026"


def test_categorical_date_axis_noop_on_non_dates():
    fig = go.Figure(go.Bar(x=["A", "B", "C"], y=[1, 2, 3]))
    categorical_date_axis(fig)
    # not date-like -> axis left untouched (no forced category type)
    assert fig.layout.xaxis.type != "category"
    assert list(fig.data[0].x) == ["A", "B", "C"]


# ── 3. Two-line month/year date ticks ────────────────────────────────────────

def test_trend_rich_two_line_date_ticks_default():
    fig = trend_rich(DATES, [10, 11, 12], "cm")
    assert fig.layout.xaxis.tickformat == DATE_TICK_FORMAT == "%b<br>%Y"


def test_trend_rich_date_ticks_off():
    fig = trend_rich(DATES, [10, 11, 12], "cm", date_ticks=False)
    assert fig.layout.xaxis.tickformat is None


def test_multiline_chart_two_line_date_ticks_default():
    series = [("A", DATES, [1, 2, 3], "#004185", 1)]
    fig = multiline_chart(series, "s")
    assert fig.layout.xaxis.tickformat == "%b<br>%Y"


# ── 4. apply_break ───────────────────────────────────────────────────────────

def test_apply_break_ranges_to_data_with_glyph():
    fig = go.Figure(go.Scatter(y=[100.0, 101.0, 102.0]))
    fig.update_yaxes(autorange=True)
    apply_break(fig, [100.0, 101.0, 102.0])
    lo, hi = fig.layout.yaxis.range
    assert lo < 100.0 and hi > 102.0          # padded, not anchored at 0
    assert fig.layout.yaxis.autorange is False
    # 1 white rect + 2 slash lines = the // break glyph
    assert len(fig.layout.shapes) == 3


def test_apply_break_single_point_symmetric_band():
    fig = go.Figure(go.Scatter(y=[50.0]))
    apply_break(fig, [50.0])
    lo, hi = fig.layout.yaxis.range
    assert lo < 50.0 < hi
    assert fig.layout.yaxis.autorange is False


def test_apply_break_empty_is_noop():
    fig = go.Figure(go.Scatter(y=[1.0]))
    apply_break(fig, [])
    assert fig.layout.yaxis.range is None      # untouched
    assert not fig.layout.shapes


# ── 5. add_injury_markers ────────────────────────────────────────────────────

def test_add_injury_markers_overlay_axis():
    fig = go.Figure(go.Scatter(x=DATES, y=[1, 2, 3]))
    before = len(fig.data)
    add_injury_markers(fig, ["2026-02-01", "2026-05-01"], ["Ankle", "Knee"])
    assert len(fig.data) == before + 1
    inj = [t for t in fig.data if t.name == "Injury"][0]
    assert inj.yaxis == "y99"
    assert inj.marker.symbol == "x"
    assert inj.marker.color == "#e74c3c"
    assert list(inj.customdata) == ["Ankle", "Knee"]
    assert "Injury" in inj.hovertemplate
    # hidden overlay axis pinned to [0,1] so the primary y-range is undisturbed
    assert fig.layout.yaxis99.overlaying == "y"
    assert fig.layout.yaxis99.visible is False
    assert tuple(fig.layout.yaxis99.range) == (0, 1)


def test_add_injury_markers_empty_is_noop():
    fig = go.Figure(go.Scatter(x=DATES, y=[1, 2, 3]))
    before = len(fig.data)
    add_injury_markers(fig, [])
    assert len(fig.data) == before
