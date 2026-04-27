"""Plotly chart template and helpers — Inter font, Aspire colour palette."""

import plotly.graph_objects as go
import plotly.io as pio
from .theme import CHART_COLORS, FONT_FAMILY, SLATE

# ── Graph config (hide modebar by default) ───────────────────────────────────
GRAPH_CONFIG = {
    "displayModeBar": False,
    "scrollZoom": False,
}

# ── Aspire Plotly template ───────────────────────────────────────────────────
_aspire_template = go.layout.Template()
_aspire_template.layout = go.Layout(
    font=dict(
        family=FONT_FAMILY,
        size=13,
        color=SLATE["700"],
    ),
    title=dict(
        font=dict(size=16, color=SLATE["800"]),
        x=0,
        xanchor="left",
    ),
    paper_bgcolor="white",
    plot_bgcolor="white",
    colorway=CHART_COLORS,
    margin=dict(l=48, r=24, t=40, b=40),
    xaxis=dict(
        gridcolor=SLATE["100"],
        linecolor=SLATE["200"],
        zerolinecolor=SLATE["200"],
        tickfont=dict(size=11, color=SLATE["500"]),
        title_font=dict(size=12, color=SLATE["500"]),
    ),
    yaxis=dict(
        gridcolor=SLATE["100"],
        linecolor=SLATE["200"],
        zerolinecolor=SLATE["200"],
        tickfont=dict(size=11, color=SLATE["500"]),
        title_font=dict(size=12, color=SLATE["500"]),
    ),
    legend=dict(
        font=dict(size=12, color=SLATE["600"]),
        bgcolor="rgba(255,255,255,0)",
        borderwidth=0,
    ),
    hoverlabel=dict(
        bgcolor="white",
        font_size=12,
        font_family=FONT_FAMILY,
        bordercolor=SLATE["200"],
    ),
)

# Register as default
pio.templates["aspire"] = _aspire_template
pio.templates.default = "aspire"


def apply_template(fig):
    """Apply the Aspire template to an existing figure."""
    fig.update_layout(template="aspire")
    return fig
