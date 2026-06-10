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


# ── v0.45 sports glow-up: inline styles → semantic classes ─────────────────
# Pin the class contract so the CSS port can't silently regress.

def test_placement_badge_emits_tone_classes():
    from aspire_dash.sports import placement_badge
    assert "placement-badge" in placement_badge(1).className
    assert "place-gold" in placement_badge(1).className
    assert "place-silver" in placement_badge(2).className
    assert "place-bronze" in placement_badge(3).className
    assert "place-top8" in placement_badge(5).className
    assert "place-rest" in placement_badge(40).className
    assert "placement-badge--sm" in placement_badge(1, size="sm").className


def test_rank_change_emits_tone_classes():
    from aspire_dash.sports import rank_change
    assert "rc-up" in rank_change(3, 7).className
    assert "rc-down" in rank_change(9, 4).className
    assert "rc-flat" in rank_change(5, 5).className
    assert rank_change(None, None).className == "rank-change__new"


def test_country_flag_emits_flag_chip():
    from aspire_dash.sports import country_flag
    out = country_flag("QAT", size="lg", show_text=True)
    assert "flag-chip" in out.className
    assert "flag-chip--lg" in out.className
    assert country_flag("AIN").className == "flag-chip__ain"


def test_data_row_header_and_highlight_classes():
    from aspire_dash.sports import data_row
    assert "is-header" in data_row(["A", "B"], header=True).className
    assert "is-highlight" in data_row(["A", "B"], highlight=True).className
    assert data_row(["A", "B"]).className == "aspire-data-row"


def test_dynamic_colour_badges_keep_inline_colour():
    from aspire_dash.sports import color_badge, source_badge
    cb = color_badge("FIE", "#e0e7ff", "#3730a3")
    assert "pill-badge" in cb.className
    assert cb.style["backgroundColor"] == "#e0e7ff"
    sb = source_badge("PSA", federation="psa")
    assert "pill-badge--source" in sb.className
    assert "background" in sb.style


def test_competition_card_classes_and_link():
    from aspire_dash.sports import competition_card
    card = competition_card("World Cup Doha", date="2026-03-01",
                            location="Doha", result="Gold", placement=1)
    assert "competition-card" in card.className
    linked = competition_card("GP Paris", href="/events/1")
    assert linked.className == "competition-card-link"


def test_gradient_stat_card_structure_class():
    from aspire_dash.sports import gradient_stat_card, mini_stat, header_stat
    gs = gradient_stat_card("Total", 12, emoji="🤺")
    assert gs.className == "gradient-stat"
    assert "background" in gs.style
    assert mini_stat("W/M", "4/6").className == "mini-stat"
    assert header_stat("Bouts", 174).className == "header-stat"


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
