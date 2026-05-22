"""Countries module — IOC/ISO/name/flag in one place, with size+shape options."""
import dash
from dash import html

from aspire_dash import countries as c

from ._shared import section, code_block

dash.register_page(__name__, path="/countries", title="Countries",
                    name="Countries & flags")


SHOWCASE = ["QAT", "KSA", "UAE", "BHR", "OMA", "KUW",  # GCC
             "USA", "GBR", "FRA", "ITA", "GER", "ESP",
             "JPN", "KOR", "CHN", "RSA", "BRA",
             "IRI", "INA", "TPE", "MAS"]


def layout():
    return html.Div([
        html.H1("Countries & flags",
                style={"fontSize": "28px", "fontWeight": 700,
                       "marginBottom": "8px"}),
        html.P("204 countries with IOC ↔ ISO-2 ↔ ISO-3 ↔ name ↔ flag "
                "emoji ↔ flag CDN URL — single import, no per-app dicts.",
                style={"color": "#64748b", "fontSize": "14px",
                       "marginBottom": "24px"}),

        # Flag sizes / shapes
        section("flag_img — sizes and shapes",
                 "Pass size in px + shape ('rect' / 'circle' / 'square')."),
        html.Div([
            _flag_demo("QAT", 24, "rect"),
            _flag_demo("QAT", 32, "rect"),
            _flag_demo("QAT", 48, "rect"),
            _flag_demo("QAT", 64, "rect"),
            _flag_demo("QAT", 48, "circle"),
            _flag_demo("FRA", 48, "circle"),
            _flag_demo("USA", 48, "circle"),
            _flag_demo("JPN", 48, "circle"),
            _flag_demo("QAT", 48, "square"),
            _flag_demo("KSA", 48, "square"),
            _flag_demo("UAE", 48, "square"),
            _flag_demo("BHR", 48, "square"),
        ], style={"display": "flex", "flexWrap": "wrap",
                   "gap": "20px", "alignItems": "end",
                   "padding": "16px"}, className="card"),
        code_block(
            "from aspire_dash import countries\n\n"
            "countries.flag_img('QAT', size=24)\n"
            "countries.flag_img('FRA', size=48, shape='circle')\n"
            "countries.flag_img('USA', size=32, shape='square', border=False)\n\n"
            "# Just the URL (for plotly markers, custom layouts, etc.)\n"
            "countries.flag_url('QAT', size=80, fmt='png')\n"
            "countries.flag_url('FRA', fmt='svg')   # resolution-independent\n"
        ),

        # Showcase grid
        section(f"Showcase ({len(SHOWCASE)} countries)",
                 "GCC + major sports nations. Each card shows ioc/iso2/iso3/name/emoji."),
        html.Div(
            [_country_card(code) for code in SHOWCASE],
            style={"display": "grid",
                    "gridTemplateColumns": "repeat(auto-fill, minmax(220px, 1fr))",
                    "gap": "12px"},
        ),

        # Lookup API
        section("Lookup / normalise — IOC, ISO-2, ISO-3, full name"),
        html.Pre([
            "countries.lookup('QAT')\n",
            "  -> {'ioc': 'QAT', 'iso2': 'QA', 'iso3': 'QAT',\n",
            "      'name': 'Qatar', 'emoji': '🇶🇦',\n",
            "      'flag_url': 'https://flagcdn.com/w40/qa.png'}\n\n",
            "countries.name('FRA')          # 'France'\n",
            "countries.iso3('INA')          # 'IDN'   (for Plotly choropleth)\n",
            "countries.normalise('Qatar')   # 'QAT'\n",
            "countries.normalise('SA')      # 'KSA'    (ISO-2 → IOC)\n",
            "countries.search('Saudi')      # 'KSA'    (fuzzy by name)\n\n",
            "# 204 countries — iterate the whole catalogue\n",
            "for code, meta in countries.ALL.items():\n",
            "    print(code, meta['name'])\n",
        ], style={"background": "#f1f5f9", "padding": "16px",
                   "borderRadius": "8px", "fontSize": "12px",
                   "lineHeight": "1.6", "fontFamily": "Fira Code, monospace"}),

        # Reference dropdown population
        section("Use it for any sport-app country dropdown",
                 "Drop-in replacement for hand-rolled country lists."),
        code_block(
            "from aspire_dash import countries\n\n"
            "options = [\n"
            "    {'label': f'{m[\"emoji\"]}  {m[\"name\"]}', 'value': code}\n"
            "    for code, m in sorted(countries.ALL.items(),\n"
            "                          key=lambda x: x[1]['name'])\n"
            "]\n"
            "dcc.Dropdown(options=options, placeholder='Country…')\n"
        ),

    ], style={"padding": "24px"})


def _flag_demo(code, size, shape):
    return html.Div([
        c.flag_img(code, size=size, shape=shape),
        html.Div(f"{code} {size}px {shape}",
                  style={"fontSize": "10px", "color": "#94a3b8",
                          "marginTop": "4px",
                          "fontFamily": "monospace"}),
    ], style={"textAlign": "center"})


def _country_card(code):
    meta = c.lookup(code)
    return html.Div([
        html.Div([
            c.flag_img(code, size=44, shape="rect"),
        ], style={"display": "flex", "alignItems": "center",
                   "justifyContent": "center",
                   "height": "60px", "background": "white"}),
        html.Div([
            html.Div(meta["name"],
                      style={"fontSize": "14px", "fontWeight": 700,
                              "color": "#1e293b"}),
            html.Div(f"{meta['emoji']}  IOC: {meta['ioc']}  ·  "
                      f"ISO-2: {meta['iso2']}  ·  ISO-3: {meta['iso3']}",
                      style={"fontSize": "10px",
                              "color": "#64748b",
                              "fontFamily": "monospace",
                              "marginTop": "2px"}),
        ], style={"padding": "10px 12px",
                   "borderTop": "1px solid #e2e8f0"}),
    ], className="card", style={"padding": "0", "overflow": "hidden"})
