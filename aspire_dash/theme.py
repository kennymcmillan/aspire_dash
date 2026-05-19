"""Design tokens derived from brand.yml — importable constants for Python code."""

import os
import yaml

_BRAND_PATH = os.path.join(os.path.dirname(__file__), "brand.yml")
with open(_BRAND_PATH, "r", encoding="utf-8") as f:
    BRAND = yaml.safe_load(f)

# ── Colours ──────────────────────────────────────────────────────────────────
COLORS = BRAND["colors"]
CHART_COLORS = COLORS["chart"]

SLATE = {k.split("-")[1]: v for k, v in COLORS.items() if k.startswith("slate-")}
ASPIRE = {k.split("-")[1]: v for k, v in COLORS.items() if k.startswith("aspire-")}

# Aspire blue scale
ASPIRE_BLUE = ASPIRE["600"]       # #004185 — primary brand colour
ASPIRE_NAVY = ASPIRE["900"]       # #001d3d — sidebar background
ASPIRE_LIGHT = ASPIRE["50"]       # #eff6ff — light blue wash

ACCENT = COLORS["accent"]         # #004185
ACCENT_HOVER = COLORS["accent-hover"]  # #003566
SECONDARY = COLORS["secondary"]   # #1876ab
SUCCESS = COLORS["success"]
WARNING = COLORS["warning"]
DANGER = COLORS["danger"]
INFO = COLORS["info"]
GOLD = COLORS["gold"]             # #fbb800 (from aspire.qa --yellow)
GOLD_LIGHT = COLORS["gold-light"]

# ── Typography ───────────────────────────────────────────────────────────────
FONT_FAMILY = BRAND["fonts"]["body"]
FONT_MONO = BRAND["fonts"]["mono"]

# ── Sidebar ──────────────────────────────────────────────────────────────────
SIDEBAR_WIDTH = BRAND["sidebar"]["width"]
SIDEBAR_BG = BRAND["sidebar"]["bg"]
SIDEBAR_BORDER = BRAND["sidebar"]["border"]
SIDEBAR_LINK_COLOR = BRAND["sidebar"]["link-color"]
SIDEBAR_LINK_HOVER_BG = BRAND["sidebar"]["link-hover-bg"]
SIDEBAR_LINK_ACTIVE_BG = BRAND["sidebar"]["link-active-bg"]

# ── Radius ───────────────────────────────────────────────────────────────────
RADIUS_SM = BRAND["radius"]["sm"]
RADIUS_MD = BRAND["radius"]["md"]
RADIUS_LG = BRAND["radius"]["lg"]
RADIUS_FULL = BRAND["radius"]["full"]

# ── Shadows ──────────────────────────────────────────────────────────────────
SHADOW_SM = BRAND["shadows"]["sm"]
SHADOW_MD = BRAND["shadows"]["md"]
SHADOW_LG = BRAND["shadows"]["lg"]

# ── Logo ─────────────────────────────────────────────────────────────────────
LOGO_FILENAME = BRAND["logo"]["filename"]
LOGO_ALT = BRAND["logo"]["alt"]


# ── Band classification → colors ─────────────────────────────────────────────
# Used by KPI tiles, target-vs-actual progress bars, and any UI that
# classifies a measured value as below / in / above an acceptable band.
# Two mappings: bootstrap class (for dbc.Progress color=) and hex (for
# inline styles / chart traces).

BAND_BS = {
    "in":    "success",   # green — value sits within target band
    "below": "warning",   # gold  — below band, action recommended
    "above": "danger",    # red   — over band, action recommended
}

BAND_HEX = {
    "in":    SUCCESS,
    "below": GOLD,
    "above": DANGER,
}


def band_color(band: str | None, *, as_hex: bool = False) -> str:
    """Map a band label to either a bootstrap color class or a hex code.

        band_color("in")             -> "success"
        band_color("above")          -> "danger"
        band_color("in", as_hex=True) -> "#16a34a"
        band_color(None)             -> "secondary" / SLATE["500"]
    """
    key = (band or "").lower()
    if as_hex:
        return BAND_HEX.get(key, SLATE.get("500", "#64748b"))
    return BAND_BS.get(key, "secondary")
