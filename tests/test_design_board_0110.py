"""0.110: data_table content fit, plotly template, region_rank_map, rank_small_multiples. Synthetic data only."""
import plotly.graph_objects as go
import plotly.io as pio
import pytest

import aspire_dash
from aspire_dash.components import rank_small_multiples, rank_sources
from aspire_dash.maps import RANK_BANDS, REGIONS, rank_band, region_rank_map
from aspire_dash.sports import data_table, ioc_to_iso3, rank_pill


def _classes(node):
    return (getattr(node, "className", "") or "").split()


# -- data_table fit ------------------------------------------------------------

def test_data_table_content_fit_is_default_and_capped():
    wrap = data_table(["A", "B"], [["a", "b"]])
    assert "is-fit-content" in _classes(wrap)
    assert wrap.style == {"maxWidth": "min(100%, 880px)"}


def test_data_table_custom_max_width():
    wrap = data_table(["A"], [["a"]], max_width="640px")
    assert wrap.style["maxWidth"] == "min(100%, 640px)"


def test_data_table_full_keeps_old_behaviour():
    wrap = data_table(["A", "B"], [["a", "b"]], fit="full")
    assert "is-fit-content" not in _classes(wrap)
    assert not getattr(wrap, "style", None)
    assert "aspire-data-table-scroll" in _classes(wrap)       # still scrolls on a phone
    assert "is-autofit" in _classes(wrap.children)


def test_data_table_content_fit_still_autofits_and_scrolls():
    wrap = data_table([{"label": "N", "grow": 3}, "P"], [["x", "y"]])
    assert "aspire-data-table-scroll" in _classes(wrap)
    assert wrap.children.style["gridTemplateColumns"].count("minmax(max-content,") == 2


def test_data_table_rejects_unknown_fit():
    with pytest.raises(ValueError):
        data_table(["A"], [["a"]], fit="wide")


def test_rank_pill_medals_for_one_to_three_only():
    assert {"rank-p1", "rank-top10"} <= set(_classes(rank_pill(1)))
    assert "rank-p3" in _classes(rank_pill(3))
    assert not any(c in ("rank-p1", "rank-p2", "rank-p3") for c in _classes(rank_pill(4)))
    assert "rank-top10" in _classes(rank_pill(4))


# -- plotly template -----------------------------------------------------------

def test_template_automargin_and_navy_hover():
    t = pio.templates["aspire"].layout
    assert t.xaxis.automargin is True and t.yaxis.automargin is True
    assert t.hoverlabel.bgcolor == "#001d3d"
    assert t.hoverlabel.font.color == "white"


def test_template_leaves_zoom_and_legend_alone():
    t = pio.templates["aspire"].layout
    assert t.xaxis.fixedrange is None and t.yaxis.fixedrange is None
    assert t.legend.orientation == "h" and t.legend.y == -0.18


# -- region_rank_map -----------------------------------------------------------

ROWS = [
    {"nation_code": "QAT", "rank_position": 27, "points": 120.5},
    {"nation_code": "KUW", "rank_position": 5, "points": 300},
    {"nation_code": "UAE", "rank_position": 40, "points": 20},
    {"nation_code": "BRN", "rank_position": None, "points": None},
    {"nation_code": "ITA", "rank_position": 1, "points": 999},       # outside both regions
]


def _by_code(fig):
    bub = fig.data[1]
    return dict(zip(bub.customdata, zip(bub.text, bub.hovertext, bub.marker.color, bub.marker.size)))


def test_gulf_map_has_all_six_members_and_ignores_outsiders():
    fig = region_rank_map(ROWS, "gulf")
    assert isinstance(fig, go.Figure)
    assert sorted(fig.data[1].customdata) == sorted(["QAT", "BRN", "KUW", "UAE", "KSA", "OMA"])
    assert "ITA" not in fig.data[1].customdata


def test_bands_numbers_and_not_ranked():
    d = _by_code(region_rank_map(ROWS, "gulf"))
    assert d["KUW"][0] == "<b>5</b>" and d["KUW"][2] == RANK_BANDS[0][1]
    assert d["QAT"][2] == RANK_BANDS[2][1]                  # 27 -> 17-32
    assert d["UAE"][2] == RANK_BANDS[3][1]                  # 40 -> 33+
    for c in ("BRN", "KSA", "OMA"):                          # null rank / no row
        assert d[c][0] == "-" and d[c][2] == RANK_BANDS[4][1] and "not ranked" in d[c][1]


def test_hover_has_rank_and_points():
    d = _by_code(region_rank_map(ROWS, "gulf"))
    assert "27" in d["QAT"][1] and "120.5 pts" in d["QAT"][1]


def test_highlight_ring_is_bigger_and_gold():
    bub = region_rank_map(ROWS, "gulf", highlight="QAT").data[1]
    codes = list(bub.customdata)
    i, j = codes.index("QAT"), codes.index("KUW")
    assert bub.marker.line.color[i] == "#fbb800" and bub.marker.line.color[j] == "#ffffff"
    assert bub.marker.size[i] > bub.marker.size[j]
    none = region_rank_map(ROWS, "gulf", highlight=None).data[1]
    assert "#fbb800" not in none.marker.line.color


def test_choropleth_joins_on_iso3():
    fig = region_rank_map(ROWS, "gulf")
    locs = dict(zip(fig.data[1].customdata, fig.data[0].locations))
    assert locs["BRN"] == "BHR" and locs["UAE"] == "ARE" and locs["KUW"] == "KWT" and locs["KSA"] == "SAU"
    assert ioc_to_iso3("BRN") == "BHR" and ioc_to_iso3("BRU") == "BRN"


def test_choropleth_z_matches_bands():
    fig = region_rank_map(ROWS, "gulf")
    z = dict(zip(fig.data[1].customdata, fig.data[0].z))
    assert z["KUW"] == 0 and z["QAT"] == 2 and z["UAE"] == 3 and z["OMA"] == 4


def test_asia_region_is_zoomed_and_larger():
    gulf, asia = region_rank_map(ROWS, "gulf"), region_rank_map(ROWS, "asia")
    assert len(asia.data[1].customdata) == 33      # 27 + IRQ JOR SYR LBN PAK MGL (0.111)
    assert set(REGIONS["gulf"]["centroids"]) <= set(REGIONS["asia"]["centroids"])
    assert list(asia.layout.geo.lonaxis.range) == [34, 150]
    assert list(gulf.layout.geo.lonaxis.range) == [43.5, 60.5]
    assert asia.layout.dragmode is False


def test_best_rank_wins_for_duplicate_codes():
    rows = [{"nation_code": "QAT", "rank_position": 30}, {"nation_code": "QAT", "rank_position": 12}]
    assert _by_code(region_rank_map(rows, "gulf"))["QAT"][0] == "<b>12</b>"


def test_empty_rows_all_not_ranked_and_bad_region():
    d = _by_code(region_rank_map([], "gulf"))
    assert all(v[0] == "-" for v in d.values())
    with pytest.raises(ValueError):
        region_rank_map(ROWS, "europe")


@pytest.mark.parametrize("rank,band", [(1, 0), (8, 0), (9, 1), (16, 1), (17, 2), (32, 2), (33, 3), (400, 3),
                                       (None, 4), (0, 4), ("x", 4)])
def test_rank_band_edges(rank, band):
    assert rank_band(rank) == band


# -- rank_small_multiples ------------------------------------------------------

SERIES = {
    "Senior Foil (FIE)": [("2024-07-01", 80), ("2025-07-01", 55), ("2026-07-01", 30)],
    "Cadet Foil (EuroF)": [("2024-07-01", 400), ("2025-07-01", 120)],
    "Senior Epee (FIE)": [("2025-07-01", 9)],
    "Empty (FIE)": [],
}


def _yr(fig, i):
    return tuple(fig.layout["yaxis" + ("" if i == 0 else str(i + 1))].range)


def test_lists_mode_one_panel_per_list_each_own_reversed_scale():
    fig = rank_small_multiples(SERIES, "lists")
    lines = [t for t in fig.data if t.mode == "lines+markers"]
    assert len(lines) == 3                                  # empty list dropped
    ranges = [_yr(fig, i) for i in range(3)]
    assert all(hi > lo for hi, lo in ranges)                # reversed: worst at the bottom
    assert len(set(ranges)) == 3                            # own scale each
    assert max(r[0] for r in ranges) > 400 and min(r[0] for r in ranges) < 15


def test_latest_point_is_ringed():
    fig = rank_small_multiples(SERIES, "lists")
    rings = [t for t in fig.data if t.mode == "markers"]
    assert sorted(t.y[0] for t in rings) == [9, 30, 120]


def test_sources_mode_overlays_lists_per_source():
    fig = rank_small_multiples(SERIES, "sources")
    lines = [t for t in fig.data if t.mode == "lines+markers"]
    assert len(lines) == 3
    assert sorted(a.text for a in fig.layout.annotations) == ["EUROF", "FIE"]
    assert rank_sources(SERIES)["Senior Foil (FIE)"] == "FIE"
    assert rank_sources({"Plain": [("2024-01-01", 3)]}) == {"Plain": "Rankings"}


def test_sources_mapping_override_and_errors():
    fig = rank_small_multiples(SERIES, "sources", sources={k: "ALL" for k in SERIES})
    assert [a.text for a in fig.layout.annotations] == ["ALL"]
    with pytest.raises(ValueError):
        rank_small_multiples(SERIES, "grid")
    with pytest.raises(ValueError):
        rank_small_multiples({"x": []}, "lists")


def test_version_bumped():
    assert aspire_dash.__version__ == "0.111.0"
