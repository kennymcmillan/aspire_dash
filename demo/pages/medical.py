"""Medical module — body silhouette heatmap + injury_list."""
import dash
from dash import html

from aspire_dash.medical import body_silhouette, injury_list, SAMS_TO_BODYMAP

from ._shared import section, code_block

dash.register_page(__name__, path="/medical", title="Medical",
                    name="Medical")


def layout():
    return html.Div([
        html.H1("Medical Components",
                style={"fontSize": "28px", "fontWeight": 700,
                       "marginBottom": "8px"}),
        html.P("Body region heatmap + injury list. Promoted from "
                "medical-dashboard for cross-app reuse (attendance, "
                "training-load, athlete profile).",
                style={"color": "#64748b", "fontSize": "14px",
                       "marginBottom": "24px"}),

        section("body_silhouette — body region heatmap",
                 "Anatomical SVG mapped to SAMS region names. Each region "
                 "is filled with an Aspire-blue gradient based on value-to-max."),
        body_silhouette({
            "THIGH":           4.5,
            "ANKLE":           0.3,
            "PELVIS/LOW BACK": 3.2,
            "SHOULDER":        2.1,
            "KNEE":            1.8,
        }, title="Injury count per region (last 90 days)"),
        code_block(
            "from aspire_dash.medical import body_silhouette\n\n"
            "body_silhouette({\n"
            '    "THIGH":           4.5,\n'
            '    "ANKLE":           0.3,\n'
            '    "PELVIS/LOW BACK": 3.2,\n'
            "}, title='Injury count per region')\n"
        ),

        section("injury_list — multi-injury container",
                 "Composes v0.12 injury_card. Renders branded empty state "
                 "when the list is empty."),
        injury_list([
            {"body_part": "L Hamstring", "severity": "severe",
             "status": "Out 4 wk",
             "detail": "Grade II strain, mid-belly.",
             "onset_date": "2026-05-15", "days_out": 7},
            {"body_part": "R Achilles", "severity": "moderate",
             "status": "Modified training",
             "detail": "Tendinopathy. Pain on push-off.",
             "onset_date": "2026-04-22", "days_out": 30},
            {"body_part": "Lower back", "severity": "mild",
             "status": "Monitoring",
             "detail": "DOMS after Sat session.",
             "onset_date": "2026-05-18", "days_out": 4},
        ]),
        code_block(
            "from aspire_dash.medical import injury_list\n\n"
            "injury_list([\n"
            "    {'body_part': 'L Hamstring', 'severity': 'severe',\n"
            "     'status': 'Out 4 wk', 'detail': 'Grade II strain.',\n"
            "     'onset_date': '2026-05-15', 'days_out': 7},\n"
            "    ...\n"
            "])\n"
            "\n"
            "# Empty list -> branded 'No active injuries' empty state\n"
            "injury_list([])"
        ),

        section("Region coverage",
                 f"SAMS_TO_BODYMAP maps {len(SAMS_TO_BODYMAP)} SAMS region "
                 "names onto bodymap SVG element IDs. Exported so apps can "
                 "audit which regions are covered (e.g. 'WRIST' collapses "
                 "into 'HAND')."),
        html.Pre(
            "\n".join(f"  {region:<25} -> {len(ids)} ids"
                      for region, ids in SAMS_TO_BODYMAP.items()),
            style={"background": "#f1f5f9", "padding": "12px",
                    "borderRadius": "6px", "fontSize": "11px",
                    "fontFamily": "Fira Code, monospace"},
        ),
    ], style={"padding": "24px"})
