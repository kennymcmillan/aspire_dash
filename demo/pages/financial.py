"""Financial reports — scoped style separate from the athletic-modern default."""
import dash
from dash import html

from aspire_dash.financial import (
    financial_kpi, variance_cell, totals_row,
    financial_table, financial_tab_bar,
)
from aspire_dash.budget import fmt_currency

from ._shared import section, code_block

dash.register_page(__name__, path="/financial", title="Financial",
                    name="Financial reports")


def layout():
    return html.Div([
        html.Div([
            html.H1("Financial reports — scoped style"),
            html.P("For monthly briefs, variance reports, quarterly KPI "
                    "summaries. Heavier type, more white space, no "
                    "hover lift — read-only artefacts. Wrap your page in "
                    "className='financial-report' to opt in. Outside the "
                    "scope the athletic style is unchanged.",
                    style={"color": "var(--slate-600)", "fontSize": "13px",
                            "marginBottom": "24px"}),

            # KPIs — Financial scope
            section("financial_kpi — heavier KPI tile"),
            html.Div([
                financial_kpi("Revenue",  "2.4 M",  sub="QAR FY 2026",
                                accent="aspire"),
                financial_kpi("Spend",    "1.8 M",  sub="79% of plan",
                                accent="secondary"),
                financial_kpi("Variance", "-150 K", sub="vs plan",
                                accent="danger"),
                financial_kpi("Margin",   "25%",    sub="up 3pp",
                                accent="gold"),
            ], style={"display": "flex", "gap": "0", "flexWrap": "wrap",
                       "marginBottom": "16px"}),
            code_block(
                "from aspire_dash.financial import financial_kpi\n\n"
                'financial_kpi("Revenue", "2.4 M", sub="QAR FY 2026",\n'
                '              accent="aspire")\n'
                'financial_kpi("Variance", "-150 K", sub="vs plan",\n'
                '              accent="danger")'
            ),

            # Variance cells
            section("variance_cell — coloured ▲▼ deltas"),
            html.Div([
                html.Span("Athletics: "),
                variance_cell(-25000),
                html.Span("  ·  Fencing: ", style={"marginLeft": "10px"}),
                variance_cell(+18000),
                html.Span("  ·  Padel: ", style={"marginLeft": "10px"}),
                variance_cell(-3500),
            ], style={"fontSize": "14px",
                       "padding": "12px", "background": "white",
                       "borderRadius": "6px",
                       "border": "1px solid var(--slate-200)",
                       "marginBottom": "16px"}),
            code_block(
                "from aspire_dash.financial import variance_cell\n\n"
                "variance_cell(-25000)   # red ▼\n"
                "variance_cell(+18000)   # green ▲"
            ),

            # Totals row
            section("totals_row — bold totals strip"),
            html.Div([
                totals_row("Total spend FY 2026", 1_842_500, currency="QAR"),
            ], style={"marginBottom": "16px"}),
            code_block(
                "from aspire_dash.financial import totals_row\n\n"
                "totals_row('Total spend FY 2026', 1_842_500)"
            ),

            # Tab bar
            section("financial_tab_bar — clean underline tabs"),
            financial_tab_bar([
                {"label": "Overview",  "value": "overview"},
                {"label": "Athletics", "value": "athletics"},
                {"label": "Fencing",   "value": "fencing"},
                {"label": "Padel",     "value": "padel"},
            ], tab_id="demo-fr-tabs"),
            code_block(
                "from aspire_dash.financial import financial_tab_bar\n\n"
                "financial_tab_bar([\n"
                "    {'label': 'Overview',  'value': 'overview'},\n"
                "    {'label': 'Athletics', 'value': 'athletics'},\n"
                "    {'label': 'Fencing',   'value': 'fencing'},\n"
                "])"
            ),

            # Branded table
            section("financial_table — aspire-blue header + TOTAL row"),
            financial_table(
                records=[
                    {"Sport": "Athletics", "Planned": 850_000,
                     "Paid": 620_000, "Variance": -8_000},
                    {"Sport": "Fencing", "Planned": 480_000,
                     "Paid": 410_000, "Variance": 18_000},
                    {"Sport": "Padel", "Planned": 240_000,
                     "Paid": 215_000, "Variance": -3_500},
                    {"Sport": "TOTAL", "Planned": 1_570_000,
                     "Paid": 1_245_000, "Variance": 6_500},
                ],
                totals_filter='{Sport} = "TOTAL"',
                negative_columns=["Variance"],
                right_align_columns=["Planned", "Paid", "Variance"],
                id="demo-fr-table",
            ),
            code_block(
                "from aspire_dash.financial import financial_table\n\n"
                "financial_table(\n"
                "    records=df.to_dict('records'),\n"
                "    totals_filter='{Sport} = \"TOTAL\"',\n"
                "    negative_columns=['Variance'],\n"
                "    right_align_columns=['Planned', 'Paid', 'Variance'],\n"
                ")"
            ),

        ], className="financial-report",
           style={"padding": "24px",
                   "maxWidth": "1100px", "margin": "0 auto"}),
    ])
