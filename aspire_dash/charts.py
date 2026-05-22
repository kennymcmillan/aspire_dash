"""Plotly chart template and helpers — Poppins font, Aspire colour palette.

Default styling tightened per the 2026-05-22 design audit:
 - gridcolor dropped to slate-50 (was slate-100) — almost invisible by
   default, lets the data carry the chart
 - tighter default margins (l=40, r=16, t=8, b=32 — was l=48, t=40)
 - axis labels reduced to 11 px, axis-title font 11 px (was 12)
 - legend defaults to horizontal at y=-0.18 (best for dashboards)
"""

import plotly.graph_objects as go
import plotly.io as pio
from .theme import CHART_COLORS, FONT_DATA, SLATE   # FONT_DATA = Inter (brand rule: tabular/numeric)

__all__ = ["GRAPH_CONFIG", "apply_template"]

# ── Graph config (hide modebar by default) ───────────────────────────────────
GRAPH_CONFIG = {
    "displayModeBar": False,
    "scrollZoom": False,
}

# ── Aspire Plotly template ───────────────────────────────────────────────────
_aspire_template = go.layout.Template()
_aspire_template.layout = go.Layout(
    font=dict(
        family=FONT_DATA,
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
    margin=dict(l=40, r=16, t=8, b=32),
    xaxis=dict(
        showgrid=False,  # vertical gridlines off — visual clutter
        linecolor=SLATE["200"],
        zerolinecolor=SLATE["200"],
        tickfont=dict(size=11, color=SLATE["500"]),
        title_font=dict(size=11, color=SLATE["500"]),
    ),
    yaxis=dict(
        gridcolor=SLATE["50"],   # near-invisible — data carries the chart
        linecolor="rgba(0,0,0,0)",
        zerolinecolor=SLATE["200"],
        tickfont=dict(size=11, color=SLATE["500"]),
        title_font=dict(size=11, color=SLATE["500"]),
    ),
    legend=dict(
        orientation="h", y=-0.18, x=0, yanchor="top",
        font=dict(size=11, color=SLATE["600"]),
        bgcolor="rgba(255,255,255,0)",
        borderwidth=0,
    ),
    hoverlabel=dict(
        bgcolor="white",
        font_size=12,
        font_family=FONT_DATA,
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
