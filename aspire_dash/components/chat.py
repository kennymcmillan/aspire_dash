"""ChatPanel: the Aspire sports chatbot embedded in any Dash app (M7, 2026-08-30).

One import gives an app a working chat page on the LangGraph engine::

    from aspire_dash.components import chat_panel, register_chat_panel
    layout = chat_panel(engine_url="https://qatar-sports-analytics.duckdns.org", sport="athletics",
                        starters=["Who are Qatar's top 5 sprinters?", "Latest squash results"])
    register_chat_panel(app)

Streaming (`POST {engine_url}/api/agent/ask/stream`, Server-Sent Events) is driven CLIENT-SIDE by
`assets/aspire-chat.js` (shipped by `setup_app`), so tokens land as they arrive and the Dash server does no
proxying; the same JS file is the client for React/Next apps (`window.AspireChat.stream(...)`). The done event
carries `answer`, `agent`, `tools_used` and `suggestions` (chips). Thread continuity = `dcc.Store` scoped
`session` (thread_scope="session") or `memory` (per page load). The debug toggle reveals the trace summary.

Server-side callbacks stay pure and small (render chips, trace); everything else is client-side.

v0.100.0 hardening (checklist 52, slice 1): one stream at a time (Enter double-fire refused), Stop button + Esc
(AbortController), Retry on error, Copy answer, delegated chip clicks (Safari-safe), transcript mirrored to
sessionStorage per thread and restored on reload, `starters=[...]` chips + `welcome=` text on an empty chat,
markdown with links/lists/code/scrolling tables, bubble colours from CSS variables (dark-mode safe).

v0.101.0 (checklist 52, slice 2): `backend="relay"` is the DEFAULT. The browser no longer calls the engine:
the JS posts to the app's OWN server (`<requests_pathname_prefix>api/agent/ask/stream`, read from Dash's
`_dash-config`, so it works under Connect's `/content/<guid>/` prefix) and `register_chat_panel` mounts that
route on `app.server`. The relay takes the user from Posit Connect's `RStudio-Connect-Credentials` header
(never from the client), forwards `{question, sport, thread_id, user_id}` to `{engine_url}/api/agent/ask/stream`,
relays the SSE bytes unbuffered and writes one audit event per question. See `chat_relay.py` for identity,
audit fields (username + question text only), the 4000-char cap and the 20/min per-user rate limit.

Backends (pass the same value to `chat_panel` and `register_chat_panel`):
  relay   (default) app server -> engine. `register_chat_panel(app, engine_url=..., audit=..., user_id_source=...)`.
          engine_url defaults to $ASPIRE_CHAT_ENGINE_URL, else the sports-api.
  local   app server runs `handler(question, history, thread_id, user)` in process and streams the event
          dicts it yields ({type: status|token|done|error, ...}); private data (e.g. SAMS) never leaves
          the app. Passing `handler=` alone implies local. history = this thread's last 20 messages
          [{role, text}], kept in app memory. Audit lines carry the username + question text only.
  engine  the old direct mode: the browser POSTs to `chat_panel(engine_url=...)`. Local dev only; no
          identity, no audit.

Adopt (relay)::

    layout = chat_panel(sport="athletics")
    register_chat_panel(app, audit=my_audit)                    # or handler=my_handler for local
"""
from __future__ import annotations

import json
import os

import dash_bootstrap_components as dbc
from dash import ClientsideFunction, Input, Output, State, dcc, html, no_update

from .chat_relay import BACKENDS, register_relay
from .chat_workspace import TAB_LABELS, pane_hidden, render_workspace, tab_labels

SPORTS = ["athletics", "fencing", "swimming", "squash", "padel", "tabletennis"]
DEFAULT_ENGINE_URL = "https://qatar-sports-analytics.duckdns.org"
DEFAULT_WELCOME = ("Ask about any tracked athlete, a ranking or a result. Answers come from the Aspire sports "
                   "database. Press Esc or Stop to cancel a long answer.")


def _ids(prefix: str) -> dict:
    """Every component id the panel uses, from one prefix (two panels on a page = two prefixes)."""
    keys = ["config", "messages", "input", "send", "sport", "thread", "status", "chips", "debug_toggle",
            "debug", "new_chat", "last", "stream_state", "stop",
            # v0.102.0 workspace: turns store, tab bar, the four panes and their bodies
            "turns", "tabs", "pane_answer", "pane_tables", "pane_charts", "pane_trace", "tables", "charts", "trace"]
    return {k: f"{prefix}-{k.replace('_', '-')}" for k in keys}


def _starters(starters) -> list[dict]:
    """Normalise `starters` to suggestion dicts: a str is both label and question; a dict needs `question`
    (or `label`). Anything else is dropped, so a bad list never breaks the layout."""
    out = []
    for s in starters or []:
        if isinstance(s, str) and s.strip():
            out.append({"label": s.strip(), "question": s.strip()})
        elif isinstance(s, dict) and (s.get("question") or s.get("label")):
            q = s.get("question") or s.get("label")
            item = {"label": s.get("label") or q, "question": q}
            if s.get("why"):
                item["why"] = s["why"]
            out.append(item)
    return out


def chat_panel(engine_url: str = DEFAULT_ENGINE_URL, sport: str | None = None, thread_scope: str = "session",
               id_prefix: str = "aspire-chat", title: str = "Ask the sports database", show_sport_picker: bool = True,
               placeholder: str = "Ask about an athlete, a ranking, a result...", height: str = "60vh",
               starters: list | None = None, welcome: str | None = DEFAULT_WELCOME,
               backend: str = "relay", lock_sport: bool = False) -> html.Div:
    """The chat panel layout. `engine_url` = the sports-api base (it proxies to the engine); `sport` pins the
    routing hint (None = the picker decides); `thread_scope` = 'session' (thread + transcript survive reloads in
    this tab) | 'memory'. `starters` = example questions (str or {label, question, why}) shown as chips on an
    empty chat when the engine has no "your athletes" chips; `welcome` = the empty-chat text (None/'' = none).
    `backend` = 'relay' (default) | 'local' (the browser talks to this app's server) | 'engine' (the browser
    talks to `engine_url` directly; local dev only). In relay/local mode `engine_url` is NOT sent to the page.
    `sport` SEEDS the picker (v0.102.0): the user's pick is what gets sent. `lock_sport=True` (with a `sport`)
    pins every question to `sport` and disables the picker; before 0.102.0 a `sport` always locked it."""
    if backend not in BACKENDS:
        raise ValueError(f"backend must be one of {BACKENDS}, not {backend!r}")
    from .inputs import aspire_tabs
    ids = _ids(id_prefix)
    storage = "session" if thread_scope == "session" else "memory"
    starter_list = _starters(starters)
    tab_bar = aspire_tabs(ids["tabs"], [{"label": lab, "value": v} for v, lab in TAB_LABELS], "answer")
    tab_bar.mobile_breakpoint = 0     # dcc.Tabs stacks vertically under 800px by default; keep one row on phones
    config = {"backend": backend, "engine_url": engine_url.rstrip("/") if backend == "engine" else "", "sport": sport, "prefix": id_prefix,
              "thread_scope": storage, "starters": starter_list, "welcome": welcome or "",
              "lock_sport": bool(lock_sport and sport)}
    return html.Div([
        dcc.Store(id=ids["config"], data=config),
        dcc.Store(id=ids["thread"], storage_type=storage, data=None),
        dcc.Store(id=ids["last"], data=None),           # the last done event (answer, agent, tools_used, suggestions)
        dcc.Store(id=ids["stream_state"], data=None),   # 'streaming' | 'idle' (drives the send button)
        # v0.102.0: this thread's finished turns {turns: [{q, answer, agent, tools_used, usage, trace, clarify, ms}],
        # sel}, written by aspire-chat.js (set_props) and restored from sessionStorage on load
        dcc.Store(id=ids["turns"], data=None),
        dbc.Card([
            dbc.CardHeader(html.Div([
                html.Span(title, className="fw-semibold"),
                html.Div([
                    # 44px-class controls (the R4 smoke floor measures tap targets on mobile)
                    dbc.Select(id=ids["sport"], options=[{"label": s.title(), "value": s} for s in SPORTS],
                               value=sport or "athletics", className="aspire-chat-sport",
                               disabled=bool(lock_sport and sport),
                               ) if show_sport_picker else html.Div(id=ids["sport"], hidden=True),
                    # icon + label; on phones (<576px) the label hides and a 44px square icon button stays,
                    # so the header controls sit on one row at 390px (slice-2 review fix)
                    dbc.Button([html.Span("+", className="aspire-chat-icon", **{"aria-hidden": "true"}),
                                html.Span("New chat", className="aspire-chat-btn-label")],
                               id=ids["new_chat"], outline=True, color="secondary", className="aspire-chat-hbtn",
                               title="New chat"),
                    dbc.Button([html.Span("\u2261", className="aspire-chat-icon", **{"aria-hidden": "true"}),
                                html.Span("Trace", className="aspire-chat-btn-label")],
                               id=ids["debug_toggle"], outline=True, color="secondary", n_clicks=0,
                               className="aspire-chat-hbtn", title="Trace: the agent, tools and usage behind the last answer"),
                ], className="aspire-chat-controls d-flex align-items-center flex-nowrap gap-2"),
            ], className="aspire-chat-header d-flex justify-content-between align-items-center flex-wrap gap-2")),
            dbc.CardBody([
                # v0.102.0: Answer / Tables / Charts / Trace. The tab bar is the library's aspire_tabs; panes are
                # siblings toggled by `hidden`, so the JS-owned message list is never unmounted.
                tab_bar,
                html.Div([
                    # aspire-chat.js owns this node's children (bubbles); no Dash callback writes to it
                    html.Div(id=ids["messages"], className="aspire-chat-messages", role="log", **{"aria-live": "polite"},
                             style={"height": height, "overflowY": "auto", "padding": "4px"}),
                    html.Div(chips_from_done({"suggestions": starter_list}), id=ids["chips"],
                             className="aspire-chat-chips d-flex flex-wrap gap-2 my-2"),
                ], id=ids["pane_answer"], className="aspire-chat-pane", role="tabpanel"),
                html.Div(html.Div(id=ids["tables"], className="aspire-chat-cards"), id=ids["pane_tables"], hidden=True,
                         className="aspire-chat-pane aspire-chat-pane--scroll", role="tabpanel", style={"height": height}),
                html.Div(html.Div(id=ids["charts"], className="aspire-chat-cards"), id=ids["pane_charts"], hidden=True,
                         className="aspire-chat-pane aspire-chat-pane--scroll", role="tabpanel", style={"height": height}),
                html.Div([
                    html.Div(id=ids["trace"]),
                    html.Details([html.Summary("Raw trace (JSON)"),
                                  html.Pre(id=ids["debug"], className="small mt-2 p-2 border rounded aspire-chat-debug",
                                           style={"whiteSpace": "pre-wrap", "maxHeight": "200px", "overflowY": "auto"})],
                                 className="aspire-chat-raw mt-2"),
                ], id=ids["pane_trace"], hidden=True, className="aspire-chat-pane aspire-chat-pane--scroll",
                    role="tabpanel", style={"height": height}),
                html.Div(id=ids["status"], className="text-muted small my-2", style={"minHeight": "1.2em"}),
                dbc.InputGroup([
                    dbc.Input(id=ids["input"], placeholder=placeholder, type="text", debounce=False, n_submit=0,
                              autoComplete="off"),
                    dbc.Button("Send", id=ids["send"], color="primary", n_clicks=0, style={"minHeight": "44px"}),
                    # shown only while streaming (aspire-chat.js); handled by the delegated click listener
                    html.Button("Stop", id=ids["stop"], type="button", hidden=True, title="Stop the answer (Esc)",
                                className="btn btn-outline-secondary aspire-chat-stop", **{"data-action": "stop"}),
                ], className="aspire-chat-inputbar"),
            ]),
        ], className="aspire-chat-panel"),
    ], className="aspire-chat", **{"data-prefix": id_prefix})


def clarify_reply(option: dict) -> str:
    """The text a clarify option sends back on the same thread. The engine binds a reply to its pending
    clarification by `aspire_id N` first (exact candidate), else by the option label, so a tracked option sends
    both and an untracked one sends its label."""
    label = str(option.get("label") or "").strip()
    aid = option.get("aspire_id")
    return f"{label} (aspire_id {aid})" if aid else label


def _chip(label, question, *, why=None, sport=None, aspire_id=None, kind="suggestion"):
    # html.Button (not dbc.Button): it accepts data-* attributes, which the delegated JS click handler reads
    attrs = {"data-question": question}
    if sport:
        attrs["data-sport"] = str(sport)          # the JS sends it as this turn's sport (unless lock_sport)
    if aspire_id:
        attrs["data-aspire-id"] = str(aspire_id)
    cls = "btn btn-sm aspire-chat-chip " + ("btn-primary aspire-chat-chip--clarify" if kind == "clarify"
                                            else "btn-outline-primary")
    return html.Button(label, type="button", title=why or question, className=cls, **attrs)


def chips_from_done(done: dict | None) -> list:
    """Pure: the chips under the conversation from a done event or a JSON-door reply.

    `clarify: {question, attr, options: [{label, aspire_id, sport}]}` (v0.102.0) renders first as a block: the
    engine's question and one primary button per option (max 8) that replies with `clarify_reply(option)` on the
    same thread, carrying the option's sport. Then `suggestions: [{label, question, why, aspire_id?, sport?}]`,
    max 4, minus any that repeat a clarify option (the engine also sends each option as a suggestion)."""
    done = done or {}
    out, seen = [], set()
    cl = done.get("clarify") if isinstance(done.get("clarify"), dict) else None
    opts = [o for o in ((cl or {}).get("options") or []) if isinstance(o, dict) and o.get("label")][:8]
    if cl and opts:
        buttons = []
        for o in opts:
            seen.add(("id", str(o["aspire_id"])) if o.get("aspire_id") else ("label", o["label"].strip().lower()))
            buttons.append(_chip(o["label"], clarify_reply(o), sport=o.get("sport"), aspire_id=o.get("aspire_id"),
                                 kind="clarify"))
        out.append(html.Div([html.Div(cl.get("question") or "Which one do you mean?", className="aspire-chat-clarify-q")]
                            + buttons, className="aspire-chat-clarify", role="group",
                            **{"aria-label": cl.get("question") or "Clarify"}))
    n = 0
    for s in done.get("suggestions") or []:
        if not isinstance(s, dict):
            continue
        q = s.get("question") or s.get("label")
        if not q:
            continue
        if (("id", str(s["aspire_id"])) if s.get("aspire_id") else ("label", str(s.get("label") or "").strip().lower())) in seen:
            continue
        out.append(_chip(s.get("label") or q, q, why=s.get("why"), sport=s.get("sport"), aspire_id=s.get("aspire_id")))
        n += 1
        if n >= 4:
            break
    return out


def trace_text(done: dict | None) -> str:
    """Pure: the debug trace line for the last answer."""
    if not done:
        return ""
    keep = {k: done.get(k) for k in ("agent", "tools_used", "usage", "thread_id", "trace") if done.get(k) is not None}
    return json.dumps(keep, indent=1, ensure_ascii=False)[:4000] if keep else ""


def register_chat_panel(app, id_prefix: str = "aspire-chat", *, backend: str | None = None,
                        engine_url: str | None = None, handler=None, user_id_source=None, audit=None,
                        rate_limit: int = 20) -> None:
    """Wire the panel: send, init (transcript restore + chips) and new-chat are CLIENTSIDE callbacks
    (assets/aspire-chat.js, namespace `aspire_chat`); chip, Stop, Retry and Copy clicks are one delegated JS
    listener; the chips + trace render and the debug toggle are server-side and pure.

    backend: 'relay' (default; 'local' when `handler` is given) mounts the relay routes on `app.server`
    (chat_relay.register_relay, once per app); 'engine' mounts nothing. `user_id_source()` -> str|None
    overrides the Connect header read; `audit(event)` overrides the default log line; `rate_limit` =
    questions per user per minute."""
    backend = backend or ("local" if handler is not None else "relay")
    if backend not in BACKENDS:
        raise ValueError(f"backend must be one of {BACKENDS}, not {backend!r}")
    if backend != "engine":
        register_relay(app, backend=backend, handler=handler, user_id_source=user_id_source, audit=audit,
                       rate_limit=rate_limit,
                       engine_url=engine_url or os.environ.get("ASPIRE_CHAT_ENGINE_URL") or DEFAULT_ENGINE_URL)
    ids = _ids(id_prefix)

    # send refuses while a stream is in flight; on accept it clears the input VALUE prop (not just the DOM),
    # so a second Enter cannot re-send the stale question
    app.clientside_callback(
        ClientsideFunction(namespace="aspire_chat", function_name="send"),
        Output(ids["stream_state"], "data"),
        Output(ids["input"], "value"),
        Input(ids["send"], "n_clicks"),
        Input(ids["input"], "n_submit"),
        State(ids["input"], "value"),
        State(ids["sport"], "value"),
        State(ids["thread"], "data"),
        State(ids["config"], "data"),
        prevent_initial_call=True,
    )
    # on load: restore the transcript from sessionStorage, else welcome + M4 "your athletes" chips
    # (POST /api/agent/chips) over the starters
    app.clientside_callback(
        ClientsideFunction(namespace="aspire_chat", function_name="init"),
        Output(ids["stream_state"], "data", allow_duplicate=True),
        Input(ids["config"], "data"),
        State(ids["thread"], "data"),
        prevent_initial_call="initial_duplicate",
    )
    # New chat: abort any stream, drop the stored transcript, reset the thread, starters back as chips
    app.clientside_callback(
        ClientsideFunction(namespace="aspire_chat", function_name="new_chat"),
        Output(ids["thread"], "data"),
        Output(ids["last"], "data"),
        Input(ids["new_chat"], "n_clicks"),
        State(ids["config"], "data"),
        prevent_initial_call=True,
    )

    @app.callback(Output(ids["chips"], "children"), Output(ids["debug"], "children"),
                  Input(ids["last"], "data"), prevent_initial_call=True)
    def _on_done(done):
        # dcc.Store fires data=None on mount: keep the server-rendered starters instead of wiping them
        if done is None:
            return no_update, ""
        return chips_from_done(done), trace_text(done)

    # v0.102.0 workspace. Panes: one Output per pane `hidden` (+ the raw-trace Pre, kept for pre-0.102 callers).
    @app.callback(Output(ids["pane_answer"], "hidden"), Output(ids["pane_tables"], "hidden"),
                  Output(ids["pane_charts"], "hidden"), Output(ids["pane_trace"], "hidden"),
                  Output(ids["debug"], "hidden"), Input(ids["tabs"], "value"))
    def _panes(value):
        hide = pane_hidden(value)
        return (*hide, hide[3])

    # the header Trace button flips between the Trace tab and the conversation
    @app.callback(Output(ids["tabs"], "value"), Input(ids["debug_toggle"], "n_clicks"), State(ids["tabs"], "value"),
                  prevent_initial_call=True)
    def _trace_button(n, current):
        return "answer" if current == "trace" else "trace"

    # finished turns -> Tables (aspire_dash data_table + medal badges), Charts, the Trace waterfall, tab counts
    @app.callback(Output(ids["tables"], "children"), Output(ids["charts"], "children"),
                  Output(ids["trace"], "children"), Output(ids["tabs"], "children"), Input(ids["turns"], "data"))
    def _workspace(data):
        from .inputs import aspire_tabs
        tables, charts, trace, counts = render_workspace(data)
        labels = tab_labels(counts)
        tabs = aspire_tabs("_", [{"label": lab, "value": v} for lab, (v, _) in zip(labels, TAB_LABELS)]).children
        return tables, charts, trace, tabs
