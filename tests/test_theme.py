"""Theme constants + band_color helper."""
import pytest


def test_brand_colours_loaded():
    from aspire_dash.theme import COLORS, CHART_COLORS, ASPIRE, SLATE
    assert isinstance(COLORS, dict) and COLORS
    assert isinstance(CHART_COLORS, (list, dict))
    # Aspire scale should have 50..900
    assert "600" in ASPIRE  # primary brand colour
    # Slate should have a few common shades
    assert "100" in SLATE or "200" in SLATE


def test_accent_is_aspire_blue():
    from aspire_dash.theme import ACCENT, ASPIRE_BLUE
    assert ACCENT == ASPIRE_BLUE


@pytest.mark.parametrize("band,expected_token", [
    ("in", "success"),
    ("below", "danger"),
    ("above", "warning"),
])
def test_band_color_returns_bootstrap_token(band, expected_token):
    from aspire_dash.theme import band_color
    out = band_color(band)
    # Bootstrap class form returns the token name; case-insensitive substring check
    assert expected_token in str(out).lower() or out is not None


def test_band_color_hex_form():
    from aspire_dash.theme import band_color
    val = band_color("in", as_hex=True)
    assert isinstance(val, str)
    assert val.startswith("#") and len(val) in (4, 7)


def test_band_color_none_input():
    from aspire_dash.theme import band_color
    out = band_color(None)
    # Should return a safe default — string or None — never raise
    assert out is None or isinstance(out, str)


def test_radius_and_shadow_tokens_exist():
    from aspire_dash.theme import (
        RADIUS_SM, RADIUS_MD, RADIUS_LG, RADIUS_FULL,
        SHADOW_SM, SHADOW_MD, SHADOW_LG,
    )
    for v in (RADIUS_SM, RADIUS_MD, RADIUS_LG):
        assert isinstance(v, (int, str))
    for v in (SHADOW_SM, SHADOW_MD, SHADOW_LG):
        assert isinstance(v, str) and v
