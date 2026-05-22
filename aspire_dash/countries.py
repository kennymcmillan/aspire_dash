"""One-stop country reference: IOC ↔ ISO-2 ↔ ISO-3 ↔ name ↔ flag.

Apps across the portfolio kept hand-rolling small country dicts
(fencing, squash, GCC, athletics rankings). This module consolidates
all of it behind one import. Backed by the comprehensive `IOC_TO_ISO`
mapping already in `aspire_dash.sports` — re-exported here for
discoverability.

Usage::

    from aspire_dash import countries

    countries.lookup("QAT")
    # {'ioc': 'QAT', 'iso2': 'QA', 'iso3': 'QAT',
    #  'name': 'Qatar', 'emoji': '🇶🇦',
    #  'flag_url': 'https://flagcdn.com/w40/qa.png'}

    countries.name("FRA")       # 'France'
    countries.emoji("FRA")      # '🇫🇷'
    countries.iso2("KSA")       # 'SA'
    countries.iso3("INA")       # 'IDN'
    countries.flag_url("USA", size=80)
    countries.search("Saudi")   # → 'KSA'

    # Reverse / normalisation
    countries.normalise("United Arab Emirates")  # 'UAE'
    countries.normalise("Qatar")                  # 'QAT'

    # Iterate everything (for dropdowns, choropleths, etc.)
    for code, meta in countries.ALL.items():
        print(code, meta["name"])
"""
from __future__ import annotations

# Re-export the heavy lifters from sports.py so callers have a single import
from .sports import (
    IOC_TO_ISO, ISO_TO_IOC,           # noqa: F401
    COUNTRY_NAME_TO_IOC,               # noqa: F401
    ioc_to_iso, ioc_to_iso3,           # noqa: F401
    normalize_country,                  # noqa: F401
    country_flag_url, country_flag,    # noqa: F401
    flag_with_name,                     # noqa: F401
)


# IOC code → human-readable country name.
# Covers every entry in IOC_TO_ISO above. Names follow IOC official usage
# (e.g. "Chinese Taipei" for TPE, "Republic of Korea" for KOR — abbreviate
# in display logic if you need shorter labels).
IOC_TO_NAME: dict[str, str] = {
    "AFG": "Afghanistan", "ALB": "Albania", "ALG": "Algeria",
    "AND": "Andorra", "ANG": "Angola", "ANT": "Antigua and Barbuda",
    "ARG": "Argentina", "ARM": "Armenia", "ARU": "Aruba",
    "AUS": "Australia", "AUT": "Austria", "AZE": "Azerbaijan",
    "BAH": "Bahamas", "BAN": "Bangladesh", "BAR": "Barbados",
    "BHR": "Bahrain", "BRN": "Bahrain", "BLR": "Belarus",
    "BEL": "Belgium", "BIZ": "Belize", "BEN": "Benin",
    "BER": "Bermuda", "BHU": "Bhutan", "BOL": "Bolivia",
    "BIH": "Bosnia and Herzegovina", "BOT": "Botswana",
    "BRA": "Brazil", "BRU": "Brunei", "BUL": "Bulgaria",
    "BUR": "Burkina Faso", "BDI": "Burundi",
    "CAM": "Cambodia", "CMR": "Cameroon", "CAN": "Canada",
    "CPV": "Cape Verde", "CAY": "Cayman Islands",
    "CAF": "Central African Republic", "CHA": "Chad", "CHI": "Chile",
    "CHN": "China", "COL": "Colombia", "COM": "Comoros",
    "COG": "Congo", "COK": "Cook Islands", "CRC": "Costa Rica",
    "CIV": "Côte d'Ivoire", "CRO": "Croatia", "CUB": "Cuba",
    "CYP": "Cyprus", "CZE": "Czech Republic", "PRK": "North Korea",
    "COD": "DR Congo", "DEN": "Denmark", "DJI": "Djibouti",
    "DMA": "Dominica", "DOM": "Dominican Republic",
    "ECU": "Ecuador", "EGY": "Egypt", "ESA": "El Salvador",
    "GEQ": "Equatorial Guinea", "ERI": "Eritrea", "EST": "Estonia",
    "SWZ": "Eswatini", "ETH": "Ethiopia", "FIJ": "Fiji",
    "FIN": "Finland", "FRA": "France", "GAB": "Gabon",
    "GAM": "Gambia", "GEO": "Georgia", "GER": "Germany",
    "GHA": "Ghana", "GRE": "Greece", "GRN": "Grenada",
    "GUA": "Guatemala", "GUI": "Guinea", "GBS": "Guinea-Bissau",
    "GUY": "Guyana", "HAI": "Haiti", "HON": "Honduras",
    "HKG": "Hong Kong", "HUN": "Hungary", "ISL": "Iceland",
    "IND": "India", "INA": "Indonesia", "IRI": "Iran",
    "IRQ": "Iraq", "IRL": "Ireland", "ISR": "Israel",
    "ITA": "Italy", "JAM": "Jamaica", "JPN": "Japan",
    "JOR": "Jordan", "KAZ": "Kazakhstan", "KEN": "Kenya",
    "KIR": "Kiribati", "KUW": "Kuwait", "KGZ": "Kyrgyzstan",
    "LAO": "Laos", "LAT": "Latvia", "LIB": "Lebanon",
    "LES": "Lesotho", "LBR": "Liberia", "LBA": "Libya",
    "LIE": "Liechtenstein", "LTU": "Lithuania", "LUX": "Luxembourg",
    "MAC": "Macao", "MAD": "Madagascar", "MAW": "Malawi",
    "MAS": "Malaysia", "MDV": "Maldives", "MLI": "Mali",
    "MLT": "Malta", "MHL": "Marshall Islands", "MTN": "Mauritania",
    "MRI": "Mauritius", "MEX": "Mexico", "FSM": "Micronesia",
    "MDA": "Moldova", "MON": "Monaco", "MGL": "Mongolia",
    "MNE": "Montenegro", "MAR": "Morocco", "MOZ": "Mozambique",
    "MYA": "Myanmar", "NAM": "Namibia", "NRU": "Nauru",
    "NEP": "Nepal", "NED": "Netherlands", "NZL": "New Zealand",
    "NCA": "Nicaragua", "NIG": "Niger", "NGR": "Nigeria",
    "MKD": "North Macedonia", "NOR": "Norway", "OMA": "Oman",
    "PAK": "Pakistan", "PLW": "Palau", "PLE": "Palestine",
    "PAN": "Panama", "PNG": "Papua New Guinea", "PAR": "Paraguay",
    "PER": "Peru", "PHI": "Philippines", "POL": "Poland",
    "POR": "Portugal", "PUR": "Puerto Rico", "QAT": "Qatar",
    "KOR": "South Korea", "ROU": "Romania", "RUS": "Russia",
    "RWA": "Rwanda", "SKN": "Saint Kitts and Nevis",
    "LCA": "Saint Lucia",
    "VIN": "Saint Vincent and the Grenadines", "SAM": "Samoa",
    "SMR": "San Marino", "STP": "São Tomé and Príncipe",
    "KSA": "Saudi Arabia", "SEN": "Senegal", "SRB": "Serbia",
    "SEY": "Seychelles", "SLE": "Sierra Leone", "SGP": "Singapore",
    "SVK": "Slovakia", "SLO": "Slovenia", "SOL": "Solomon Islands",
    "SOM": "Somalia", "RSA": "South Africa", "SSD": "South Sudan",
    "ESP": "Spain", "SRI": "Sri Lanka", "SUD": "Sudan",
    "SUR": "Suriname", "SWE": "Sweden", "SUI": "Switzerland",
    "SYR": "Syria", "TPE": "Chinese Taipei", "TJK": "Tajikistan",
    "TAN": "Tanzania", "THA": "Thailand", "TLS": "Timor-Leste",
    "TOG": "Togo", "TGA": "Tonga", "TTO": "Trinidad and Tobago",
    "TUN": "Tunisia", "TUR": "Türkiye", "TKM": "Turkmenistan",
    "TUV": "Tuvalu", "UGA": "Uganda", "UKR": "Ukraine",
    "UAE": "United Arab Emirates", "GBR": "United Kingdom",
    "USA": "United States", "URU": "Uruguay", "UZB": "Uzbekistan",
    "VAN": "Vanuatu", "VEN": "Venezuela", "VIE": "Vietnam",
    "ISV": "US Virgin Islands", "YEM": "Yemen", "ZAM": "Zambia",
    "ZIM": "Zimbabwe",
}


def flag_emoji(iso2: str) -> str:
    """Convert an ISO-2 code (e.g. 'QA') to its flag emoji ('🇶🇦').

    Works for any valid ISO-2 country code via Unicode regional
    indicator symbols.

        >>> flag_emoji('QA')
        '🇶🇦'
        >>> flag_emoji('US')
        '🇺🇸'
    """
    if not iso2 or len(iso2) != 2 or not iso2.isalpha():
        return ""
    code = iso2.upper()
    # Regional indicator symbol "A" = U+1F1E6 (= ord('A') + 0x1F1A5)
    return "".join(chr(0x1F1A5 + ord(c)) for c in code)


def ioc_emoji(ioc_code: str) -> str:
    """Get flag emoji from an IOC code.

        >>> ioc_emoji('QAT')
        '🇶🇦'
        >>> ioc_emoji('KSA')
        '🇸🇦'
    """
    return flag_emoji(ioc_to_iso(ioc_code))


def iso2(code) -> str:
    """Canonicalise any code/name to ISO-2. Empty string if unknown."""
    ioc = normalize_country(code)
    return ioc_to_iso(ioc).upper() if ioc else ""


def iso3(code) -> str:
    """Canonicalise any code/name to ISO-3 (alpha-3 for Plotly choropleth)."""
    ioc = normalize_country(code)
    return ioc_to_iso3(ioc) if ioc else ""


def name(code) -> str:
    """Full country name from any code/name.  Returns input if unknown."""
    ioc = normalize_country(code)
    return IOC_TO_NAME.get(ioc.upper() if ioc else "", code)


def emoji(code) -> str:
    """Flag emoji from any code/name."""
    return ioc_emoji(normalize_country(code))


FLAGCDN_PNG_SIZES = (20, 40, 80, 160, 320, 640, 1280, 2560)


def flag_url(code, size: int = 40, fmt: str = "png") -> str:
    """Flag CDN URL from any code/name.

    `size`  — width in px. flagcdn snaps to {20, 40, 80, 160, 320, 640,
              1280, 2560}; closest match returned.
    `fmt`   — 'png' (default) or 'svg' (resolution-independent).

        >>> flag_url('QAT', size=80)
        'https://flagcdn.com/w80/qa.png'
        >>> flag_url('FRA', fmt='svg')
        'https://flagcdn.com/fr.svg'
    """
    iso = iso2(code).lower()
    if not iso:
        return ""
    if fmt.lower() == "svg":
        return f"https://flagcdn.com/{iso}.svg"
    # Snap size to nearest available CDN width
    snap = min(FLAGCDN_PNG_SIZES, key=lambda s: abs(s - int(size)))
    return f"https://flagcdn.com/w{snap}/{iso}.png"


def flag_img(code, *, size: int = 32, shape: str = "rect",
              border: bool = True, alt: str | None = None):
    """`html.Img` of a country flag with size + shape options.

    `shape` — 'rect' (default), 'circle', or 'square' (uses CSS clip).
    `border` — adds a 1 px slate hairline (helps light flags read).

        >>> flag_img('QAT', size=24)
        >>> flag_img('FRA', size=48, shape='circle')
        >>> flag_img('USA', size=32, shape='square', border=False)
    """
    from dash import html
    url = flag_url(code, size=max(size * 2, 40))   # 2x for retina
    if not url:
        return html.Span("")
    style = {
        "width":  f"{size}px",
        "height": f"{size}px" if shape != "rect" else "auto",
        "objectFit": "cover",
        "display":   "inline-block",
        "verticalAlign": "middle",
    }
    if shape == "circle":
        style["borderRadius"] = "50%"
    elif shape == "square":
        style["borderRadius"] = "4px"
    if border:
        style["border"] = "1px solid rgba(15,23,42,0.15)"
    return html.Img(
        src=url,
        style=style,
        alt=alt or (name(code) + " flag"),
    )


def lookup(code) -> dict:
    """Full record for a country code/name. ``code`` can be IOC, ISO-2,
    ISO-3, or full name. Returns ``{}`` if unknown."""
    ioc = normalize_country(code)
    if not ioc or ioc not in IOC_TO_ISO:
        # Maybe ISO-2 → IOC
        if code and len(code) == 2:
            ioc = ISO_TO_IOC.get(code.upper(), "")
        if not ioc or ioc not in IOC_TO_ISO:
            return {}
    iso2_c = IOC_TO_ISO[ioc]
    return {
        "ioc":      ioc,
        "iso2":     iso2_c,
        "iso3":     ioc_to_iso3(ioc),
        "name":     IOC_TO_NAME.get(ioc, ioc),
        "emoji":    flag_emoji(iso2_c),
        "flag_url": f"https://flagcdn.com/w40/{iso2_c.lower()}.png",
    }


def search(query: str) -> str:
    """Fuzzy-find IOC code from partial name match.  First hit wins.

        >>> search("Saudi")
        'KSA'
        >>> search("ireland")
        'IRL'
    """
    q = (query or "").lower().strip()
    if not q:
        return ""
    # Exact name match first
    for ioc, n in IOC_TO_NAME.items():
        if n.lower() == q:
            return ioc
    # Substring
    for ioc, n in IOC_TO_NAME.items():
        if q in n.lower():
            return ioc
    return ""


def normalise(code_or_name: str) -> str:
    """Canonicalise any input to its IOC 3-letter code.

        >>> normalise('Qatar')
        'QAT'
        >>> normalise('SA')      # ISO-2
        'KSA'
        >>> normalise('saudi arabia')
        'KSA'
    """
    if not code_or_name:
        return ""
    upper = code_or_name.strip().upper()
    if upper in IOC_TO_ISO:
        return upper
    if len(upper) == 2 and upper in ISO_TO_IOC:
        return ISO_TO_IOC[upper]
    if upper in COUNTRY_NAME_TO_IOC:
        return COUNTRY_NAME_TO_IOC[upper]
    return search(code_or_name) or upper


# Convenience: dict of every country we know about.
# Keyed by IOC, values are the full lookup dict.
ALL: dict[str, dict] = {
    ioc: {
        "ioc":      ioc,
        "iso2":     iso_,
        "iso3":     ioc_to_iso3(ioc),
        "name":     IOC_TO_NAME.get(ioc, ioc),
        "emoji":    flag_emoji(iso_),
        "flag_url": f"https://flagcdn.com/w40/{iso_.lower()}.png",
    }
    for ioc, iso_ in IOC_TO_ISO.items()
}
