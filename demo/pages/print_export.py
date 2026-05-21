"""Print & Export — print_header, print_footer, export_buttons,
a4_report_shell (v0.10.0), register_print_button, safe_markdown_label."""
import dash
from dash import html

from aspire_dash.components.print_export import (
    print_header, print_footer, export_buttons,
    a4_report_shell, safe_markdown_label,
)

from ._shared import section, example, code_block

dash.register_page(__name__, path="/print-export",
                    title="Print & Export", name="Print & Export")


def _sample_a4_body():
    return html.Div([
        html.H2("Sample report body",
                 style={"fontSize": "14px", "color": "#0f172a",
                         "marginBottom": "8px"}),
        html.P("Drop any Dash components here — KPI tiles, charts, tables. "
                "The wrapper handles the page layout, Aspire branding, "
                "print toolbar, and window.print() wiring.",
                style={"fontSize": "12px", "color": "#475569",
                       "lineHeight": "1.6"}),
        html.Ul([
            html.Li("Header bar with Aspire mark + title",
                    style={"fontSize": "11px"}),
            html.Li("Subtitle + period label (top-right)",
                    style={"fontSize": "11px"}),
            html.Li("Sticky 'Back' link + Print button (no-print)",
                    style={"fontSize": "11px"}),
            html.Li("A4-sized white page with the boxShadow elevation",
                    style={"fontSize": "11px"}),
        ]),
    ])


def layout():
    return html.Div([
        html.H1("Print & Export",
                style={"fontSize": "28px", "fontWeight": 700,
                       "marginBottom": "8px"}),
        html.P("Reusable shells + helpers for printable reports and CSV/Excel "
                "exports.",
                style={"color": "#64748b", "fontSize": "14px",
                       "marginBottom": "24px"}),

        section("a4_report_shell (v0.10.0 ✨)",
                 "Standard A4 printable layout — toolbar + Aspire header bar + "
                 "body slot. Used for the fencer reports, weekly briefs, "
                 "monthly summaries in the fencing planner."),
        html.Div([
            html.Div("Live preview (scaled to fit) — opens at /print-export "
                     "in your app",
                     style={"fontSize": "11px", "color": "#94a3b8",
                            "marginBottom": "6px"}),
            html.Div(
                a4_report_shell(
                    title="Fencing · Sample Report",
                    body=_sample_a4_body(),
                    subtitle="Aspire Academy",
                    back_href="#",
                    print_button_id="demo-print-btn",
                ),
                style={"transform": "scale(0.55)",
                       "transform-origin": "top left",
                       "width": "182%",  # offset the scale-down
                       "height": "350px", "overflow": "hidden",
                       "border": "1px solid #e2e8f0",
                       "borderRadius": "6px",
                       "marginBottom": "8px"},
            ),
            code_block(
                "from aspire_dash.components.print_export import (\n"
                "    a4_report_shell, register_print_button,\n"
                ")\n\n"
                "def layout(sams_id):\n"
                "    return a4_report_shell(\n"
                '        title="Fencing · Player Report",\n'
                "        body=_player_body(sams_id),\n"
                '        back_href=dash.get_relative_path("/scorecard"),\n'
                "    )\n\n"
                "# Wire window.print() once at app startup:\n"
                "register_print_button(app)\n"
            ),
        ]),

        section("export_buttons",
                 "CSV + Excel export buttons that wrap a shared dcc.Download. "
                 "Use with send_export() from a callback."),
        example(
            "Two buttons",
            export_buttons(export_id="demo-export", csv=True, excel=True),
            "from aspire_dash.components.print_export import (\n"
            "    export_buttons, send_export,\n"
            ")\n\n"
            'export_buttons(export_id="report-export")\n\n'
            "# Callback\n"
            "@callback(Output('report-export-download', 'data'),\n"
            "          Input('report-export-csv', 'n_clicks'),\n"
            "          Input('report-export-xlsx', 'n_clicks'),\n"
            "          State('store', 'data'),\n"
            "          prevent_initial_call=True)\n"
            "def _export(*_, store):\n"
            "    return send_export(ctx.triggered_id, df, 'fencers')",
        ),

        section("print_header + print_footer",
                 "Compact strips shown ONLY when printing (CSS @media print). "
                 "Useful when you don't need the full a4_report_shell."),
        example("Header + footer",
                 html.Div([
                     html.Div("Print header / footer — visible only when "
                              "printing. Toggle the .print-* classes in dev "
                              "to preview.",
                              style={"fontSize": "11px",
                                      "color": "#94a3b8",
                                      "padding": "12px",
                                      "background": "#f1f5f9",
                                      "border": "1px dashed #cbd5e1",
                                      "borderRadius": "4px"}),
                 ]),
                 "from aspire_dash.components.print_export import (\n"
                 "    print_header, print_footer,\n"
                 ")\n\n"
                 'print_header(title="Q2 Report", subtitle="2026")\n'
                 'print_footer(text="Confidential")'),

        section("safe_markdown_label",
                 "Strip []() from upstream-data strings before embedding in "
                 "markdown link labels. Defensive against names that contain "
                 "those characters (or worse, javascript: protocols)."),
        example(
            "Sanitisation",
            html.Pre(
                f"safe_markdown_label('[Test] (foo)')  →  {safe_markdown_label('[Test] (foo)')!r}\n"
                f"safe_markdown_label('Ali Turki')      →  {safe_markdown_label('Ali Turki')!r}\n",
                style={"background": "#f1f5f9", "padding": "8px",
                        "borderRadius": "4px", "fontSize": "11px",
                        "fontFamily": "Fira Code, monospace"},
            ),
            "from aspire_dash.components.print_export import safe_markdown_label\n\n"
            "# In an AG Grid cellRenderer='markdown' column:\n"
            "summary['fencer_name'] = [\n"
            "    f'[{safe_markdown_label(n)}](/fencer/{int(pid)})'\n"
            "    for n, pid in zip(names, ids)\n"
            "]",
        ),
    ], style={"padding": "24px"})
