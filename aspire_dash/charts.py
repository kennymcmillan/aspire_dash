"""Plotly chart template and helpers — Poppins font, Aspire colour palette.

Default styling tightened per the 2026-05-22 design audit:
 - gridcolor dropped to slate-50 (was slate-100) — almost invisible by
   default, lets the data carry the chart
 - tighter default margins (l=40, r=16, t=8, b=32 — was l=48, t=40)
 - axis labels reduced to 11 px, axis-title font 11 px (was 12)
 - legend defaults to horizontal at y=-0.18 (best for dashboards)
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from .theme import (
    CHART_COLORS, FONT_DATA, SLATE, ASPIRE, GOLD, SUCCESS, DANGER,
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
            "aspire_hover_template",
            # v0.90 test-history column chart (promoted from endurance-dashboard)
            "history_figure"]

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


# ═════════════════════════════════════════════════════════════════════════════
# v0.90 - Test-history column chart (promoted from endurance-dashboard)
# One bar per test date: navy bars, gold-ringed best test, a value chip boxed at
# each bar top, a dashed mean rule, and ggrepel-style right-margin mean/benchmark
# labels that fan out (with leader lines) when they would collide. All colours
# read from the Aspire palette tokens rather than re-hardcoded hexes.
# ═════════════════════════════════════════════════════════════════════════════

# Palette - Aspire tokens. VALUE_BOX (lighter navy chip) and REFLINE (target
# amber, the app --target token) have no exact palette token, so they stay named
# literals; everything else maps to a theme token.
_HIST_BAR_LATEST = ASPIRE["600"]                 # aspire-600 - the latest test
_HIST_BAR_MUTED = _hex_to_rgba(ASPIRE["600"], 0.24)  # navy at low opacity - prior tests
_HIST_BEST_OUTLINE = GOLD                        # Aspire gold ring on the best test
_HIST_MEAN_LINE = SLATE["500"]                   # slate-500 - the dashed mean rule
_HIST_VALUE_BOX = "#0a5ba8"                      # lighter navy chip behind each value
_HIST_MEAN_LABEL = SLATE["600"]                  # slate-600 - readable mean label
_HIST_REFLINE = "#92400e"                        # target amber - benchmark rules
_HIST_AXIS = SLATE["700"]                        # slate-700 - axis + label text
_HIST_MUTED_TXT = SLATE["500"]                   # slate-500 - secondary notes


def _num_fmt(v, unit=""):
    """Compact number: 3dp for seconds, 0dp for magnitudes >=100, else 1dp."""
    if v is None or pd.isna(v):
        return "--"
    if unit == "s":
        return f"{v:.3f}"
    if abs(v) >= 100:
        return f"{v:.0f}"
    return f"{v:.1f}"


def _hist_fmt_delta(delta, unit="", prev=None, dp=2):
    """A 'vs last test' delta so absolute-vs-percentage is never ambiguous:
    a metric WITH a unit shows the absolute change in that unit ('+1.70 cm'); a
    unitless metric shows the percentage change vs the prior value ('+3.4%')."""
    if delta is None or (isinstance(delta, float) and pd.isna(delta)):
        return ""
    if unit:
        return f"{delta:+.{dp}f} {unit}".strip()
    if prev not in (None, 0) and not (isinstance(prev, float) and pd.isna(prev)) \
            and abs(prev) > 1e-9:
        return f"{delta / abs(prev) * 100:+.1f}%"
    return f"{delta:+.{dp}f}"


def _repel_1d(values, lo, hi, gap):
    """ggrepel-style 1D spread: given `values` sorted ascending, return positions at
    least `gap` apart and kept within [lo, hi]. Push-up pass, then a pull-down pass
    if the top overflows, so a cluster of near-equal marks fans out instead of
    stacking. Used to de-collide the right-margin mean / benchmark labels."""
    disp = list(values)
    for i in range(1, len(disp)):
        if disp[i] - disp[i - 1] < gap:
            disp[i] = disp[i - 1] + gap
    if disp and disp[-1] > hi:
        disp[-1] = hi
        for i in range(len(disp) - 2, -1, -1):
            if disp[i + 1] - disp[i] < gap:
                disp[i] = disp[i + 1] - gap
    return disp


def history_figure(series, unit=None, title=None, *, lower_is_better=False,
                   benchmarks=None, last_n=12, height=360, width=560):
    """Column history chart from `series` = [(date, value), ...] oldest->newest.

    The latest bar is highlighted (aspire-600), the best test is gold-ringed, each
    bar carries a value chip boxed at its top, and a dashed mean rule is drawn. The
    mean + benchmark labels sit in the RIGHT margin, de-collided ggrepel-style with
    thin leader lines back to each rule's true height.

    Parameters
    ----------
    series : list[tuple]
        ``[(date, value), ...]`` oldest -> newest. Values that are ``None``/NaN are
        dropped; dates are parsed with pandas.
    unit : str or None
        Value unit ('cm', 's', ...). Drives number formatting and axis title.
    title : str or None
        Chart + axis title.
    lower_is_better : bool
        When True the *smallest* value is the best test (e.g. a sprint time).
    benchmarks : list[tuple] or None
        ``[(label, value), ...]`` drawn as dotted reference lines. A value of
        ``None`` renders a small 'benchmark pending' note so the slot stays visible.
    last_n : int
        Keep only the most recent ``last_n`` tests (default 12).
    height, width : int or None
        Figure size. Pass ``width=None`` for a responsive full-width chart.
    """
    unit = unit or ""
    series = [(d, v) for d, v in (series or []) if v is not None and not pd.isna(v)]
    series = series[-last_n:]
    if not series:
        fig = go.Figure()
        fig.update_layout(height=height, width=width, template="aspire",
                          annotations=[dict(text="No test history", showarrow=False,
                                            xref="paper", yref="paper", x=0.5, y=0.5,
                                            font=dict(size=15, color=_HIST_MUTED_TXT))])
        return fig

    dates = [pd.to_datetime(d).strftime("%d-%b-%Y") for d, _ in series]
    vals = [float(v) for _, v in series]
    n = len(vals)
    best_idx = (vals.index(min(vals)) if lower_is_better else vals.index(max(vals)))

    colors = [_HIST_BAR_MUTED] * n
    colors[-1] = _HIST_BAR_LATEST
    line_colors = ["rgba(0,0,0,0)"] * n
    line_widths = [0] * n
    line_colors[best_idx] = _HIST_BEST_OUTLINE
    line_widths[best_idx] = 2.5

    fig = go.Figure()
    fig.add_bar(x=dates, y=vals, marker_color=colors,
                marker_line_color=line_colors, marker_line_width=line_widths,
                cliponaxis=False,
                hovertemplate="%{x}<br>" + (title or "value") + ": %{y}<extra></extra>")
    # Value chips: each test's number in a small navy box with white text, sat at the
    # TOP of its own bar (boxing it inside the bar top de-collides it from the mean rule).
    for d, v in zip(dates, vals):
        fig.add_annotation(x=d, y=v, text=_num_fmt(v, unit), showarrow=False,
                           yanchor="top", yshift=-3, font=dict(size=11, color="white"),
                           bgcolor=_HIST_VALUE_BOX, borderpad=2)
    # Mean rule (thicker dashed). Its LABEL is drawn later, with the benchmark labels,
    # in the RIGHT margin where a ggrepel-style pass spreads any that would overlap.
    mean_v = sum(vals) / n
    fig.add_hline(y=mean_v, line_width=2, line_dash="dash", line_color=_HIST_MEAN_LINE)
    # latest-vs-previous delta annotation
    if n >= 2:
        dlt = vals[-1] - vals[-2]
        good = (dlt < 0) if lower_is_better else (dlt > 0)
        col = SUCCESS if (good and abs(dlt) > 1e-9) else (DANGER if abs(dlt) > 1e-9 else _HIST_MUTED_TXT)
        fig.add_annotation(x=dates[-1], y=vals[-1], yshift=30, showarrow=False,
                           text=f"{_hist_fmt_delta(dlt, unit, vals[-2])} vs last",
                           font=dict(size=13, color=col))

    pending = []
    drawn_benchmarks = []
    for name, val in (benchmarks or []):
        if val is None:
            pending.append(name)
            continue
        fig.add_hline(y=val, line_width=2, line_dash="dot", line_color=_HIST_REFLINE)
        drawn_benchmarks.append((val, f"{val:g} {name}"))
    if pending:
        fig.add_annotation(xref="paper", yref="paper", x=0.02, y=0.02,
                           xanchor="left", yanchor="bottom", showarrow=False, align="left",
                           text="benchmark pending: " + ", ".join(pending),
                           font=dict(size=11, color=_HIST_MUTED_TXT))

    # 15% headroom above/below so bars, labels and benchmark lines never hug the
    # frame. Range spans the bars AND any drawn benchmark lines.
    pts = list(vals) + [v for _, v in (benchmarks or []) if v is not None]
    lo, hi = min(pts), max(pts)
    span = (hi - lo) or abs(hi) or 1.0
    # extra top headroom so the outside value labels + the delta chip clear the frame
    yrange = [min(0, lo - 0.10 * span), hi + 0.24 * span]

    # Right-margin labels for the mean + benchmark rules, de-collided ggrepel-style:
    # spread any that sit too close and draw a thin leader line from the label back to
    # its true line height, so no two labels overlap.
    ymarks = [(mean_v, f"mean {_num_fmt(mean_v, unit)}", _HIST_MEAN_LABEL)]
    ymarks += [(v, txt, _HIST_REFLINE) for v, txt in drawn_benchmarks]
    ymarks.sort(key=lambda m: m[0])
    disp = _repel_1d([m[0] for m in ymarks], yrange[0] + 0.03 * span,
                     yrange[1] - 0.03 * span, 0.11 * span)
    for (true_y, txt, colr), dy in zip(ymarks, disp):
        if abs(dy - true_y) > 1e-9:
            fig.add_shape(type="line", xref="paper", yref="y", x0=1.0, y0=true_y,
                          x1=1.035, y1=dy, line=dict(color=colr, width=1))
        fig.add_annotation(xref="paper", x=1.045, xanchor="left", yref="y", y=dy,
                           yanchor="middle", showarrow=False, text=txt,
                           font=dict(size=11, color=colr))

    ytitle = f"{title} ({unit})" if (title and unit) else (title or unit or None)
    fig.update_layout(
        template="aspire", height=height, width=width,
        margin=dict(l=60, r=120, t=44, b=70), bargap=0.30, showlegend=False,
        title=dict(text=title or "", font=dict(size=15, color=_HIST_AXIS), x=0.02, xanchor="left"),
        xaxis=dict(title=None, type="category", tickfont=dict(size=12, color=_HIST_AXIS),
                   tickangle=-45, showgrid=False, linecolor="#cbd5e1", ticks="outside",
                   tickcolor="#cbd5e1"),
        # gridlines sit BELOW the bars/labels and stay faint, so no text is occluded
        yaxis=dict(title=dict(text=ytitle, font=dict(size=13, color=_HIST_AXIS)),
                   tickfont=dict(size=12, color=_HIST_AXIS), gridcolor="rgba(148,163,184,0.22)",
                   gridwidth=1, layer="below traces", zeroline=False, range=yrange))
    return fig
