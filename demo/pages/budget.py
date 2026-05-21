"""Budget — formatters + variance/utilisation cards + rollup chips."""
import dash
from dash import html

from aspire_dash.budget import (
    fmt_currency, fmt_k, fmt_m, fmt_pct,
    variance_card, utilisation_card, rollup_chips,
)

from ._shared import section, example, code_block

dash.register_page(__name__, path="/budget", title="Budget", name="Budget")


def layout():
    return html.Div([
        html.H1("Budget Components",
                style={"fontSize": "28px", "fontWeight": 700,
                       "marginBottom": "8px"}),
        html.P("Currency formatters + spend/budget cards for finance "
                "dashboards.",
                style={"color": "#64748b", "fontSize": "14px",
                       "marginBottom": "24px"}),

        section("Formatters",
                 "Quick number → display string."),
        html.Pre(
            f"fmt_currency(2_400_000)    → {fmt_currency(2_400_000)}\n"
            f"fmt_k(89_500)               → {fmt_k(89_500)}\n"
            f"fmt_m(2_400_000)            → {fmt_m(2_400_000)}\n"
            f"fmt_pct(0.87)               → {fmt_pct(0.87)}\n",
            style={"background": "#f1f5f9", "padding": "10px",
                    "borderRadius": "4px", "fontSize": "12px",
                    "fontFamily": "Fira Code, monospace",
                    "marginBottom": "20px"},
        ),

        section("variance_card",
                 "Actual vs Budget, with delta + colour."),
        example("Under budget",
                 variance_card(label="Travel",
                                actual=85_000, budget=100_000),
                 "variance_card('Travel', actual=85_000, budget=100_000)"),
        example("Over budget",
                 variance_card(label="Equipment",
                                actual=125_000, budget=100_000),
                 "variance_card('Equipment', actual=125_000, budget=100_000)"),

        section("utilisation_card",
                 "Spend vs budget with progress bar."),
        example("Mid-year",
                 utilisation_card(label="Operations",
                                   spent=540_000, budget=1_200_000),
                 "utilisation_card('Operations', spent=540_000, budget=1_200_000)"),

        section("rollup_chips",
                 "Tiny coloured pills for quick category totals."),
        example("Three rollups",
                 rollup_chips([
                     {"label": "Approved", "value": 4_200_000},
                     {"label": "Pending",  "value": 350_000},
                     {"label": "Denied",   "value": 75_000},
                 ], formatter=fmt_m),
                 "rollup_chips([\n"
                 "    {'label': 'Approved', 'value': 4_200_000},\n"
                 "    {'label': 'Pending',  'value':   350_000},\n"
                 "], formatter=fmt_m)"),
    ], style={"padding": "24px"})
