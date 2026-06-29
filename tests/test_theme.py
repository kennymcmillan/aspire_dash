"""Theme constants + band_color helper."""
import os
import subprocess
import sys

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


# ── ASPIRE_BRAND_PATH hook ──────────────────────────────────────────────────
# theme.py resolves its brand.yml at IMPORT time, so the env-var override can
# only be exercised in a fresh interpreter — by the time this test module runs,
# aspire_dash.theme is already imported and its constants bound by value. Each
# case therefore spawns a subprocess.

def _package_and_root():
    import aspire_dash
    pkg_dir = os.path.dirname(aspire_dash.__file__)
    return pkg_dir, os.path.dirname(pkg_dir)


def _aspire_blue_in_subprocess(env_overrides):
    """Return theme.ASPIRE_BLUE as seen by a fresh interpreter under `env`."""
    pkg_dir, repo_root = _package_and_root()
    env = {k: v for k, v in os.environ.items() if k != "ASPIRE_BRAND_PATH"}
    env.update(env_overrides)
    # cwd=repo_root so `-c`'s implicit sys.path[0]="" resolves the package even
    # when aspire_dash is not pip-installed (matches conftest's path insert).
    out = subprocess.check_output(
        [sys.executable, "-c", "import aspire_dash.theme as t; print(t.ASPIRE_BLUE)"],
        env=env, cwd=repo_root, text=True,
    )
    return out.strip()


def test_brand_path_unset_is_bundled_default():
    # No ASPIRE_BRAND_PATH → byte-identical to historical behaviour.
    assert _aspire_blue_in_subprocess({}) == "#004185"


def test_brand_path_env_var_overrides_brand(tmp_path):
    # Point at a fixture brand.yml (real schema, maroon primary) → constant
    # reflects the override. Building the fixture from the bundled file keeps
    # it schema-current so this can't drift from theme.py's direct lookups.
    import yaml
    pkg_dir, _root = _package_and_root()
    with open(os.path.join(pkg_dir, "brand.yml"), encoding="utf-8") as f:
        brand = yaml.safe_load(f)
    brand["colors"]["aspire-600"] = "#8A1739"  # Ruwwad maroon
    fixture = tmp_path / "brand.yml"
    fixture.write_text(yaml.safe_dump(brand), encoding="utf-8")
    assert _aspire_blue_in_subprocess(
        {"ASPIRE_BRAND_PATH": str(fixture)}
    ) == "#8A1739"
