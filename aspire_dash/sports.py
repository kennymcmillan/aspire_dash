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
        return html.Span("AIN", style={
            "display": "inline-flex", "alignItems": "center",
            "padding": "1px 8px", "borderRadius": "9999px",
            "backgroundColor": SLATE["200"], "color": SLATE["700"],
            "fontSize": "11px", "fontWeight": "600",
        })

    sizes = {"sm": 16, "md": 20, "lg": 24}
    px = sizes.get(size, 20)
    url = country_flag_url(code, size=max(40, px * 2))  # 2x for retina

    children = [
        html.Img(src=url, style={
            "width": f"{px}px", "height": f"{int(px * 0.75)}px",
            "objectFit": "cover", "borderRadius": "2px",
            "border": f"1px solid {SLATE['200']}",
        }, title=code),
    ]
    if show_text:
        children.append(html.Span(code, style={
            "fontSize": "12px", "fontWeight": "500", "color": SLATE["700"],
        }))

    return html.Span(children, style={
        "display": "inline-flex", "alignItems": "center", "gap": "4px",
    })


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
    name_style = {"fontWeight": "600", "color": ACCENT} if is_highlighted else {}

    return html.Div([
        country_flag(nationality, size="md"),
        html.Span(name, style=name_style),
    ], style={"display": "flex", "alignItems": "center", "gap": "6px"})


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
STAT_COLORS = {
    "blue": {"bg": "linear-gradient(135deg, #eff6ff, #dbeafe)", "border": "#bfdbfe", "text": "#1e40af"},
    "green": {"bg": "linear-gradient(135deg, #f0fdf4, #dcfce7)", "border": "#bbf7d0", "text": "#166534"},
    "red": {"bg": "linear-gradient(135deg, #fef2f2, #fee2e2)", "border": "#fecaca", "text": "#991b1b"},
    "amber": {"bg": "linear-gradient(135deg, #fffbeb, #fef3c7)", "border": "#fde68a", "text": "#92400e"},
    "purple": {"bg": "linear-gradient(135deg, #faf5ff, #f3e8ff)", "border": "#e9d5ff", "text": "#6b21a8"},
    "teal": {"bg": "linear-gradient(135deg, #f0fdfa, #ccfbf1)", "border": "#99f6e4", "text": "#115e59"},
    "gray": {"bg": "linear-gradient(135deg, #f9fafb, #f3f4f6)", "border": "#e5e7eb", "text": "#374151"},
}


def stat_card(label, value, sub=None, icon=None, color="blue"):
    """Gradient stat card for sport dashboards (competitions, wins, rankings).

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
        "borderRadius": "10px", "padding": "16px",
        "transition": "transform 0.15s, box-shadow 0.15s",
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
        bg, color = "#fef3c7", "#92400e"
        icon = "fa-solid fa-trophy"
    elif p == 2:
        bg, color = "#f3f4f6", "#374151"
        icon = "fa-solid fa-medal"
    elif p == 3:
        bg, color = "#fef2f2", "#92400e"
        icon = "fa-solid fa-medal"
    elif p <= 8:
        bg, color = "#dbeafe", "#1e40af"
        icon = None
    elif p <= 16:
        bg, color = "#f0fdf4", "#166534"
        icon = None
    else:
        bg, color = "#f9fafb", "#6b7280"
        icon = None

    font = "13px" if size == "md" else "11px"
    pad = "3px 10px" if size == "md" else "2px 8px"

    children = []
    if icon:
        children.append(html.I(className=icon, style={
            "fontSize": "10px", "marginRight": "4px",
        }))
    children.append(str(place))

    return html.Span(children, style={
        "display": "inline-flex", "alignItems": "center",
        "padding": pad, "borderRadius": "9999px",
        "fontSize": font, "fontWeight": "700",
        "backgroundColor": bg, "color": color,
    })


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
        return html.Span("NEW", style={
            "fontSize": "10px", "fontWeight": "600", "color": SLATE["400"],
            "padding": "1px 6px", "borderRadius": "4px",
            "backgroundColor": SLATE["100"],
        })

    diff = previous - current  # positive = improved
    if diff > 0:
        icon, color, text = "fa-solid fa-caret-up", SUCCESS, f"+{diff}"
    elif diff < 0:
        icon, color, text = "fa-solid fa-caret-down", DANGER, str(diff)
    else:
        icon, color, text = "fa-solid fa-minus", SLATE["400"], "="

    return html.Span([
        html.I(className=icon, style={"marginRight": "3px", "fontSize": "12px"}),
        text,
    ], style={
        "display": "inline-flex", "alignItems": "center",
        "fontSize": "11px", "fontWeight": "600", "color": color,
    })


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

    return html.Span(children, style={
        "display": "inline-flex", "gap": "4px", "alignItems": "center",
    })


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

    return html.Span(children, style={
        "display": "inline-flex", "gap": "4px", "alignItems": "center",
    })


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
    bg = SLATE["100"] if header else ("#eff6ff" if highlight else "white")
    weight = "600" if header else "400"
    border = f"1px solid {SLATE['200']}"

    return html.Div(
        [html.Div(c, style={
            "flex": "1", "padding": "8px 12px",
            "fontSize": "13px", "fontWeight": weight,
            "color": SLATE["800"] if header else SLATE["700"],
            "borderRight": border,
            "overflow": "hidden", "textOverflow": "ellipsis",
            "whiteSpace": "nowrap",
        }) for c in cells],
        style={
            "display": "flex", "backgroundColor": bg,
            "borderBottom": border,
        },
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
        icon, color = "fa-solid fa-arrow-trend-up", SUCCESS
    elif last < first:
        icon, color = "fa-solid fa-arrow-trend-down", DANGER
    else:
        icon, color = "fa-solid fa-minus", SLATE["400"]

    children = []
    if label:
        children.append(html.Span(label, style={
            "fontSize": "11px", "color": SLATE["500"], "marginRight": "4px",
        }))
    children.append(html.I(className=icon, style={"fontSize": "13px", "color": color}))

    return html.Span(children, style={
        "display": "inline-flex", "alignItems": "center",
    })


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
    return html.Div([
        html.Div([
            html.Div(str(value), style={
                "fontSize": "28px", "fontWeight": "800", "color": color,
                "fontVariantNumeric": "tabular-nums",
            }),
            html.Span(emoji, style={"fontSize": "24px", "opacity": "0.3"}) if emoji else None,
        ], style={"display": "flex", "justifyContent": "space-between", "alignItems": "center"}),
        html.Div(label, style={
            "fontSize": "12px", "fontWeight": "600", "color": SLATE["500"],
            "textTransform": "uppercase", "letterSpacing": "0.05em", "marginTop": "4px",
        }),
    ], style={
        "padding": "16px", "background": bg,
        "borderRadius": "12px", "border": "1px solid rgba(0,0,0,0.05)",
    })


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
        html.Div(label, style={"fontSize": "10px", "fontWeight": "600", "color": SLATE["400"],
                                "textTransform": "uppercase"}),
        html.Div(str(value), style={"fontSize": "18px", "fontWeight": "800", "color": color,
                                      "fontVariantNumeric": "tabular-nums"}),
    ])


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
        html.Div(str(value), style={"fontSize": "20px", "fontWeight": "700", "color": SLATE["800"],
                                      "fontVariantNumeric": "tabular-nums"}),
        html.Div(label, style={"fontSize": "11px", "color": SLATE["400"], "textTransform": "uppercase"}),
    ], style={"textAlign": "center"})


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
    return html.Span(text, style={
        "display": "inline-flex", "alignItems": "center",
        "padding": "2px 8px", "borderRadius": "9999px",
        "fontSize": "11px", "fontWeight": "600",
        "backgroundColor": bg, "color": color,
        "whiteSpace": "nowrap",
    })


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
