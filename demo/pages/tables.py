"""Tables & Grids — aspire_grid (read-only + editable) + NUMERIC_COL_DEF."""
import dash
from dash import html

try:
    from aspire_dash.tables import aspire_grid, NUMERIC_COL_DEF
except Exception:
    aspire_grid = None
    NUMERIC_COL_DEF = {}

from ._shared import section, example

dash.register_page(__name__, path="/tables", title="Tables", name="Tables")


_SAMPLE_ROWS = [
    {"fencer": "Ali Turki Owaida", "age_group": "SENIOR",
     "sessions": 423, "lesson_min": 1055, "fencing_min": 6065},
    {"fencer": "Khaled Hussein",   "age_group": "SENIOR",
     "sessions": 423, "lesson_min": 1160, "fencing_min": 6415},
    {"fencer": "Abdalla Khalifa",  "age_group": "SENIOR",
     "sessions": 417, "lesson_min": 860,  "fencing_min": 5955},
    {"fencer": "Omar Deif",        "age_group": "U17",
     "sessions": 423, "lesson_min": 845,  "fencing_min": 6740},
]


def layout():
    if aspire_grid is None:
        return html.Div([
            html.H1("Tables — dash-ag-grid not installed",
                    style={"fontSize": "20px", "color": "#ef4444"}),
            html.P("Install dash-ag-grid in your app's requirements to use "
                    "aspire_grid. The wrapper itself ships with aspire_dash."),
        ], style={"padding": "24px"})

    return html.Div([
        html.H1("Tables & Grids",
                style={"fontSize": "28px", "fontWeight": 700,
                       "marginBottom": "8px"}),
        html.P("Branded AG Grid wrapper with read-only and editable presets. "
                "The editable preset (v0.10.0) ships Excel-style Tab/Enter "
                "commit + undo/redo and explicitly warns against wrapping in "
                "dcc.Loading — that causes a 'screen reloads on click' bug.",
                style={"color": "#64748b", "fontSize": "14px",
                       "marginBottom": "24px"}),

        section("aspire_grid — read-only",
                 "Default branded grid. No surprises."),
        example(
            "Per-fencer summary",
            aspire_grid(
                id="demo-grid-ro",
                columnDefs=[
                    {"field": "fencer",     "headerName": "Fencer",
                     "pinned": "left", "width": 200},
                    {"field": "age_group",  "headerName": "AG", "width": 80},
                    {"field": "sessions",   "headerName": "Sessions",
                     "type": "numericColumn"},
                    {"field": "lesson_min", "headerName": "Lesson min",
                     "type": "numericColumn"},
                    {"field": "fencing_min","headerName": "Fencing min",
                     "type": "numericColumn"},
                ],
                rowData=_SAMPLE_ROWS,
                height="180px",
            ),
            "from aspire_dash.tables import aspire_grid\n\n"
            "aspire_grid(\n"
            '    id="my-grid",\n'
            "    columnDefs=[\n"
            '        {"field": "fencer", "pinned": "left"},\n'
            '        {"field": "age_group"},\n'
            '        {"field": "sessions", "type": "numericColumn"},\n'
            "    ],\n"
            "    rowData=df.to_dict('records'),\n"
            ")",
        ),

        section("aspire_grid — editable (v0.10.0 ✨)",
                 "Excel-style: Tab/Enter commit, double-click to edit, "
                 "Escape cancels, Ctrl+Z undoes. Reads commits via "
                 "cellValueChanged (Input) and current state via "
                 "virtualRowData (State)."),
        example(
            "Editable cells",
            aspire_grid(
                id="demo-grid-edit",
                columnDefs=[
                    {"field": "fencer", "pinned": "left", "width": 200,
                     "editable": False},
                    {"field": "age_group", "width": 80, "editable": False},
                    {**NUMERIC_COL_DEF, "field": "lesson_min",
                     "headerName": "Lesson min", "editable": True},
                    {**NUMERIC_COL_DEF, "field": "fencing_min",
                     "headerName": "Fencing min", "editable": True},
                ],
                rowData=[r.copy() for r in _SAMPLE_ROWS],
                editable=True,
                height="180px",
            ),
            "from aspire_dash.tables import aspire_grid, NUMERIC_COL_DEF\n\n"
            "aspire_grid(\n"
            '    id="edit-grid", editable=True,\n'
            "    columnDefs=[\n"
            '        {"field": "fencer", "editable": False, "pinned": "left"},\n'
            "        {**NUMERIC_COL_DEF,\n"
            '         "field": "lesson_min", "editable": True},\n'
            "    ],\n"
            "    rowData=rows,\n"
            ")\n\n"
            "@callback(Output('save-status', 'children'),\n"
            "          Input('edit-grid', 'cellValueChanged'),\n"
            "          prevent_initial_call=True)\n"
            "def autosave(change):\n"
            "    if change[0]['oldValue'] == change[0]['value']: return ''  # no-op\n"
            "    save_to_db(change[0]['data'])\n"
            "    return 'saved'",
        ),

        section("⚠ Don't wrap in dcc.Loading",
                 "The Loading spinner overlays on every cellClicked callback — "
                 "even when the callback returns no_update — which the user "
                 "perceives as 'the screen reloads on click'. Use "
                 "skel_sync_overlay as a sibling Div instead "
                 "(see the Skeletons page)."),
    ], style={"padding": "24px"})
