"""Inputs — toggle_group, mode_toggle, filter_bar, aspire_tabs, date_picker_single."""
import dash
from dash import html
from datetime import date

from aspire_dash.components.inputs import (
    toggle_group, mode_toggle, filter_bar, aspire_tabs, date_picker_single,
)

from ._shared import section, example

dash.register_page(__name__, path="/inputs", title="Inputs", name="Inputs")


def layout():
    return html.Div([
        html.H1("Inputs & Filters",
                style={"fontSize": "28px", "fontWeight": 700,
                       "marginBottom": "8px"}),
        html.P("Selectors, toggles, and the new date_picker_single helper "
                "(v0.10.0) that avoids the moment.js ddd-token rendering bug.",
                style={"color": "#64748b", "fontSize": "14px",
                       "marginBottom": "24px"}),

        section("date_picker_single",
                 "Wraps dcc.DatePickerSingle with safe 'D MMM YYYY' format."),
        example(
            "Default — safe format",
            date_picker_single("demo-date", value=date.today().isoformat()),
            'date_picker_single("my-date", value="2026-05-22")\n'
            '# Renders "22 May 2026" — avoids the Tu19 bug from "ddd DD MMM YYYY"',
        ),
        example(
            "Long day name (dddd is safe)",
            date_picker_single("demo-date-long",
                                value=date.today().isoformat(),
                                display_format="dddd D MMM YYYY",
                                width="200px"),
            'date_picker_single(\n'
            '    "my-date",\n'
            '    value=today,\n'
            '    display_format="dddd D MMM YYYY",  # "Thursday 22 May 2026"\n'
            ')',
        ),

        section("toggle_group",
                 "Segmented button group — Excel-style mutually-exclusive picks."),
        example(
            "Range selector",
            toggle_group("demo-toggle",
                          options=[{"label": "Week", "value": "wk"},
                                   {"label": "Month", "value": "mo"},
                                   {"label": "Season", "value": "se"}],
                          value="wk"),
            'toggle_group("range",\n'
            '    options=[{"label": "Week",   "value": "wk"},\n'
            '             {"label": "Month",  "value": "mo"},\n'
            '             {"label": "Season", "value": "se"}],\n'
            '    value="wk",\n'
            ')',
        ),

        section("mode_toggle",
                 "Like toggle_group but auto-wires a callback to a store id_prefix-store."),
        example(
            "Analysis mode picker",
            mode_toggle("demo-mode",
                         options=[{"label": "Daily",  "value": "d"},
                                  {"label": "Weekly", "value": "w"}],
                         default="d", register_callback=False),
            'mode_toggle("analysis",\n'
            '    options=[{"label": "Daily",  "value": "d"},\n'
            '             {"label": "Weekly", "value": "w"}],\n'
            '    default="d",\n'
            ')\n'
            '# Read from dcc.Store(id="analysis-store")',
        ),

        section("filter_bar",
                 "Right-aligned filter strip — drop any controls in."),
        example(
            "Filter row",
            filter_bar([
                date_picker_single("fb-date", value=date.today().isoformat()),
                toggle_group("fb-toggle",
                              options=[{"label": "A", "value": "a"},
                                       {"label": "B", "value": "b"}],
                              value="a"),
            ]),
            "filter_bar([\n"
            "    date_picker_single('fb-date', value=today),\n"
            "    toggle_group('fb-toggle', options=[...], value='a'),\n"
            "])",
        ),

        section("aspire_tabs",
                 "Styled tab component."),
        example(
            "Three tabs",
            aspire_tabs("demo-tabs",
                         tabs=[{"label": "Overview", "value": "overview"},
                               {"label": "Details",  "value": "details"},
                               {"label": "Settings", "value": "settings"}],
                         value="overview"),
            "aspire_tabs('demo-tabs',\n"
            "    tabs=[{'label': 'Overview', 'value': 'overview'},\n"
            "          {'label': 'Details',  'value': 'details'},\n"
            "          {'label': 'Settings', 'value': 'settings'}],\n"
            "    value='overview',\n"
            ")",
        ),
    ], style={"padding": "24px"})
