"""Financial-report style — a SCOPED visual register distinct from the
default athletic-modern look.

Use this module for:
- Monthly briefs
- Variance reports
- Quarterly KPI summaries
- Spend dashboards
- Anything where the reader expects "clean financial" not "premium analytics"

The .financial-report CSS scope overrides aspire_dash defaults INSIDE
its container:
- Heavier value type (32 px bold, tabular-nums everywhere)
- More white space (16-20 px paddings vs the athletic 12-14 px)
- No card hover lift (financial pages are read-only, not interactive)
- Slate-50 KPI backgrounds vs pure white
- Heavier 6 px left accent stripe (athletic uses 4 px)

Outside the scope, the rest of the app still uses the athletic styling.

Helpers in this module:
- financial_kpi(label, value, sub, accent)
- variance_cell(value, currency)
- totals_row(label, value, currency)
- financial_table(df, currency_columns)
- financial_tab_bar(tabs, value, tab_id)

Promoted from aspire-budget-dashboard.
"""
from __future__ import annotations

from dash import html, dcc, dash_table

from .budget import fmt_currency


# ── KPI tile — financial variant ────────────────────────────────────────────

def financial_kpi(label: str, value, sub: str = "",
                   *, accent: str = "aspire"):
    """Bigger, heavier KPI for financial reports. Slate-50 bg, 6 px stripe.

    >>> financial_kpi("Revenue", "2.4M QAR", sub="FY 2026", accent="aspire")
    >>> financial_kpi("Variance", "-15 K", sub="vs plan", accent="danger")
    """
    return html.Div([
        html.Div(label, className="fr-kpi-label"),
        html.Div(str(value), className="fr-kpi-value"),
        html.Div(sub, className="fr-kpi-sub") if sub else None,
    ], className=f"fr-kpi accent-{accent}")


def variance_cell(value, currency: str | None = "QAR"):
    """Coloured variance — green for positive, red for negative, bold."""
    is_neg = value < 0
    colour = "var(--danger, #dc2626)" if is_neg else "var(--success, #16a34a)"
    arrow = "▼" if is_neg else "▲"
    formatted = fmt_currency(abs(value), currency=currency) if currency \
                 else f"{abs(value):,.0f}"
    return html.Span(f"{arrow} {formatted}", style={
        "color": colour, "fontWeight": "700",
        "fontVariantNumeric": "tabular-nums",
    })


def totals_row(label: str, value, currency: str | None = "QAR"):
    """Bold totals row — slate-50 bg + 2 px top border for prominence."""
    return html.Div([
        html.Span(label, style={"flex": "1", "fontWeight": "700"}),
        html.Span(
            fmt_currency(value, currency=currency) if currency
              else f"{value:,.0f}",
            style={"fontWeight": "700",
                    "fontVariantNumeric": "tabular-nums"},
        ),
    ], className="fr-totals-row")


# ── Tab bar — financial variant ────────────────────────────────────────────

def financial_tab_bar(tabs: list[dict], value: str | None = None,
                       tab_id: str = "fr-tabs"):
    """Tab bar with the budget app's clean look (vs the athletic chip toggle).

    >>> financial_tab_bar([
    ...     {"label": "Overview",  "value": "overview"},
    ...     {"label": "Athletics", "value": "athletics"},
    ...     {"label": "Fencing",   "value": "fencing"},
    ... ])
    """
    return dcc.Tabs(
        id=tab_id, value=value or (tabs[0]["value"] if tabs else None),
        children=[dcc.Tab(label=t["label"], value=t["value"],
                            className="fr-tab",
                            selected_className="fr-tab-selected")
                   for t in tabs],
        className="fr-tabs",
    )


# ── Branded table ──────────────────────────────────────────────────────────

def financial_table(records: list[dict], columns: list[dict] | None = None,
                     *, totals_filter: str | None = None,
                     negative_columns: list[str] | None = None,
                     right_align_columns: list[str] | None = None,
                     id: str | None = None):
    """Wrap dash_table.DataTable with the financial-report style.

    Mirrors the SUMMARY_TABLE_STYLE / TOP_TABLE_STYLE patterns from
    aspire-budget-dashboard:
    - aspire-blue header with white uppercase 11 px label
    - slate-50 TOTAL row when ``totals_filter`` provided (e.g.
      ``'{Sport} = "TOTAL"'``)
    - Negative numbers in ``negative_columns`` rendered red + bold

    >>> financial_table(records=[...], columns=[...],
    ...                 totals_filter='{Sport} = "TOTAL"',
    ...                 negative_columns=["Variance"],
    ...                 right_align_columns=["Planned", "Paid", "Variance"])
    """
    if columns is None and records:
        columns = [{"name": k, "id": k} for k in records[0].keys()]

    cond_cell = []
    if right_align_columns:
        cond_cell.extend({"if": {"column_id": c}, "textAlign": "right"}
                          for c in right_align_columns)

    cond_data = []
    if totals_filter:
        cond_data.append({
            "if": {"filter_query": totals_filter},
            "backgroundColor": "var(--slate-100, #f0f3f8)",
            "fontWeight": "700",
            "borderTop": "2px solid var(--slate-700, #334155)",
        })
    if negative_columns:
        for col in negative_columns:
            cond_data.append({
                "if": {"filter_query": f"{{{col}}} < 0", "column_id": col},
                "color": "var(--danger, #dc2626)", "fontWeight": "700",
            })

    return dash_table.DataTable(
        id=id or "fr-table",
        data=records,
        columns=columns,
        style_cell={
            "padding": "8px 12px",
            "fontFamily": "'Poppins', sans-serif",
            "fontSize": "13px",
            "fontVariantNumeric": "tabular-nums",
            "borderColor": "var(--slate-100, #f1f5f9)",
        },
        style_header={
            "backgroundColor": "var(--aspire-600, #004185)",
            "color": "white",
            "fontWeight": "700",
            "fontSize": "11px",
            "textTransform": "uppercase",
            "letterSpacing": "0.5px",
            "textAlign": "right",
        },
        style_cell_conditional=cond_cell,
        style_data_conditional=cond_data,
        style_as_list_view=True,
    )
