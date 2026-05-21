"""Component Showcase — every shared component on one page."""

import dash
from dash import html, dcc, callback, Input, Output, ctx
import dash_bootstrap_components as dbc
from aspire_dash.components import (
    card, summary_card, toast, badge, info_box, empty_state,
    toggle_group, filter_bar,
)
from aspire_dash.theme import (
    ACCENT, ACCENT_HOVER, SECONDARY, GOLD, GOLD_LIGHT,
    ASPIRE, SLATE, CHART_COLORS,
    SUCCESS, WARNING, DANGER, INFO,
    SHADOW_SM, SHADOW_MD, SHADOW_LG,
)

dash.register_page(__name__, path="/", title="Component Showcase", name="Component Showcase")


def layout(**kwargs):
    return html.Div([
        # ── Section: Summary Cards ──
        html.H2("Summary Cards", className="section-title", style={"marginTop": "0"}),
        html.P("KPI cards with colour variants — used for dashboards and reports.",
               style={"fontSize": "13px", "color": SLATE["500"], "marginBottom": "12px"}),

        html.Div([
            html.Div(summary_card("Total Budget", "QAR 12,450,000", sub="FY 2026", icon="fa-solid fa-wallet"), style={"flex": "1"}),
            html.Div(summary_card("Paid", "QAR 8,200,000", sub="65.9%", icon="fa-solid fa-check-circle", color_class="paid"), style={"flex": "1"}),
            html.Div(summary_card("Encumbered", "QAR 1,850,000", sub="14.9%", icon="fa-solid fa-clock", color_class="encumbered"), style={"flex": "1"}),
            html.Div(summary_card("Planned", "QAR 900,000", sub="7.2%", icon="fa-solid fa-calendar", color_class="planned"), style={"flex": "1"}),
            html.Div(summary_card("Remaining", "QAR 1,500,000", sub="12.0%", icon="fa-solid fa-piggy-bank"), style={"flex": "1"}),
        ], style={"display": "flex", "gap": "12px", "marginBottom": "24px"}),

        # ── Section: Badges ──
        html.H2("Badges", className="section-title"),
        card([
            html.Div([
                badge("Default", "gray"), " ",
                badge("Info", "blue"), " ",
                badge("Success", "green"), " ",
                badge("Danger", "red"), " ",
                badge("Warning", "amber"), " ",
                badge("Teal", "teal"), " ",
            ], style={"display": "flex", "gap": "8px", "flexWrap": "wrap", "marginBottom": "16px"}),

            html.Div("Status badges:", style={"fontSize": "12px", "color": SLATE["500"], "marginBottom": "8px"}),
            html.Div([
                html.Span("Draft", className="status-badge draft"), " ",
                html.Span("Active", className="status-badge active"), " ",
                html.Span("Closed", className="status-badge closed"), " ",
            ], style={"display": "flex", "gap": "8px"}),
        ]),

        # ── Section: Buttons ──
        html.H2("Buttons", className="section-title"),
        card([
            html.Div([
                dbc.Button("Primary", color="primary", className="me-2"),
                dbc.Button("Secondary", color="secondary", className="me-2"),
                dbc.Button("Success", color="success", className="me-2"),
                dbc.Button("Danger", color="danger", className="me-2"),
                dbc.Button("Warning", color="warning", className="me-2"),
                dbc.Button("Info", color="info", className="me-2"),
                dbc.Button("Light", color="light", className="me-2"),
            ], style={"display": "flex", "gap": "4px", "flexWrap": "wrap", "marginBottom": "12px"}),
            html.Div([
                dbc.Button("Small", color="primary", size="sm", className="me-2"),
                dbc.Button("Disabled", color="primary", disabled=True, className="me-2"),
                dbc.Button([html.I(className="fa-solid fa-plus", style={"marginRight": "6px"}), "With Icon"],
                           color="primary", className="me-2"),
            ], style={"display": "flex", "gap": "4px", "alignItems": "center"}),
        ]),

        # ── Section: Progress Bars ──
        html.H2("Progress Bars", className="section-title"),
        card([
            html.Div("65% — On Track", style={"fontSize": "12px", "fontWeight": "600", "color": SLATE["600"], "marginBottom": "4px"}),
            html.Div([
                html.Div(style={"width": "65%", "backgroundColor": SUCCESS, "height": "100%", "borderRadius": "9999px"}),
            ], className="progress-bar-bg", style={"marginBottom": "16px"}),

            html.Div("88% — Caution", style={"fontSize": "12px", "fontWeight": "600", "color": SLATE["600"], "marginBottom": "4px"}),
            html.Div([
                html.Div(style={"width": "88%", "backgroundColor": WARNING, "height": "100%", "borderRadius": "9999px"}),
            ], className="progress-bar-bg", style={"marginBottom": "16px"}),

            html.Div("105% — Over Budget", style={"fontSize": "12px", "fontWeight": "600", "color": SLATE["600"], "marginBottom": "4px"}),
            html.Div([
                html.Div(style={"width": "100%", "backgroundColor": DANGER, "height": "100%", "borderRadius": "9999px"}),
            ], className="progress-bar-bg", style={"marginBottom": "16px"}),

            html.Div("Mini progress bars:", style={"fontSize": "12px", "color": SLATE["500"], "marginBottom": "8px"}),
            html.Div([
                html.Div([
                    html.Div(style={"width": "45%", "backgroundColor": ACCENT}),
                ], className="mini-progress", style={"flex": "1"}),
                html.Div([
                    html.Div(style={"width": "72%", "backgroundColor": SUCCESS}),
                ], className="mini-progress", style={"flex": "1"}),
                html.Div([
                    html.Div(style={"width": "95%", "backgroundColor": WARNING}),
                ], className="mini-progress", style={"flex": "1"}),
            ], style={"display": "flex", "gap": "12px"}),
        ]),

        # ── Section: Info Box ──
        html.H2("Info & Alert Boxes", className="section-title"),
        info_box("Tip", html.Ul([
            html.Li("Edit brand.yml to change colours, then refresh this page", style={"fontSize": "13px"}),
            html.Li("All CSS variables update automatically", style={"fontSize": "13px"}),
            html.Li("Gold accent from aspire.qa: #fbb800", style={"fontSize": "13px"}),
        ], style={"margin": "0", "paddingLeft": "20px"})),

        # Warning variant
        html.Div([
            html.Div([
                html.I(className="fa-solid fa-triangle-exclamation", style={"color": WARNING, "marginRight": "8px"}),
                html.Strong("Year Closed", style={"color": "#92400e"}),
            ], style={"display": "flex", "alignItems": "center", "marginBottom": "4px"}),
            html.Div("This budget year is closed. All data is read-only.", style={"fontSize": "13px", "color": "#92400e"}),
        ], style={
            "background": "#fffbeb", "border": "1px solid #fde68a",
            "borderRadius": "8px", "padding": "12px 16px", "marginBottom": "16px",
        }),

        # ── Section: Toggle Group ──
        html.H2("Toggle Group", className="section-title"),
        card([
            html.Div([
                html.Div([
                    html.Div("Range:", className="control-label"),
                    toggle_group("range", [
                        {"label": "7d", "value": "7d"},
                        {"label": "14d", "value": "14d"},
                        {"label": "28d", "value": "28d"},
                        {"label": "All", "value": "all"},
                    ], value="14d"),
                ]),
                html.Div([
                    html.Div("Mode:", className="control-label"),
                    toggle_group("mode", [
                        {"label": "SD Bands", "value": "sd"},
                        {"label": "4pt MA", "value": "ma"},
                        {"label": "Acute", "value": "acute"},
                    ], value="sd"),
                ]),
            ], style={"display": "flex", "gap": "24px"}),
        ]),

        # ── Section: Filter Bar ──
        html.H2("Filter Bar", className="section-title"),
        filter_bar([
            html.Div([
                html.Div("Sport", className="control-label"),
                dcc.Dropdown(
                    options=["Football", "Athletics", "Swimming", "Fencing", "Squash", "Padel"],
                    value="Football",
                    style={"width": "160px"},
                    clearable=False,
                ),
            ]),
            html.Div([
                html.Div("Status", className="control-label"),
                dcc.Dropdown(
                    options=["All", "On Track", "Caution", "Over Budget"],
                    value="All",
                    style={"width": "140px"},
                    clearable=False,
                ),
            ]),
            html.Div([
                html.Div("Quick Filters", className="control-label"),
                html.Div([
                    html.Button("All", className="filter-pill active", style={"marginRight": "4px"}),
                    html.Button("Has Paid", className="filter-pill", style={"marginRight": "4px"}),
                    html.Button("Has Enc.", className="filter-pill"),
                ]),
            ]),
        ]),

        # ── Section: Empty State ──
        html.H2("Empty State", className="section-title"),
        card([empty_state(
            icon="fa-solid fa-magnifying-glass",
            text="No results found",
            hint="Try adjusting your filters or search query",
        )]),

        # ── Section: Athlete Cards ──
        html.H2("Athlete Cards (WHOOP style)", className="section-title"),
        html.Div([
            html.Div([
                html.Div([
                    html.Div("AM", style={
                        "width": "28px", "height": "28px", "borderRadius": "50%",
                        "background": "#22c55e", "color": "white", "fontWeight": "700",
                        "fontSize": "10px", "display": "flex", "alignItems": "center",
                        "justifyContent": "center",
                    }),
                    html.Div("Ahmed Mohamed", style={"fontWeight": "700", "fontSize": "14px", "color": SLATE["800"]}),
                ], style={"display": "flex", "alignItems": "center", "gap": "8px", "marginBottom": "8px"}),
                html.Div([
                    html.Span("Recovery: ", style={"fontSize": "11px", "color": SLATE["400"]}),
                    html.Span("87%", style={"fontSize": "11px", "fontWeight": "700", "color": "#22c55e"}),
                ]),
            ], className="athlete-card card-green", style={"flex": "1"}),

            html.Div([
                html.Div([
                    html.Div("KA", style={
                        "width": "28px", "height": "28px", "borderRadius": "50%",
                        "background": "#eab308", "color": "white", "fontWeight": "700",
                        "fontSize": "10px", "display": "flex", "alignItems": "center",
                        "justifyContent": "center",
                    }),
                    html.Div("Khalid Al-Thani", style={"fontWeight": "700", "fontSize": "14px", "color": SLATE["800"]}),
                ], style={"display": "flex", "alignItems": "center", "gap": "8px", "marginBottom": "8px"}),
                html.Div([
                    html.Span("Recovery: ", style={"fontSize": "11px", "color": SLATE["400"]}),
                    html.Span("52%", style={"fontSize": "11px", "fontWeight": "700", "color": "#eab308"}),
                ]),
            ], className="athlete-card card-yellow", style={"flex": "1"}),

            html.Div([
                html.Div([
                    html.Div("SA", style={
                        "width": "28px", "height": "28px", "borderRadius": "50%",
                        "background": "#ef4444", "color": "white", "fontWeight": "700",
                        "fontSize": "10px", "display": "flex", "alignItems": "center",
                        "justifyContent": "center",
                    }),
                    html.Div("Sara Ali", style={"fontWeight": "700", "fontSize": "14px", "color": SLATE["800"]}),
                ], style={"display": "flex", "alignItems": "center", "gap": "8px", "marginBottom": "8px"}),
                html.Div([
                    html.Span("Recovery: ", style={"fontSize": "11px", "color": SLATE["400"]}),
                    html.Span("28%", style={"fontSize": "11px", "fontWeight": "700", "color": "#ef4444"}),
                ]),
            ], className="athlete-card card-red", style={"flex": "1"}),
        ], style={"display": "flex", "gap": "12px", "marginBottom": "24px"}),

        # ── Section: Toast Demo ──
        html.H2("Toast Notifications", className="section-title"),
        card([
            html.Div([
                dbc.Button("Show Success Toast", id="demo-toast-success-btn", color="success", size="sm", className="me-2"),
                dbc.Button("Show Error Toast", id="demo-toast-error-btn", color="danger", size="sm"),
            ]),
        ]),
        toast("demo-toast"),

        # ── Section: Shadows ──
        html.H2("Shadow Scale", className="section-title"),
        html.Div([
            html.Div([
                html.Div("shadow-sm", style={"fontSize": "12px", "color": SLATE["500"], "marginBottom": "4px"}),
                html.Div(style={
                    "height": "60px", "background": "white", "borderRadius": "12px",
                    "boxShadow": SHADOW_SM,
                }),
            ], style={"flex": "1"}),
            html.Div([
                html.Div("shadow-md", style={"fontSize": "12px", "color": SLATE["500"], "marginBottom": "4px"}),
                html.Div(style={
                    "height": "60px", "background": "white", "borderRadius": "12px",
                    "boxShadow": SHADOW_MD,
                }),
            ], style={"flex": "1"}),
            html.Div([
                html.Div("shadow-lg", style={"fontSize": "12px", "color": SLATE["500"], "marginBottom": "4px"}),
                html.Div(style={
                    "height": "60px", "background": "white", "borderRadius": "12px",
                    "boxShadow": SHADOW_LG,
                }),
            ], style={"flex": "1"}),
        ], style={"display": "flex", "gap": "16px", "marginBottom": "24px"}),

        # ── Section: Skeleton Loader ──
        html.H2("Skeleton Loader", className="section-title"),
        card([
            html.Div(style={"height": "16px", "width": "40%", "marginBottom": "8px"}, className="skeleton"),
            html.Div(style={"height": "12px", "width": "70%", "marginBottom": "8px"}, className="skeleton"),
            html.Div(style={"height": "12px", "width": "55%"}, className="skeleton"),
        ]),

    ], style={"maxWidth": "1200px"})


# Toast callback
@callback(
    Output("demo-toast", "is_open"),
    Output("demo-toast", "header"),
    Output("demo-toast", "children"),
    Output("demo-toast", "icon"),
    Input("demo-toast-success-btn", "n_clicks"),
    Input("demo-toast-error-btn", "n_clicks"),
    prevent_initial_call=True,
)
def show_toast(s, e):
    if ctx.triggered_id == "demo-toast-success-btn":
        return True, "Success", "Record saved successfully", "success"
    return True, "Error", "Something went wrong", "danger"
