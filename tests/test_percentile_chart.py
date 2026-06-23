"""percentile_age_chart: per-band-PB percentile -> bigger star + hover text.

Pairs with aspire_data.benchmarks.best_pb_by_ageband(with_percentile=True):
each age-band PB carries a percentile; the star scales with it (best-for-age =
biggest) and the hover surfaces the number. No percentile = today's behaviour.
"""
from __future__ import annotations

from aspire_dash.plots import percentile_age_chart


def _band_pbs():
    return [
        {"age": 13.0, "mark": 5.5, "pb": True, "percentile": 40},
        {"age": 14.0, "mark": 6.0, "pb": True, "percentile": 80},
    ]


def _star_trace(fig):
    return next(t for t in fig.data if getattr(t.marker, "symbol", None) == "star")


def test_pb_star_size_scales_with_percentile():
    star = _star_trace(percentile_age_chart(marks=_band_pbs()))
    sizes = list(star.marker.size)
    assert len(sizes) == 2
    assert sizes[1] > sizes[0]          # 80th pct star bigger than the 40th


def test_hover_surfaces_percentile():
    star = _star_trace(percentile_age_chart(marks=_band_pbs()))
    assert "%{text}" in star.hovertemplate
    texts = list(star.text)
    assert "40th pct" in texts[0]
    assert "80th pct" in texts[1]


def test_no_percentile_keeps_uniform_star():
    marks = [{"age": 13, "mark": 5.5, "pb": True},
             {"age": 14, "mark": 6.0, "pb": True}]
    star = _star_trace(percentile_age_chart(marks=marks))
    assert star.marker.size == 19       # scalar, unchanged from before
    assert all(t == "" for t in star.text)


def test_time_format_still_applies_with_percentile():
    # value_format="time" must still format the y value; percentile text rides along
    marks = [{"age": 16.0, "mark": 110.0, "pb": True, "percentile": 75}]
    star = _star_trace(percentile_age_chart(marks=marks, value_format="time",
                                            lower_is_better=True))
    assert "customdata[0]" in star.hovertemplate   # y replaced by formatted value
    assert "%{text}" in star.hovertemplate         # percentile suffix preserved
    assert "75th pct" in list(star.text)[0]
