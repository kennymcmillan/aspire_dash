"""ChatPanel: the Aspire sports chatbot embedded in any Dash app (M7, 2026-08-30).

One import gives an app a working chat page on the LangGraph engine::

    from aspire_dash.components import chat_panel, register_chat_panel
    layout = chat_panel(engine_url="https://qatar-sports-analytics.duckdns.org", sport="athletics")
    register_chat_panel(app)

Streaming (`POST {engine_url}/api/agent/ask/stream`, Server-Sent Events) is driven CLIENT-SIDE by
`assets/aspire-chat.js` (shipped by `setup_app`), so tokens land as they arrive and the Dash server does no
proxying; the same JS file is the client for React/Next apps (`window.AspireChat.stream(...)`). The done event
carries `answer`, `agent`, `tools_used` and `suggestions` (chips). Thread continuity = `dcc.Store` scoped
`session` (thread_scope="session") or `memory` (per page load). The debug toggle reveals the trace summary.

Server-side callbacks stay pure and small (render chips, reset the thread); everything else is client-side.
"""
from __future__ import annotations

import json

import dash_bootstrap_components as dbc
from dash import ClientsideFunction, Input, Output, State, dcc, html

SPORTS = ["athletics", "fencing", "swimming", "squash", "padel", "tabletennis"]
DEFAULT_ENGINE_URL = "https://qatar-sports-analytics.duckdns.org"


def _ids(prefix: str) -> dict:
    """Every component id the panel uses, from one prefix (two panels on a page = two prefixes)."""
    keys = ["config", "messages", "input", "send", "sport", "thread", "status", "chips", "debug_toggle",
            "debug", "new_chat", "last", "stream_state"]
    return {k: f"{prefix}-{k.replace('_', '-')}" for k in keys}


def chat_panel(engine_url: str = DEFAULT_ENGINE_URL, sport: str | None = None, thread_scope: str = "session",
               id_prefix: str = "aspire-chat", title: str = "Ask the sports database", show_sport_picker: bool = True,
               placeholder: str = "Ask about an athlete, a ranking, a result...", height: str = "60vh") -> html.Div:
    """The chat panel layout. `engine_url` = the sports-api base (it proxies to the engine); `sport` pins the
    routing hint (None = the picker decides); `thread_scope` = 'session' (survives reloads in this tab) | 'memory'."""
    ids = _ids(id_prefix)
    storage = "session" if thread_scope == "session" else "memory"
    config = {"engine_url": engine_url.rstrip("/"), "sport": sport, "prefix": id_prefix}
    return html.Div([
        dcc.Store(id=ids["config"], data=config),
        dcc.Store(id=ids["thread"], storage_type=storage, data=None),
        dcc.Store(id=ids["last"], data=None),           # the last done event (answer, agent, tools_used, suggestions)
        dcc.Store(id=ids["stream_state"], data=None),   # 'streaming' | 'idle' (drives the send button)
        dbc.Card([
            dbc.CardHeader(html.Div([
                html.Span(title, className="fw-semibold"),
                html.Div([
                    # 44px-class controls (the R4 smoke floor measures tap targets on mobile)
                    dbc.Select(id=ids["sport"], options=[{"label": s.title(), "value": s} for s in SPORTS],
                               value=sport or "athletics", style={"width": "160px", "minHeight": "44px"},
                               className="me-2") if show_sport_picker else html.Div(id=ids["sport"], hidden=True),
                    dbc.Button("New chat", id=ids["new_chat"], outline=True, color="secondary", className="me-2",
                               style={"minHeight": "44px"}),
                    dbc.Button("Trace", id=ids["debug_toggle"], outline=True, color="secondary", n_clicks=0,
                               style={"minHeight": "44px"}, title="Show the agent, tools and usage behind the last answer"),
                ], className="d-flex align-items-center flex-wrap gap-1"),
            ], className="d-flex justify-content-between align-items-center flex-wrap gap-2")),
            dbc.CardBody([
                html.Div(id=ids["messages"], className="aspire-chat-messages",
                         style={"height": height, "overflowY": "auto", "padding": "4px"}),
                html.Div(id=ids["chips"], className="aspire-chat-chips d-flex flex-wrap gap-2 my-2"),
                html.Div(id=ids["status"], className="text-muted small mb-2", style={"minHeight": "1.2em"}),
                dbc.InputGroup([
                    dbc.Input(id=ids["input"], placeholder=placeholder, type="text", debounce=False, n_submit=0,
                              autoComplete="off"),
                    dbc.Button("Send", id=ids["send"], color="primary", n_clicks=0, style={"minHeight": "44px"}),
                ]),
                html.Pre(id=ids["debug"], className="small mt-2 p-2 bg-light border rounded", hidden=True,
                         style={"whiteSpace": "pre-wrap", "maxHeight": "200px", "overflowY": "auto"}),
            ]),
        ], className="aspire-chat-panel"),
    ], className="aspire-chat", **{"data-prefix": id_prefix})


def chips_from_done(done: dict | None) -> list:
    """Pure: suggestion chips from a done event (`suggestions: [{label, question, why}]`), max 4."""
    out = []
    for s in (done or {}).get("suggestions") or []:
        q = s.get("question") or s.get("label")
        if not q:
            continue
        # html.Button (not dbc.Button): it accepts data-* attributes, which the client-side chip handler reads
        out.append(html.Button(s.get("label") or q, type="button", title=s.get("why") or q,
                               className="btn btn-sm btn-outline-primary aspire-chat-chip", **{"data-question": q}))
        if len(out) >= 4:
            break
    return out


def trace_text(done: dict | None) -> str:
    """Pure: the debug trace line for the last answer."""
    if not done:
        return ""
    keep = {k: done.get(k) for k in ("agent", "tools_used", "usage", "thread_id", "trace") if done.get(k) is not None}
    return json.dumps(keep, indent=1, ensure_ascii=False)[:4000]


def register_chat_panel(app, id_prefix: str = "aspire-chat") -> None:
    """Wire the panel: the send/stream path is a CLIENTSIDE callback (assets/aspire-chat.js, namespace
    `aspire_chat`), the chips, trace and new-chat paths are server-side and pure."""
    ids = _ids(id_prefix)

    app.clientside_callback(
        ClientsideFunction(namespace="aspire_chat", function_name="send"),
        Output(ids["stream_state"], "data"),
        Input(ids["send"], "n_clicks"),
        Input(ids["input"], "n_submit"),
        State(ids["input"], "value"),
        State(ids["sport"], "value"),
        State(ids["thread"], "data"),
        State(ids["config"], "data"),
        prevent_initial_call=True,
    )
    app.clientside_callback(
        ClientsideFunction(namespace="aspire_chat", function_name="chip_click"),
        Output(ids["input"], "value"),
        Input(ids["chips"], "n_clicks"),
        State(ids["config"], "data"),
        prevent_initial_call=True,
    )

    @app.callback(Output(ids["chips"], "children"), Output(ids["debug"], "children"),
                  Input(ids["last"], "data"), prevent_initial_call=True)
    def _on_done(done):
        return chips_from_done(done), trace_text(done)

    @app.callback(Output(ids["debug"], "hidden"), Input(ids["debug_toggle"], "n_clicks"))
    def _toggle_debug(n):
        return not bool((n or 0) % 2)   # odd click = shown

    @app.callback(Output(ids["thread"], "data"), Output(ids["messages"], "children"),
                  Output(ids["chips"], "children", allow_duplicate=True),
                  Input(ids["new_chat"], "n_clicks"), prevent_initial_call=True)
    def _new_chat(_n):
        return None, [], []
