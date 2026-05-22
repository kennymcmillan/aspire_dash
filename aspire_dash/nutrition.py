"""Nutrition components — macro tile strip + per-macro progress.

Promoted from aspire-nutrition. The macro_strip pattern is the
'4 KPI tiles with progress bar to target' layout used on every
diary day + analysis page. Generalises to any per-day-vs-target
display (training load vs plan, hydration vs goal, etc.).
"""
from __future__ import annotations

from dash import html

from .theme import ASPIRE, SLATE


_MACRO_DEFAULTS = {
    "energy":  {"label": "Energy",  "unit": "kcal", "color": ASPIRE["600"]},
    "protein": {"label": "Protein", "unit": "g",    "color": "#16a34a"},
    "carbs":   {"label": "Carbs",   "unit": "g",    "color": "#f59e0b"},
    "fat":     {"label": "Fat",     "unit": "g",    "color": "#dc2626"},
}


def macro_tile(label: str, value: float, target: float | None = None, *,
                unit: str = "", accent: str | None = None,
                show_progress: bool = True):
    """One nutrition macro tile — value + target + slim progress bar.

    `value` and `target` can be any numeric. If `target` is given and
    `show_progress` is True, a thin bar shows the ratio (clamped 0-120%).

        >>> macro_tile("Protein", 110, target=140, unit="g", accent="#16a34a")
    """
    accent = accent or ASPIRE["600"]
    pct = None
    if target and target > 0:
        pct = min(120, max(0, 100 * value / target))

    children = [
        html.Div(label, style={
            "fontSize": "10.5px", "fontWeight": 600,
            "textTransform": "uppercase", "letterSpacing": "0.5px",
            "color": SLATE["500"], "marginBottom": "6px",
        }),
        html.Div([
            html.Span(f"{value:g}",
                       style={"fontSize": "26px", "fontWeight": 700,
                              "color": SLATE["900"],
                              "fontVariantNumeric": "tabular-nums lining-nums",
                              "lineHeight": "1.1"}),
            html.Span(unit, style={"fontSize": "11px",
                                      "color": SLATE["400"],
                                      "marginLeft": "3px",
                                      "fontWeight": 500}),
            html.Span(f" / {target:g}{unit}" if target else "",
                       style={"fontSize": "11px",
                              "color": SLATE["400"],
                              "marginLeft": "6px",
                              "fontWeight": 500}),
        ]),
    ]
    if show_progress and pct is not None:
        # Bar colour shifts when over target
        bar_color = "#dc2626" if pct > 110 else \
                    "#f59e0b" if pct > 100 else accent
        children.append(html.Div([
            html.Div(style={
                "width": f"{min(100, pct)}%",
                "height": "100%",
                "background": bar_color,
                "borderRadius": "3px",
                "transition": "width 0.3s ease-out",
            }),
        ], style={
            "marginTop": "8px",
            "height": "5px",
            "background": SLATE["100"],
            "borderRadius": "3px",
            "overflow": "hidden",
        }))

    return html.Div(children, style={
        "flex": "1", "minWidth": "120px",
        "padding": "14px 16px",
        "background": "white",
        "border": f"1px solid {SLATE['200']}",
        "borderLeft": f"3px solid {accent}",
        "borderRadius": "8px",
    })


def macro_strip(macros: dict, targets: dict | None = None,
                 *, layout: str = "row"):
    """Horizontal strip of 4 macro tiles (energy/protein/carbs/fat).

    `macros`  — `{"energy": 2400, "protein": 110, "carbs": 280, "fat": 75}`
    `targets` — same shape, optional. When provided each tile shows a
                small progress bar vs target.

        >>> macro_strip(
        ...     macros={"energy": 2400, "protein": 110, "carbs": 280, "fat": 75},
        ...     targets={"energy": 2800, "protein": 140, "carbs": 320, "fat": 80},
        ... )
    """
    targets = targets or {}
    tiles = []
    for key, defaults in _MACRO_DEFAULTS.items():
        if key not in macros:
            continue
        tiles.append(macro_tile(
            defaults["label"],
            macros[key],
            target=targets.get(key),
            unit=defaults["unit"],
            accent=defaults["color"],
        ))
    return html.Div(tiles, style={
        "display": "flex",
        "flexDirection": "column" if layout == "column" else "row",
        "gap": "10px",
        "flexWrap": "wrap",
    })
