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
