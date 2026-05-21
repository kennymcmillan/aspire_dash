"""Cards & Layouts — sport cards, grids, login page preview."""

import dash
from dash import html
from aspire_dash.components import card, summary_card, info_box, badge
from aspire_dash.theme import SLATE, ACCENT, SUCCESS, WARNING, DANGER, GOLD

dash.register_page(__name__, path="/cards", title="Cards & Layouts", name="Cards & Layouts")


def _sport_card(name, icon_class, budget, spent, status):
    pct = round(spent / budget * 100, 1) if budget else 0
    status_map = {
        "green": {"css": "status-green", "color": SUCCESS, "bg": "#f0fdf4", "border": "#bbf7d0"},
        "yellow": {"css": "status-yellow", "color": WARNING, "bg": "#fffbeb", "border": "#fde68a"},
        "red": {"css": "status-red", "color": DANGER, "bg": "#fef2f2", "border": "#fecaca"},
    }
    s = status_map.get(status, status_map["green"])

    return html.Div([
        html.Div([
            html.Span([
                html.I(className=icon_class, style={"marginRight": "6px", "fontSize": "13px"}),
                name,
            ], style={"fontWeight": "600", "fontSize": "14px"}),
            html.Span(f"{pct}%", style={
                "fontSize": "12px", "fontWeight": "700", "color": s["color"],
            }),
        ], style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "8px"}),
        html.Div([
            html.Div([
                html.Span("Budget: ", style={"color": SLATE["500"]}),
                html.Span(f"QAR {budget:,.0f}", style={"fontWeight": "500"}),
            ], style={"fontSize": "12px"}),
            html.Div([
                html.Span("Spent: ", style={"color": SLATE["500"]}),
                html.Span(f"QAR {spent:,.0f}", style={"fontWeight": "500"}),
            ], style={"fontSize": "12px"}),
        ], style={"marginBottom": "8px"}),
        # Mini progress
        html.Div([
            html.Div(style={
                "width": f"{min(pct, 100)}%",
                "backgroundColor": s["color"],
                "height": "100%", "borderRadius": "3px",
            }),
        ], className="mini-progress"),
        html.Div([
            html.Span("View details", style={
                "fontSize": "11px", "color": ACCENT, "cursor": "pointer",
            }),
        ], style={"marginTop": "8px", "paddingTop": "8px", "borderTop": "1px solid rgba(0,0,0,0.06)"}),
    ], className=f"sport-card {s['css']}", style={
        "background": s["bg"], "borderColor": s["border"],
    })


def layout(**kwargs):
    return html.Div([
        # Sport Cards Grid
        html.H2("Sport Cards Grid", className="section-title"),
        html.P("Interactive cards with mini progress bars — hover for elevation effect.",
               style={"fontSize": "13px", "color": SLATE["500"], "marginBottom": "12px"}),

        html.Div([
            _sport_card("Football", "fa-solid fa-futbol", 3200000, 2800000, "yellow"),
            _sport_card("Athletics", "fa-solid fa-person-running", 2100000, 1600000, "green"),
            _sport_card("Swimming", "fa-solid fa-person-swimming", 1800000, 1750000, "red"),
            _sport_card("Fencing", "fa-solid fa-shield-halved", 1500000, 1100000, "green"),
            _sport_card("Squash", "fa-solid fa-table-tennis-paddle-ball", 1200000, 800000, "green"),
            _sport_card("Padel", "fa-solid fa-table-tennis-paddle-ball", 900000, 650000, "green"),
            _sport_card("Table Tennis", "fa-solid fa-table-tennis-paddle-ball", 850000, 400000, "green"),
            _sport_card("Gymnastics", "fa-solid fa-dumbbell", 700000, 550000, "green"),
        ], style={
            "display": "grid",
            "gridTemplateColumns": "repeat(auto-fill, minmax(240px, 1fr))",
            "gap": "12px",
            "marginBottom": "32px",
        }),

        # Report-style stacked bar
        html.H2("Report Bar Chart", className="section-title"),
        card([
            _report_bar("Football", 56, 20, 12),
            _report_bar("Athletics", 48, 15, 13),
            _report_bar("Swimming", 72, 18, 7),
            _report_bar("Fencing", 52, 12, 9),
            _report_bar("Squash", 40, 18, 9),
        ]),

        # Login page preview
        html.H2("Login Page Preview", className="section-title"),
        html.Div([
            html.Div([
                html.Div([
                    html.Img(src="/assets/aspire-logo.png", style={"height": "40px", "margin": "0 auto 16px", "display": "block"}),
                    html.H2("Sign In", style={"color": "white", "textAlign": "center", "marginBottom": "24px", "fontSize": "22px"}),
                    html.Div("Email address", style={
                        "width": "100%", "padding": "10px 14px", "border": f"1px solid {SLATE['600']}",
                        "borderRadius": "8px", "background": SLATE["700"], "color": "rgba(255,255,255,0.5)",
                        "fontSize": "14px", "marginBottom": "12px", "boxSizing": "border-box"}),
                    html.Div("Password", style={
                        "width": "100%", "padding": "10px 14px", "border": f"1px solid {SLATE['600']}",
                        "borderRadius": "8px", "background": SLATE["700"], "color": "rgba(255,255,255,0.5)",
                        "fontSize": "14px", "marginBottom": "20px", "boxSizing": "border-box"}),
                    html.Button("Sign In", style={
                        "width": "100%", "padding": "12px", "border": "none", "borderRadius": "8px",
                        "background": f"linear-gradient(135deg, {ACCENT}, {ACCENT}cc)",
                        "color": "white", "fontWeight": "600", "fontSize": "15px", "cursor": "pointer",
                    }),
                ], style={
                    "background": SLATE["800"], "border": f"1px solid {SLATE['700']}",
                    "borderRadius": "16px", "padding": "40px", "width": "360px",
                    "boxShadow": "0 20px 60px rgba(0,0,0,0.3)",
                }),
            ], style={
                "background": f"linear-gradient(135deg, {SLATE['900']}, {SLATE['800']})",
                "borderRadius": "12px", "padding": "60px",
                "display": "flex", "alignItems": "center", "justifyContent": "center",
            }),
        ], style={"marginBottom": "24px"}),

        # Gold accent demo
        html.H2("Gold Accent (#fbb800)", className="section-title"),
        html.Div([
            html.Div([
                html.Div("Award", style={
                    "fontSize": "11px", "fontWeight": "600", "color": "#92400e",
                    "textTransform": "uppercase", "letterSpacing": "0.05em", "marginBottom": "4px",
                }),
                html.Div("Best Performance", style={"fontSize": "18px", "fontWeight": "700", "color": SLATE["800"]}),
                html.Div(style={
                    "width": "40px", "height": "3px", "background": GOLD,
                    "borderRadius": "2px", "marginTop": "8px",
                }),
            ], style={
                "background": "white", "border": f"2px solid {GOLD}",
                "borderRadius": "12px", "padding": "20px", "flex": "1",
                "borderLeft": f"4px solid {GOLD}",
            }),
            html.Div([
                html.Span([html.I(className="fa-solid fa-star", style={"marginRight": "6px"}), "Gold Standard"], style={
                    "background": GOLD, "color": "white", "padding": "6px 16px",
                    "borderRadius": "9999px", "fontWeight": "600", "fontSize": "13px",
                }),
            ], style={"display": "flex", "alignItems": "center", "flex": "1", "justifyContent": "center"}),
        ], style={"display": "flex", "gap": "16px", "marginBottom": "24px"}),

    ], style={"maxWidth": "1200px"})


def _report_bar(sport, paid_pct, enc_pct, plan_pct):
    total = paid_pct + enc_pct + plan_pct
    return html.Div([
        html.Div(sport, className="report-bar-label", style={"width": "120px", "flexShrink": "0"}),
        html.Div([
            html.Div(style={"width": f"{paid_pct}%", "backgroundColor": SUCCESS, "height": "100%"}),
            html.Div(style={"width": f"{enc_pct}%", "backgroundColor": WARNING, "height": "100%"}),
            html.Div(style={"width": f"{plan_pct}%", "backgroundColor": ACCENT, "height": "100%"}),
        ], className="report-bar-container", style={"flex": "1", "height": "24px", "display": "flex"}),
        html.Div(f"{total}%", className="report-bar-pct", style={
            "width": "50px", "textAlign": "right", "fontWeight": "600", "fontSize": "13px",
        }),
    ], className="report-bar-row", style={
        "display": "flex", "alignItems": "center", "gap": "12px",
        "padding": "8px 0", "borderBottom": f"1px solid {SLATE['100']}",
    })
