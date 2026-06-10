"""Layouts — sidebar vs topnav side-by-side + the Aspire Quarto template."""
import dash
from dash import html

from ._shared import section, code_block

dash.register_page(__name__, path="/layouts", title="Layouts", name="Layouts")


# ── Visual diagrams (CSS-only, no Plotly) ────────────────────────────────────

def _sidebar_diagram():
    """Diagram of the sidebar layout — sidebar on left, header, content."""
    return html.Div([
        # Sidebar
        html.Div([
            html.Div("LOGO", style={"fontSize": "10px", "fontWeight": 700,
                                     "color": "white", "marginBottom": "10px"}),
            *[html.Div(f"• Nav item {i+1}",
                       style={"fontSize": "9px", "color": "#cbd5e1",
                              "marginBottom": "4px"})
              for i in range(5)],
        ], style={"width": "70px", "background": "#001d3d",
                   "padding": "10px 8px", "borderRadius": "4px 0 0 4px"}),
        # Main column
        html.Div([
            html.Div("Header / breadcrumbs",
                      style={"fontSize": "10px", "color": "#64748b",
                              "padding": "8px",
                              "borderBottom": "1px solid #e2e8f0"}),
            html.Div("Page content",
                      style={"fontSize": "11px", "color": "#94a3b8",
                              "padding": "16px", "textAlign": "center",
                              "fontStyle": "italic"}),
        ], style={"flex": 1, "background": "#f8fafc",
                   "borderRadius": "0 4px 4px 0"}),
    ], style={"display": "flex", "height": "140px",
               "border": "1px solid #e2e8f0", "borderRadius": "4px",
               "overflow": "hidden"})


def _topnav_diagram():
    """Diagram of the topnav layout — full-width top bar, content."""
    return html.Div([
        # Top bar
        html.Div([
            html.Span("LOGO", style={"fontSize": "10px", "fontWeight": 700,
                                       "color": "white"}),
            html.Span("•", style={"color": "#475569", "margin": "0 8px"}),
            *[html.Span(f"Nav {i+1}",
                        style={"fontSize": "9px", "color": "#cbd5e1",
                                "marginRight": "10px"})
              for i in range(5)],
        ], style={"background": "#001d3d", "padding": "10px 14px",
                   "borderRadius": "4px 4px 0 0",
                   "display": "flex", "alignItems": "center"}),
        # Page area
        html.Div("Page content (wider than sidebar layout)",
                  style={"fontSize": "11px", "color": "#94a3b8",
                          "padding": "24px", "textAlign": "center",
                          "fontStyle": "italic",
                          "background": "#f8fafc", "height": "108px",
                          "borderRadius": "0 0 4px 4px"}),
    ], style={"border": "1px solid #e2e8f0", "borderRadius": "4px",
               "overflow": "hidden"})


def _quarto_diagram():
    """Diagram of a Quarto report layout — title page, sections, charts."""
    return html.Div([
        # Cover strip
        html.Div([
            html.Div("ASPIRE ACADEMY",
                      style={"color": "white", "fontSize": "9px",
                             "letterSpacing": "0.1em"}),
            html.Div("Quarterly Performance Brief",
                      style={"color": "white", "fontSize": "11px",
                             "fontWeight": 700, "marginTop": "2px"}),
        ], style={"background": "#004185", "padding": "12px 16px"}),
        # Body
        html.Div([
            html.Div("§ Executive summary",
                      style={"fontSize": "9px", "fontWeight": 700,
                              "color": "#004185", "marginBottom": "4px"}),
            html.Div("Body copy lorem ipsum dolor sit amet…",
                      style={"fontSize": "8px", "color": "#64748b",
                              "marginBottom": "10px"}),
            html.Div([
                html.Div(style={"flex": 1, "background": "#dbeafe",
                                 "height": "30px", "borderRadius": "2px"}),
                html.Div(style={"flex": 1, "background": "#dbeafe",
                                 "height": "30px", "borderRadius": "2px"}),
            ], style={"display": "flex", "gap": "4px",
                       "marginBottom": "6px"}),
            html.Div("§ Detailed breakdown",
                      style={"fontSize": "9px", "fontWeight": 700,
                              "color": "#004185"}),
        ], style={"padding": "10px 16px", "background": "white",
                   "height": "100px"}),
    ], style={"border": "1px solid #e2e8f0", "borderRadius": "4px",
               "overflow": "hidden"})


# ── Page layout ──────────────────────────────────────────────────────────────

def layout():
    return html.Div([
        html.H1("Layouts",
                style={"fontSize": "28px", "fontWeight": 700,
                       "marginBottom": "8px"}),
        html.P("The three Aspire layouts: sidebar shells (data-heavy apps), "
                "topnav shells (workflow apps), and Quarto report shells "
                "(printable executive artefacts).",
                style={"color": "#64748b", "fontSize": "14px",
                       "marginBottom": "24px"}),

        # Two-up: sidebar vs topnav
        html.Div([
            html.Div([
                html.H3("Sidebar layout",
                        style={"fontSize": "15px", "fontWeight": 700,
                                "color": "#0f172a", "marginBottom": "4px"}),
                html.P("Best for data-heavy apps with many distinct pages "
                        "(dashboards, reports, lookups). Holds 10+ nav items "
                        "comfortably.",
                        style={"fontSize": "12px", "color": "#64748b",
                                "margin": "0 0 10px 0"}),
                _sidebar_diagram(),
                html.Div([
                    html.Strong("Live in: ", style={"fontSize": "11px",
                                                      "color": "#475569"}),
                    html.A("mapping_app",
                            href="https://posit.aspire.qa/content/5dd51925-0db5-4cd2-9c47-69b4b59f8aa6/",
                            target="_blank",
                            style={"fontSize": "11px", "color": "#0369a1"}),
                    html.Span(" · ", style={"color": "#cbd5e1"}),
                    html.A("aspire_dash demo (this app)",
                            href="#",
                            style={"fontSize": "11px", "color": "#0369a1"}),
                ], style={"marginTop": "8px"}),
            ], style={"flex": "1 1 320px", "minWidth": "0",
                       "padding": "16px",
                       "border": "1px solid #e2e8f0",
                       "borderRadius": "6px",
                       "background": "white",
                       "overflow": "hidden"}),

            html.Div([
                html.H3("Topnav layout",
                        style={"fontSize": "15px", "fontWeight": 700,
                                "color": "#0f172a", "marginBottom": "4px"}),
                html.P("Best for workflow apps with 3-6 main surfaces "
                        "(data entry, weekly grids). Frees full screen "
                        "width for tables and charts.",
                        style={"fontSize": "12px", "color": "#64748b",
                                "margin": "0 0 10px 0"}),
                _topnav_diagram(),
                html.Div([
                    html.Strong("Live in: ", style={"fontSize": "11px",
                                                      "color": "#475569"}),
                    html.A("Fencing Training Plan",
                            href="https://posit.aspire.qa/content/d83e61a9-9f74-487f-b837-161236b703fc/",
                            target="_blank",
                            style={"fontSize": "11px", "color": "#0369a1"}),
                    html.Span(" · ", style={"color": "#cbd5e1"}),
                    html.A("Medical Dashboard",
                            href="https://posit.aspire.qa/content/c12b9927-a2d7-47bf-9194-f59662e64a30/",
                            target="_blank",
                            style={"fontSize": "11px", "color": "#0369a1"}),
                ], style={"marginTop": "8px"}),
            ], style={"flex": "1 1 320px", "minWidth": "0",
                       "padding": "16px",
                       "border": "1px solid #e2e8f0",
                       "borderRadius": "6px",
                       "background": "white",
                       "overflow": "hidden"}),
        ], style={"display": "flex", "flexWrap": "wrap", "gap": "16px",
                   "marginBottom": "24px"}),

        # Code samples
        section("Sidebar — code",
                 "Pass the nav as a list of {label, href, icon, section} dicts."),
        code_block(
            "from aspire_dash import setup_app, STYLESHEETS\n"
            "from aspire_dash.components import sidebar, header, dark_mode_toggle\n"
            "from aspire_dash.layouts import page_layout\n\n"
            "app = Dash(__name__, use_pages=True, external_stylesheets=STYLESHEETS,\n"
            "           suppress_callback_exceptions=True)\n"
            "setup_app(app)\n\n"
            "nav = [\n"
            "    {'label': 'Overview', 'href': '/', 'icon': 'fa-solid fa-gauge'},\n"
            "    {'label': 'Reports',  'href': '/reports',\n"
            "     'icon': 'fa-solid fa-file', 'section': 'Reports'},\n"
            "]\n\n"
            "app.layout = page_layout(\n"
            "    sidebar_el=sidebar(title='My App', nav_items=nav),\n"
            "    header_el=header(title='My App',\n"
            "                     right_content=dark_mode_toggle()),\n"
            "    use_pages=True,\n"
            ")\n"
        ),

        section("Topnav — code",
                 "Same idea, different shell. Pair with register_topnav_active "
                 "to highlight the current page."),
        code_block(
            "from aspire_dash.components import topnav, register_topnav_active\n\n"
            "NAV_ITEMS = [\n"
            "    {'label': 'Data Entry', 'href': '/',\n"
            "     'icon': 'fa-solid fa-keyboard', 'id': 'nav-entry'},\n"
            "    {'label': 'Overview',   'href': '/overview',\n"
            "     'icon': 'fa-solid fa-gauge',    'id': 'nav-overview'},\n"
            "]\n\n"
            "app.layout = html.Div([\n"
            "    dcc.Location(id='url'),\n"
            "    topnav(brand='Aspire Fencing', nav_items=NAV_ITEMS),\n"
            "    dash.page_container,\n"
            "])\n"
            "register_topnav_active(app, NAV_ITEMS)\n"
        ),

        # Quarto
        html.Div([
            html.Div([
                html.H3("Aspire Quarto Reports",
                        style={"fontSize": "15px", "fontWeight": 700,
                                "color": "#0f172a", "marginBottom": "4px"}),
                html.P("For executive briefings, monthly reports, and any "
                        "static / scheduled document — render once, share as "
                        "PDF/HTML. Aspire-branded Quarto extension at "
                        "kennymcmillan/aspire (live in every Quarto report "
                        "under Posit_reports). Pairs with the A4 Dash report "
                        "shell for interactive equivalents.",
                        style={"fontSize": "12px", "color": "#64748b",
                                "margin": "0 0 10px 0"}),
                _quarto_diagram(),
                html.Div([
                    html.Strong("Examples: ",
                                 style={"fontSize": "11px", "color": "#475569"}),
                    html.A("GCC Games tournament report",
                            href="https://posit.aspire.qa/content/409f1a32-3742-4f73-9d6c-f8404be0488d/",
                            target="_blank",
                            style={"fontSize": "11px", "color": "#0369a1"}),
                    html.Span(" · ", style={"color": "#cbd5e1"}),
                    html.A("Repo",
                            href="https://github.com/kennymcmillan/aspire",
                            target="_blank",
                            style={"fontSize": "11px", "color": "#0369a1"}),
                ], style={"marginTop": "8px"}),
            ], style={"flex": 1, "padding": "16px",
                       "border": "1px solid #e2e8f0",
                       "borderRadius": "6px",
                       "background": "white",
                       "marginBottom": "16px"}),
        ]),

        section("Quarto — usage",
                 "Install the extension, then add to the YAML header. "
                 "Renders to HTML and PDF (via Typst). Use for static "
                 "reports where Dash interactivity isn't needed."),
        code_block(
            "# In your report's _quarto.yml or YAML header\n"
            "format:\n"
            "  aspire-html: default\n"
            "  aspire-pdf: default\n\n"
            "# Install the extension\n"
            "quarto add kennymcmillan/aspire\n\n"
            "# Render\n"
            "quarto render report.qmd\n"
        ),

        # Decision guide
        section("Which layout when?",
                 "Match the shell to the user's workflow shape."),
        html.Div([
            html.Table([
                html.Thead(html.Tr([
                    html.Th("Use case", style={"padding": "8px",
                                                 "background": "#f8fafc",
                                                 "fontSize": "11px",
                                                 "textAlign": "left",
                                                 "fontWeight": 600,
                                                 "color": "#475569"}),
                    html.Th("Pick", style={"padding": "8px",
                                             "background": "#f8fafc",
                                             "fontSize": "11px",
                                             "textAlign": "left",
                                             "fontWeight": 600,
                                             "color": "#475569"}),
                    html.Th("Why", style={"padding": "8px",
                                            "background": "#f8fafc",
                                            "fontSize": "11px",
                                            "textAlign": "left",
                                            "fontWeight": 600,
                                            "color": "#475569"}),
                ])),
                html.Tbody([
                    _row("Daily coach data entry, 4-6 surfaces",
                          "Topnav", "Compact, wide grid area"),
                    _row("Many distinct lookups / dashboards",
                          "Sidebar", "Holds 10+ nav items"),
                    _row("Monthly board brief",
                          "Quarto + a4_report_shell",
                          "Static PDF, no interactivity needed"),
                    _row("In-app per-fencer printable",
                          "a4_report_shell (Dash)",
                          "Interactive context, click-to-print"),
                    _row("Per-week interactive + monthly PDF",
                          "Topnav + Quarto + Connect schedule",
                          "Dash for the live app, scheduled Quarto for the digest"),
                ]),
            ], style={"width": "100%", "borderCollapse": "collapse"}),
        ]),
    ], style={"padding": "24px"})


def _row(use_case, pick, why):
    return html.Tr([
        html.Td(use_case, style={"padding": "8px", "fontSize": "11px",
                                  "borderBottom": "1px solid #f1f5f9"}),
        html.Td(pick, style={"padding": "8px", "fontSize": "11px",
                              "fontWeight": 600, "color": "#0369a1",
                              "borderBottom": "1px solid #f1f5f9"}),
        html.Td(why, style={"padding": "8px", "fontSize": "11px",
                              "color": "#64748b",
                              "borderBottom": "1px solid #f1f5f9"}),
    ])
