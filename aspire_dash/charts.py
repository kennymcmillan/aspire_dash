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
from .theme import (
    CHART_COLORS, FONT_DATA, SLATE, ASPIRE,
    SEQUENTIAL_BLUE, SEQUENTIAL_GOLD, SEQUENTIAL_RED,
    SEQUENTIAL_GREEN, DIVERGING_RED_GREEN,
)   # FONT_DATA = Inter (brand rule: tabular/numeric)


def _scale(colors):
    """Convert a brand list into Plotly's [(stop, color), ...] form."""
    if not colors:
        return None
    n = len(colors)
    return [[i / (n - 1), c] for i, c in enumerate(colors)]


# Exported colour scales — pass directly to Plotly's
# `color_continuous_scale=` / `colorscale=`. Replaces stock Plotly
# defaults (Reds, Blues, Viridis) with Aspire-anchored equivalents.
ASPIRE_BLUE_SCALE     = _scale(SEQUENTIAL_BLUE)     # magnitude
ASPIRE_GOLD_SCALE     = _scale(SEQUENTIAL_GOLD)     # achievement
ASPIRE_HEAT_SCALE     = _scale(SEQUENTIAL_RED)      # load / risk
ASPIRE_RECOVERY_SCALE = _scale(SEQUENTIAL_GREEN)    # readiness / availability
ASPIRE_VARIANCE_SCALE = _scale(DIVERGING_RED_GREEN) # bad ← neutral → good

__all__ = ["GRAPH_CONFIG", "apply_template",
            "ASPIRE_BLUE_SCALE", "ASPIRE_GOLD_SCALE",
            "ASPIRE_HEAT_SCALE", "ASPIRE_RECOVERY_SCALE",
            "ASPIRE_VARIANCE_SCALE",
            # v0.28 chart-polish helpers
            "add_reference_line", "aspire_area_fill",
            "aspire_bar_gradient", "add_drop_shadow_trace",
            "aspire_hover_template", "progression_vs_typical_bar"]

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
    # v0.28 — premium hover labels (slate-700 bg + white text + branded
    # radius). Replaces stock Plotly white-on-white tooltips. Matches the
    # Linear / Stripe / Whoop tooltip feel.
    hoverlabel=dict(
        bgcolor=SLATE["800"],
        font_size=12,
        font_family=FONT_DATA,
        font_color="white",
        bordercolor=SLATE["900"],
        align="left",
    ),
    # v0.28 — branded modebar (when shown). Default GRAPH_CONFIG hides it,
    # but apps that opt back in get Aspire-blue active icons.
    modebar=dict(
        bgcolor="rgba(255,255,255,0)",
        color=SLATE["400"],
        activecolor=ASPIRE["600"],
    ),
)

# Register as default
pio.templates["aspire"] = _aspire_template
pio.templates.default = "aspire"


def apply_template(fig):
    """Apply the Aspire template to an existing figure."""
    fig.update_layout(template="aspire")
    return fig


# ═════════════════════════════════════════════════════════════════════════════
# v0.28 — Branded chart polish helpers (lift every figure portfolio-wide)
# All Aspire-tokened so every app inherits the same chart vocabulary.
# ═════════════════════════════════════════════════════════════════════════════


def _hex_to_rgba(hex_, alpha):
    h = hex_.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


# ── 1. Reference lines (mean / target / threshold) ──────────────────────────

_REF_STYLES = {
    "mean":      {"color": SLATE["500"], "dash": "dot",     "width": 1.5},
    "target":    {"color": ASPIRE["600"], "dash": "dash",   "width": 1.5},
    "threshold": {"color": "#dc2626",     "dash": "dashdot","width": 1.5},
    "baseline":  {"color": SLATE["400"], "dash": "solid",   "width": 1},
}


def add_reference_line(fig, value, *, kind: str = "mean", label: str | None = None,
                        annotation_position: str = "top right"):
    """Add a horizontal reference line with branded styling.

    `kind` ∈ {'mean', 'target', 'threshold', 'baseline'} — picks the
    colour/dash preset so every chart's reference lines look identical.
    Pass `label` to annotate the line.

    >>> add_reference_line(fig, value=df['load'].mean(), kind='mean', label='Avg')
    >>> add_reference_line(fig, value=14.0, kind='target', label='Target')
    >>> add_reference_line(fig, value=21.0, kind='threshold', label='Risk')
    """
    style = _REF_STYLES.get(kind, _REF_STYLES["mean"])
    annotation = None
    if label:
        annotation = dict(
            text=label,
            font=dict(size=10, color=style["color"], family=FONT_DATA),
            bgcolor="rgba(255,255,255,0.85)", bordercolor=style["color"],
            borderwidth=1, borderpad=3,
        )
    fig.add_hline(
        y=value,
        line=dict(color=style["color"], dash=style["dash"], width=style["width"]),
        annotation=annotation,
        annotation_position=annotation_position,
    )
    return fig


# ── 2. Gradient fills for area / bar charts ─────────────────────────────────
# Matches the .athlete-card-v2 zone-gradient feel — top-tinted → fade

def aspire_area_fill(trace, color: str = None, alpha_top: float = 0.30,
                      alpha_bottom: float = 0.02):
    """Apply an Aspire-branded vertical gradient fill to a Scatter trace.

    Pass `color` as a hex (defaults to Aspire-600). Configures Plotly's
    `fill='tozeroy'` + `fillcolor=<rgba>` for premium area-chart styling.

    >>> fig.add_trace(go.Scatter(x=df.date, y=df.value, mode='lines',
    ...                          line=dict(color=ASPIRE['600'], width=2)))
    >>> aspire_area_fill(fig.data[-1])
    """
    color = color or ASPIRE["600"]
    trace.update(
        fill="tozeroy",
        fillcolor=_hex_to_rgba(color, alpha_top),
    )
    return trace


def aspire_bar_gradient(color: str = None) -> dict:
    """Return a `marker=` dict for bar/waterfall traces with Aspire
    gradient fill + slate-tinted edge.

    >>> fig.add_trace(go.Bar(x=..., y=..., **aspire_bar_gradient()))
    """
    color = color or ASPIRE["600"]
    return dict(
        marker=dict(
            color=color,
            line=dict(color=_hex_to_rgba(color, 0.4), width=0),
        ),
        opacity=0.92,
    )


# ── 3. Drop-shadow trace (slate-tinted depth under main line) ───────────────

def add_drop_shadow_trace(fig, trace_idx: int = 0, *, offset: float = 0.5):
    """Insert a slate-tinted shadow trace UNDER an existing line trace.

    Adds the same line shape, shifted down `offset` (chart Y units), at
    8% slate alpha — subtle depth like Linear charts.

    Note: Plotly's `Figure.data` is immutable-list-shaped (can only
    reorder existing traces, not insert new ones). So we use
    `fig.add_trace()` then re-order via `data` to put shadow first.

    >>> add_drop_shadow_trace(fig, trace_idx=0)
    """
    if trace_idx >= len(fig.data):
        return fig
    src = fig.data[trace_idx]
    if not hasattr(src, "y") or src.y is None:
        return fig
    shadow_y = [(v - offset) if v is not None else None for v in src.y]
    import plotly.graph_objects as _go
    fig.add_trace(_go.Scatter(
        x=src.x, y=shadow_y, mode="lines",
        line=dict(color=_hex_to_rgba(SLATE["800"], 0.08), width=3),
        showlegend=False, hoverinfo="skip",
        name="__shadow__",
    ))
    # Reorder so the shadow draws first (under the source)
    n = len(fig.data)
    order = list(range(n - 1))
    order.insert(trace_idx, n - 1)   # shadow at trace_idx position
    fig.data = tuple(fig.data[i] for i in order)
    return fig


# ── 4. Branded hover template ───────────────────────────────────────────────

def aspire_hover_template(unit: str = "", title_key: str = "x",
                           value_key: str = "y", precision: int = 1) -> str:
    """Return a Plotly hovertemplate string with branded styling.

    Uses HTML so the slate-700 hoverlabel bg renders proper line breaks
    + bold metric name. Pass to `hovertemplate=` on any trace.

    >>> fig.add_trace(go.Scatter(x=..., y=...,
    ...     hovertemplate=aspire_hover_template(unit='ms')))
    """
    return (
        f"<b>%{{{title_key}}}</b><br>"
        f"%{{{value_key}:.{precision}f}}{unit}"
        "<extra></extra>"
    )


def progression_vs_typical_bar(categories, actual, typical, *,
                               actual_name: str = "Actual",
                               typical_name: str = "Typical",
                               unit: str = "", title: str | None = None,
                               x_title: str | None = None,
                               y_title: str | None = None, height: int = 320):
    """Grouped bars per category comparing an athlete's value to a typical/expected
    value, with a bold vertical arrow + signed delta label per category
    (green ▲ when above typical, red ▼ when below). Returns a styled go.Figure.

    Built for "actual vs expected" comparisons (e.g. year-on-year improvement vs
    the population norm by age), but works for any paired-by-category data.

    >>> progression_vs_typical_bar(
    ...     ["15→16", "16→17", "17→18"], actual=[8, 13, 6], typical=[5, 2, 2],
    ...     unit=" cm", actual_name="His improvement", typical_name="Typical for age",
    ...     title="Year-on-year improvement vs typical",
    ...     x_title="Age step (years)", y_title="Improvement (cm)")
    """
    cats = list(categories)
    actual = list(actual)
    typical = list(typical)
    blue = ASPIRE.get("600", "#004185")
    GREEN, RED = "#16a34a", "#dc2626"
    GREEN_BG, RED_BG = "#e7f6ee", "#fdeaec"

    fig = go.Figure()
    fig.add_trace(go.Bar(x=cats, y=typical, name=typical_name, marker_color="#cbd5e1",
                         hovertemplate=f"{typical_name}: %{{y}}{unit}<extra></extra>"))
    fig.add_trace(go.Bar(x=cats, y=actual, name=actual_name, marker_color=blue,
                         hovertemplate=f"{actual_name}: %{{y}}{unit}<extra></extra>"))

    for c, a, t in zip(cats, actual, typical):
        diff = a - t
        col = GREEN if diff >= 0 else RED
        bg = GREEN_BG if diff >= 0 else RED_BG
        if diff != 0:  # bold vertical arrow from typical level to actual level
            fig.add_annotation(x=c, y=a, ax=c, ay=t, xref="x", yref="y",
                               axref="x", ayref="y", showarrow=True, arrowhead=2,
                               arrowsize=1.6, arrowwidth=4, arrowcolor=col)
        fig.add_annotation(
            x=c, y=max(a, t, 0), yshift=20, showarrow=False,
            text=f"<b>{'▲' if diff >= 0 else '▼'} {'+' if diff >= 0 else ''}{diff:g}{unit}</b>",
            font=dict(color=col, size=14), bgcolor=bg, bordercolor=col,
            borderwidth=1.5, borderpad=4)

    layout = dict(barmode="group", height=height,
                  margin=dict(l=50, r=20, t=64 if title else 30, b=44),
                  legend=dict(orientation="h", yanchor="bottom", y=1.02,
                              xanchor="center", x=0.5))
    if title:
        layout["title"] = dict(text=title, font=dict(size=15, color=blue),
                               x=0.5, xanchor="center")
    if x_title:
        layout["xaxis_title"] = x_title
    if y_title:
        layout["yaxis_title"] = y_title
    fig.update_layout(**layout)
    apply_template(fig)
    vals = actual + typical + [0]
    fig.update_yaxes(range=[min(vals) - 2, max(vals) + 13])  # headroom for labels
    return fig
