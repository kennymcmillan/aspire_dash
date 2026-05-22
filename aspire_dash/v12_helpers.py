"""aspire_dash v0.12.0 — new helpers ported from the Forge prototypes.

Lives in a single module for the v0.12.0 release so the additions are
easy to audit. In a future minor we may split these out into their
existing topic modules (kpi.py, inputs.py, athlete.py, etc.).

All helpers are PURE additions — no existing API changes. Consumer
apps opt in by importing from `aspire_dash.v12_helpers`.

Public API:
    kpi_tile_v2      — KPI tile with delta arrow + accent stripe colour
    date_toolbar     — unified [◀ date ▶ Today] toolbar
    status_pill_v2   — pill with leading icon + tone palette
    athlete_card     — Whoop-style card (photo + name + score + sub-metrics)
    aspire_grid_v2   — AG Grid with .ag-theme-aspire branded header
    aspire_loading   — full-page loading panel with branded spinner
    aspire_empty     — branded empty state (Aspire-tinted icon)
    sparkline_tile   — KPI value + inline mini-line-chart
    injury_card      — medical-domain card with severity colour stripe
    asymmetry_bar    — VALD-style left/right asymmetry bar
"""
from __future__ import annotations

from dash import html, dcc


# ── 1. KPI tile with delta ──────────────────────────────────────────────────

def kpi_tile_v2(
    label: str,
    value,
    sub: str | None = None,
    *,
    delta: str | None = None,
    delta_direction: str = "flat",   # 'up' | 'down' | 'flat'
    accent: str = "aspire",          # aspire | secondary | gold | success | warning | danger
):
    """KPI tile with optional delta arrow + Whoop-quality typography.

    >>> kpi_tile_v2("Sessions", 423, delta="+12", delta_direction="up",
    ...             sub="vs last month", accent="aspire")
    """
    arrow = {"up": "▲", "down": "▼", "flat": "·"}.get(delta_direction, "·")
    children = [
        html.Div(label, className="kpi-label"),
        html.Div(str(value), className="kpi-value"),
    ]
    if delta is not None or sub is not None:
        delta_children = []
        if delta is not None:
            delta_children.append(
                html.Span(f"{arrow} {delta}",
                           className=f"kpi-delta-{delta_direction}")
            )
        if sub is not None:
            delta_children.append(html.Span(sub))
        children.append(html.Div(delta_children, className="kpi-delta"))
    return html.Div(children, className=f"kpi-tile accent-{accent}")


# ── 2. Date picker toolbar ──────────────────────────────────────────────────

def date_toolbar(
    *,
    prev_id: str,
    next_id: str,
    today_id: str,
    display_text: str,
    display_id: str | None = None,
):
    """Unified date toolbar — [◀] [date] [▶] [TODAY] in one branded control.

    Wire callbacks separately:
        @callback(Output("focus-date", "data"), Input(prev_id, "n_clicks"), ...)

    >>> date_toolbar(
    ...     prev_id="prev", next_id="next", today_id="today",
    ...     display_text="22 May 2026", display_id="date-display",
    ... )
    """
    display_kwargs = {"id": display_id} if display_id else {}
    return html.Div([
        html.Button(html.I(className="fa-solid fa-chevron-left"),
                    id=prev_id, n_clicks=0, className="dt-btn",
                    **{"aria-label": "Previous day"}),
        html.Div([
            html.I(className="fa-solid fa-calendar",
                   style={"color": "var(--aspire-600)", "fontSize": "12px"}),
            html.Span(display_text, **display_kwargs),
        ], className="dt-display"),
        html.Button(html.I(className="fa-solid fa-chevron-right"),
                    id=next_id, n_clicks=0, className="dt-btn",
                    **{"aria-label": "Next day"}),
        html.Button("TODAY", id=today_id, n_clicks=0, className="dt-btn dt-today"),
    ], className="date-toolbar")


# ── 3. Status pill with icon ────────────────────────────────────────────────

_TONE_ICON = {
    "success": "fa-circle-check",
    "warning": "fa-circle-exclamation",
    "danger":  "fa-circle-xmark",
    "info":    "fa-circle-info",
    "neutral": "fa-circle",
}


def status_pill_v2(
    label: str,
    *,
    tone: str = "neutral",       # success | warning | danger | info | neutral
    icon: str | None = None,     # auto-picked from tone if not given
    solid: bool = False,
):
    """Status pill with leading icon. Auto-icons based on tone.

    >>> status_pill_v2("Saved", tone="success")
    >>> status_pill_v2("Failed", tone="danger", solid=True)
    """
    icon_class = icon or _TONE_ICON.get(tone, "fa-circle")
    classes = ["status-pill", f"status-{tone}"]
    if solid:
        classes.append("is-solid")
    return html.Span([
        html.I(className=f"fa-solid {icon_class}"),
        html.Span(label),
    ], className=" ".join(classes))


# ── 4. Athlete card (Whoop-style) ───────────────────────────────────────────

def athlete_card(
    name: str,
    *,
    photo_url: str | None = None,
    meta: str = "",          # e.g. "SENIOR · Fencing"
    score: int | float | None = None,
    score_label: str | None = None,
    tone: str = "aspire",    # good | warn | danger | aspire
    sub_metrics: list[dict] | None = None,   # [{label, value}, ...]
    href: str | None = None,
):
    """Compact Whoop/Firstbeat-style card with photo + name + score +
    inline sub-metrics.

    >>> athlete_card(
    ...     "Ali Turki Owaida",
    ...     meta="SENIOR · Fencing",
    ...     score=68, tone="good",
    ...     sub_metrics=[
    ...         {"label": "Strain", "value": "15.8"},
    ...         {"label": "HRV",    "value": "52ms"},
    ...         {"label": "Sleep",  "value": "7h 12"},
    ...     ],
    ... )
    """
    # Avatar — photo or initials
    initials = "".join(p[0] for p in name.split()[:2]).upper()
    if photo_url:
        avatar = html.Img(src=photo_url, alt=name, style={
            "width": "40px", "height": "40px", "borderRadius": "50%",
            "objectFit": "cover", "border": "2px solid var(--slate-200)",
            "background": "var(--slate-100)",
        })
    else:
        avatar = html.Div(initials, style={
            "width": "40px", "height": "40px", "borderRadius": "50%",
            "background": "var(--aspire-600)", "color": "white",
            "display": "inline-flex", "alignItems": "center",
            "justifyContent": "center",
            "fontWeight": 700, "fontSize": "13px",
        })

    children = [
        html.Div([
            avatar,
            html.Div([
                html.Div(name, className="amc-name"),
                html.Div(meta, className="amc-meta") if meta else None,
            ], style={"minWidth": "0", "flex": "1"}),
            html.Div(str(score) if score is not None else "—",
                      className="amc-score") if score is not None else None,
        ], className="amc-header"),
    ]
    if sub_metrics:
        children.append(html.Div([
            html.Div([
                html.Div(m["label"], className="amc-metric-label"),
                html.Div(str(m.get("value", "—")), className="amc-metric-value"),
            ], className="amc-metric") for m in sub_metrics
        ], className="amc-metrics"))

    card = html.Div(children, className=f"athlete-mini-card tone-{tone}")
    if href:
        return html.A(card, href=href,
                       style={"textDecoration": "none", "color": "inherit"})
    return card


# ── 5. AG Grid Aspire theme ─────────────────────────────────────────────────

def aspire_grid_v2(grid_id, columnDefs, rowData, *, height="400px",
                    editable=False, **kwargs):
    """AG Grid pre-wrapped with the .ag-theme-aspire CSS overrides
    (uppercase aspire-blue header, slate borders, aspire-50 hover).
    """
    import dash_ag_grid as dag
    default_col = {"resizable": True, "sortable": True, "filter": True}
    if editable:
        default_col["editable"] = True
    options = {
        "rowHeight": 32,
        "headerHeight": 38,
        "suppressMovableColumns": True,
        "animateRows": False,
    }
    if editable:
        options["stopEditingWhenCellsLoseFocus"] = True
        options["enterNavigatesVertically"] = True
        options["enterNavigatesVerticallyAfterEdit"] = True
        options["undoRedoCellEditing"] = True
    return dag.AgGrid(
        id=grid_id,
        columnDefs=columnDefs,
        rowData=rowData,
        defaultColDef=default_col,
        dashGridOptions=options,
        className="ag-theme-quartz aspire-themed",
        style={"height": height, "width": "100%"},
        **kwargs,
    )


# ── 6. Aspire loading overlay ───────────────────────────────────────────────

def aspire_loading(text="Loading…", sub=None):
    """Branded full-area loading state with the Aspire-blue spinner."""
    children = [
        html.Div(className="aspire-loading-spinner"),
        html.Div(text, className="aspire-loading-text"),
    ]
    if sub:
        children.append(html.Div(sub, className="aspire-loading-sub"))
    return html.Div(children, className="aspire-loading")


# ── 7. Aspire empty state ───────────────────────────────────────────────────

def aspire_empty(text, hint=None, *, icon="fa-inbox"):
    """Branded empty state — Aspire-blue tinted icon, friendly copy."""
    children = [
        html.Div(html.I(className=f"fa-solid {icon}"), className="aspire-empty-icon"),
        html.Div(text, className="aspire-empty-text"),
    ]
    if hint:
        children.append(html.Div(hint, className="aspire-empty-hint"))
    return html.Div(children, className="aspire-empty")


# ── 8. Sparkline tile ───────────────────────────────────────────────────────

def sparkline_tile(
    label: str,
    value,
    series: list[float],
    *,
    delta: str | None = None,
    delta_direction: str = "flat",   # up | down | flat
    color: str | None = None,
):
    """KPI tile with an inline sparkline. `series` is a list of recent
    values (last 7-14 typical). Renders via Plotly mini-chart."""
    import plotly.graph_objects as go
    color = color or "#004185"
    # Convert hex to rgba for the fill — Plotly doesn't accept 8-char hex
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    fill_rgba = f"rgba({r},{g},{b},0.12)"
    fig = go.Figure(go.Scatter(
        y=series,
        mode="lines",
        line=dict(color=color, width=2),
        fill="tozeroy",
        fillcolor=fill_rgba,
        hoverinfo="skip",
    ))
    fig.update_layout(
        height=36, margin=dict(t=0, b=0, l=0, r=0),
        showlegend=False, paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False), yaxis=dict(visible=False),
    )
    delta_color = {"up": "#16a34a", "down": "#dc2626"}.get(delta_direction, "var(--slate-400)")
    delta_arrow = {"up": "▲", "down": "▼", "flat": "·"}.get(delta_direction, "·")

    text_block = [
        html.Div(label, className="spk-label"),
        html.Div(str(value), className="spk-value"),
    ]
    if delta is not None:
        text_block.append(
            html.Div(f"{delta_arrow} {delta}", className="spk-delta",
                      style={"color": delta_color})
        )
    return html.Div([
        html.Div(text_block, className="spk-text"),
        html.Div(dcc.Graph(figure=fig,
                            config={"displayModeBar": False, "staticPlot": True},
                            style={"height": "36px"}),
                  className="spk-chart"),
    ], className="sparkline-tile")


# ── 9. Injury card ──────────────────────────────────────────────────────────

def injury_card(
    body_part: str,
    *,
    severity: str = "moderate",   # mild | moderate | severe | resolved
    status: str = "Ongoing",
    detail: str = "",
    onset_date: str | None = None,
    days_out: int | None = None,
):
    """Medical-domain injury card. Severity-coloured left stripe."""
    meta = []
    if onset_date:
        meta.append(html.Span(f"Onset: {onset_date}"))
    if days_out is not None:
        meta.append(html.Span(f"{days_out} days out"))
    return html.Div([
        html.Div([
            html.Span(body_part, className="inj-body-part"),
            html.Span(status, className="inj-status"),
        ], className="inj-header"),
        html.Div(detail, className="inj-detail") if detail else None,
        html.Div(meta, className="inj-meta") if meta else None,
    ], className=f"injury-card severity-{severity}")


# ── 11. Metric ring (Whoop-style SVG donut) ────────────────────────────────

# v0.30 — sourced from theme.SEMANTIC_PALETTE + theme constants instead
# of hardcoded hex. One brand-swap touches every ring tone everywhere.
from .theme import SEMANTIC_PALETTE as _SEM, ASPIRE as _A

_TONE_COLOURS = {
    # (stroke for the SVG arc, text colour for the value label inside)
    "good":      ("#16a34a", _SEM["success"]["text"]),
    "warn":      ("#d97706", _SEM["warning"]["text"]),
    "danger":    ("#dc2626", _SEM["danger"]["text"]),
    "aspire":    (_A["600"], _A["700"]),
    "secondary": ("#1876ab", _SEM["info"]["text"]),
    "gold":      ("#fbb800", _SEM["gold"]["text"]),
}


def metric_ring(
    value,
    pct: float,
    *,
    label: str = "",
    tone: str = "aspire",
    color: str | None = None,    # v0.30.1 — overrides tone when given
    size: int = 80,
    unit: str = "",
):
    """SVG ring with value in the centre + percent arc on the ring.

    Whoop-style. Pass the displayed `value` (any string) + the arc `pct`
    (0-100) separately — they don't have to match (e.g. value="7h12"
    while pct=72 if 7h12 of 10h goal).

    `color` (v0.30.1+): pass an explicit hex (e.g. ``"#16a34a"``) to
    override the tone preset. Used by `athlete_card_v2` to honour
    per-ring colours (recovery green/amber/red varies by score, can't
    be expressed as a single tone).

    >>> metric_ring(68, pct=68, label="Recovery", tone="good")
    >>> metric_ring(82, pct=82, label="Recovery", color="#16a34a")  # explicit
    """
    import math
    import uuid
    if color:
        stroke = color
        # derive a darker text colour from the stroke (just darken slightly)
        text_color = color
    else:
        stroke, text_color = _TONE_COLOURS.get(tone, _TONE_COLOURS["aspire"])

    # v0.30.1 — light → mid → dark gradient stroke (was flat colour).
    # Derive a darker stop by reducing each RGB channel by ~25%.
    def _darken(hex_, factor=0.75):
        h = hex_.lstrip("#")
        if len(h) == 3: h = "".join(c*2 for c in h)
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return f"#{int(r*factor):02x}{int(g*factor):02x}{int(b*factor):02x}"

    grad_id = f"g{uuid.uuid4().hex[:8]}"
    stroke_dark = _darken(stroke, 0.70)
    pct = max(0, min(100, pct or 0))
    sw = 6 if size <= 80 else 8
    r = (size - sw) / 2
    circ = 2 * math.pi * r
    dash_offset = circ - (pct / 100) * circ
    cx = size / 2

    fs_value = "22px" if size >= 100 else "16px" if size >= 70 else "12px"
    fs_label = "10px"

    # v0.30.1 — gradient stroke (was flat) via inline <linearGradient>.
    # Light tint at the top of the arc → richer colour at the end.
    svg_inner = (
        f'<svg width="{size}" height="{size}" '
        f'style="transform:rotate(-90deg)" xmlns="http://www.w3.org/2000/svg">'
        f'<defs>'
        f'<linearGradient id="{grad_id}" x1="0%" y1="0%" x2="100%" y2="100%">'
        f'<stop offset="0%" stop-color="{stroke}" stop-opacity="0.85"/>'
        f'<stop offset="100%" stop-color="{stroke_dark}" stop-opacity="1"/>'
        f'</linearGradient>'
        f'</defs>'
        f'<circle cx="{cx}" cy="{cx}" r="{r}" fill="none" '
        f'stroke="#e2e8f0" stroke-width="{sw}"/>'
        f'<circle cx="{cx}" cy="{cx}" r="{r}" fill="none" '
        f'stroke="url(#{grad_id})" stroke-width="{sw}" '
        f'stroke-dasharray="{circ:.2f}" stroke-dashoffset="{dash_offset:.2f}" '
        f'stroke-linecap="round" '
        f'style="transition:stroke-dashoffset 0.5s ease-out"/>'
        f'</svg>'
    )

    # Render SVG as data URL — works universally. dcc.Markdown +
    # dangerously_allow_html was rendering the markup as raw text
    # on Connect's deployed runtime in v0.13–v0.18.
    import base64
    svg_b64 = base64.b64encode(svg_inner.encode("utf-8")).decode("ascii")
    return html.Div([
        html.Div([
            html.Img(src=f"data:image/svg+xml;base64,{svg_b64}",
                      style={"position": "absolute", "inset": "0",
                              "width": "100%", "height": "100%"},
                      alt=label),
            html.Div(
                html.Span(f"{value}{unit}", style={
                    "fontWeight": "700", "fontSize": fs_value,
                    "color": text_color, "fontVariantNumeric": "tabular-nums",
                }),
                style={"position": "absolute", "inset": "0",
                        "display": "flex", "alignItems": "center",
                        "justifyContent": "center"},
            ),
        ], style={"position": "relative",
                   "width": f"{size}px", "height": f"{size}px"}),
        html.Div(label, style={
            "marginTop": "4px", "fontSize": fs_label, "fontWeight": "600",
            "textTransform": "uppercase", "letterSpacing": "0.05em",
            "color": "#64748b", "textAlign": "center",
        }) if label else None,
    ], style={"display": "inline-flex", "flexDirection": "column",
               "alignItems": "center"})


def athlete_card_rings(
    name: str,
    rings: list[dict],
    *,
    photo_url: str | None = None,
    meta: str = "",
    tone: str = "aspire",
    href: str | None = None,
):
    """Whoop-style card with photo + name + 3 metric rings inline.

    `rings` is a list of dicts: `{value, pct, label, tone}`. Pass 2-4
    rings depending on layout. Each renders via `metric_ring()`.

    >>> athlete_card_rings(
    ...     "Ali Turki Owaida",
    ...     meta="SENIOR · Fencing",
    ...     rings=[
    ...         {"value": 68,     "pct": 68, "label": "Recovery", "tone": "good"},
    ...         {"value": "15.8", "pct": 75, "label": "Strain",   "tone": "aspire"},
    ...         {"value": "7h12", "pct": 72, "label": "Sleep",    "tone": "good"},
    ...     ],
    ... )
    """
    # Avatar — photo or initials
    initials = "".join(p[0] for p in name.split()[:2]).upper()
    if photo_url:
        avatar = html.Img(src=photo_url, alt=name, style={
            "width": "44px", "height": "44px", "borderRadius": "50%",
            "objectFit": "cover", "border": "2px solid var(--slate-200)",
            "background": "var(--slate-100)",
        })
    else:
        avatar = html.Div(initials, style={
            "width": "44px", "height": "44px", "borderRadius": "50%",
            "background": "var(--aspire-600)", "color": "white",
            "display": "inline-flex", "alignItems": "center",
            "justifyContent": "center",
            "fontWeight": 700, "fontSize": "14px",
        })

    children = [
        html.Div([
            avatar,
            html.Div([
                html.Div(name, className="amc-name"),
                html.Div(meta, className="amc-meta") if meta else None,
            ], style={"minWidth": "0", "flex": "1"}),
        ], className="amc-header"),
        html.Div([
            metric_ring(r["value"], r["pct"],
                        label=r.get("label", ""),
                        tone=r.get("tone", "aspire"),
                        size=r.get("size", 70))
            for r in rings
        ], style={"display": "flex", "gap": "12px",
                   "justifyContent": "space-around",
                   "marginTop": "8px"}),
    ]

    card = html.Div(children, className=f"athlete-mini-card tone-{tone}")
    if href:
        return html.A(card, href=href,
                       style={"textDecoration": "none", "color": "inherit"})
    return card


# ── 10. Asymmetry bar (VALD) ────────────────────────────────────────────────

def asymmetry_bar(left_pct: int, right_pct: int | None = None):
    """L/R asymmetry split bar. Border colour reflects deviation from 50/50."""
    if right_pct is None:
        right_pct = 100 - left_pct
    deviation = abs(left_pct - 50)
    dev_class = ("" if deviation < 5 else
                 "dev-warn" if deviation < 10 else "dev-danger")
    return html.Div([
        html.Div(f"{left_pct}% L", className="asym-left",
                  style={"width": f"{left_pct}%"}),
        html.Div(f"R {right_pct}%", className="asym-right",
                  style={"width": f"{right_pct}%"}),
    ], className=f"asymmetry-bar {dev_class}")


# ── v0.26 — athlete_card_v2 (Whoop-style, photo + zone gradient + rings) ────

def _initials(name: str) -> str:
    return "".join(p[0] for p in name.split()[:2]).upper()


def athlete_card_v2(
    name: str,
    rings: list[dict],
    *,
    zone: str = "neutral",          # green | yellow | red | aspire | neutral
    photo_url: str | None = None,
    meta: str = "",
    href: str | None = None,
    is_target: bool = False,        # v0.31.4 — gold accent + 🎯 badge for target athletes
):
    """Premium athlete card with photo (or initials fallback) + zone-coloured
    gradient bg + 3 mini metric rings.

    Built for the Whoop coach dashboard but works for any player-facing
    surface (future composite player dashboard, athlete profile pages).

    `rings` is a list of `{value, pct, label, color}` dicts (max 3
    recommended for clean layout). Use `metric_ring()` internally.

    `zone` colours the gradient + avatar border:
        green   — healthy / high recovery / ready
        yellow  — caution / moderate / monitor
        red     — alert / low recovery / sidelined
        aspire  — neutral brand tone (no health signal)
        neutral — grey (no data yet)

    `photo_url` — SAMS imageUrl or any direct CDN URL. Falls back to
    initials with a brand gradient when missing.

    >>> athlete_card_v2(
    ...     "Ali Owaida", meta="Senior · Fencing", zone="green",
    ...     photo_url="https://azfpictures.blob.core.windows.net/...",
    ...     rings=[
    ...         {"value": 68, "pct": 68, "label": "Recovery", "color": "#16a34a"},
    ...         {"value": "15.8", "pct": 75, "label": "Strain", "color": "#004185"},
    ...         {"value": "7h12", "pct": 72, "label": "Sleep", "color": "#16a34a"},
    ...     ],
    ... )
    """
    # Avatar — photo or initials
    if photo_url:
        avatar = html.Img(
            src=photo_url, alt=name,
            className="acv2-avatar",
        )
    else:
        avatar = html.Div(
            _initials(name),
            className="acv2-avatar-initials",
        )

    # Header (avatar + name + meta + optional 🎯 target badge)
    header_children = [
        avatar,
        html.Div([
            html.Div(name, className="acv2-name"),
            html.Div(meta, className="acv2-meta") if meta else None,
        ], className="acv2-text"),
    ]
    if is_target:
        header_children.append(
            html.Span("🎯", className="acv2-target-badge",
                       title="Target Athlete")
        )
    header = html.Div(header_children, className="acv2-header")

    # Ring row — 3 rings via metric_ring()
    # v0.30.1 — honour per-ring `color` (hex) OR `tone` (preset) instead
    # of defaulting everything to aspire blue.
    ring_blocks = []
    for r in rings:
        ring_blocks.append(html.Div([
            metric_ring(
                r["value"], r["pct"],
                label="",
                color=r.get("color"),
                tone=r.get("tone", "aspire"),
                size=58,
            ),
            html.Div(r.get("label", ""), className="acv2-ring-label"),
        ], className="acv2-ring-block"))

    ring_row = html.Div(ring_blocks, className="acv2-rings")

    card_class = f"athlete-card-v2 zone-{zone}"
    if is_target:
        card_class += " is-target"
    card = html.Div([header, ring_row], className=card_class)

    if href:
        return html.A(card, href=href,
                       style={"textDecoration": "none", "color": "inherit",
                              "display": "block"})
    return card


# ── v0.31 — athlete_card_compact (legacy whoop-style dense layout) ──────────

def athlete_card_compact(
    name: str,
    rings: list[dict],
    stats: list[dict] | None = None,
    *,
    zone: str = "neutral",
    photo_url: str | None = None,
    meta: str = "",
    href: str | None = None,
    is_target: bool = False,        # v0.31.4 — gold accent + 🎯 badge
):
    """Compact athlete card — denser layout, more info per card than v2.

    Layout (top → bottom):
      - Header: 40 px avatar (photo OR initials) + name (+ optional meta)
      - Rings row: 3 small rings (48 px), inline
      - Stats row (optional): list of `{label, value, color, status_dot}`
        e.g. ``[{"label": "HRV", "value": "62 ms", "color": "#1876ab"},
                 {"label": "RHR", "value": "52 bpm", "status_dot": "green"}]``

    Use this for grids where you want 4+ cards across (squad views,
    sport rosters). For 2-3 across with hero photo, use `athlete_card_v2`.

    `zone` — green / yellow / red / aspire / gold / neutral → tints the
    card bg with the universal `.zone-*` modifier (v0.29).

    >>> athlete_card_compact(
    ...     "Ali Owaida", meta="Senior · Fencing", zone="green",
    ...     photo_url="https://...",
    ...     rings=[
    ...         {"value": 68, "pct": 68, "label": "Recovery", "color": "#16a34a"},
    ...         {"value": "15.8", "pct": 75, "label": "Strain", "color": "#004185"},
    ...         {"value": "7h12", "pct": 72, "label": "Sleep", "color": "#16a34a"},
    ...     ],
    ...     stats=[
    ...         {"label": "HRV", "value": "62 ms"},
    ...         {"label": "RHR", "value": "52 bpm", "status_dot": "green"},
    ...         {"label": "Deep", "value": "98 m"},
    ...     ],
    ... )
    """
    # Avatar — 40 px photo or initials
    if photo_url:
        avatar = html.Img(
            src=photo_url, alt=name,
            className="acc-avatar",
        )
    else:
        avatar = html.Div(_initials(name), className="acc-avatar-initials")

    header_children = [
        avatar,
        html.Div([
            html.Div(name, className="acc-name"),
            html.Div(meta, className="acc-meta") if meta else None,
        ], className="acc-text"),
    ]
    if is_target:
        header_children.append(
            html.Span("🎯", className="acc-target-badge",
                       title="Target Athlete")
        )
    header = html.Div(header_children, className="acc-header")

    # Rings row — smaller (48 px) than v2's 58 px for density
    ring_blocks = []
    for r in rings:
        ring_blocks.append(html.Div([
            metric_ring(
                r["value"], r["pct"],
                label="",
                color=r.get("color"),
                tone=r.get("tone", "aspire"),
                size=48,
            ),
            html.Div(r.get("label", ""), className="acc-ring-label"),
        ], className="acc-ring-block"))
    ring_row = html.Div(ring_blocks, className="acc-rings")

    # Optional stats row
    stat_row = None
    if stats:
        stat_dot_colors = {
            "green":  "#16a34a",
            "yellow": "#d97706",
            "red":    "#dc2626",
            "aspire": "#004185",
        }
        stat_items = []
        for s in stats:
            dot = None
            if s.get("status_dot"):
                dot = html.Span(className="acc-stat-dot",
                                  style={"backgroundColor":
                                          stat_dot_colors.get(s["status_dot"], "#94a3b8")})
            stat_items.append(html.Div([
                html.Span(s.get("label", ""), className="acc-stat-label"),
                html.Span([dot, s.get("value", "")] if dot else s.get("value", ""),
                            className="acc-stat-value"),
            ], className="acc-stat-item"))
        stat_row = html.Div(stat_items, className="acc-stats")

    children = [header, ring_row]
    if stat_row is not None:
        children.append(stat_row)

    card_class = f"athlete-card-compact zone-{zone}"
    if is_target:
        card_class += " is-target"
    card = html.Div(children, className=card_class)

    if href:
        return html.A(card, href=href,
                       style={"textDecoration": "none", "color": "inherit",
                              "display": "block"})
    return card
