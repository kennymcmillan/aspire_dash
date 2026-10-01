"""Chat panel demo against a FAKE local engine (R4 smoke target, checklist 52 slices 1-2).

    python tests/smoke/chat_demo.py [port] [engine_port]   # then open http://127.0.0.1:8765/content/abc/

Two servers, as in production:
  - the FAKE ENGINE (plain Flask, `engine_port`) stands in for the sports-api contract:
      POST /api/agent/ask/stream  SSE: thread, status, token*(text,node), done(answer, agent, tools_used,
                                  usage, suggestions, trace) | error
      POST /api/agent/chips       {"chips": []}  (no "your athletes" memory, so the starters show)
      GET  /_smoke/count          how many streams were started; /_smoke/last_user = last forwarded user_id
  - the DASH APP (`port`) under url_base_pathname=/content/abc/ (a Connect-style prefix) with
    backend="relay" (default): the browser only talks to the app, the app relays to the engine.
      GET  /content/abc/_smoke/audit   the audit events the relay wrote
Question keywords steer the fake: "slow" = 120 ms per token (for Stop), "flaky" = an error event the first
time, a normal answer on Retry.
"""
from __future__ import annotations

import json
import logging
import os
import sys
import threading
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

import dash  # noqa: E402
import dash_bootstrap_components as dbc  # noqa: E402
from flask import Flask, Response, jsonify, request  # noqa: E402
from werkzeug.serving import make_server  # noqa: E402

from aspire_dash.components import chat_panel, register_chat_panel  # noqa: E402

PREFIX = "/content/abc/"
ANSWER = (
    "## Qatar 100m: top 3\n"
    "Here is the *current* picture from the **record** layer.\n\n"
    "| Rank | Athlete | PB | Where | When | Notes |\n"
    "|---|---|---|---|---|---|\n"
    "| 1 | Athlete A | 10.12 | Doha | 2026-05-01 | season best, wind +1.2 |\n"
    "| 2 | Athlete B | 10.31 | Lusail | 2026-04-12 | indoor carry-over |\n"
    "| 3 | Athlete C | 10.40 | Doha | 2026-03-30 | junior |\n\n"
    "1. Gap to the Asian medal line is 0.08 s.\n"
    "2. Next race: Diamond League.\n\n"
    "Source: [World Athletics](https://worldathletics.org/) via `athlete_record`.\n\n"
    "```sql\nSELECT pb FROM records WHERE id = 42;\n```\n"
)
SUGGESTIONS = [
    {"label": "Compare A vs B", "question": "Compare Athlete A and Athlete B", "why": "head to head"},
    {"label": "A's last 5", "question": "Show Athlete A last 5 results", "why": "recent form"},
]
_state = {"count": 0, "flaky_seen": set(), "last_user": None, "bodies": []}
# v0.102.0: every answer carries trace.spans (node rows + nested model/tool calls); "Ali" asks a clarify question
TRACE = {"llm_calls": 1, "llm_ms": 610, "tool_calls": 2, "tool_ms": 330, "tool_errors": 0, "cached_tokens": 900,
         "spans": [{"k": "node", "node": "router", "name": "router", "t": 0, "ms": 45, "err": False},
                   {"k": "node", "node": "athletics_agent", "name": "athletics_agent", "t": 45, "ms": 1010, "err": False},
                   {"k": "llm", "node": "athletics_agent", "name": "gpt-4o-mini", "t": 60, "ms": 610, "err": False,
                    "in": 3200, "out": 240, "cached": 900, "calls": ["athlete_record"]},
                   {"k": "tool", "node": "athletics_agent", "name": "athlete_record", "t": 690, "ms": 210, "err": False},
                   {"k": "tool", "node": "athletics_agent", "name": "athlete_context", "t": 905, "ms": 120, "err": False},
                   {"k": "node", "node": "writer", "name": "writer", "t": 1060, "ms": 90, "err": False}]}
USAGE = {"llm_calls": 1, "input_tokens": 3200, "output_tokens": 240, "cost_usd": 0.0031}
CLARIFY = {"question": "Which sport do you mean for 'Ali': Squash, Padel?", "attr": "sport",
           "options": [{"label": "Squash", "aspire_id": 4242, "sport": "squash", "tracked": True},
                       {"label": "Padel", "aspire_id": None, "sport": "padel", "tracked": False}]}
_lock = threading.Lock()
AUDITS: list[dict] = []
log = logging.getLogger("aspire_dash.chat")


def _sse(obj) -> str:
    return "data: " + json.dumps(obj) + "\n\n"


def build_engine() -> Flask:
    eng = Flask("fake_engine")

    @eng.post("/api/agent/ask/stream")
    def _stream():
        body = request.get_json(force=True) or {}
        q = body.get("question") or ""
        thread = body.get("thread_id") or f"t-{int(time.time() * 1000)}"
        with _lock:
            _state["count"] += 1
            _state["last_user"] = body.get("user_id")
            _state["bodies"].append({k: body.get(k) for k in ("question", "sport", "thread_id")})
        clarify = "ali" in q.lower().split() and "aspire_id" not in q
        delay = 0.12 if "slow" in q.lower() else 0.02
        flaky_first = "flaky" in q.lower() and q not in _state["flaky_seen"]
        if flaky_first:
            _state["flaky_seen"].add(q)

        def gen():
            yield _sse({"type": "thread", "thread_id": thread})
            yield _sse({"type": "status", "text": "athletics_agent: reading the record"})
            if flaky_first:
                time.sleep(0.2)
                yield _sse({"type": "error", "error": "engine timeout (fake)"})
                return
            if clarify:
                time.sleep(0.1)
                yield _sse({"type": "token", "text": CLARIFY["question"], "node": "parameter_finder"})
                yield _sse({"type": "done", "answer": CLARIFY["question"], "agent": "parameter_finder",
                            "tools_used": ["resolve_athlete"], "usage": {"llm_calls": 0},
                            "trace": {"spans": [{"k": "node", "node": "parameter_finder", "name": "parameter_finder",
                                                 "t": 0, "ms": 40, "err": False}]},
                            "clarify": CLARIFY,
                            "suggestions": [{"label": "Squash", "question": "Ali PB (aspire_id 4242)",
                                             "aspire_id": 4242, "sport": "squash"},
                                            {"label": "Padel", "question": "Ali PB (padel)", "sport": "padel"}]})
                return
            for i in range(0, len(ANSWER), 6):
                time.sleep(delay)
                yield _sse({"type": "token", "text": ANSWER[i:i + 6], "node": "athletics_agent"})
            yield _sse({"type": "done", "answer": ANSWER, "agent": "athletics_agent",
                        "tools_used": ["athlete_record", "athlete_context"], "usage": USAGE,
                        "suggestions": SUGGESTIONS, "trace": TRACE})
        return Response(gen(), mimetype="text/event-stream", headers={"Cache-Control": "no-cache"})

    @eng.post("/api/agent/chips")
    def _chips():
        return jsonify({"chips": []})

    @eng.get("/_smoke/count")
    def _count():
        return jsonify({"count": _state["count"], "last_user": _state["last_user"], "bodies": _state["bodies"]})

    return eng


def _audit(event: dict) -> None:
    AUDITS.append(event)
    log.info("chat_audit %s", json.dumps(event, default=str))


def build_app(engine_url: str, backend: str = "relay") -> dash.Dash:
    app = dash.Dash(__name__, assets_folder=os.path.join(ROOT, "aspire_dash", "assets"),
                    external_stylesheets=[dbc.themes.BOOTSTRAP], url_base_pathname=PREFIX)
    app.layout = dbc.Container([
        chat_panel(engine_url=engine_url, id_prefix="demo", height="50vh", backend=backend,
                   starters=["Who are Qatar's top 100m sprinters?", "Latest squash results"]),
    ], fluid=True, className="py-3")
    register_chat_panel(app, id_prefix="demo", backend=backend, engine_url=engine_url, audit=_audit)

    @app.server.get(PREFIX + "_smoke/audit")
    def _audits():
        return jsonify(AUDITS)

    return app


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(name)s %(message)s")
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    eport = int(sys.argv[2]) if len(sys.argv) > 2 else port + 1
    esrv = make_server("127.0.0.1", eport, build_engine(), threaded=True)
    threading.Thread(target=esrv.serve_forever, daemon=True).start()
    build_app(f"http://127.0.0.1:{eport}").run(host="127.0.0.1", port=port, debug=False, threaded=True)
