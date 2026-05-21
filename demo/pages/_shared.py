"""Tiny helpers shared by the demo pages."""
from dash import html


def section(title: str, description: str = ""):
    """Section heading with optional description."""
    children = [html.H2(title, style={"fontSize": "20px", "fontWeight": 700,
                                       "color": "#0f172a",
                                       "margin": "24px 0 4px 0"})]
    if description:
        children.append(html.P(description,
                                style={"fontSize": "13px", "color": "#64748b",
                                       "margin": "0 0 12px 0"}))
    return html.Div(children)


def code_block(code: str):
    """Aspire-styled <pre> for code samples."""
    return html.Pre(
        code.strip(),
        style={"background": "#0f172a", "color": "#e2e8f0",
                "padding": "12px 14px", "borderRadius": "6px",
                "fontSize": "11.5px", "fontFamily": "Fira Code, monospace",
                "overflowX": "auto", "margin": "8px 0 18px 0",
                "lineHeight": "1.55"},
    )


def example(label: str, preview, code: str):
    """Sub-example block — small label + live preview + code snippet."""
    return html.Div([
        html.Div(label, style={"fontSize": "11px", "fontWeight": 600,
                                 "color": "#475569",
                                 "textTransform": "uppercase",
                                 "letterSpacing": "0.05em",
                                 "marginBottom": "6px"}),
        html.Div(preview,
                  style={"padding": "16px", "border": "1px solid #e2e8f0",
                         "borderRadius": "6px", "background": "white",
                         "marginBottom": "8px"}),
        code_block(code),
    ], style={"marginBottom": "18px"})
