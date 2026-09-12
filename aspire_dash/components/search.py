"""Search box + clickable hit list (v0.76, promoted from the Data Explorer app).

The UI half of a search: a debounced input, a results container, and one builder for a hit
row that carries a pattern id `{"type": "<prefix>-hit", "key": <key>}` so ONE callback handles
clicks from search results and from any other list that reuses `search_hit` (recents, examples).

    from aspire_dash.components import search_box, search_hit, hit_list, search_hit_id
    layout: search_box("ds", "Search datasets (e.g. ranking, wind, dob)")
    results callback: return hit_list([search_hit("ds", d.key, d.label, badges=[("Squash", "light"), ("Public", "success")], why="column: dob") ...])
    click callback: Input(search_hit_id("ds"), "n_clicks") with ALL; trig = ctx.triggered_id["key"]

Tip: pattern callbacks also fire when hits are (re)rendered; only treat it as a click when
`ctx.triggered[0]["value"]` is truthy.
"""
from __future__ import annotations

from dash import html, ALL
import dash_bootstrap_components as dbc


def search_box(id_prefix: str, placeholder: str = "Search…", *, debounce: bool = True):
    return html.Div([
        dbc.Input(id=f"{id_prefix}-search", type="search", debounce=debounce, placeholder=placeholder),
        html.Div(id=f"{id_prefix}-search-results", className="mt-1"),
    ])


def search_hit_id(id_prefix: str) -> dict:
    """The pattern id to use as an Input with ALL."""
    return {"type": f"{id_prefix}-hit", "key": ALL}


def search_hit(id_prefix: str, key: str, label: str, *, badges: list[tuple[str, str]] | None = None,
               why: str | None = None):
    """One clickable row. `badges` = [(text, bootstrap colour)]; light colours get dark text."""
    body = [html.Span(label, className="fw-semibold me-2")]
    for text, color in badges or []:
        body.append(dbc.Badge(text, color=color, text_color="dark" if color in ("light", "warning", "info") else None,
                              className="me-1"))
    if why:
        body.append(html.Small(why, className="text-muted ms-1"))
    return dbc.ListGroupItem(body, id={"type": f"{id_prefix}-hit", "key": key}, action=True,
                             n_clicks=0, className="py-1")


def hit_list(items: list, *, empty_text: str | None = None):
    if not items:
        return html.Small(empty_text, className="text-muted") if empty_text else ""
    return dbc.ListGroup(items, flush=True, className="border rounded")
