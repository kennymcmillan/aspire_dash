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


__all__ = ['print_header', 'print_footer', 'export_buttons', 'send_export',
           'a4_report_shell', 'register_print_button', 'safe_markdown_label']

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


# ── A4 Report Shell ─────────────────────────────────────────────────────────

def a4_report_shell(
    title: str,
    body,
    *,
    subtitle: str = "",
    back_href: str = "/",
    back_label: str = "← Back",
    print_button_id: str = "ar-print-btn",
    period_label_id: str = None,
    width: str = "210mm",
    min_height: str = "297mm",
    page_padding: str = "12mm 14mm",
):
    """Standard printable A4 report layout — toolbar + page body.

    Used for per-fencer reports, weekly summaries, monthly briefs, etc.
    A no-print toolbar (Back link + Print button) sits above an A4-sized
    white page with the Aspire title bar and the caller's body content
    inside.

    Wire the Print button with ``register_print_button(app)`` (or attach
    your own ``clientside_callback`` calling ``window.print()``).

    Parameters
    ----------
    title : str
        Header title under the Aspire mark (e.g. "Fencing · Player Report").
    body : Dash component or list
        The page content to render below the header bar.
    subtitle : str
        Smaller pre-title line (defaults to "Aspire Academy").
    back_href : str
        Target of the Back link. Use ``dash.get_relative_path("/overview")``
        when called from within a registered page.
    back_label : str
        Label for the Back link (defaults to ``"← Back"``).
    print_button_id : str
        Component id for the Print button (so callers can register a
        clientside callback to fire window.print()).
    period_label_id : str or None
        Optional id for the period-label span (top-right of the title bar).
        Caller updates via callback. Falls back to a static empty span.
    width, min_height, page_padding : str
        CSS sizing — defaults match A4 portrait.

    Returns
    -------
    ``html.Div`` ready to drop into a page layout.
    """
    period_label_kwargs = (
        {"id": period_label_id} if period_label_id else {}
    )
    return html.Div([
        # Toolbar — hidden when printing
        html.Div([
            dcc.Link(back_label, href=back_href,
                      style={"fontSize": "13px", "color": "#0369a1",
                              "textDecoration": "none",
                              "marginRight": "auto"}),
            html.Button([
                html.I(className="fa-solid fa-print",
                       style={"marginRight": "6px"}),
                "Print / Save PDF",
            ], id=print_button_id, n_clicks=0,
               style={"background": "#004185", "color": "white",
                       "border": "none", "borderRadius": "8px",   # v0.24: canonical
                       "padding": "8px 16px", "fontSize": "13px", # v0.24: on-scale
                       "cursor": "pointer"}),
        ], className="no-print",
           style={"display": "flex", "alignItems": "center",
                   "padding": "12px 20px", "background": "#f7f9fc",  # v0.24: on-scale + BG_PAGE
                   "borderBottom": "1px solid #e2e8f0"}),

        # A4 page
        html.Div([
            # Title strip
            html.Div([
                html.Div([
                    html.I(className="fa-solid fa-medal",
                           style={"color": "white", "fontSize": "14px"}),
                ], style={"background": "#004185", "padding": "8px",   # v0.24: on-scale
                           "borderRadius": "8px",                       # v0.24: canonical
                           "display": "inline-flex",
                           "alignItems": "center"}),
                html.Div([
                    html.Div(subtitle or "Aspire Academy",
                              style={"fontSize": "11px", "color": "#94a3b8",
                                     "textTransform": "uppercase",
                                     "letterSpacing": "0.06em"}),
                    html.Div(title,
                              style={"fontSize": "16px", "fontWeight": 700,
                                     "color": "#0f172a"}),
                ], style={"marginLeft": "10px"}),
                html.Span(**period_label_kwargs,
                          style={"marginLeft": "auto",
                                 "fontSize": "13px", "fontWeight": 600,
                                 "color": "#004185"}),
            ], style={"display": "flex", "alignItems": "center",
                       "borderBottom": "2px solid #004185",
                       "padding": "10px 0", "marginBottom": "14px"}),

            # Body
            body if isinstance(body, list) else [body],
        ], style={"width": width, "minHeight": min_height,
                   "padding": page_padding, "margin": "0 auto",
                   "background": "white",
                   "boxShadow": "0 0 6px rgba(0,0,0,0.08)"}),
    ])


def register_print_button(app, *, button_id: str = "ar-print-btn"):
    """Wire the Print button to ``window.print()`` via clientside callback.

    Call once per app — by default it targets the ``ar-print-btn`` id
    used by ``a4_report_shell``. Pass a different ``button_id`` if you
    customised it.
    """
    app.clientside_callback(
        "function(n) { if (n) { window.print(); } return ''; }",
        Output(button_id, "title"),
        Input(button_id, "n_clicks"),
        prevent_initial_call=True,
    )


def safe_markdown_label(name: str) -> str:
    """Strip ``[]()`` and other markdown-syntactic chars from a string
    before embedding it in a markdown link label.

    Prevents data-driven labels (e.g. a fencer name pulled from an
    upstream API) from breaking the markdown renderer or injecting an
    unintended link target. Use whenever you build markdown via f-string
    on user/external data:

    >>> f"[{safe_markdown_label(name)}](/{id})"
    """
    if name is None:
        return ""
    return (str(name)
            .replace("[", "").replace("]", "")
            .replace("(", "").replace(")", ""))



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


