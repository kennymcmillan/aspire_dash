"""In-app help (v0.76, promoted from the Data Explorer app): a side drawer with "How do I…"
answers, grouped example links, pointers + contact; a Help button for the header; and a
first-visit welcome modal remembered per browser. Callbacks via `register_help(app)`.

    from aspire_dash.components import help_drawer, help_button, welcome_modal, register_help
    layout = html.Div([page_layout(sb, header(right_content=help_button()), use_pages=True),
                       help_drawer(sections=[("Find a dataset", "Type a word…")],
                                   examples=[("Squash", "Egyptian men top 30", "datasets?ds=…")]),
                       welcome_modal("Welcome", "One line.", ["Step 1", "Step 2"])])
    register_help(app)
"""
from __future__ import annotations

from dash import html, dcc, Input, Output, State, no_update
import dash_bootstrap_components as dbc

DEFAULT_PREFIX = "help"


def help_button(id_prefix: str = DEFAULT_PREFIX, label: str = "Help"):
    return dbc.Button([html.I(className="fa-solid fa-circle-question me-1"), label],
                      id=f"{id_prefix}-open", color="secondary", outline=True, size="sm",
                      className="ms-2", n_clicks=0)


def help_drawer(sections: list[tuple[str, str]], examples: list[tuple[str, str, str]] | None = None,
                pointers=None, contact: str | None = None, *, title: str = "Help",
                examples_title: str = "Try an example", id_prefix: str = DEFAULT_PREFIX,
                width: str = "420px"):
    """`sections` = [(question, answer)], rendered as a collapsed accordion.
    `examples` = [(group, label, href)] grouped in order of first appearance; hrefs should be
    RELATIVE (no leading slash) so they work under the Connect content path.
    `pointers` = any Dash children shown above the contact line. No backdrop: the page stays usable."""
    steps = dbc.Accordion(
        [dbc.AccordionItem(html.P(text, className="mb-0 small"), title=q) for q, text in sections],
        start_collapsed=True, flush=True, always_open=False, className="mb-3")
    by_group: dict[str, list] = {}
    for group, label, href in examples or []:
        by_group.setdefault(group, []).append(html.Li(html.A(label, href=href, className="small")))
    ex_block = [html.Div([html.Small(g, className="fw-semibold"), html.Ul(items, className="mb-1 ps-3")])
                for g, items in by_group.items()]
    body = [html.H6("How do I…"), steps]
    if ex_block:
        body += [html.H6(examples_title), *ex_block]
    tail = []
    if pointers:
        tail.append(html.Div(pointers, className="small text-muted"))
    if contact:
        tail.append(html.Small(["Something wrong or missing? Email ",
                                html.A(contact, href=f"mailto:{contact}"), "."], className="text-muted"))
    if tail:
        body += [html.Hr(), *tail]
    return dbc.Offcanvas(body, id=f"{id_prefix}-drawer", title=title, placement="end", is_open=False,
                         backdrop=False, scrollable=True, style={"width": width, "maxWidth": "90vw"})


def welcome_modal(title: str, intro: str, steps: list[str], *, footnote: str | None = None,
                  button: str = "Got it", id_prefix: str = DEFAULT_PREFIX):
    """Shown once per browser (local store `<prefix>-welcome-seen`)."""
    return html.Div([
        dcc.Store(id=f"{id_prefix}-welcome-seen", storage_type="local"),
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle(title)),
            dbc.ModalBody([html.P(intro), html.Ol([html.Li(s) for s in steps], className="small"),
                           html.Small(footnote, className="text-muted") if footnote else None]),
            dbc.ModalFooter(dbc.Button(button, id=f"{id_prefix}-welcome-close", color="primary", n_clicks=0)),
        ], id=f"{id_prefix}-welcome", is_open=False, centered=True),
    ])


def register_help(app, id_prefix: str = DEFAULT_PREFIX, *, welcome: bool = True) -> None:
    """Toggle the drawer from the button; show the welcome once. Call after the app exists."""
    @app.callback(Output(f"{id_prefix}-drawer", "is_open"), Input(f"{id_prefix}-open", "n_clicks"),
                  State(f"{id_prefix}-drawer", "is_open"), prevent_initial_call=True)
    def _toggle(n, is_open):
        return not is_open

    if welcome:
        @app.callback(Output(f"{id_prefix}-welcome", "is_open"), Output(f"{id_prefix}-welcome-seen", "data"),
                      Input(f"{id_prefix}-welcome-seen", "data"), Input(f"{id_prefix}-welcome-close", "n_clicks"))
        def _welcome(seen, n_close):
            if n_close:
                return False, True
            if seen:
                return no_update, no_update
            return True, no_update
