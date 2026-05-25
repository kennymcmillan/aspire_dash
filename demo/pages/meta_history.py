"""Meta inline bar + history table — compact data display patterns.

Both promoted in v0.37 from aspire-nutrition (diary period-metadata card,
consultation injury-history block). Used widely across capture flows and
athlete-profile pages."""
import dash
from dash import html

from aspire_dash.components import meta_inline_bar, history_table

from ._shared import section, example

dash.register_page(__name__, path="/meta-history",
                   title="Meta + history", name="Meta + history")


def layout():
    return html.Div([
        html.H1("Meta bar + history table",
                style={"fontSize": "28px", "fontWeight": 700,
                       "marginBottom": "8px"}),
        html.P("Two compact data display patterns for the top of a page "
               "or the body of an entity card.",
               style={"color": "#64748b", "fontSize": "14px",
                      "marginBottom": "24px"}),

        section("meta_inline_bar",
                 "Compact label:value horizontal bar wrapped in a small "
                 "card. Replaces dbc.Row + md columns that wrap to a "
                 "second row even when the optional notes are empty. "
                 "Notes row is omitted entirely when notes=None."),
        example(
            "Card form (default)",
            meta_inline_bar(
                [
                    ("Period",  "4-day"),
                    ("Athlete", "Test Athlete"),
                    ("MRN",     "12345"),
                    ("Sport",   "Athletics"),
                    ("Dates",   "2026-05-01 -> 2026-05-04"),
                ],
                notes="First diary after training-camp return.",
                title="Period metadata",
            ),
            "from aspire_dash.components import meta_inline_bar\n\n"
            "meta_inline_bar(\n"
            "    [\n"
            "        ('Period',  '4-day'),\n"
            "        ('Athlete', 'Test Athlete'),\n"
            "        ('MRN',     '12345'),\n"
            "        ('Sport',   'Athletics'),\n"
            "        ('Dates',   '2026-05-01 -> 2026-05-04'),\n"
            "    ],\n"
            "    notes='First diary after training-camp return.',\n"
            "    title='Period metadata',\n"
            ")",
        ),
        example(
            "Without notes row (cleaner when the comment field is empty)",
            meta_inline_bar(
                [("Period", "1-day"), ("Athlete", "—"), ("MRN", None)],
                title="Period metadata",
            ),
            "meta_inline_bar(\n"
            "    [('Period', '1-day'), ('Athlete', None), ('MRN', None)],\n"
            "    title='Period metadata',\n"
            ")",
        ),
        example(
            "fluid=True — drop the card wrapper",
            html.Div(
                meta_inline_bar(
                    [("Sport", "Squash"), ("Coach", "JM")],
                    fluid=True,
                ),
                style={"padding": "8px 12px",
                        "border": "1px dashed #cbd5e1",
                        "borderRadius": "6px"},
            ),
            "meta_inline_bar(items, fluid=True)\n"
            "# Drop into an existing card body",
        ),

        section("history_table",
                 "Compact striped table with optional summary chips above "
                 "and a status-badge column driven by row data. "
                 "Genericises the injury-history pattern so VALD test "
                 "history, training-load weeks, attendance logs, "
                 "supplement history, etc share one look."),
        example(
            "Injury history (the source pattern)",
            history_table(
                [
                    {"date_of_injury": "2026-04-15", "region": "Knee · L",
                     "diagnosis": "MCL grade I",
                     "availability": "Out", "days_lost": 14,
                     "returned": "2026-04-29"},
                    {"date_of_injury": "2026-02-02", "region": "Ankle · R",
                     "diagnosis": "Lateral sprain",
                     "availability": "Modified", "days_lost": 5,
                     "returned": "2026-02-07"},
                    {"date_of_injury": "2025-11-10", "region": "Hamstring · L",
                     "diagnosis": "Grade I strain",
                     "availability": "Available", "days_lost": 0,
                     "returned": "2025-11-10"},
                ],
                columns=[
                    {"key": "date_of_injury", "label": "Date"},
                    {"key": "region",         "label": "Region · Side"},
                    {"key": "diagnosis",      "label": "Diagnosis"},
                    {"key": "availability",   "label": "Status"},
                    {"key": "days_lost",      "label": "Days lost"},
                    {"key": "returned",       "label": "Returned"},
                ],
                summary_chips=[
                    ("3",   "injuries",      "primary"),
                    ("19",  "days lost",     "muted"),
                    ("1",   "currently out", "danger"),
                ],
                status_column="availability",
                status_palette={"Available": "success",
                                 "Modified":  "warning",
                                 "Out":       "danger"},
            ),
            "history_table(\n"
            "    injuries,\n"
            "    columns=[\n"
            "        {'key': 'date_of_injury', 'label': 'Date'},\n"
            "        {'key': 'region',         'label': 'Region'},\n"
            "        {'key': 'diagnosis',      'label': 'Diagnosis'},\n"
            "        {'key': 'availability',   'label': 'Status'},\n"
            "        {'key': 'days_lost',      'label': 'Days lost'},\n"
            "    ],\n"
            "    summary_chips=[\n"
            "        (str(len(injuries)),  'injuries',      'primary'),\n"
            "        (str(days_lost_sum),  'days lost',     'muted'),\n"
            "        (str(out_count),      'currently out', 'danger'),\n"
            "    ],\n"
            "    status_column='availability',\n"
            "    status_palette={'Available': 'success',\n"
            "                     'Modified': 'warning',\n"
            "                     'Out':       'danger'},\n"
            ")",
        ),
        example(
            "Empty state — no summary chips, no status column",
            history_table([],
                          columns=[{"key": "date", "label": "Date"}],
                          empty_message="No tests on file yet."),
            "history_table([], columns=[...],\n"
            "              empty_message='No tests on file yet.')",
        ),

    ], style={"maxWidth": "1100px"})
