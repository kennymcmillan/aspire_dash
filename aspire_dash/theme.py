"""Design tokens derived from brand.yml — importable constants for Python code."""

import os
import yaml

_BRAND_PATH = os.path.join(os.path.dirname(__file__), "brand.yml")
with open(_BRAND_PATH, "r", encoding="utf-8") as f:
    BRAND = yaml.safe_load(f)

# ── Colours ──────────────────────────────────────────────────────────────────
COLORS = BRAND["colors"]
CHART_COLORS = COLORS["chart"]

# v0.25 — Aspire-anchored sequential + diverging scales for Plotly's
# `color_continuous_scale=` and `color_discrete_sequence=`. Replaces
# off-brand Plotly stock defaults (Reds, Blues, Viridis) so every
# chart in the portfolio reads as Aspire.
SEQUENTIAL_BLUE   = COLORS.get("sequential_blue",   [])
SEQUENTIAL_GOLD   = COLORS.get("sequential_gold",   [])
SEQUENTIAL_RED    = COLORS.get("sequential_red",    [])
SEQUENTIAL_GREEN  = COLORS.get("sequential_green",  [])
DIVERGING_RED_GREEN = COLORS.get("diverging_red_green", [])
DIVERGING_GREEN_RED = COLORS.get("diverging_green_red", [])

# Convenience — alias the most common ones
ASPIRE_SCALE   = SEQUENTIAL_BLUE      # "magnitude" use case
GOLD_SCALE_C   = SEQUENTIAL_GOLD      # "achievement" / "intensity"
HEAT_RED_SCALE = SEQUENTIAL_RED       # "danger / load / risk"
HEAT_GREEN_SCALE = SEQUENTIAL_GREEN   # "recovery / readiness / availability"
VARIANCE_SCALE = DIVERGING_RED_GREEN  # bad ← neutral → good (default)

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
FONT_HEADING = BRAND["fonts"]["heading"]
FONT_DATA = BRAND["fonts"]["data"]      # Inter — for tabular/numeric (charts, tables)
FONT_MONO = BRAND["fonts"]["mono"]

# Page background — v0.23 token (was hardcoded as #f7f9fc / #f8fafc in 6 modules)
BG_PAGE = BRAND.get("bg_page", "#f7f9fc")

# ── v0.24 — design-system rhythm tokens ─────────────────────────────────────
# Each is a dict so you can import the WHOLE table or pick a single key.
# Encourage: use these everywhere instead of magic strings.

SPACING  = BRAND.get("spacing",  {"xs": 4, "sm": 8, "md": 12, "lg": 16,
                                    "xl": 20, "xxl": 24, "xxxl": 32})
MOTION   = BRAND.get("motion",   {})
Z_INDEX  = BRAND.get("z_index",  {})
BORDERS  = BRAND.get("borders",  {"thin": "1px", "medium": "2px", "thick": "4px"})
TRACKING = BRAND.get("tracking", {"normal": "0", "wider": "0.5px"})
DENSITY  = BRAND.get("density",  {"comfortable": 1.0})
GOLD_SCALE = {k.split("-")[1]: v for k, v in COLORS.items()
              if k.startswith("gold-scale-")} or BRAND.get("gold-scale", {})

# Convenience — every component picks the same canonical eyebrow style
EYEBROW_STYLE = {
    "fontSize":       "11px",
    "fontWeight":     600,
    "color":          SLATE.get("600", "#475569"),
    "textTransform":  "uppercase",
    "letterSpacing":  TRACKING.get("wider", "0.5px"),
    "fontFamily":     FONT_HEADING,
}

# Convenience — canonical transition
TRANSITION_FAST = f"all {MOTION.get('duration_fast', '150ms')} {MOTION.get('ease_out', 'ease-out')}"
TRANSITION_NORMAL = f"all {MOTION.get('duration_normal', '200ms')} {MOTION.get('ease_out', 'ease-out')}"


# ── v0.29 cascade — semantic palette unification ───────────────────────────
# These three dicts kill ~50 hex-pair duplicates across feedback.py,
# sports.py, v12_helpers.py, firstbeat.py. Every component now reads from
# ONE source. Brand swap = 1-file change.
#
# Audit finding: 677 hardcoded "#xxxxxx" hits across 29 files. Of those,
# ~210 were ring/badge/zone tone tables reinvented per-module. These dicts
# consolidate them.

#: Semantic tone → (bg, border, text) for badges/pills/chips
SEMANTIC_PALETTE = {
    "success":  {"bg": "#dcfce7", "border": "#bbf7d0", "text": "#166534"},
    "warning":  {"bg": "#fef3c7", "border": "#fde68a", "text": "#92400e"},
    "danger":   {"bg": "#fee2e2", "border": "#fecaca", "text": "#991b1b"},
    "info":     {"bg": "#dbeafe", "border": "#bfdbfe", "text": "#1e40af"},
    "aspire":   {"bg": "#eff6ff", "border": "#bfdbfe", "text": "#003566"},
    "gold":     {"bg": "#fef3c7", "border": "#fde68a", "text": "#92400e"},
    "neutral":  {"bg": "#f1f5f9", "border": "#e2e8f0", "text": "#475569"},
    "purple":   {"bg": "#f3e8ff", "border": "#e9d5ff", "text": "#6b21a8"},
    "teal":     {"bg": "#ccfbf1", "border": "#99f6e4", "text": "#115e59"},
}

#: Zone tone → CSS class name (apply via .zone-<key>) for the Whoop-style
#: gradient bg (top-left tint → white). Now universal — any card can wear
#: it, not just .athlete-card-v2.
ZONE_BG_TONES = ("green", "yellow", "red", "aspire", "neutral", "gold")

#: Gradient surface — for cards/tiles that want depth without zone-coding
GRADIENT_BG_TONES = {
    "white":   "linear-gradient(180deg, #ffffff 0%, #f7f9fc 100%)",
    "slate":   "linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%)",
    "aspire":  "linear-gradient(135deg, rgba(0,65,133,0.08) 0%, rgba(255,255,255,1) 60%)",
    "gold":    "linear-gradient(135deg, rgba(251,184,0,0.10) 0%, rgba(255,255,255,1) 60%)",
    "success": "linear-gradient(135deg, rgba(22,163,74,0.08) 0%, rgba(255,255,255,1) 60%)",
    "warning": "linear-gradient(135deg, rgba(234,179,8,0.10) 0%, rgba(255,255,255,1) 60%)",
    "danger":  "linear-gradient(135deg, rgba(220,38,38,0.10) 0%, rgba(255,255,255,1) 60%)",
}


def semantic_tone(tone: str) -> dict:
    """Return `{bg, border, text}` for any semantic tone.
    Pass into a Python style dict, or use the matching `.aspire-card--<tone>`
    CSS class for the same result without inline styling."""
    return SEMANTIC_PALETTE.get(tone, SEMANTIC_PALETTE["neutral"])
TRANSITION_NORMAL = f"all {MOTION.get('duration_normal', '200ms')} {MOTION.get('ease_out', 'ease-out')}"

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
