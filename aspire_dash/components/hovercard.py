"""Rich graph hover cards (v0.90, promoted from endurance-dashboard).

A Power-BI "tooltip page" replacement for Plotly/Dash: hovering a point pops a
branded speech-bubble card (photo, maturation badge, headline metric + change,
extra rows, measured date) driven by Plotly ``hoverData`` -> a ``dcc.Tooltip``.

Reusable by design:
  * :func:`hovercard_graph` pairs a graph with a tooltip and stamps each point's
    card data onto the trace as ``customdata``.
  * ONE MATCH callback renders the card for every graph that uses it, and ONE
    clientside callback flips the card away from screen edges so it never clips.
  * The card data is a self-describing dict (see :func:`render_card`), so the
    generic renderer needs no per-app code; an app just builds the metas.

Both callbacks are AUTO-REGISTERED on import via Dash's global callback registry
(bare ``@callback`` / ``clientside_callback``), so an app needs no ``register_*``
call. The card chrome comes from the ``.hover-card*`` / ``.hovercard-*`` classes
in ``00_aspire_base.css``.
"""
from __future__ import annotations

import json

from dash import (MATCH, Input, Output, callback, clientside_callback, dcc, html,
                  no_update)

from .cards import graph_card

__all__ = ["render_card", "hovercard_graph", "HOVERCARD_ARROW"]

GRAPH = "hovercard-graph"
TIP = "hovercard-tip"

#: Default speech-bubble pointer colour — a subtle on-brand aspire-700 navy
#: (was a soft red in the source). Override per graph via ``arrow_color=``.
HOVERCARD_ARROW = "#003566"


def _delta(delta):
    """Small up/down change chip; None/'' renders nothing."""
    if delta in (None, "", "0", "+0", "-0"):
        return None
    s = str(delta)
    up = not s.startswith("-")
    arrow = "▲" if up else "▼"
    cls = "hc-delta " + ("hc-up" if up else "hc-down")
    return html.Span(f"{arrow} {s.lstrip('+')}", className=cls)


def render_card(meta):
    """Build the hover card from a point's meta dict (or JSON string)::

        {name, photo, mat, mat_tone, date, prev_date,
         headline: {label, value, unit, delta},
         rows: [{label, value, delta}, ...]}
    """
    if isinstance(meta, str):
        meta = json.loads(meta)
    head = meta.get("headline", {})
    photo = meta.get("photo")
    img = (html.Img(src=photo, className="hc-photo")
           if photo else html.Div("", className="hc-photo hc-photo--empty"))
    mat = meta.get("mat")
    rows = [html.Div([html.Span(r["label"], className="hc-row-label"),
                      html.Span(r.get("value", ""), className="hc-row-val"),
                      _delta(r.get("delta"))], className="hc-row")
            for r in meta.get("rows", [])]
    return html.Div([
        html.Div([img, html.Div([
            html.Div(meta.get("name", ""), className="hc-name"),
            (html.Span(mat, className=f"badge {meta.get('mat_tone', 'badge-gray')} hc-mat")
             if mat else None),
        ], className="hc-id")], className="hc-head"),
        html.Div([
            html.Div(head.get("label", ""), className="hc-metric-label"),
            html.Div([html.Span(head.get("value", ""), className="hc-metric-val"),
                      html.Span(head.get("unit", ""), className="hc-metric-unit"),
                      _delta(head.get("delta"))], className="hc-metric-line"),
        ], className="hc-headline"),
        (html.Div(rows, className="hc-rows") if rows else None),
        (html.Div(
            f"Measured {meta['date']}"
            + (f"  ·  vs {meta['prev_date']}" if meta.get("prev_date") else ""),
            className="hc-foot") if meta.get("date") else None),
    ], className="hover-card")


def hovercard_graph(figure, index, metas=None, *, title=None, config=None,
                    selector=None, height=None, arrow_color=None):
    """A graph card whose points show the rich athlete hover card.

    ``metas`` (list aligned to a trace's points) is stamped onto the trace picked by
    ``selector`` (default the lines+markers trace). Pass ``metas=None`` when the
    caller has already set customdata per-trace itself (combo charts with several
    series). ``arrow_color`` sets the speech-bubble pointer colour (defaults to the
    on-brand :data:`HOVERCARD_ARROW` navy).

    The native Plotly hoverlabel is hidden in CSS (``.hovercard-wrap .hoverlayer``)
    so only the card shows, while hover events still fire and drive the card.
    """
    arrow = arrow_color or HOVERCARD_ARROW
    if metas is not None:
        sel = selector if selector is not None else dict(mode="lines+markers")
        figure.update_traces(customdata=metas, selector=sel)
    figure.update_layout(hovermode="closest")
    return html.Div([
        # clear_on_unhover so the card disappears when the cursor leaves a point;
        # direction='bottom' so it opens BELOW the point, clear of the top menu.
        graph_card(figure, config=config, title=title,
                   id={"type": GRAPH, "index": index}, clear_on_unhover=True),
        dcc.Tooltip(id={"type": TIP, "index": index}, className="hovercard-tip",
                    direction="bottom", background_color=arrow,
                    border_color=arrow, zindex=5000, loading_text=""),
    ], className="hovercard-wrap")


@callback(
    Output({"type": TIP, "index": MATCH}, "show"),
    Output({"type": TIP, "index": MATCH}, "bbox"),
    Output({"type": TIP, "index": MATCH}, "children"),
    Input({"type": GRAPH, "index": MATCH}, "hoverData"),
    prevent_initial_call=True,
)
def _show_hovercard(hover):
    if not hover or not hover.get("points"):
        return False, no_update, no_update
    pt = hover["points"][0]
    cd = pt.get("customdata")
    if cd is None:
        return False, no_update, no_update
    return True, pt.get("bbox"), render_card(cd)


# Open the card AWAY from the screen edges so it is never clipped: if the card would
# spill off the right it opens left, off the left it opens right, otherwise below.
# The flip uses the point's position on the SCREEN, not inside its chart (Plotly's
# bbox is chart-relative and these charts sit in a grid), by adding the chart's own
# viewport offset (getBoundingClientRect) onto bbox.x. The flip is the only thing
# keeping the card on screen, so it is hardened to never silently no-op: the chart
# element is resolved by two independent paths, the width is measured from the
# rendered card (falling back to the 256px design width), usable width excludes the
# scrollbar, and a card already past an edge is pulled back as a last resort. A CSS
# max-width belt caps the card at the viewport width too, so it can never be wider
# than the screen even if this JS is unavailable.
clientside_callback(
    """
    function(hoverData) {
        var dc = window.dash_clientside;
        if (!hoverData || !hoverData.points || !hoverData.points.length) return dc.no_update;
        var bb = hoverData.points[0].bbox;
        if (!bb) return 'bottom';

        // Resolve THIS graph's plot element, robustly, to turn the chart-relative bbox
        // into a true on-screen x. prop_id is always present and already IS Dash's
        // stringified id ('{...}.hoverData' -> strip the trailing '.hoverData').
        var plot = null;
        try {
            var ctx = dc.callback_context, domId = null;
            if (ctx && ctx.triggered_id) {
                domId = JSON.stringify(ctx.triggered_id, Object.keys(ctx.triggered_id).sort());
            }
            if (!domId && ctx && ctx.triggered && ctx.triggered.length) {
                var pid = ctx.triggered[0].prop_id, dot = pid.lastIndexOf('.');
                if (dot > 0) domId = pid.slice(0, dot);
            }
            var el = domId ? document.getElementById(domId) : null;
            plot = el && (el.querySelector('.js-plotly-plot')
                          || (el.classList && el.classList.contains('js-plotly-plot') ? el : null));
            if (!plot && ctx && ctx.outputs_list) {   // fallback: via this tooltip's wrap
                var o = Array.isArray(ctx.outputs_list) ? ctx.outputs_list[0] : ctx.outputs_list;
                if (o && o.id) {
                    var tipId = (typeof o.id === 'object')
                        ? JSON.stringify(o.id, Object.keys(o.id).sort()) : o.id;
                    var tip = document.getElementById(tipId);
                    var wrap = tip && tip.closest && tip.closest('.hovercard-wrap');
                    if (wrap) plot = wrap.querySelector('.js-plotly-plot');
                }
            }
        } catch (e) { /* handled by the no-geometry fallback below */ }

        var W = document.documentElement.clientWidth || window.innerWidth;
        var MARGIN = 12;

        // Real half-width of the branded card. It is a fixed-width div, but measure the
        // rendered card when present so the guard self-corrects if the design changes;
        // 256px is the CSS design width used until the first card mounts.
        var card = document.querySelector('.hovercard-tip .hover-card');
        var cardW = (card && card.offsetWidth) || 256;
        var half = cardW / 2 + 8;

        var plotRect = plot ? plot.getBoundingClientRect() : null;
        if (!plotRect) {
            // No geometry: if a card is already rendered and overflowing, pull it to the
            // safe side; otherwise keep the default below-the-point placement.
            if (card) {
                var cr = card.getBoundingClientRect();
                if (cr.right > W - MARGIN) return 'left';
                if (cr.left < MARGIN)      return 'right';
            }
            return 'bottom';
        }

        var cx = plotRect.left + (bb.x0 + bb.x1) / 2;   // point centre in viewport pixels
        if (cx + half > W - MARGIN) return 'left';      // would clip the right edge -> open left
        if (cx - half < MARGIN)     return 'right';     // would clip the left edge  -> open right
        return 'bottom';
    }
    """,
    Output({"type": TIP, "index": MATCH}, "direction"),
    Input({"type": GRAPH, "index": MATCH}, "hoverData"),
    prevent_initial_call=True,
)
