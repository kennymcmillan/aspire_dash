"""AG Grid wrappers with Aspire defaults + editable / dirty-tracking presets.

Lifted from mapping_app's editable athlete table, SAMS_register's
read-only browser, and iso-leg-press's results table. The base config —
12px Inter, slate borders, Aspire-blue header — is identical across
them, so callers just pass ``columnDefs`` + ``rowData``.

Note: ``aspire_grid`` requires ``dash-ag-grid``. Add to your app's
``requirements.txt`` if you use it.
"""
from __future__ import annotations

from dash import dcc, html, Input, Output, State

from .theme import ASPIRE_BLUE, ASPIRE_NAVY, SLATE  # noqa: F401


def _import_dag():
    import dash_ag_grid as dag
    return dag


# ── Default config presets ────────────────────────────────────────────────

DEFAULT_COL_DEF = {
    "resizable": True,
    "sortable": True,
    "filter": True,
    "minWidth": 130,
    "cellStyle": {"fontSize": "12px", "fontFamily": "Inter, sans-serif"},
}
EDITABLE_COL_DEF = {**DEFAULT_COL_DEF, "editable": True}

DEFAULT_GRID_OPTIONS = {
    "rowHeight": 32,
    "headerHeight": 38,
    "suppressMovableColumns": True,
    "enableCellTextSelection": True,
    "animateRows": False,
}
EDITABLE_GRID_OPTIONS = {
    **DEFAULT_GRID_OPTIONS,
    # Excel-style commit: tab/enter/click-elsewhere commits the edit and
    # fires cellValueChanged. Escape cancels.
    "stopEditingWhenCellsLoseFocus": True,
    "enterNavigatesVertically": True,
    "enterNavigatesVerticallyAfterEdit": True,
    "undoRedoCellEditing": True,
    "undoRedoCellEditingLimit": 20,
    # Do NOT set singleClickEdit: True — it makes every plain click on a
    # cell fire cellClicked, which (combined with a dcc.Loading wrapper)
    # produces a 'screen reloads on click' visual bug for the user. Stick
    # with the AG Grid default (double-click to edit).
}

# Numeric column preset — pass via `columnDefs`. Uses the built-in
# `cellDataType` instead of custom `valueParser`-function shapes, which
# the dash-ag-grid runtime silently rejects in some 35.x builds.
NUMERIC_COL_DEF = {
    "type": "numericColumn",
    "cellDataType": "number",
    "cellEditor": "agNumberCellEditor",
}

#: Style block applied to .ag-theme-alpine to recolour the header with
#: Aspire blue and tighten the row borders to slate-200. Include in your
#: app's assets/custom.css OR import the rules from 00_aspire_base.css
#: (added in v0.6).
ASPIRE_AG_THEME_OVERRIDES = """
.ag-theme-alpine {
    --ag-header-background-color: var(--aspire-600, #004185);
    --ag-header-foreground-color: white;
    --ag-row-border-color: var(--slate-200, #e2e8f0);
    --ag-font-family: Inter, sans-serif;
    --ag-font-size: 12px;
}
.ag-theme-alpine .ag-cell-inline-editing { background: #fff8e1; }
.ag-theme-alpine .ag-row-modified { background: #fff8e1 !important; }
""".strip()


def aspire_grid(
    id: str,
    columnDefs: list[dict] | None = None,
    rowData: list[dict] | None = None,
    *,
    editable: bool = False,
    height: str = "calc(100vh - 200px)",
    grid_options_overrides: dict | None = None,
    column_def_overrides: dict | None = None,
):
    """Branded AG Grid with sensible defaults.

    Parameters
    ----------
    id : str
        Component id (used by callbacks to read ``rowData`` /
        ``virtualRowData`` / ``cellValueChanged``).
    columnDefs : list of dict
        AG Grid column definitions. Defaults to ``[]`` so the layout
        can render before data lands.
    rowData : list of dict
        Initial rows.
    editable : bool
        If True, every column is editable by default and the grid uses
        ``stopEditingWhenCellsLoseFocus``. Override per column via
        ``columnDefs[i]["editable"] = False``.
    height : str
        CSS height. Defaults to fill the viewport below a 200px header.
    grid_options_overrides : dict or None
        Merge into ``dashGridOptions``.
    column_def_overrides : dict or None
        Merge into ``defaultColDef``.

    Returns
    -------
    ``dag.AgGrid`` component.

    Notes
    -----
    Do NOT wrap an editable grid in ``dcc.Loading`` — the spinner
    overlays on every cellClicked callback even when the callback
    returns ``no_update``, producing a 'screen reloads on click' visual
    flash. For initial-load feedback prefer ``skel_sync_overlay``
    (sibling Div with display:none toggle) above the grid.

    For numeric cells, merge ``NUMERIC_COL_DEF`` into your column def
    rather than supplying a custom ``valueParser`` — the
    ``cellDataType: "number"`` route is the built-in path and is
    documented by Plotly.
    """
    dag = _import_dag()
    default_col = (EDITABLE_COL_DEF if editable else DEFAULT_COL_DEF).copy()
    if column_def_overrides:
        default_col.update(column_def_overrides)
    grid_options = (EDITABLE_GRID_OPTIONS if editable else DEFAULT_GRID_OPTIONS).copy()
    if grid_options_overrides:
        grid_options.update(grid_options_overrides)

    return dag.AgGrid(
        id=id,
        columnDefs=columnDefs or [],
        rowData=rowData or [],
        defaultColDef=default_col,
        dashGridOptions=grid_options,
        style={"height": height, "width": "100%"},
        className="ag-theme-alpine",
    )


def register_dirty_tracking(
    app,
    grid_id: str,
    *,
    key_field: str,
    dirty_store_id: str | None = None,
):
    """Wire a dirty-row tracker to an editable AG Grid.

    Each edit captures the row's key field into a ``dcc.Store`` so a
    Save callback can push only changed rows back to the backend.
    Pattern from mapping_app.

    Parameters
    ----------
    app : Dash
    grid_id : str
        ID of the grid (matches ``aspire_grid(id=...)``).
    key_field : str
        Column name that uniquely identifies a row (e.g. ``"sams_mrn"``).
    dirty_store_id : str or None
        ID of the ``dcc.Store`` that holds the dirty-key list. Defaults
        to ``f"{grid_id}-dirty"``. Add this store to your layout::

            dcc.Store(id=f"{grid_id}-dirty", data=[])

    Returns
    -------
    str — the dirty-store id (for convenience).
    """
    store_id = dirty_store_id or f"{grid_id}-dirty"

    @app.callback(
        Output(store_id, "data"),
        Input(grid_id, "cellValueChanged"),
        State(store_id, "data"),
        prevent_initial_call=True,
    )
    def _track_dirty(change, dirty):
        if not change:
            return dirty
        rec = change[0] if isinstance(change, list) else change
        row = rec.get("data") or {}
        key = row.get(key_field)
        if key is None:
            return dirty
        if dirty is None:
            dirty = []
        if key not in dirty:
            dirty.append(key)
        return dirty

    return store_id


# ── Plain dash_table.DataTable wrapper ─────────────────────────────────────

def aspire_datatable(
    id: str,
    data: list[dict] | None = None,
    columns: list[dict] | None = None,
    *,
    page_size: int = 50,
    sort: bool = True,
    filter_: bool = True,
    export: str | None = None,
    style_overrides: dict | None = None,
    totals_row_label: str | None = None,
):
    """Branded ``dash_table.DataTable`` with Aspire-blue headers + zebra rows.

    Use this when AG Grid is overkill — read-only summary tables, modest
    row counts (< 500), no editing.

    Parameters
    ----------
    id : str
        Component id.
    data : list of dict
        Row data (``df.to_dict("records")``).
    columns : list of dict
        Column definitions (``[{"name": "Sport", "id": "sport"}, ...]``).
    page_size : int
        Rows per page (default 50).
    sort : bool
        Enable native sorting.
    filter_ : bool
        Enable native filter row.
    export : str or None
        ``"csv"`` to enable native CSV export; default disabled.
    style_overrides : dict or None
        Merge into the returned style kwargs (advanced — usually you
        want one of the conditional dicts).
    totals_row_label : str or None
        If set, the first-column value matching this label is rendered
        in navy with white text (e.g. ``"TOTAL"`` row).
    """
    from dash import dash_table

    base_style = dict(
        style_cell={
            "padding": "8px 10px",
            "fontFamily": "Inter, sans-serif",
            "fontSize": "13px",
            "textAlign": "left",
        },
        style_header={
            "backgroundColor": ASPIRE_BLUE,
            "color": "white",
            "fontWeight": "700",
            "border": "none",
        },
        style_data_conditional=[
            {"if": {"row_index": "odd"}, "backgroundColor": "#fafbfc"},
        ],
        style_as_list_view=True,
    )

    if totals_row_label:
        # first column is index 0; using filter_query on first column id
        first_id = (columns or [{"id": ""}])[0].get("id", "")
        base_style["style_data_conditional"].append({
            "if": {"filter_query": f'{{{first_id}}} = "{totals_row_label}"'},
            "backgroundColor": ASPIRE_NAVY,
            "color": "white",
            "fontWeight": "700",
        })

    if style_overrides:
        base_style.update(style_overrides)

    kwargs = dict(
        id=id,
        data=data or [],
        columns=columns or [],
        page_size=page_size,
        sort_action="native" if sort else "none",
        filter_action="native" if filter_ else "none",
    )
    if export == "csv":
        kwargs["export_format"] = "csv"
    kwargs.update(base_style)

    return dash_table.DataTable(**kwargs)
