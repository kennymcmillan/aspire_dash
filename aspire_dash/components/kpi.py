"""KPI tiles + KPI strip — the Aspire metric-card signature.

Auto-split from the legacy single-file components.py during the
0.8 → 1.0 refactor. Backwards-compatible: `from aspire_dash.components
import X` keeps working via the package __init__.
"""
import dash
from dash import html, dcc, clientside_callback, Input, Output, State
import dash_bootstrap_components as dbc

from ..theme import (
    SIDEBAR_WIDTH, SIDEBAR_BG, SIDEBAR_BORDER, SIDEBAR_LINK_COLOR,
    SIDEBAR_LINK_HOVER_BG, SIDEBAR_LINK_ACTIVE_BG,
    FONT_FAMILY, ACCENT, ACCENT_HOVER,
    LOGO_FILENAME, LOGO_ALT, SLATE, ASPIRE,
    SHADOW_SM, SHADOW_MD, RADIUS_LG, RADIUS_FULL,
)


__all__ = ['kpi_tile', 'kpi_tile_row', 'kpi_strip', 'kpi_stat']

# ── KPI Tile ────────────────────────────────────────────────────────────────

def kpi_tile(label, value, unit="", color=None, target=None, size="lg",
             md_col=3, className="mb-2"):
    """KPI tile: uppercase label · big value · unit subtitle · optional
    vs-target progress bar with band coloring.

    Used for metric strips (calories / mph / kg / pct), dashboard KPI
    rows, and the macro-totals card on data-bound pages.

    Parameters
    ----------
    label : str
        Uppercase title (e.g. "Energy", "Protein").
    value : float | int | None
        The big number. None renders as "—".
    unit : str
        Right of the number (e.g. "kcal", "g", "mg"). Also shown in
        the target-comparison subtitle when target is provided.
    color : str
        Hex/CSS color for the left-stripe accent + value text. Falls
        back to ASPIRE_BLUE if not supplied.
    target : dict | None
        Optional vs-target context. Shape:
            {target_value | target_resolved_target,  # absolute target
             pct_of_target,                          # already-computed %
             band: "in" | "below" | "above"}
        When present, the tile gets a progress bar + a "X% of target"
        subtitle colored by band_color(band).
    size : "lg" | "sm"
        Visual density. lg = 1.8rem value, sm = 1.4rem value.
    md_col : int
        Bootstrap col width within a dbc.Row (1-12). Default 3 = 4-up.
    className : str
        Extra classes on the wrapping Col.

    Returns a dbc.Col so the tiles slot into a dbc.Row directly.
    """
    from aspire_dash.theme import band_color, ASPIRE_BLUE  # local — avoid cycle

    accent = color or ASPIRE_BLUE
    value_text_size = "1.8rem" if size == "lg" else "1.4rem"
    label_text_size = "0.7rem" if size == "lg" else "0.65rem"
    padding         = "12px 16px" if size == "lg" else "8px 12px"
    border_width    = "4px" if size == "lg" else "3px"
    border_radius   = "8px" if size == "lg" else "6px"

    bar = None
    sub = html.Div(unit, className="text-muted small",
                   style={"fontSize": label_text_size})

    has_target = bool(target) and (target.get("target_resolved_target")
                                   or target.get("target_value"))
    if has_target and value:
        tgt_val = (target.get("target_resolved_target")
                   or target.get("target_value"))
        band = (target.get("band") or "").lower()
        pct = target.get("pct_of_target")
        bc_hex = band_color(band, as_hex=True)
        bc_bs  = band_color(band)
        bar = dbc.Progress(
            value=min(100, (value / tgt_val) * 100) if tgt_val else 0,
            style={"height": "5px", "marginTop": "6px"},
            color=bc_bs,
        )
        pct_txt = (f"{pct:.0f}% of target" if pct is not None
                   else f"{value/tgt_val*100:.0f}% of {tgt_val:,.0f}{unit}")
        sub = html.Div([
            html.Span(unit), html.Span(" · "),
            html.Span(pct_txt, style={"color": bc_hex, "fontWeight": "600"}),
        ], className="text-muted small")

    return dbc.Col(html.Div([
        html.Div(label, className="text-muted small",
                 style={"textTransform": "uppercase",
                        "letterSpacing": "0.5px",
                        "fontSize": label_text_size}),
        html.Div(f"{value:,.0f}" if value else "—",
                 style={"fontSize": value_text_size,
                        "fontWeight": "700",
                        "color": accent, "lineHeight": "1.1"}),
        sub,
        bar,
    ], style={"padding": padding,
              "background": "white",
              "border": f"1px solid {SLATE['200']}",
              "borderRadius": border_radius,
              "borderLeft": f"{border_width} solid {accent}",
              "height": "100%"}),
        md=md_col, className=className)


def kpi_strip(metrics, *, size="lg", colors=None):
    """One-line convenience for a KPI row from a plain dict.

    Each entry in `metrics` is one of:
        {"label": "Energy", "value": 1971, "unit": "kcal"}            # 3-key
        ("Energy", 1971, "kcal")                                       # tuple

    `colors` is an optional dict mapping label.lower() -> color hex.
    Defaults to ASPIRE_BLUE for every tile.

    Example:
        kpi_strip([
            {"label": "Athletes", "value": 142,  "unit": ""},
            {"label": "Sports",   "value": 7,    "unit": ""},
            {"label": "Diaries",  "value": 1042, "unit": "this year"},
            {"label": "Avg kcal", "value": 2104, "unit": "kcal/day"},
        ])
    """
    from aspire_dash.theme import ASPIRE_BLUE
    colors = colors or {}
    specs = []
    for m in metrics:
        if isinstance(m, dict):
            label = m["label"]
            value = m.get("value")
            unit = m.get("unit", "")
        elif isinstance(m, tuple):
            if len(m) == 3:
                label, value, unit = m
            elif len(m) == 2:
                label, value = m
                unit = ""
            else:
                raise ValueError(f"kpi_strip tuple must be (label, value[, unit]): {m!r}")
        else:
            raise ValueError(f"kpi_strip entry must be dict or tuple: {m!r}")
        color = colors.get(label.lower(), ASPIRE_BLUE)
        specs.append((label, value, unit, color))
    return kpi_tile_row(specs, size=size)


def kpi_tile_row(specs, target_by_key=None, size="lg", className="g-2"):
    """Render a row of kpi_tile() components from a spec list.

    Each spec is a tuple:
        (label, key, value, unit, color)        # 5-tuple, with target lookup
        (label, value, unit, color)             # 4-tuple, no target lookup

    target_by_key : dict[str, dict] | None
        Maps key -> target dict (see kpi_tile docstring). Only used
        for 5-tuple specs.
    """
    by_key = target_by_key or {}
    cols = []
    for spec in specs:
        if len(spec) == 5:
            label, key, value, unit, color = spec
        elif len(spec) == 4:
            label, value, unit, color = spec
            key = None
        else:
            raise ValueError(f"kpi_tile_row spec must be 4 or 5 elements: {spec!r}")
        target = by_key.get((key or "").lower()) if key else None
        cols.append(kpi_tile(label, value, unit, color, target=target, size=size))
    return dbc.Row(cols, className=className)



# ── KPI Stat (vertical label/value/sub) ────────────────────────────────────

def kpi_stat(label, value, sub: str = "", color: str | None = None, icon: str | None = None):
    """Vertical KPI tile — uppercase label · big value · optional subtitle.

    Distinct from ``summary_card`` (denser layout, white-on-white) and
    ``kpi_tile`` (vs-target progress bar). This one is the bare KPI used
    in medical-dashboard squad cards and the budget app's variance row.

    Use directly inside a flex/grid or wrap in ``dbc.Col``.

    Parameters
    ----------
    label : str
        Uppercase eyebrow (e.g. "Days lost", "Budget").
    value : str | int | float
        Big number — pre-format thousands / currency / pct before passing in.
    sub : str
        Optional subtitle (e.g. "vs target", "138/174").
    color : str or None
        Hex for the value text. Defaults to Aspire blue.
    icon : str or None
        FontAwesome class for an inline label icon.
    """
    val_color = color or ASPIRE["600"]
    icon_el = html.I(className=icon, style={
        "fontSize": "10px", "marginRight": "6px", "color": SLATE["400"],
    }) if icon else None
    return html.Div([
        html.Div(
            [icon_el, label] if icon_el else label,
            style={
                "fontSize": "11px", "fontWeight": "600",
                "color": SLATE["500"], "textTransform": "uppercase",
                "letterSpacing": "0.4px",
                "display": "flex", "alignItems": "center",
            },
        ),
        html.Div(str(value), style={
            "fontSize": "26px", "fontWeight": "700", "color": val_color,
            "marginTop": "4px", "fontVariantNumeric": "tabular-nums",
            "lineHeight": "1.15",
        }),
        html.Div(sub, style={
            "fontSize": "12px", "color": SLATE["400"], "marginTop": "2px",
        }) if sub else None,
    ], style={
        "background": "white",
        "border": f"1px solid {SLATE['200']}",
        "borderRadius": f"{RADIUS_LG}px",
        "padding": "14px 16px",
        "boxShadow": SHADOW_SM,
    })


