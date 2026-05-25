"""Linear step cards — collapsible numbered step flows.

Promoted in v0.37 from aspire-nutrition's diary + consultation pages.
Renders three independent step strips so you can verify the click-to-
toggle behaviour AND see the summary span (the muted line next to the
title that's filled by a state callback in real apps)."""
import dash
from dash import html
import dash_bootstrap_components as dbc

from aspire_dash.components import linear_step_card_collapse

from ._shared import section, example

dash.register_page(__name__, path="/linear-steps",
                   title="Linear steps", name="Linear steps")


def layout():
    return html.Div([
        html.H1("Linear step cards",
                style={"fontSize": "28px", "fontWeight": 700,
                       "marginBottom": "8px"}),
        html.P("Numbered, collapsible step cards for capture / wizard / "
               "consultation flows. Click any header to toggle. The "
               "summary span (greyed italic next to the title) is filled "
               "by the consumer's state callback in real apps — here we "
               "show static text so you can see the slot.",
               style={"color": "#64748b", "fontSize": "14px",
                      "marginBottom": "24px"}),

        section("linear_step_card_collapse — mode B",
                 "Pattern-matched collapse id. Wire the toggle with "
                 "register_linear_step_toggle(app) once in your app — "
                 "this demo wires the default 'linear-step-header' type "
                 "from demo/app.py so headers below are live."),
        example(
            "Independent sections — click each header",
            html.Div([
                linear_step_card_collapse(
                    step=1, title="Demographics",
                    initial_open=True,
                    body=html.Div([
                        html.P("Name, DOB, sport, contact details ..."),
                        dbc.Input(placeholder="Free-text demo field"),
                    ]),
                ),
                linear_step_card_collapse(
                    step=2, title="Context  ·  symptoms / history / goals",
                    body=html.Div("Section body goes here."),
                ),
                linear_step_card_collapse(
                    step=3, title="Anthropometry",
                    body=html.Div("Body mass / stature / skinfolds ..."),
                ),
            ]),
            "from aspire_dash.components import (\n"
            "    linear_step_card_collapse, register_linear_step_toggle,\n"
            ")\n\n"
            "layout = html.Div([\n"
            "    linear_step_card_collapse(\n"
            "        step=1, title='Demographics',\n"
            "        initial_open=True,\n"
            "        body=demographics_form(),\n"
            "    ),\n"
            "    linear_step_card_collapse(\n"
            "        step=2, title='Context',\n"
            "        body=context_form(),\n"
            "    ),\n"
            "])\n\n"
            "# After Dash() — wires click-to-toggle for the whole strip:\n"
            "register_linear_step_toggle(app)",
        ),

        section("Custom header_type",
                "When a page mounts multiple INDEPENDENT step strips that "
                "shouldn't toggle each other, pass a unique header_type "
                "and call register_linear_step_toggle(app, "
                "header_type='your-type') once per strip."),
        example(
            "A second independent strip (header_type='demo-secondary')",
            html.Div([
                linear_step_card_collapse(
                    step=1, title="Pick template",
                    header_type="demo-secondary",
                    body=html.Div("Pick the period template ..."),
                ),
                linear_step_card_collapse(
                    step=2, title="Upload diary",
                    header_type="demo-secondary",
                    body=html.Div("Drop .xlsx here ..."),
                ),
            ]),
            "linear_step_card_collapse(\n"
            "    step=1, title='Pick template',\n"
            "    header_type='wizard-A',     # disjoint from default\n"
            "    body=...,\n"
            ")\n\n"
            "# Each strip needs its own toggle registration:\n"
            "register_linear_step_toggle(app, header_type='wizard-A')",
        ),

        section("Mode A — string collapse_id",
                 "Pass collapse_id='step-X-collapse' when your app already "
                 "owns the toggle callback (typical for the nutrition "
                 "diary, where one big callback drives summaries + auto-"
                 "open + click-toggle in one Output set). DON'T also call "
                 "register_linear_step_toggle in this mode."),
        example(
            "Static example (no toggle wired here)",
            linear_step_card_collapse(
                step=1, title="Step with string id",
                collapse_id="demo-step-1-collapse",
                summary_id="demo-step-1-summary",
                initial_open=True,
                body=html.Div("This card uses a string collapse_id so "
                              "the consumer's own callback can target it."),
            ),
            "linear_step_card_collapse(\n"
            "    step=1, title='Pick template',\n"
            "    summary_id='step-1-summary',\n"
            "    collapse_id='step-1-collapse',\n"
            "    initial_open=True,\n"
            "    body=template_picker(),\n"
            ")",
        ),

    ], style={"maxWidth": "1100px"})
