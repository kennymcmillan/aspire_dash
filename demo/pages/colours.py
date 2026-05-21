"""Colour Palette — visual reference of all brand tokens."""

import dash
from dash import html
from aspire_dash.theme import ASPIRE, SLATE, CHART_COLORS, GOLD, SUCCESS, WARNING, DANGER, INFO, SECONDARY

dash.register_page(__name__, path="/colours", title="Colour Palette", name="Colour Palette")


def _swatch(name, hex_val, text_color="white"):
    return html.Div([
        html.Div(style={
            "width": "100%", "height": "56px", "backgroundColor": hex_val,
            "borderRadius": "8px 8px 0 0",
        }),
        html.Div([
            html.Div(name, style={"fontWeight": "600", "fontSize": "12px", "color": "#1e293b"}),
            html.Div(hex_val, style={"fontSize": "11px", "color": "#64748b", "fontFamily": "monospace"}),
        ], style={"padding": "8px 10px", "background": "white", "borderRadius": "0 0 8px 8px",
                   "border": "1px solid #e2e8f0", "borderTop": "none"}),
    ], style={"minWidth": "100px"})


def layout(**kwargs):
    return html.Div([
        html.H2("Aspire Blue Scale", className="section-title", style={"marginTop": "0"}),
        html.P("Primary brand colours derived from aspire.qa (#004185).",
               style={"fontSize": "13px", "color": "#64748b", "marginBottom": "12px"}),
        html.Div([
            _swatch(f"aspire-{k}", v) for k, v in sorted(ASPIRE.items(), key=lambda x: -int(x[0]))
        ], style={"display": "flex", "gap": "8px", "flexWrap": "wrap", "marginBottom": "32px"}),

        html.H2("Slate (Neutrals)", className="section-title"),
        html.Div([
            _swatch(f"slate-{k}", v) for k, v in sorted(SLATE.items(), key=lambda x: -int(x[0]))
        ], style={"display": "flex", "gap": "8px", "flexWrap": "wrap", "marginBottom": "32px"}),

        html.H2("Semantic Colours", className="section-title"),
        html.Div([
            _swatch("success", SUCCESS),
            _swatch("warning", WARNING),
            _swatch("danger", DANGER),
            _swatch("info", INFO),
            _swatch("secondary", SECONDARY),
            _swatch("gold", GOLD),
        ], style={"display": "flex", "gap": "8px", "flexWrap": "wrap", "marginBottom": "32px"}),

        html.H2("Chart Palette (10 colours)", className="section-title"),
        html.P("Colourblind-friendly order. Aspire blue first.",
               style={"fontSize": "13px", "color": "#64748b", "marginBottom": "12px"}),
        html.Div([
            _swatch(f"chart-{i}", c) for i, c in enumerate(CHART_COLORS)
        ], style={"display": "flex", "gap": "8px", "flexWrap": "wrap", "marginBottom": "32px"}),

        # CSS variable quick reference
        html.H2("CSS Variable Quick Reference", className="section-title"),
        html.Div([
            html.Table([
                html.Thead(html.Tr([
                    html.Th("Variable", style={"textAlign": "left", "padding": "8px 12px"}),
                    html.Th("Value", style={"textAlign": "left", "padding": "8px 12px"}),
                    html.Th("Preview", style={"textAlign": "left", "padding": "8px 12px"}),
                ])),
                html.Tbody([
                    _var_row("--aspire-600", "#004185"),
                    _var_row("--aspire-900", "#001d3d"),
                    _var_row("--aspire-secondary", "#1876ab"),
                    _var_row("--gold", "#fbb800"),
                    _var_row("--slate-100", "#f1f5f9"),
                    _var_row("--slate-800", "#1e293b"),
                    _var_row("--radius-sm", "6px"),
                    _var_row("--radius-md", "8px"),
                    _var_row("--radius-lg", "12px"),
                ]),
            ], className="table", style={
                "width": "100%", "background": "white", "borderRadius": "8px",
                "overflow": "hidden", "fontSize": "13px",
            }),
        ], style={"marginBottom": "24px"}),

    ], style={"maxWidth": "1200px"})


def _var_row(name, value):
    is_color = value.startswith("#")
    return html.Tr([
        html.Td(html.Code(name), style={"padding": "8px 12px", "fontFamily": "monospace", "fontSize": "12px"}),
        html.Td(value, style={"padding": "8px 12px", "fontFamily": "monospace", "fontSize": "12px"}),
        html.Td(
            html.Div(style={
                "width": "24px", "height": "24px", "borderRadius": "4px",
                "backgroundColor": value, "border": "1px solid #e2e8f0",
            }) if is_color else "",
            style={"padding": "8px 12px"},
        ),
    ])
