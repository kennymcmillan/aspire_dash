"""Assets — Aspire logo + brand image inventory."""
import dash
from dash import html

from ._shared import section, code_block

dash.register_page(__name__, path="/assets", title="Assets", name="Assets")


# The assets/ folder is auto-populated by setup_app() — these paths are
# served at /assets/<filename> by every aspire_dash app.

LOGO_FILES = [
    ("aspire-logo.png",  "Primary mark (PNG, transparent bg)",  "auto"),
]


def layout():
    return html.Div([
        html.H1("Assets", style={"fontSize": "28px", "fontWeight": 700,
                                   "marginBottom": "8px"}),
        html.P("Aspire-branded assets that ship with aspire_dash. "
                "setup_app() copies these into your app's /assets folder on "
                "first launch, so they're served at /assets/<filename>.",
                style={"color": "#64748b", "fontSize": "14px",
                       "marginBottom": "24px"}),

        section("Logo — primary",
                 "The Aspire mark. Sits in headers, sidebars, print footers."),
        html.Div([
            html.Div([
                html.Div([
                    html.Img(src=dash.get_relative_path("/assets/aspire-logo.png"),
                              style={"height": "60px"}),
                ], style={"padding": "16px",
                           "background": "white",
                           "border": "1px solid #e2e8f0",
                           "borderRadius": "6px"}),
                html.Div("On white",
                          style={"fontSize": "11px",
                                  "color": "#94a3b8", "marginTop": "4px",
                                  "textAlign": "center"}),
            ], style={"flex": 1}),
            html.Div([
                html.Div([
                    html.Img(src=dash.get_relative_path("/assets/aspire-logo.png"),
                              style={"height": "60px"}),
                ], style={"padding": "16px",
                           "background": "#001d3d",
                           "border": "1px solid #001d3d",
                           "borderRadius": "6px"}),
                html.Div("On Aspire navy",
                          style={"fontSize": "11px",
                                  "color": "#94a3b8", "marginTop": "4px",
                                  "textAlign": "center"}),
            ], style={"flex": 1}),
            html.Div([
                html.Div([
                    html.Img(src=dash.get_relative_path("/assets/aspire-logo.png"),
                              style={"height": "60px"}),
                ], style={"padding": "16px",
                           "background": "#004185",
                           "border": "1px solid #004185",
                           "borderRadius": "6px"}),
                html.Div("On Aspire blue",
                          style={"fontSize": "11px",
                                  "color": "#94a3b8", "marginTop": "4px",
                                  "textAlign": "center"}),
            ], style={"flex": 1}),
        ], style={"display": "flex", "gap": "16px",
                   "marginBottom": "20px"}),

        section("How to use", "setup_app() auto-copies; reference as a "
                              "static asset URL."),
        code_block(
            "# In your app.py\n"
            "from aspire_dash import setup_app\n"
            "setup_app(app)   # auto-copies /assets/aspire-logo.png\n\n"
            "# In any layout\n"
            "html.Img(src='/assets/aspire-logo.png',\n"
            "         style={'height': '32px'})\n\n"
            "# Or via the sidebar/header helpers (handled automatically)\n"
            "sidebar(title='My App', nav_items=nav)\n"
        ),

        section("Other shared assets",
                 "Anything in aspire_dash/assets/ ships with setup_app()."),
        html.Div([
            html.Strong("CSS: ", style={"fontSize": "12px",
                                          "color": "#475569"}),
            html.Code("/assets/00_aspire_base.css",
                       style={"fontSize": "11px", "background": "#f1f5f9",
                              "padding": "2px 6px", "borderRadius": "3px"}),
            html.Span("  ", style={"width": "10px", "display": "inline-block"}),
            html.Code("/assets/01_aspire_print.css",
                       style={"fontSize": "11px", "background": "#f1f5f9",
                              "padding": "2px 6px", "borderRadius": "3px"}),
            html.Span("  ", style={"width": "10px", "display": "inline-block"}),
            html.Code("/assets/02_aspire_skeletons.css",
                       style={"fontSize": "11px", "background": "#f1f5f9",
                              "padding": "2px 6px", "borderRadius": "3px"}),
        ], style={"marginBottom": "8px"}),
        html.Div([
            html.Strong("JS: ", style={"fontSize": "12px",
                                         "color": "#475569"}),
            html.Code("/assets/sidebar_toggle.js",
                       style={"fontSize": "11px", "background": "#f1f5f9",
                              "padding": "2px 6px", "borderRadius": "3px"}),
            html.Span("  ", style={"width": "10px", "display": "inline-block"}),
            html.Code("/assets/dark_mode.js",
                       style={"fontSize": "11px", "background": "#f1f5f9",
                              "padding": "2px 6px", "borderRadius": "3px"}),
        ], style={"marginBottom": "20px"}),

        section("Brand spec",
                 "Single source of truth — overrideable via brand.yml in "
                 "the library root."),
        code_block(
            "# brand.yml — colours, fonts, logo path\n"
            "# Lives at aspire_dash/brand.yml\n"
            "# Loaded by aspire_dash.theme on import\n\n"
            "colours:\n"
            "  primary: '#004185'    # aspire-600\n"
            "  navy:    '#001d3d'\n"
            "  accent:  '#0369a1'\n\n"
            "fonts:\n"
            "  body: 'Inter, sans-serif'\n\n"
            "logo:\n"
            "  filename: 'aspire-logo.png'\n"
            "  alt: 'Aspire Academy'\n"
        ),
    ], style={"padding": "24px"})
