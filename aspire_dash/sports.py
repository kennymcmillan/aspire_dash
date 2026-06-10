"""Reusable sport report components — country flags, stat cards, result badges.

These components are sport-agnostic and can be used across fencing, athletics,
swimming, squash, and padel report apps.
"""

from dash import html, dcc
from .theme import SLATE, ACCENT, GOLD, SUCCESS, WARNING, DANGER, SHADOW_SM, RADIUS_LG


# ── IOC → ISO Country Code Mapping ─────────────────────────────────────────

IOC_TO_ISO = {
    "AFG": "AF", "ALB": "AL", "ALG": "DZ", "AND": "AD", "ANG": "AO",
    "ANT": "AG", "ARG": "AR", "ARM": "AM", "ARU": "AW", "AUS": "AU",
    "AUT": "AT", "AZE": "AZ", "BAH": "BS", "BAN": "BD", "BAR": "BB",
    "BHR": "BH", "BRN": "BH", "BLR": "BY", "BEL": "BE", "BIZ": "BZ",
    "BEN": "BJ", "BER": "BM", "BHU": "BT", "BOL": "BO", "BIH": "BA",
    "BOT": "BW", "BRA": "BR", "BRU": "BN", "BUL": "BG", "BUR": "BF",
    "BDI": "BI", "CAM": "KH", "CMR": "CM", "CAN": "CA", "CPV": "CV",
    "CAY": "KY", "CAF": "CF", "CHA": "TD", "CHI": "CL", "CHN": "CN",
    "COL": "CO", "COM": "KM", "COG": "CG", "COK": "CK", "CRC": "CR",
    "CIV": "CI", "CRO": "HR", "CUB": "CU", "CYP": "CY", "CZE": "CZ",
    "PRK": "KP", "COD": "CD", "DEN": "DK", "DJI": "DJ", "DMA": "DM",
    "DOM": "DO", "ECU": "EC", "EGY": "EG", "ESA": "SV", "GEQ": "GQ",
    "ERI": "ER", "EST": "EE", "SWZ": "SZ", "ETH": "ET", "FIJ": "FJ",
    "FIN": "FI", "FRA": "FR", "GAB": "GA", "GAM": "GM", "GEO": "GE",
    "GER": "DE", "GHA": "GH", "GRE": "GR", "GRN": "GD", "GUA": "GT",
    "GUI": "GN", "GBS": "GW", "GUY": "GY", "HAI": "HT", "HON": "HN",
    "HKG": "HK", "HUN": "HU", "ISL": "IS", "IND": "IN", "INA": "ID",
    "IRI": "IR", "IRQ": "IQ", "IRL": "IE", "ISR": "IL", "ITA": "IT",
    "JAM": "JM", "JPN": "JP", "JOR": "JO", "KAZ": "KZ", "KEN": "KE",
    "KIR": "KI", "KUW": "KW", "KGZ": "KG", "LAO": "LA", "LAT": "LV",
    "LIB": "LB", "LES": "LS", "LBR": "LR", "LBA": "LY", "LIE": "LI",
    "LTU": "LT", "LUX": "LU", "MAC": "MO", "MAD": "MG", "MAW": "MW",
    "MAS": "MY", "MDV": "MV", "MLI": "ML", "MLT": "MT", "MHL": "MH",
    "MTN": "MR", "MRI": "MU", "MEX": "MX", "FSM": "FM", "MDA": "MD",
    "MON": "MC", "MGL": "MN", "MNE": "ME", "MAR": "MA", "MOZ": "MZ",
    "MYA": "MM", "NAM": "NA", "NRU": "NR", "NEP": "NP", "NED": "NL",
    "NZL": "NZ", "NCA": "NI", "NIG": "NE", "NGR": "NG", "MKD": "MK",
    "NOR": "NO", "OMA": "OM", "PAK": "PK", "PLW": "PW", "PLE": "PS",
    "PAN": "PA", "PNG": "PG", "PAR": "PY", "PER": "PE", "PHI": "PH",
    "POL": "PL", "POR": "PT", "PUR": "PR", "QAT": "QA", "KOR": "KR",
    "ROU": "RO", "RUS": "RU", "RWA": "RW", "SKN": "KN", "LCA": "LC",
    "VIN": "VC", "SAM": "WS", "SMR": "SM", "STP": "ST", "KSA": "SA",
    "SEN": "SN", "SRB": "RS", "SEY": "SC", "SLE": "SL", "SGP": "SG",
    "SVK": "SK", "SLO": "SI", "SOL": "SB", "SOM": "SO", "RSA": "ZA",
    "SSD": "SS", "ESP": "ES", "SRI": "LK", "SUD": "SD", "SUR": "SR",
    "SWE": "SE", "SUI": "CH", "SYR": "SY", "TPE": "TW", "TJK": "TJ",
    "TAN": "TZ", "THA": "TH", "TLS": "TL", "TOG": "TG", "TGA": "TO",
    "TTO": "TT", "TUN": "TN", "TUR": "TR", "TKM": "TM", "TUV": "TV",
    "UGA": "UG", "UKR": "UA", "UAE": "AE", "GBR": "GB", "USA": "US",
    "URU": "UY", "UZB": "UZ", "VAN": "VU", "VEN": "VE", "VIE": "VN",
    "ISV": "VI", "YEM": "YE", "ZAM": "ZM", "ZIM": "ZW",
}

COUNTRY_NAME_TO_IOC = {
    "QATAR": "QAT", "UNITED STATES": "USA", "UNITED KINGDOM": "GBR",
    "GREAT BRITAIN": "GBR", "SAUDI ARABIA": "KSA",
    "UNITED ARAB EMIRATES": "UAE", "SOUTH KOREA": "KOR",
    "NORTH KOREA": "PRK", "HONG KONG": "HKG",
}

# Reverse lookup: ISO → IOC
ISO_TO_IOC = {v: k for k, v in IOC_TO_ISO.items()}

# IOC → ISO 3166-1 alpha-3 (for Plotly choropleth maps)
# Most IOC codes match ISO-3, these are the ones that differ:
_IOC_TO_ISO3_OVERRIDES = {
    "GER": "DEU", "SUI": "CHE", "RSA": "ZAF", "NED": "NLD", "TPE": "TWN",
    "KSA": "SAU", "UAE": "ARE", "INA": "IDN", "PHI": "PHL", "MAS": "MYS",
    "VIE": "VNM", "MGL": "MNG", "CAM": "KHM", "IRI": "IRN", "BAN": "BGD",
    "SRI": "LKA", "MYA": "MMR", "BRU": "BRN", "CRO": "HRV", "SLO": "SVN",
    "BUL": "BGR", "GRE": "GRC", "DEN": "DNK", "POR": "PRT", "CZE": "CZE",
    "SVK": "SVK", "KUW": "KWT", "OMA": "OMN", "LIB": "LBN", "CHI": "CHL",
    "NGR": "NGA", "ANG": "AGO", "ALG": "DZA", "CMR": "CMR", "CIV": "CIV",
    "MOZ": "MOZ", "NAM": "NAM", "BOT": "BWA", "ZIM": "ZWE", "PLE": "PSE",
    "PUR": "PRI", "ISV": "VIR", "HAI": "HTI",
}


def ioc_to_iso3(ioc_code):
    """Convert IOC code to ISO 3166-1 alpha-3 for Plotly maps."""
    if not ioc_code:
        return ""
    code = ioc_code.strip().upper()
    return _IOC_TO_ISO3_OVERRIDES.get(code, code)


def normalize_country(code):
    """Normalize a country code or name to IOC 3-letter format."""
    if not code:
        return code
    upper = code.strip().upper()
    if upper in IOC_TO_ISO:
        return upper
    return COUNTRY_NAME_TO_IOC.get(upper, upper)


def ioc_to_iso(ioc_code):
    """Convert IOC code (QAT) to ISO 2-letter code (QA)."""
    if not ioc_code:
        return ""
    code = ioc_code.strip().upper()
    if code in ("AIN", "_AIN", "AIN_", "_AI"):
        return ""  # No ISO code for neutral athletes
    return IOC_TO_ISO.get(code, code[:2])


def country_flag_url(ioc_code, size=24):
    """Return a flag emoji or flagcdn.com URL for the given IOC code.

    Uses flagcdn.com for reliable SVG flags in Dash apps.
    """
    iso = ioc_to_iso(ioc_code).lower()
    if not iso or len(iso) != 2:
        return ""
    return f"https://flagcdn.com/w{size}/{iso}.png"


# ── Country Flag Component ──────────────────────────────────────────────────

def country_flag(ioc_code, size="md", show_text=False):
    """Render a country flag image from an IOC code.

    Parameters
    ----------
    ioc_code : str
        IOC 3-letter country code (e.g. "QAT", "USA").
    size : str
        "sm" (16px), "md" (20px), "lg" (24px).
    show_text : bool
        Show the IOC code text next to the flag.
    """
    if not ioc_code:
        return html.Span()

    code = ioc_code.strip().upper()

    # Special: AIN / _AI (Individual Neutral Athletes — various source formats)
    if code in ("AIN", "_AIN", "AIN_", "_AI"):
        return html.Span("AIN", className="flag-chip__ain")

    sizes = {"sm": 16, "md": 20, "lg": 24}
    px = sizes.get(size, 20)
    size_mod = size if size in sizes else "md"
    url = country_flag_url(code, size=max(40, px * 2))  # 2x for retina

    children = [
        html.Img(src=url, className="flag-chip__img", title=code),
    ]
    if show_text:
        children.append(html.Span(code, className="flag-chip__code"))

    return html.Span(children, className=f"flag-chip flag-chip--{size_mod}")


def flag_with_name(nationality, name, highlight_nation=None):
    """Flag + athlete name, with optional highlighting for a focus nation.

    Parameters
    ----------
    nationality : str
        IOC country code.
    name : str
        Athlete / team name.
    highlight_nation : str or None
        If nationality matches this, name is bold + accent colored.
    """
    is_highlighted = (
        highlight_nation
        and nationality
        and nationality.upper() == highlight_nation.upper()
    )
    name_cls = "flag-name__label is-highlight" if is_highlighted else "flag-name__label"

    return html.Div([
        country_flag(nationality, size="md"),
        html.Span(name, className=name_cls),
    ], className="flag-name")


# ── Default Nation Selector ────────────────────────────────────────────────

FOCUS_NATIONS = [
    "QAT", "UAE", "KSA", "USA", "FRA", "ITA", "GER",
    "CHN", "JPN", "KOR", "HUN", "EGY", "GBR",
]


def nation_selector(selector_id="nation-selector", value="QAT", nations=None):
    """Dropdown to select the focus/default nation.

    Parameters
    ----------
    selector_id : str
        Component ID for the dropdown.
    value : str
        Default selected IOC code.
    nations : list[str] or None
        Override the list of nation options (IOC codes).
    """
    opts = nations or FOCUS_NATIONS
    return dcc.Dropdown(
        id=selector_id,
        options=[{"label": c, "value": c} for c in opts],
        value=value,
        clearable=False,
        style={"width": "100px", "fontSize": "13px"},
    )


# ── Stat Card (Gradient) ───────────────────────────────────────────────────

# Color presets for gradient stat cards
# v0.30 — derived from theme.SEMANTIC_PALETTE so a brand change in one
# place cascades. Was a parallel hex universe; now reads from the single
# semantic source. Old keys preserved for back-compat (blue→aspire,
# green→success, red→danger, amber→warning, gray→neutral).
from .theme import SEMANTIC_PALETTE as _SEM_

def _grad_bg(light, mid):
    return f"linear-gradient(135deg, {light}, {mid})"

STAT_COLORS = {
    "blue":   {"bg": _grad_bg("#eff6ff", _SEM_["info"]["bg"]),    "border": _SEM_["info"]["border"],    "text": _SEM_["info"]["text"]},
    "green":  {"bg": _grad_bg("#f0fdf4", _SEM_["success"]["bg"]), "border": _SEM_["success"]["border"], "text": _SEM_["success"]["text"]},
    "red":    {"bg": _grad_bg("#fef2f2", _SEM_["danger"]["bg"]),  "border": _SEM_["danger"]["border"],  "text": _SEM_["danger"]["text"]},
    "amber":  {"bg": _grad_bg("#fffbeb", _SEM_["warning"]["bg"]), "border": _SEM_["warning"]["border"], "text": _SEM_["warning"]["text"]},
    "purple": {"bg": _grad_bg("#faf5ff", _SEM_["purple"]["bg"]),  "border": _SEM_["purple"]["border"],  "text": _SEM_["purple"]["text"]},
    "teal":   {"bg": _grad_bg("#f0fdfa", _SEM_["teal"]["bg"]),    "border": _SEM_["teal"]["border"],    "text": _SEM_["teal"]["text"]},
    "gray":   {"bg": _grad_bg("#f9fafb", _SEM_["neutral"]["bg"]), "border": _SEM_["neutral"]["border"], "text": _SEM_["neutral"]["text"]},
}


def stat_card(label, value, sub=None, icon=None, color="blue"):
    """Gradient stat card for sport dashboards (competitions, wins, rankings).

    .. deprecated:: 0.8
        Use :func:`aspire_dash.components.kpi_tile` for new code.
        ``stat_card`` predates the Aspire signature (left-accent stripe +
        vs-target progress bar). Kept as alias-with-warning through 0.x.

    Parameters
    ----------
    label : str
        Card title (e.g. "Total Competitions").
    value : str or number
        Primary value to display.
    sub : str or None
        Subtitle text below value.
    icon : str or None
        FontAwesome class (e.g. "fa-solid fa-trophy").
    color : str
        Preset name: blue, green, red, amber, purple, teal, gray.
    """
    import warnings
    warnings.warn(
        "aspire_dash.sports.stat_card is deprecated; use kpi_tile() from "
        "aspire_dash.components for the new Aspire signature "
        "(left-accent stripe + optional vs-target progress bar). "
        "stat_card will be removed at 1.0.",
        DeprecationWarning, stacklevel=2,
    )
    c = STAT_COLORS.get(color, STAT_COLORS["blue"])

    icon_el = html.I(className=icon, style={
        "fontSize": "18px", "color": c["text"], "opacity": "0.6",
    }) if icon else None

    return html.Div([
        html.Div([
            html.Div(label, style={
                "fontSize": "11px", "fontWeight": "600", "textTransform": "uppercase",
                "letterSpacing": "0.05em", "color": SLATE["500"], "marginBottom": "4px",
            }),
            icon_el,
        ], style={
            "display": "flex", "justifyContent": "space-between", "alignItems": "flex-start",
        }) if icon else html.Div(label, style={
            "fontSize": "11px", "fontWeight": "600", "textTransform": "uppercase",
            "letterSpacing": "0.05em", "color": SLATE["500"], "marginBottom": "4px",
        }),
        html.Div(str(value), style={
            "fontSize": "24px", "fontWeight": "700", "color": c["text"],
            "fontVariantNumeric": "tabular-nums",
        }),
        html.Div(sub, style={
            "fontSize": "12px", "color": SLATE["500"], "marginTop": "2px",
        }) if sub else None,
    ], style={
        "background": c["bg"], "border": f"1px solid {c['border']}",
        "borderRadius": "8px", "padding": "16px",       # v0.24: canonical 8 px
        "transition": "transform 0.2s, box-shadow 0.2s, border-color 0.2s",
    })


# ── Placement Badge ─────────────────────────────────────────────────────────

def placement_badge(place, size="md"):
    """Colored placement badge (gold/silver/bronze for top 3, blue 4-8, gray 9+).

    Parameters
    ----------
    place : int or str
        Placement number (1, 2, 3, etc.) or text.
    size : str
        "sm" or "md".
    """
    try:
        p = int(place)
    except (ValueError, TypeError):
        p = 999

    if p == 1:
        tone, icon = "place-gold", "fa-solid fa-trophy"
    elif p == 2:
        tone, icon = "place-silver", "fa-solid fa-medal"
    elif p == 3:
        tone, icon = "place-bronze", "fa-solid fa-medal"
    elif p <= 8:
        tone, icon = "place-top8", None
    elif p <= 16:
        tone, icon = "place-top16", None
    else:
        tone, icon = "place-rest", None

    cls = f"placement-badge {tone}"
    if size != "md":
        cls += " placement-badge--sm"

    children = []
    if icon:
        children.append(html.I(className=icon))
    children.append(str(place))

    return html.Span(children, className=cls)


# ── Rank Change Indicator ──────────────────────────────────────────────────

def rank_change(current, previous):
    """Show rank change arrow (green up, red down, gray dash).

    Parameters
    ----------
    current : int or None
        Current rank.
    previous : int or None
        Previous rank.
    """
    if current is None or previous is None:
        return html.Span("NEW", className="rank-change__new")

    diff = previous - current  # positive = improved
    if diff > 0:
        icon, tone, text = "fa-solid fa-caret-up", "rc-up", f"+{diff}"
    elif diff < 0:
        icon, tone, text = "fa-solid fa-caret-down", "rc-down", str(diff)
    else:
        icon, tone, text = "fa-solid fa-minus", "rc-flat", "="

    return html.Span([
        html.I(className=icon),
        text,
    ], className=f"rank-change {tone}")


# ── Competition Hierarchy ──────────────────────────────────────────────────

COMP_HIERARCHY = {
    "olympic": {"label": "Olympics", "color": "amber", "rank": 1},
    "world_championship": {"label": "World Champ", "color": "red", "rank": 2},
    "grand_prix": {"label": "Grand Prix", "color": "amber", "rank": 3},
    "world_cup": {"label": "World Cup", "color": "green", "rank": 4},
    "continental_championship": {"label": "Continental Champ", "color": "purple", "rank": 5},
    "zonal": {"label": "Zonal", "color": "teal", "rank": 6},
    "satellite": {"label": "Satellite", "color": "blue", "rank": 7},
    "development": {"label": "Development", "color": "gray", "rank": 8},
}


def competition_badge(tier, source=None):
    """Badge for competition tier and optional source (FIE, EuroF, PSA, etc).

    Parameters
    ----------
    tier : str
        Competition tier key (e.g. "world_cup", "grand_prix").
    source : str or None
        Data source (e.g. "FIE", "EuroF", "PSA", "WA").
    """
    from .components import badge

    children = []
    info = COMP_HIERARCHY.get(tier, {"label": tier.replace("_", " ").title(), "color": "gray"})
    children.append(badge(info["label"], color=info["color"]))

    if source:
        source_colors = {
            "fie": "blue", "eurof": "teal", "ftl": "amber",
            "psa": "green", "wa": "red", "fip": "purple",
        }
        children.append(badge(source.upper(), color=source_colors.get(source.lower(), "gray")))

    return html.Span(children, className="badge-row")


# ── Category Badge ─────────────────────────────────────────────────────────

CATEGORY_COLORS = {
    "senior": "blue",
    "junior": "red",
    "cadet": "green",
    "u23": "purple",
    "u20": "amber",
    "veteran": "teal",
}


def category_badge(category, weapon=None, gender=None):
    """Badges for athlete category, weapon, and gender.

    Parameters
    ----------
    category : str
        "senior", "junior", "cadet", etc.
    weapon : str or None
        Sport-specific weapon/event (e.g. "foil", "epee", "sabre").
    gender : str or None
        "men" / "women" / "M" / "F".
    """
    from .components import badge

    children = []

    # Category
    cat_lower = (category or "").lower()
    children.append(badge(
        category.title() if category else "Unknown",
        color=CATEGORY_COLORS.get(cat_lower, "gray"),
    ))

    # Weapon / event
    if weapon:
        weapon_emojis = {
            "foil": "🤺", "epee": "⚔️", "sabre": "🗡️",
        }
        label = f"{weapon_emojis.get(weapon.lower(), '')} {weapon.title()}".strip()
        children.append(badge(label, color="gray"))

    # Gender
    if gender:
        g = gender.strip().upper()
        if g in ("M", "MEN", "MALE"):
            children.append(badge("Men", color="blue"))
        elif g in ("F", "W", "WOMEN", "FEMALE"):
            children.append(badge("Women", color="red"))

    return html.Span(children, className="badge-row")


# ── Season Utilities ───────────────────────────────────────────────────────

def format_season(season_str):
    """Format a fencing/sport season string (e.g. '2025' -> '2024-2025')."""
    if not season_str:
        return ""
    s = str(season_str).strip()
    if "-" in s:
        return s
    try:
        year = int(s)
        return f"{year - 1}-{year}"
    except ValueError:
        return s


def get_current_season():
    """Get the current sport season (Sep-Aug cycle)."""
    from datetime import date
    today = date.today()
    if today.month >= 9:
        return f"{today.year}-{today.year + 1}"
    return f"{today.year - 1}-{today.year}"


# ── Data Grid Row ──────────────────────────────────────────────────────────

def data_row(cells, header=False, highlight=False):
    """A single row for data grids/tables.

    Parameters
    ----------
    cells : list
        List of cell contents (str, number, or Dash component).
    header : bool
        Render as header row (bold, gray background).
    highlight : bool
        Highlight row (light blue background, for focus nation).
    """
    cls = "aspire-data-row"
    if header:
        cls += " is-header"
    elif highlight:
        cls += " is-highlight"

    return html.Div(
        [html.Div(c, className="aspire-data-row__cell") for c in cells],
        className=cls,
    )


# ── Trend Arrow (mini) ─────────────────────────────────────────────────────

def trend_arrow(values, label=None):
    """Compact trend indicator from a list of values (last vs first).

    Parameters
    ----------
    values : list[float]
        Historical values (oldest first).
    label : str or None
        Optional label before the arrow.
    """
    if not values or len(values) < 2:
        return html.Span()

    first, last = values[0], values[-1]
    if last > first:
        icon, tone = "fa-solid fa-arrow-trend-up", "ta-up"
    elif last < first:
        icon, tone = "fa-solid fa-arrow-trend-down", "ta-down"
    else:
        icon, tone = "fa-solid fa-minus", "ta-flat"

    children = []
    if label:
        children.append(html.Span(label, className="trend-arrow__label"))
    children.append(html.I(className=icon))

    return html.Span(children, className=f"trend-arrow {tone}")


# ── Fencing Round Ordering ─────────────────────────────────────────────────
# FIE uses A-table (main draw) and B-table (placement) codes.
# FTL/EuroF use human-readable names. This mapping unifies them.

ROUND_ORDER = {
    "A256": 10, "Table of 256": 10, "Preliminary": 10,
    "A128": 20, "Table of 128": 20,
    "A64": 30, "Table of 64": 30,
    "A32": 40, "Table of 32": 40,
    "A16": 50, "Table of 16": 50,
    "A8": 60, "Table of 8": 60, "Quarter-Final": 60, "Quarter-Finals": 60,
    "A4": 70, "Semi-Final": 70, "Semi-Finals": 70,
    "A2": 80, "Final": 80,
    "B64": 110, "B32": 120, "B16": 130, "B8": 140, "B4": 150, "B2": 160,
}

ROUND_DISPLAY = {
    "A256": "Table of 256", "A128": "Table of 128", "A64": "Table of 64",
    "A32": "Table of 32", "A16": "Table of 16", "A8": "Table of 8",
    "A4": "Semi-Final", "A2": "Final",
    "B64": "Placement 33-64", "B32": "Placement 17-32", "B16": "Placement 9-16",
    "B8": "Placement 5-8", "B4": "Placement 3-4", "B2": "Bronze Match",
}


def round_sort_key(round_name):
    """Sort key for fencing tableau round names (lower = earlier round)."""
    return ROUND_ORDER.get(round_name, 200)


def format_round_name(round_name):
    """Convert FIE round codes (A2, B4) to human-readable names."""
    return ROUND_DISPLAY.get(round_name, round_name)


def sort_rounds(round_names):
    """Sort round names in competition order (earliest first)."""
    return sorted(round_names, key=round_sort_key)


# ── Gradient Stat Card ────────────────────────────────────────────────────

def gradient_stat_card(label, value, emoji="", bg="linear-gradient(135deg, #dbeafe, #bfdbfe)",
                       color="#1e40af"):
    """Large stat card with gradient background and optional emoji.

    Parameters
    ----------
    label : str
        Card label (e.g. "Total Fencers").
    value : str or number
        Primary value.
    emoji : str
        Optional emoji shown as faded accent.
    bg : str
        CSS background (gradient or solid).
    color : str
        Text color for the value.
    """
    # bg + value colour are caller-supplied (data-driven) — stay inline
    return html.Div([
        html.Div([
            html.Div(str(value), className="gradient-stat__value",
                     style={"color": color}),
            html.Span(emoji, className="gradient-stat__emoji") if emoji else None,
        ], className="gradient-stat__top"),
        html.Div(label, className="gradient-stat__label"),
    ], className="gradient-stat", style={"background": bg})


# ── Mini Stat ─────────────────────────────────────────────────────────────

def mini_stat(label, value, color="#1e40af"):
    """Compact stat display for dense grids (e.g. fencer cards).

    Parameters
    ----------
    label : str
        Short label (e.g. "W/M", "TD", "Win%").
    value : str
        Display value.
    color : str
        Value text color.
    """
    return html.Div([
        html.Div(label, className="mini-stat__label"),
        html.Div(str(value), className="mini-stat__value", style={"color": color}),
    ], className="mini-stat")


# ── Header Stat ───────────────────────────────────────────────────────────

def header_stat(label, value):
    """Centered label/value pair for profile headers.

    Parameters
    ----------
    label : str
        Stat label (e.g. "Competitions", "Pool Bouts").
    value : str or number
        Stat value.
    """
    return html.Div([
        html.Div(str(value), className="header-stat__value"),
        html.Div(label, className="header-stat__label"),
    ], className="header-stat")


# ── Color Badge ───────────────────────────────────────────────────────────

def color_badge(text, bg="#f3f4f6", color="#374151"):
    """Custom-colored pill badge with explicit bg and text color.

    Unlike ``badge()`` in components.py (which uses preset color names),
    this accepts any hex colors — useful for source badges, level badges, etc.

    Parameters
    ----------
    text : str
        Badge text.
    bg : str
        Background color (hex).
    color : str
        Text color (hex).
    """
    # bg + text colour are caller-supplied (data-driven) — stay inline
    return html.Span(text, className="pill-badge",
                     style={"backgroundColor": bg, "color": color})


# ── Sport dropdown ─────────────────────────────────────────────────────────

#: Default sport list used across Aspire dashboards. Override per app as
#: needed — most apps only show a subset of these.
ASPIRE_SPORTS = [
    "Athletics", "Fencing", "Padel", "Squash",
    "Swimming", "Table Tennis", "Shooting",
]


def sport_dropdown(
    id: str,
    sports: list[str] | list[dict] | dict | None = None,
    value: str | list | None = None,
    multi: bool = False,
    placeholder: str = "Select sport...",
    clearable: bool = True,
    include_all: bool = False,
):
    """Branded sport-selection dropdown.

    Standardises the sport dropdown across budget, medical, attendance,
    training, nutrition, mapping, GCC. Pass a list of sport names, a
    list of ``{"label", "value"}`` dicts, or a ``{id: name}`` dict.

    Parameters
    ----------
    id : str
        Component id.
    sports : list[str] | list[dict] | dict | None
        Sport options. None uses ``ASPIRE_SPORTS``.
    value : str or list or None
        Initial selection.
    multi : bool
        Allow multi-select.
    placeholder : str
        Placeholder text.
    clearable : bool
        Show the clear button.
    include_all : bool
        Prepend an ``"All sports"`` option (value ``"all"``).
    """
    if sports is None:
        opts = [{"label": s, "value": s} for s in ASPIRE_SPORTS]
    elif isinstance(sports, dict):
        opts = [{"label": v, "value": k} for k, v in sports.items()]
    elif sports and isinstance(sports[0], dict):
        opts = list(sports)
    else:
        opts = [{"label": s, "value": s} for s in sports]

    if include_all:
        opts = [{"label": "All sports", "value": "all"}] + opts

    return dcc.Dropdown(
        id=id,
        options=opts,
        value=value,
        multi=multi,
        placeholder=placeholder,
        clearable=clearable,
        style={"minWidth": "180px"},
    )


# ─────────────────────────────────────────────────────────────────────────────
# v0.18 — Sport-federation source badge + competition card + world map
# Extracted from DASH_Fencing_Reports_App. Sport-agnostic so the same
# helpers cover Squash (PSA/ESF/ASF), TT (ITTF/WTT), Athletics (WA/IAAF),
# Swimming (FINA/WAQ), Padel (FIP/WPT).
# ─────────────────────────────────────────────────────────────────────────────

SOURCE_BADGE_COLORS = {
    "fie":    ("#e0e7ff", "#3730a3"),
    "eurof":  ("#ccfbf1", "#115e59"),
    "ftl":    ("#ffedd5", "#9a3412"),
    "psa":    ("#fee2e2", "#991b1b"),
    "esf":    ("#dbeafe", "#1e40af"),
    "asf":    ("#fef3c7", "#92400e"),
    "ittf":   ("#e0e7ff", "#3730a3"),
    "wtt":    ("#dcfce7", "#166534"),
    "wa":     ("#fee2e2", "#991b1b"),
    "iaaf":   ("#fee2e2", "#991b1b"),
    "tila":   ("#f3e8ff", "#6b21a8"),
    "fip":    ("#dbeafe", "#1e40af"),
    "wpt":    ("#dcfce7", "#166534"),
    "fina":   ("#cffafe", "#155e75"),
    "waq":    ("#cffafe", "#155e75"),
    "olympic":("#fef3c7", "#92400e"),
    "gcc":    ("#fef3c7", "#92400e"),
    "default":("#f1f5f9", "#475569"),
}


def source_badge(label, *, federation=None):
    """Sport-federation tag — coloured pill consistent with the
    federation's brand. Auto-resolves colour from SOURCE_BADGE_COLORS."""
    from dash import html
    key = (federation or label or "").lower()
    bg, fg = SOURCE_BADGE_COLORS.get(key, SOURCE_BADGE_COLORS["default"])
    # federation colours are data-driven (SOURCE_BADGE_COLORS) — stay inline
    return html.Span(label, className="pill-badge pill-badge--source",
                     style={"background": bg, "color": fg})


def competition_card(event, *, date=None, location=None, result=None,
                      placement=None, federation=None, category=None,
                      href=None):
    """Competition event card — event / date / location / result chain."""
    from dash import html
    header = []
    if federation:
        header.append(source_badge(federation, federation=federation))
    if category:
        header.append(html.Span(category, className="competition-card__category"))
    body = []
    if header:
        body.append(html.Div(header, style={"marginBottom": "4px"}))
    body.append(html.Div(event, className="competition-card__title"))
    meta = []
    if date:
        meta.append(html.I(className="fa-solid fa-calendar"))
        meta.append(html.Span(date))
    if location:
        if date:
            meta.append(html.Span(" · ", className="competition-card__meta-sep"))
        meta.append(html.I(className="fa-solid fa-location-dot"))
        meta.append(html.Span(location))
    if meta:
        body.append(html.Div(meta, className="competition-card__meta"))
    if result or placement is not None:
        place_tone = (
            "place-1" if placement == 1
            else "place-2" if placement == 2
            else "place-3" if placement == 3
            else "place-n"
        )
        body.append(html.Div([
            html.Span(f"#{placement}" if placement else "",
                      className=f"competition-card__placement {place_tone}"),
            html.Span(result or "", className="competition-card__result-text"),
        ], className="competition-card__result"))
    card = html.Div(body, className="card competition-card")
    if href:
        return html.A(card, href=href, className="competition-card-link")
    return card


def world_map(df, country_col, value_col, *, title=None, height=380,
               scope="world", highlight_country=None):
    """Choropleth world map — country distribution of a metric. ISO-3 codes."""
    import plotly.graph_objects as go
    fig = go.Figure(go.Choropleth(
        locations=df[country_col], z=df[value_col],
        locationmode="ISO-3",
        colorscale=[[0.0, "#dbeafe"], [0.5, "#0059b3"], [1.0, "#001d3d"]],
        marker_line_color="white", marker_line_width=0.6,
        colorbar=dict(thickness=10,
                       title=dict(text=value_col, side="right",
                                  font=dict(size=11))),
    ))
    if highlight_country:
        fig.add_trace(go.Choropleth(
            locations=[highlight_country], z=[1],
            locationmode="ISO-3",
            colorscale=[[0, "#fbb800"], [1, "#fbb800"]],
            showscale=False,
            marker_line_color="#001d3d", marker_line_width=1.5,
            hoverinfo="skip",
        ))
    fig.update_layout(
        title=title, height=height,
        geo=dict(scope=scope, showcoastlines=True,
                  coastlinecolor=SLATE["200"],
                  showland=True, landcolor=SLATE["50"],
                  showcountries=True, countrycolor="white",
                  projection_type="natural earth"),
        margin=dict(t=24 if title else 8, b=8, l=8, r=8),
        font=dict(family="Poppins", size=11),
    )
    return fig
