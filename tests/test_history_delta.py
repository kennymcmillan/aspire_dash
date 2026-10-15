"""history_figure: every 'vs last' change shows absolute AND percentage (0.105.0)."""
from aspire_dash.charts import _hist_fmt_delta, history_figure

SERIES = [("2026-04-26", 1343.0), ("2026-09-30", 1263.0), ("2026-10-14", 1726.0)]


def test_delta_with_unit_shows_absolute_and_percent():
    assert _hist_fmt_delta(462.23, "N", 1263.0) == "+462.23 N (+36.6%)"


def test_unitless_delta_shows_absolute_and_percent():
    assert _hist_fmt_delta(0.12, "", 3.0) == "+0.12 (+4.0%)"


def test_no_previous_value_shows_absolute_only():
    assert _hist_fmt_delta(1.5, "cm", None) == "+1.50 cm"
    assert _hist_fmt_delta(1.5, "cm", 0) == "+1.50 cm"


def test_missing_delta_is_blank():
    assert _hist_fmt_delta(None, "cm", 10) == ""


def test_latest_label_carries_both():
    texts = [a.text or "" for a in history_figure(SERIES, unit="N").layout.annotations]
    assert "+463 N (+36.7%) vs last" in texts


def test_every_bar_hover_shows_change_vs_previous_test():
    fig = history_figure(SERIES, unit="N", title="Peak Force")
    bar = fig.data[0]
    hover = [str(c[0]) for c in bar.customdata]
    assert hover[0] == "first test"
    assert hover[1] == "-80 N (-6.0%)"
    assert hover[2] == "+463 N (+36.7%)"
    assert "vs last" in bar.hovertemplate and "%{customdata[0]}" in bar.hovertemplate


def test_delta_precision_matches_the_value():
    from aspire_dash.charts import _delta_dp
    assert _delta_dp(29703.0, "N/m") == 0
    assert _delta_dp(0.167, "s") == 3
    assert _delta_dp(42.1, "cm") == 2
