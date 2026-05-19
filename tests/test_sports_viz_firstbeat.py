"""Smoke for sports / viz / firstbeat modules."""
import pytest

from conftest import is_dash_component


# ── sports ─────────────────────────────────────────────────────────────────

def test_country_flag_with_known_ioc():
    from aspire_dash.sports import country_flag
    assert is_dash_component(country_flag("QAT"))


def test_ioc_to_iso_known():
    from aspire_dash.sports import ioc_to_iso
    assert ioc_to_iso("QAT") == "QA"


def test_stat_card_renders():
    from aspire_dash.sports import stat_card
    out = stat_card("Wins", "12", color="green")
    assert is_dash_component(out)


def test_placement_badge_top3():
    from aspire_dash.sports import placement_badge
    assert is_dash_component(placement_badge(1))
    assert is_dash_component(placement_badge(2))
    assert is_dash_component(placement_badge(8))


def test_format_season_round_trip():
    from aspire_dash.sports import format_season
    assert format_season("2026") == "2025-2026"
    assert format_season("2025-2026") == "2025-2026"


# ── viz ────────────────────────────────────────────────────────────────────

def test_sparkline_empty_renders_placeholder():
    from aspire_dash.viz import sparkline
    out = sparkline([])
    assert is_dash_component(out) or out is not None


def test_sparkline_with_values():
    try:
        import dash_svg  # noqa: F401
    except ImportError:
        pytest.skip("dash-svg not installed")
    from aspire_dash.viz import sparkline
    out = sparkline([1.0, 2.0, 1.5, 3.0])
    assert is_dash_component(out)


# ── firstbeat ──────────────────────────────────────────────────────────────

def test_zone_bars_renders():
    from aspire_dash.firstbeat import zone_bars
    zones = {"zone1": 10, "zone2": 30, "zone3": 50, "zone4": 15, "zone5": 5}
    assert is_dash_component(zone_bars(zones))


def test_acwr_badge_renders():
    from aspire_dash.firstbeat import acwr_badge
    assert is_dash_component(acwr_badge(1.05))
    assert is_dash_component(acwr_badge(None))


def test_get_acwr_status_buckets():
    from aspire_dash.firstbeat import get_acwr_status
    for acwr in (0.6, 1.0, 1.4, 1.7):
        out = get_acwr_status(acwr)
        assert isinstance(out, dict)
        assert "status" in out and "color" in out


# ── v0.7 sport dropdown ────────────────────────────────────────────────────

def test_sport_dropdown_default_list():
    from aspire_dash.sports import sport_dropdown, ASPIRE_SPORTS
    out = sport_dropdown("sp-dd")
    assert is_dash_component(out)
    assert "Athletics" in ASPIRE_SPORTS


def test_sport_dropdown_with_dict_options():
    from aspire_dash.sports import sport_dropdown
    out = sport_dropdown("sp-dd", sports={1: "Athletics", 2: "Fencing"},
                         value=1, include_all=True)
    assert is_dash_component(out)


def test_sport_dropdown_multi():
    from aspire_dash.sports import sport_dropdown
    assert is_dash_component(sport_dropdown("sp-dd", multi=True))


# ── v0.7 aspire_datatable ──────────────────────────────────────────────────

def test_aspire_datatable_renders():
    from aspire_dash.tables import aspire_datatable
    out = aspire_datatable(
        "tbl",
        data=[{"Sport": "A", "Budget": 1000}, {"Sport": "TOTAL", "Budget": 1000}],
        columns=[{"name": "Sport", "id": "Sport"},
                 {"name": "Budget", "id": "Budget"}],
        totals_row_label="TOTAL",
    )
    assert is_dash_component(out)
