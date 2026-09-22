"""Click-to-open test-history modal (v0.90, promoted from endurance-dashboard).

A deliberate click reads cleaner than a hover and works on touch: wrap any metric
card in :func:`history_trigger`, mount one :func:`history_modal` per page, and a
click opens the shared modal holding that metric's :func:`aspire_dash.charts.history_figure`.

The open/close toggle callback is AUTO-REGISTERED on import via Dash's global
callback registry (a bare ``@callback``), so an app needs no ``register_*`` call.
The store carries only the small raw series/params per trigger; the figure is
built on click, so switching athletes does not re-serialise every card's figure.

The modal chrome (aspire-blue header, gold hairline, branded Close button) comes
from the ``.hist-modal*`` / ``.hist-clickable`` classes in ``00_aspire_base.css``.
"""
from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import dcc, html, callback, Input, Output, State, ctx, ALL, no_update

from ..charts import history_figure

__all__ = ["history_trigger", "history_modal"]


def history_trigger(index, inner):
    """Wrap a metric card so a click opens the shared history modal for ``index``.

    ``index`` keys the modal's figure store (see :func:`history_modal`); ``inner``
    is the card content to make clickable."""
    return html.Div(inner, id={"type": "hist-card", "index": str(index)}, n_clicks=0,
                    className="hist-clickable", style={"cursor": "pointer", "height": "100%"})


def history_modal(figures: dict):
    """The shared history modal + its figure store. Mount once per page.

    ``figures`` maps ``str(index)`` -> a record for every trigger on the page::

        {"title": str, "label": str, "unit": str, "series": [(date, value), ...],
         "lower_is_better": bool, "benchmarks": [(label, value), ...]}

    ``series`` and the build params are stored raw; the figure is built on click by
    :func:`aspire_dash.charts.history_figure`."""
    return html.Div([
        dcc.Store(id="hist-fig-store", data=figures or {}),
        dbc.Modal(id="hist-modal", is_open=False, size="xl", centered=True, scrollable=True,
                  className="hist-modal", children=[
            dbc.ModalHeader(dbc.ModalTitle(id="hist-modal-title"), close_button=True),
            dbc.ModalBody(id="hist-modal-body", style={"padding": "20px 24px"}),
            dbc.ModalFooter(dbc.Button("Close", id="hist-modal-close",
                                       className="hist-modal-close-btn", size="sm", n_clicks=0)),
        ]),
    ])


@callback(
    Output("hist-modal", "is_open"),
    Output("hist-modal-title", "children"),
    Output("hist-modal-body", "children"),
    Input({"type": "hist-card", "index": ALL}, "n_clicks"),
    Input("hist-modal-close", "n_clicks"),
    State("hist-fig-store", "data"),
    prevent_initial_call=True,
)
def _history_modal_toggle(card_clicks, _close, store):
    trig = ctx.triggered_id
    if trig == "hist-modal-close":
        return False, no_update, no_update
    # a card was clicked (ignore the initial 0-click registrations)
    if isinstance(trig, dict) and trig.get("type") == "hist-card" and any(card_clicks or []):
        rec = (store or {}).get(trig["index"])
        if rec:
            # Build the figure HERE, on click. The store carries only the small raw
            # series/params, so we don't build + serialise every card's figure on
            # every athlete switch. The aspire-blue header + chrome come from CSS.
            fig = history_figure(rec.get("series") or [], unit=rec.get("unit", ""),
                                 title=rec.get("label"),
                                 lower_is_better=rec.get("lower_is_better", False),
                                 benchmarks=rec.get("benchmarks"), height=400, width=None)
            # r margin widened for the right-margin mean / benchmark labels; shorter
            # height so the modal doesn't need a vertical scroll.
            fig.update_layout(margin=dict(l=66, r=130, t=52, b=78), font=dict(size=14),
                              title=None)
            body = dcc.Graph(figure=fig, config={"displayModeBar": False}, responsive=True,
                             style={"width": "100%", "height": "400px"})
            return True, rec.get("title", "History"), body
    return no_update, no_update, no_update
