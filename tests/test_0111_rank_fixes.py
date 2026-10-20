"""0.111: trend_arrow for ranks + Asia map members that hold team ranks (Fencing Reports, 2026-10-20)."""
from aspire_dash.maps import REGIONS, region_rank_map
from aspire_dash.sports import trend_arrow


def _tone(span):
    return span.className.split()[-1]


def test_trend_arrow_rank_getting_worse_is_down():
    # Qatar epee men 48 -> 59 showed a green up arrow
    assert _tone(trend_arrow([48, 52, 59], lower_is_better=True)) == "ta-down"
    assert _tone(trend_arrow([59, 48], lower_is_better=True)) == "ta-up"


def test_trend_arrow_default_unchanged():
    assert _tone(trend_arrow([48, 59])) == "ta-up"
    assert _tone(trend_arrow([59, 48])) == "ta-down"
    assert _tone(trend_arrow([5, 5], lower_is_better=True)) == "ta-flat"


def test_asia_map_draws_iraq_and_jordan_inside_the_window():
    fig = region_rank_map([{"nation_code": "IRQ", "rank_position": 30, "points": 10},
                           {"nation_code": "JOR", "rank_position": 41, "points": 4}], "asia")
    assert {"IRQ", "JOR"} <= set(fig.data[1].customdata)
    lon0, lon1 = REGIONS["asia"]["lon"]
    lat0, lat1 = REGIONS["asia"]["lat"]
    for lon, lat in REGIONS["asia"]["centroids"].values():
        assert lon0 <= lon <= lon1 and lat0 <= lat <= lat1


def test_asia_members_are_ioc_codes_with_a_country_name():
    # 2026-10-20: Lebanon went in as ISO "LBN" and showed as a raw code; IOC is LIB
    from aspire_dash.countries import name
    for code in REGIONS["asia"]["centroids"]:
        assert name(code) != code, code
