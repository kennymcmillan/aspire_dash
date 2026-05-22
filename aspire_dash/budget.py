"""Budget / variance primitives — currency, variance cards, rollup chips.

Lifted from aspire-budget-dashboard's _kpi_card / fmt_k / variance-row
patterns. Also useful beyond finance — anywhere you compare actual vs
target (medal counts vs goals, PB vs baseline, attendance vs roster).
"""
from __future__ import annotations

from dash import html

from .theme import (
    ASPIRE_BLUE, ASPIRE_NAVY, GOLD, SLATE,
    SUCCESS, DANGER, WARNING, RADIUS_LG, SHADOW_SM,
)


# ── Currency formatting ────────────────────────────────────────────────────

def fmt_currency(value, currency: str = "QAR", precision: int = 0) -> str:
    """Render a value as a localised currency string.

    Examples::

        fmt_currency(1234567)        # "QAR 1,234,567"
        fmt_currency(1234567, "USD") # "USD 1,234,567"
        fmt_currency(None)           # "—"
    """
    if value is None:
        return "—"
    try:
        n = float(value)
    except (TypeError, ValueError):
        return "—"
    return f"{currency} {n:,.{precision}f}"


def fmt_k(value, suffix: str = "k") -> str:
    """Render in thousands. ``1_234_567 → '1,235k'``.

    Pass ``suffix=""`` for plain comma-grouped thousands.
    """
    if value is None:
        return "—"
    try:
        n = float(value)
    except (TypeError, ValueError):
        return "—"
    return f"{n / 1000:,.0f}{suffix}"


def fmt_m(value, suffix: str = "M") -> str:
    """Render in millions. ``12_345_678 → '12.3M'``."""
    if value is None:
        return "—"
    try:
        n = float(value)
    except (TypeError, ValueError):
        return "—"
    return f"{n / 1_000_000:,.1f}{suffix}"


def fmt_pct(value, precision: int = 0) -> str:
    """Render as a percentage. ``0.7345 → '73%'`` or ``73.45 → '73%'``.

    Accepts both fractions (≤1.0) and percent values (>1.0).
    """
    if value is None:
        return "—"
    try:
        n = float(value)
    except (TypeError, ValueError):
        return "—"
    if abs(n) <= 1.0:
        n = n * 100
    return f"{n:,.{precision}f}%"


# ── Variance card ──────────────────────────────────────────────────────────

def variance_card(
    label: str,
    actual,
    target,
    *,
    formatter=None,
    currency: str | None = None,
    higher_is_better: bool = True,
    show_pct: bool = True,
    sub: str | None = None,
):
    """KPI card with delta colour-coded by variance sign.

    Pattern from aspire-budget-dashboard's variance cards — adapts to any
    actual-vs-target comparison.

    Parameters
    ----------
    label : str
        Uppercase eyebrow (e.g. "Variance", "vs PB").
    actual : float | int | None
    target : float | int | None
    formatter : callable or None
        Function that takes a number and returns a string. Defaults to
        ``fmt_currency`` if ``currency`` is provided, else ``fmt_k``.
    currency : str or None
        Convenience: when set, uses ``fmt_currency(_, currency)``.
    higher_is_better : bool
        If True (default), positive variance is green and negative red
        (budget surplus, PB improvement). If False, flips the colours
        (spending over budget, slower time).
    show_pct : bool
        Show the variance as % of target alongside the absolute number.
    sub : str or None
        Override the auto-generated subtitle.
    """
    fmt = formatter or (
        (lambda v: fmt_currency(v, currency)) if currency else fmt_k
    )

    try:
        a = float(actual) if actual is not None else None
        t = float(target) if target is not None else None
    except (TypeError, ValueError):
        a = t = None

    variance = (a - t) if (a is not None and t is not None) else None
    is_positive = (variance or 0) >= 0
    is_good = is_positive if higher_is_better else not is_positive

    color = SUCCESS if is_good else DANGER
    arrow = "▲" if is_positive else "▼"
    sign = "+" if is_positive else "−"

    if variance is None:
        big = "—"
        sub_txt = sub or "no data"
    else:
        big = f"{sign}{fmt(abs(variance))}"
        if show_pct and t:
            pct = abs(variance) / abs(t) * 100 if t else 0
            sub_txt = sub or f"{arrow} {pct:,.0f}% vs {fmt(t)}"
        else:
            sub_txt = sub or f"{arrow} vs {fmt(t) if t is not None else '—'}"

    return html.Div([
        html.Div(label, style={
            "fontSize": "11px", "fontWeight": "600",
            "color": SLATE["500"], "textTransform": "uppercase",
            "letterSpacing": "0.4px",
        }),
        html.Div(big, style={
            "fontSize": "26px", "fontWeight": "700", "color": color,
            "marginTop": "4px", "fontVariantNumeric": "tabular-nums",
        }),
        html.Div(sub_txt, style={
            "fontSize": "12px", "color": SLATE["500"], "marginTop": "2px",
        }),
    ], style={
        "background": "white",
        "border": f"1px solid {SLATE['200']}",
        "borderLeft": f"4px solid {color}",
        "borderRadius": f"{RADIUS_LG}px",
        "padding": "14px 16px",
        "boxShadow": SHADOW_SM,
    })


def utilisation_card(
    label: str,
    used,
    total,
    *,
    formatter=None,
    currency: str | None = None,
    sub: str | None = None,
):
    """% utilisation card with progress bar (used / total).

    Bands: <60% slate, 60-90% Aspire blue, 90-100% gold, >100% red.
    """
    fmt = formatter or (
        (lambda v: fmt_currency(v, currency)) if currency else fmt_k
    )
    try:
        u = float(used) if used is not None else 0
        t = float(total) if total is not None else 0
    except (TypeError, ValueError):
        u = t = 0
    pct = (u / t * 100) if t else 0

    if pct > 100:
        color = DANGER
    elif pct >= 90:
        color = GOLD
    elif pct >= 60:
        color = ASPIRE_BLUE
    else:
        color = SLATE["500"]

    return html.Div([
        html.Div(label, style={
            "fontSize": "11px", "fontWeight": "600",
            "color": SLATE["500"], "textTransform": "uppercase",
            "letterSpacing": "0.4px",
        }),
        html.Div(f"{pct:,.0f}%", style={
            "fontSize": "26px", "fontWeight": "700", "color": color,
            "marginTop": "4px", "fontVariantNumeric": "tabular-nums",
        }),
        html.Div(sub or f"{fmt(u)} of {fmt(t)}", style={
            "fontSize": "12px", "color": SLATE["500"], "marginTop": "2px",
        }),
        html.Div(style={
            "height": "4px", "background": SLATE["100"],
            "borderRadius": "999px", "marginTop": "8px",
            "overflow": "hidden",
        }, children=html.Div(style={
            "height": "100%",
            "width": f"{min(100, max(0, pct)):.0f}%",
            "background": color,
            "transition": "width 200ms ease",
        })),
    ], style={
        "background": "white",
        "border": f"1px solid {SLATE['200']}",
        "borderRadius": f"{RADIUS_LG}px",
        "padding": "14px 16px",
        "boxShadow": SHADOW_SM,
    })


# ── Rollup chip strip (per-sport totals etc.) ──────────────────────────────

def rollup_chips(items: list[dict], formatter=None):
    """Horizontal flex strip of ``label: value`` chips.

    Used in budget for per-sport totals, GCC for medal-by-sport, etc.

    Parameters
    ----------
    items : list of dict
        Each dict: ``{"label": str, "value": number, "color": optional hex}``.
    formatter : callable or None
        Defaults to ``fmt_k``.
    """
    fmt = formatter or fmt_k
    chips = []
    for it in items:
        color = it.get("color") or ASPIRE_BLUE
        chips.append(html.Div([
            html.Div(it["label"], style={
                "fontSize": "10px", "fontWeight": "600",
                "color": SLATE["500"], "textTransform": "uppercase",
                "letterSpacing": "0.4px",
            }),
            html.Div(fmt(it["value"]), style={
                "fontSize": "14px", "fontWeight": "700", "color": color,
                "fontVariantNumeric": "tabular-nums",
            }),
        ], style={
            "padding": "6px 12px",
            "background": "white",
            "border": f"1px solid {SLATE['200']}",
            "borderLeft": f"3px solid {color}",
            "borderRadius": "8px",   # v0.24: canonical (was 6)
            "marginRight": "8px", "marginBottom": "8px",
            "display": "inline-block",
        }))
    return html.Div(chips, style={"display": "flex", "flexWrap": "wrap"})
