"""Palette Lab — compare colour palette options side by side."""

import dash
from dash import html
from aspire_dash.theme import SLATE

dash.register_page(__name__, path="/palette-lab", title="Palette Lab", name="Palette Lab")

# ── Palette definitions ──────────────────────────────────────────────────────

NAVY = "#004185"
GOLD = "#fbb800"

CURRENT = {
    "name": "Current",
    "desc": "Tailwind defaults — vivid, cool-toned",
    "success": "#22c55e",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "chart": ["#004185", "#22c55e", "#f59e0b", "#ef4444", "#8b5cf6", "#06b6d4", "#f97316", "#ec4899", "#14b8a6", "#6366f1"],
}

OPTION_A = {
    "name": "Option A: Grounded",
    "desc": "All -600 level — richer, more authoritative, distinct from gold",
    "success": "#16a34a",
    "warning": "#d97706",
    "danger": "#dc2626",
    "chart": ["#004185", "#16a34a", "#d97706", "#dc2626", "#7c3aed", "#0891b2", "#ea580c", "#db2777", "#0d9488", "#4f46e5"],
}

OPTION_B = {
    "name": "Option B: Emerald & Rose",
    "desc": "Emerald green (blue-undertone) harmonises with navy. Rose-red warmer than pure red.",
    "success": "#059669",
    "warning": "#d97706",
    "danger": "#e11d48",
    "chart": ["#004185", "#059669", "#d97706", "#e11d48", "#7c3aed", "#0891b2", "#ea580c", "#db2777", "#0d9488", "#4f46e5"],
}

OPTION_C = {
    "name": "Option C: Premium Dark",
    "desc": "Deepest tones — very premium, serious analytics feel. -700 level.",
    "success": "#15803d",
    "warning": "#b45309",
    "danger": "#b91c1c",
    "chart": ["#004185", "#15803d", "#b45309", "#b91c1c", "#6d28d9", "#0e7490", "#c2410c", "#be185d", "#0f766e", "#4338ca"],
}

OPTION_D = {
    "name": "Option D: Warm Harmony",
    "desc": "Warm-shifted greens and reds that complement gold. Teal as secondary accent.",
    "success": "#0d9488",
    "warning": "#ca8a04",
    "danger": "#dc2626",
    "chart": ["#004185", "#0d9488", "#ca8a04", "#dc2626", "#7c3aed", "#0284c7", "#ea580c", "#db2777", "#059669", "#4f46e5"],
}

PALETTES = [CURRENT, OPTION_A, OPTION_B, OPTION_C, OPTION_D]


def _color_block(hex_val, label, width="80px", height="48px"):
    """Swatch with hex label below."""
    return html.Div([
        html.Div(style={
            "width": width, "height": height, "backgroundColor": hex_val,
            "borderRadius": "6px", "border": "1px solid rgba(0,0,0,0.08)",
        }),
        html.Div(hex_val, style={
            "fontSize": "10px", "color": SLATE["500"], "fontFamily": "monospace",
            "textAlign": "center", "marginTop": "3px",
        }),
        html.Div(label, style={
            "fontSize": "10px", "color": SLATE["400"], "textAlign": "center",
        }) if label else None,
    ], style={"display": "flex", "flexDirection": "column", "alignItems": "center"})


def _mini_bar_chart(colors, bar_height="32px"):
    """Horizontal stacked bar showing chart palette."""
    return html.Div([
        html.Div(style={
            "flex": "1", "backgroundColor": c, "height": bar_height,
            "borderRadius": "4px 0 0 4px" if i == 0 else ("0 4px 4px 0" if i == len(colors) - 1 else "0"),
        }) for i, c in enumerate(colors)
    ], style={"display": "flex", "gap": "1px", "borderRadius": "4px", "overflow": "hidden"})


def _status_badges(palette):
    """Row of status badges using palette semantic colours."""
    def _badge(text, bg, fg):
        return html.Span(text, style={
            "padding": "4px 12px", "borderRadius": "9999px",
            "fontSize": "12px", "fontWeight": "600",
            "backgroundColor": bg, "color": fg,
        })
    return html.Div([
        _badge("On Track", palette["success"], "white"),
        _badge("At Risk", palette["warning"], "white"),
        _badge("Over Budget", palette["danger"], "white"),
        _badge("Award", GOLD, "white"),
    ], style={"display": "flex", "gap": "8px", "flexWrap": "wrap"})


def _kpi_cards(palette):
    """Mini KPI cards row using semantic colours."""
    cards = [
        ("Revenue", "QAR 3.2M", palette["success"], "#f0fdf4"),
        ("Expenses", "QAR 2.8M", palette["warning"], "#fffbeb"),
        ("Overdue", "QAR 420K", palette["danger"], "#fef2f2"),
    ]
    children = []
    for label, value, accent, bg in cards:
        children.append(html.Div([
            html.Div(label, style={"fontSize": "11px", "color": SLATE["500"], "marginBottom": "2px"}),
            html.Div(value, style={"fontSize": "18px", "fontWeight": "700", "color": SLATE["800"]}),
            html.Div(style={
                "width": "100%", "height": "3px", "backgroundColor": "#e2e8f0",
                "borderRadius": "2px", "marginTop": "8px",
            }, children=[
                html.Div(style={
                    "width": "65%", "height": "100%", "backgroundColor": accent,
                    "borderRadius": "2px",
                }),
            ]),
        ], style={
            "padding": "12px 16px", "background": bg, "borderRadius": "8px",
            "border": f"1px solid {accent}22", "flex": "1", "minWidth": "140px",
        }))
    return html.Div(children, style={"display": "flex", "gap": "8px", "flexWrap": "wrap"})


def _sport_cards_row(palette):
    """Mini sport cards showing how status colours look in context."""
    sports = [
        ("Football", 87.5, palette["success"]),
        ("Athletics", 76.2, palette["success"]),
        ("Swimming", 97.2, palette["danger"]),
        ("Fencing", 73.3, palette["warning"]),
    ]
    children = []
    for name, pct, color in sports:
        children.append(html.Div([
            html.Div([
                html.Span(name, style={"fontWeight": "600", "fontSize": "12px"}),
                html.Span(f"{pct}%", style={"fontSize": "12px", "fontWeight": "700", "color": color}),
            ], style={"display": "flex", "justifyContent": "space-between", "marginBottom": "6px"}),
            html.Div([
                html.Div(style={
                    "width": f"{min(pct, 100)}%", "backgroundColor": color,
                    "height": "100%", "borderRadius": "3px",
                }),
            ], style={
                "height": "6px", "backgroundColor": "#e2e8f0",
                "borderRadius": "3px", "overflow": "hidden",
            }),
        ], style={
            "padding": "10px 14px", "background": "white",
            "borderRadius": "8px", "border": "1px solid #e2e8f0",
            "flex": "1", "minWidth": "140px",
        }))
    return html.Div(children, style={"display": "flex", "gap": "8px", "flexWrap": "wrap"})


def _navy_context(palette):
    """Show colours against navy background (sidebar context)."""
    return html.Div([
        html.Div([
            html.Div(style={
                "width": "10px", "height": "10px", "borderRadius": "50%",
                "backgroundColor": palette["success"], "display": "inline-block",
            }),
            html.Span(" Active", style={"color": "rgba(255,255,255,0.8)", "fontSize": "12px", "marginLeft": "6px"}),
        ], style={"marginBottom": "6px"}),
        html.Div([
            html.Div(style={
                "width": "10px", "height": "10px", "borderRadius": "50%",
                "backgroundColor": palette["warning"], "display": "inline-block",
            }),
            html.Span(" Pending", style={"color": "rgba(255,255,255,0.8)", "fontSize": "12px", "marginLeft": "6px"}),
        ], style={"marginBottom": "6px"}),
        html.Div([
            html.Div(style={
                "width": "10px", "height": "10px", "borderRadius": "50%",
                "backgroundColor": palette["danger"], "display": "inline-block",
            }),
            html.Span(" Alert", style={"color": "rgba(255,255,255,0.8)", "fontSize": "12px", "marginLeft": "6px"}),
        ], style={"marginBottom": "6px"}),
        html.Div([
            html.Div(style={
                "width": "10px", "height": "10px", "borderRadius": "50%",
                "backgroundColor": GOLD, "display": "inline-block",
            }),
            html.Span(" Gold", style={"color": "rgba(255,255,255,0.8)", "fontSize": "12px", "marginLeft": "6px"}),
        ]),
    ], style={
        "backgroundColor": NAVY, "padding": "16px", "borderRadius": "8px",
        "minWidth": "130px",
    })


def _palette_section(palette):
    """Full comparison section for one palette option."""
    return html.Div([
        # Title
        html.H3(palette["name"], style={
            "fontSize": "16px", "fontWeight": "700", "color": SLATE["800"],
            "marginBottom": "4px",
        }),
        html.P(palette["desc"], style={
            "fontSize": "12px", "color": SLATE["500"], "marginBottom": "16px",
        }),

        # Semantic swatches
        html.Div("Semantic Colours", style={
            "fontSize": "11px", "fontWeight": "600", "color": SLATE["400"],
            "textTransform": "uppercase", "letterSpacing": "0.05em", "marginBottom": "8px",
        }),
        html.Div([
            _color_block(NAVY, "primary"),
            _color_block(palette["success"], "success"),
            _color_block(palette["warning"], "warning"),
            _color_block(palette["danger"], "danger"),
            _color_block(GOLD, "gold"),
            _navy_context(palette),
        ], style={"display": "flex", "gap": "12px", "marginBottom": "16px", "alignItems": "flex-start", "flexWrap": "wrap"}),

        # Status badges
        html.Div("Status Badges", style={
            "fontSize": "11px", "fontWeight": "600", "color": SLATE["400"],
            "textTransform": "uppercase", "letterSpacing": "0.05em", "marginBottom": "8px",
        }),
        _status_badges(palette),

        # KPI cards
        html.Div("KPI Cards", style={
            "fontSize": "11px", "fontWeight": "600", "color": SLATE["400"],
            "textTransform": "uppercase", "letterSpacing": "0.05em",
            "marginBottom": "8px", "marginTop": "16px",
        }),
        _kpi_cards(palette),

        # Sport progress cards
        html.Div("Sport Cards", style={
            "fontSize": "11px", "fontWeight": "600", "color": SLATE["400"],
            "textTransform": "uppercase", "letterSpacing": "0.05em",
            "marginBottom": "8px", "marginTop": "16px",
        }),
        _sport_cards_row(palette),

        # Chart palette bar
        html.Div("Chart Palette (10 colours)", style={
            "fontSize": "11px", "fontWeight": "600", "color": SLATE["400"],
            "textTransform": "uppercase", "letterSpacing": "0.05em",
            "marginBottom": "8px", "marginTop": "16px",
        }),
        _mini_bar_chart(palette["chart"]),
        html.Div([
            _color_block(c, f"chart-{i}", width="60px", height="32px")
            for i, c in enumerate(palette["chart"])
        ], style={"display": "flex", "gap": "6px", "marginTop": "8px", "flexWrap": "wrap"}),

    ], style={
        "padding": "24px", "background": "white",
        "borderRadius": "12px", "border": "1px solid #e2e8f0",
        "boxShadow": "0 1px 3px rgba(0,0,0,0.04)",
    })


def layout(**kwargs):
    return html.Div([
        html.H2("Palette Lab", className="section-title", style={"marginTop": "0"}),
        html.P(
            "Compare palette options side by side. All options keep the Aspire navy blue and gold — "
            "only semantic colours and chart palette vary.",
            style={"fontSize": "13px", "color": SLATE["500"], "marginBottom": "24px"},
        ),

        html.Div([
            _palette_section(p) for p in PALETTES
        ], style={"display": "flex", "flexDirection": "column", "gap": "24px"}),

    ], style={"maxWidth": "1200px"})
