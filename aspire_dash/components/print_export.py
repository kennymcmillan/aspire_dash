"""Print + export: print_header, print_footer, export_buttons, send_export.

Auto-split from the legacy single-file components.py during the
0.8 → 1.0 refactor. Backwards-compatible: `from aspire_dash.components
import X` keeps working via the package __init__.
"""
import dash
from dash import html, dcc, clientside_callback, Input, Output, State
import dash_bootstrap_components as dbc

from ..theme import (
    SIDEBAR_WIDTH, SIDEBAR_BG, SIDEBAR_BORDER, SIDEBAR_LINK_COLOR,
    SIDEBAR_LINK_HOVER_BG, SIDEBAR_LINK_ACTIVE_BG,
    FONT_FAMILY, ACCENT, ACCENT_HOVER,
    LOGO_FILENAME, LOGO_ALT, SLATE, ASPIRE,
    SHADOW_SM, SHADOW_MD, RADIUS_LG, RADIUS_FULL,
)


__all__ = ['print_header', 'print_footer', 'export_buttons', 'send_export']

# ── Print Header/Footer ─────────────────────────────────────────────────────

def print_header(title="", subtitle="", logo_src="/assets/aspire-logo.png"):
    """Header shown only when printing — hidden on screen."""
    return html.Div([
        html.Div([
            html.Img(src=logo_src, style={"height": "24px"}),
            html.Span(title, style={"fontWeight": "700", "fontSize": "14px", "marginLeft": "8px"}),
        ], style={"display": "flex", "alignItems": "center"}),
        html.Span(subtitle, style={"fontSize": "11px", "color": SLATE["500"]}),
    ], className="print-header")


def print_footer(text="Aspire Academy — Confidential"):
    """Footer shown only when printing — hidden on screen."""
    return html.Div(text, className="print-footer")



# ── Export Buttons ──────────────────────────────────────────────────────────

def export_buttons(export_id="data-export", csv=True, excel=True, style=None):
    """CSV/Excel export buttons with a shared dcc.Download.

    Parameters
    ----------
    export_id : str
        Base ID. Buttons get ``{export_id}-csv`` and ``{export_id}-xlsx``;
        the Download component gets ``{export_id}-download``.
    csv : bool
        Show the CSV button (default True).
    excel : bool
        Show the Excel button (default True).
    style : dict or None
        Extra style for the container div.

    Returns
    -------
    html.Div containing the buttons and a dcc.Download.

    Usage
    -----
    Layout::

        from aspire_dash.components import export_buttons, register_export_callback

        html.Div([
            html.H3("My Table"),
            export_buttons("my-export"),
        ])

    Then in your callbacks module::

        register_export_callback("my-export", app)

    And define a callback that builds the DataFrame::

        @callback(
            Output("my-export-download", "data"),
            Input("my-export-csv", "n_clicks"),
            Input("my-export-xlsx", "n_clicks"),
            ...
        )
        def do_export(csv_clicks, xlsx_clicks, ...):
            return send_export(ctx.triggered_id, df, "filename")
    """
    container_style = {"display": "flex", "gap": "8px"}
    if style:
        container_style.update(style)

    children = []
    if csv:
        children.append(html.Button(
            [html.I(className="fa-solid fa-file-csv", style={"marginRight": "6px"}), "CSV"],
            id=f"{export_id}-csv", className="btn-outline", n_clicks=0,
            style={"fontSize": "12px", "padding": "4px 12px"},
        ))
    if excel:
        children.append(html.Button(
            [html.I(className="fa-solid fa-file-excel", style={"marginRight": "6px"}), "Excel"],
            id=f"{export_id}-xlsx", className="btn-outline", n_clicks=0,
            style={"fontSize": "12px", "padding": "4px 12px"},
        ))
    children.append(dcc.Download(id=f"{export_id}-download"))

    return html.Div(children, style=container_style)


def send_export(triggered_id, df, filename_base, sheet_name="Sheet1"):
    """Build a dcc.Download-compatible dict for CSV or Excel.

    Parameters
    ----------
    triggered_id : str
        The ``ctx.triggered_id`` — must end with ``-csv`` or ``-xlsx``.
    df : pandas.DataFrame
        Data to export.
    filename_base : str
        Filename without extension (e.g. ``"cpet_data_time"``).
    sheet_name : str
        Excel sheet name (default ``"Sheet1"``).

    Returns
    -------
    dict suitable for assigning to ``dcc.Download.data``.
    """
    if triggered_id and triggered_id.endswith("-csv"):
        return dict(content=df.to_csv(index=False), filename=f"{filename_base}.csv")

    # Excel
    import io
    import base64
    buf = io.BytesIO()
    df.to_excel(buf, index=False, sheet_name=sheet_name)
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode()
    return dict(content=encoded, filename=f"{filename_base}.xlsx", base64=True)


