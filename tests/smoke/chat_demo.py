"""Chat panel demo against a FAKE local engine (R4 smoke target, checklist 52 slice 1).

    python tests/smoke/chat_demo.py [port]      # then open http://127.0.0.1:8765

The Flask routes below stand in for the sports-api engine contract:
  POST /api/agent/ask/stream  SSE: thread, status, token*(text,node), done(answer, agent, tools_used,
                              usage, suggestions, trace) | error
  POST /api/agent/chips       {"chips": []}  (no "your athletes" memory, so the starters show)
Question keywords steer the fake: "slow" = 120 ms per token (for Stop), "flaky" = an error event the first
time, a normal answer on Retry. GET /_smoke/count returns how many streams were started.
"""
from __future__ import annotations

import json
import os
import sys
import threading
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

import dash  # noqa: E402
import dash_bootstrap_components as dbc  # noqa: E402
from flask import Response, jsonify, request  # noqa: E402

from aspire_dash.components import chat_panel, register_chat_panel  # noqa: E402

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
_state = {"count": 0, "flaky_seen": set()}
_lock = threading.Lock()


def _sse(obj) -> str:
    return "data: " + json.dumps(obj) + "\n\n"


def build_app() -> dash.Dash:
    app = dash.Dash(__name__, assets_folder=os.path.join(ROOT, "aspire_dash", "assets"),
                    external_stylesheets=[dbc.themes.BOOTSTRAP])
    port = int(os.environ.get("CHAT_DEMO_PORT", "8765"))
    app.layout = dbc.Container([
        chat_panel(engine_url=f"http://127.0.0.1:{port}", id_prefix="demo", height="50vh",
                   starters=["Who are Qatar's top 100m sprinters?", "Latest squash results"]),
    ], fluid=True, className="py-3")
    register_chat_panel(app, id_prefix="demo")
    server = app.server

    @server.post("/api/agent/ask/stream")
    def _stream():
        body = request.get_json(force=True) or {}
        q = body.get("question") or ""
        thread = body.get("thread_id") or f"t-{int(time.time() * 1000)}"
        with _lock:
            _state["count"] += 1
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
            for i in range(0, len(ANSWER), 6):
                time.sleep(delay)
                yield _sse({"type": "token", "text": ANSWER[i:i + 6], "node": "athletics_agent"})
            yield _sse({"type": "done", "answer": ANSWER, "agent": "athletics_agent",
                        "tools_used": ["athlete_record"], "usage": {"in": 10, "out": 20},
                        "suggestions": SUGGESTIONS, "trace": {"ms": 123}})
        return Response(gen(), mimetype="text/event-stream", headers={"Cache-Control": "no-cache"})

    @server.post("/api/agent/chips")
    def _chips():
        return jsonify({"chips": []})

    @server.get("/_smoke/count")
    def _count():
        return jsonify({"count": _state["count"]})

    return app


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    os.environ["CHAT_DEMO_PORT"] = str(port)
    build_app().run(host="127.0.0.1", port=port, debug=False, threaded=True)
