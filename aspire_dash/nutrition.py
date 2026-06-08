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
                "borderRadius": "4px",   # v0.24: on-scale (was 3)
                "transition": "width 0.3s ease-out",
            }),
        ], style={
            "marginTop": "8px",
            "height": "5px",
            "background": SLATE["100"],
            "borderRadius": "4px",   # v0.24: on-scale (was 3)
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


# ── Macro chips + summary ──────────────────────────────────────────────────
# Promoted from aspire-nutrition's 24h-recall match picker. Use these wherever
# you need to show a food's macro shape inline (a match option, a diary row, a
# supplement panel). The three chip colours match the analysis macro palette so
# a macro means the same colour everywhere: carbs amber / protein blue / fat red.
_CHIP = {"carbs": "#f59e0b", "protein": "#0059b3", "fat": "#dc2626"}


def macro_summary(carbs=None, protein=None, fat=None, kcal=None) -> str:
    """Compact 'C28 P7 F1 · 365 kcal' line for a food/serving. Skips any macro
    that's None; returns '' when nothing is known.

        >>> macro_summary(carbs=28, protein=7, fat=1, kcal=365)
        'C28 P7 F1 · 365 kcal'
    """
    bits = []
    for v, letter in ((carbs, "C"), (protein, "P"), (fat, "F")):
        try:
            if v is not None:
                bits.append(f"{letter}{float(v):.0f}")
        except (TypeError, ValueError):
            pass
    s = " ".join(bits)
    try:
        if kcal is not None:
            s = (s + " · " if s else "") + f"{float(kcal):.0f} kcal"
    except (TypeError, ValueError):
        pass
    return s


def macro_chips(carbs=None, protein=None, fat=None, kcal=None, *,
                per: str | None = "100 g", empty: str = "no macros"):
    """Coloured C / P / F pills + kcal for a food/serving — returns an html.Div
    (flex row). `per` appends a faint basis hint ('/100 g') when set; `empty`
    is shown (muted) when no macro is known.

        >>> macro_chips(carbs=28, protein=7, fat=1, kcal=365)   # -> html.Div(...)
    """
    pills = []
    for v, letter, key in ((carbs, "C", "carbs"), (protein, "P", "protein"),
                           (fat, "F", "fat")):
        try:
            if v is not None:
                pills.append(html.Span(f"{letter} {float(v):.0f}", style={
                    "background": _CHIP[key], "color": "#fff",
                    "borderRadius": "4px", "padding": "1px 6px",
                    "fontSize": "0.7rem", "fontWeight": 600}))
        except (TypeError, ValueError):
            pass
    if not pills:
        return html.Span(empty, style={"fontSize": "0.7rem", "color": SLATE["400"]})
    try:
        if kcal is not None:
            pills.append(html.Span(f"{float(kcal):.0f} kcal",
                                   style={"fontSize": "0.7rem", "color": SLATE["500"]}))
    except (TypeError, ValueError):
        pass
    if per:
        pills.append(html.Span(f"/{per}",
                               style={"fontSize": "0.65rem", "color": SLATE["400"]}))
    return html.Div(pills, style={"display": "flex", "alignItems": "center",
                                  "gap": "4px", "flexWrap": "wrap"})
