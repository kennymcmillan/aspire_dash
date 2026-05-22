"""KPI components — kpi_tile, kpi_strip, kpi_stat, kpi_tile_row."""
import dash
from dash import html

from aspire_dash.components.kpi import kpi_tile, kpi_strip, kpi_stat, kpi_tile_row
from aspire_dash.theme import ASPIRE

from ._shared import section, example

dash.register_page(__name__, path="/kpis", title="KPIs", name="KPIs")


def layout():
    return html.Div([
        html.H1("KPI Components",
                style={"fontSize": "28px", "fontWeight": 700,
                       "marginBottom": "8px"}),
        html.P("Single tiles, horizontal strips, and dense rows.",
                style={"color": "#64748b", "fontSize": "14px",
                       "marginBottom": "24px"}),

        section("kpi_tile",
                 "Single metric with label, value, and optional unit + "
                 "target progress."),
        example(
            "Basic",
            kpi_tile("Sessions", 423, size="lg"),
            'kpi_tile("Sessions", 423, size="lg")',
        ),
        example(
            "With target progress bar",
            kpi_tile("Attendance", 87, unit="%", size="lg",
                      target={"target_value": 90, "band": "ok"}),
            'kpi_tile("Attendance", 87, unit="%",\n'
            '         target={"target_value": 90, "band": "ok"})',
        ),

        section("kpi_strip",
                 "Horizontal flow of small KPIs from a list of dicts or tuples."),
        example(
            "Four metrics (dicts)",
            kpi_strip([
                {"label": "Sessions",    "value": 423, "unit": ""},
                {"label": "Attendance",  "value": 87,  "unit": "%"},
                {"label": "Total min",   "value": 11505, "unit": "min"},
                {"label": "Logged",      "value": 92, "unit": "%"},
            ]),
            "kpi_strip([\n"
            "    {'label': 'Sessions',   'value': 423,   'unit': ''},\n"
            "    {'label': 'Attendance', 'value': 87,    'unit': '%'},\n"
            "    {'label': 'Total min',  'value': 11505, 'unit': 'min'},\n"
            "    {'label': 'Logged',     'value': 92,    'unit': '%'},\n"
            "])",
        ),
        example(
            "Tuples shorthand",
            kpi_strip([
                ("Athletes", 142,  ""),
                ("Sports",   7,    ""),
                ("Diaries",  1042, "this yr"),
            ]),
            "kpi_strip([\n"
            "    ('Athletes', 142,  ''),\n"
            "    ('Sports',   7,    ''),\n"
            "    ('Diaries',  1042, 'this yr'),\n"
            "])",
        ),

        section("kpi_tile_row",
                 "Bootstrap-row of kpi_tile components. Specs are TUPLES "
                 "(label, value, unit, color) — not dicts. Values must be "
                 "numeric (kpi_tile formats with .1f). Use formatters in "
                 "budget.py if you need '$2.4M'-style display."),
        example(
            "Three numeric tiles",
            kpi_tile_row([
                ("Revenue", 2400000, "QAR",  ASPIRE["600"]),
                ("Spend",   1800000, "QAR",  ASPIRE["700"]),
                ("Margin",  25,      "%",    ASPIRE["500"]),
            ]),
            "from aspire_dash.theme import ASPIRE\n\n"
            "kpi_tile_row([\n"
            "    ('Revenue', 2400000, 'QAR', ASPIRE['600']),\n"
            "    ('Spend',   1800000, 'QAR', ASPIRE['700']),\n"
            "    ('Margin',  25,      '%',   ASPIRE['500']),\n"
            "])",
        ),

        section("kpi_stat",
                 "Even smaller — vertical label / big value / sub line."),
        example(
            "Inline stats",
            html.Div([
                kpi_stat("Sessions", "423", "since Sept"),
                kpi_stat("Attendance", "87%", "23 fencers"),
                kpi_stat("Total min", "11,505", "all activities"),
            ], style={"display": "flex", "gap": "24px"}),
            'kpi_stat("Sessions", "423", "since Sept")\n'
            'kpi_stat("Attendance", "87%", "23 fencers")',
        ),
    ], style={"padding": "24px"})
