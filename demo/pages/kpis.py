"""KPI components — kpi_tile, kpi_strip, kpi_stat, kpi_tile_row."""
import dash
from dash import html

from aspire_dash.components.kpi import kpi_tile, kpi_strip, kpi_stat, kpi_tile_row

from ._shared import section, example

dash.register_page(__name__, path="/kpis", title="KPIs", name="KPIs")


def layout():
    return html.Div([
        html.H1("KPI Components",
                style={"fontSize": "28px", "fontWeight": 700,
                       "marginBottom": "8px"}),
        html.P("Single tiles, horizontal strips, and dense rows. All read "
                "from the same Aspire palette so the entire app feels cohesive.",
                style={"color": "#64748b", "fontSize": "14px",
                       "marginBottom": "24px"}),

        section("kpi_tile",
                 "Single metric with label, value, and optional unit + target progress."),
        example(
            "Basic", kpi_tile("Sessions", 423, unit="", size="lg"),
            'kpi_tile("Sessions", 423, size="lg")',
        ),
        example(
            "With target", kpi_tile("Attendance", 87, unit="%",
                                     target=90, size="lg"),
            'kpi_tile("Attendance", 87, unit="%", target=90)',
        ),

        section("kpi_strip",
                 "Horizontal flow of small KPIs — good for headers + filter bars."),
        example(
            "Four metrics",
            kpi_strip([
                {"label": "Sessions", "value": 423},
                {"label": "Attendance", "value": "87%"},
                {"label": "Total min", "value": "11,505"},
                {"label": "Logged", "value": "92%"},
            ]),
            "kpi_strip([\n"
            "    {'label': 'Sessions', 'value': 423},\n"
            "    {'label': 'Attendance', 'value': '87%'},\n"
            "    {'label': 'Total min', 'value': '11,505'},\n"
            "    {'label': 'Logged', 'value': '92%'},\n"
            "])",
        ),

        section("kpi_tile_row",
                 "Dense tile row — used on dashboard pages."),
        example(
            "Three tiles",
            kpi_tile_row([
                {"label": "Revenue", "value": "$2.4M", "key": "rev"},
                {"label": "Spend", "value": "$1.8M", "key": "spend"},
                {"label": "Margin", "value": "25%", "key": "margin"},
            ]),
            "kpi_tile_row([\n"
            "    {'label': 'Revenue', 'value': '$2.4M', 'key': 'rev'},\n"
            "    {'label': 'Spend', 'value': '$1.8M', 'key': 'spend'},\n"
            "    {'label': 'Margin', 'value': '25%', 'key': 'margin'},\n"
            "])",
        ),

        section("kpi_stat",
                 "Even smaller — label/value pair, slate sub-line."),
        example(
            "Inline stat",
            html.Div([
                kpi_stat("Sessions", "423", "since Sept"),
                kpi_stat("Attendance", "87%", "23 fencers"),
            ], style={"display": "flex", "gap": "20px"}),
            'kpi_stat("Sessions", "423", "since Sept")',
        ),
    ], style={"padding": "24px"})
