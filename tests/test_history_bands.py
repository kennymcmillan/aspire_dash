"""history_figure(bands=...): shaded performance zones behind the bars (0.103.0)."""
from aspire_dash.charts import history_figure

SERIES = [("2026-08-01", 2.6), ("2026-09-01", 3.2), ("2026-10-01", 3.6)]
BANDS = [("Developing", None, 3.0), ("Good", 3.0, 3.5), ("Very good", 3.5, 4.0),
         ("Elite", 4.0, None)]


def _rects(fig):
    return [s for s in fig.layout.shapes if s.type == "rect"]


def test_bands_draw_one_shaded_rect_each_below_the_bars():
    fig = history_figure(SERIES, unit="x BW", bands=BANDS)
    rects = _rects(fig)
    assert len(rects) == 4
    assert all(r.layer == "below" for r in rects)
    lo, hi = fig.layout.yaxis.range
    # open ends run to the axis edge; every finite edge is inside the range
    assert rects[0].y0 == lo and rects[0].y1 == 3.0
    assert rects[-1].y0 == 4.0 and rects[-1].y1 == hi
    assert lo <= 2.6 and hi >= 4.0


def test_band_labels_drawn_inside_the_plot():
    fig = history_figure(SERIES, unit="x BW", bands=BANDS)
    texts = [a.text for a in fig.layout.annotations]
    for name in ("Developing", "Good", "Very good", "Elite"):
        assert any(name in (t or "") for t in texts)


def test_no_bands_is_unchanged():
    assert _rects(history_figure(SERIES, unit="x BW")) == []


def test_band_labels_carry_their_cut_offs():
    texts = " ".join(a.text or "" for a in history_figure(SERIES, bands=BANDS).layout.annotations)
    assert "&lt; 3" in texts and "3–3.5" in texts and "≥ 4" in texts


def test_band_chips_sit_in_the_right_margin_not_over_the_bars():
    fig = history_figure(SERIES, bands=BANDS)
    chips = [a for a in fig.layout.annotations if a.bgcolor and "Elite" in (a.text or "")
             or (a.bgcolor and "Developing" in (a.text or ""))]
    assert len(chips) == 2 and all(a.x > 1 for a in chips)


def test_open_top_band_gets_at_least_one_band_width_of_height():
    # edges 3 / 3.5 / 4 -> typical width 0.5 -> the Elite zone shows >= 4..4.5
    fig = history_figure([("2026-01-01", 2.0), ("2026-02-01", 2.2)], bands=BANDS)
    assert fig.layout.yaxis.range[1] >= 4.5
