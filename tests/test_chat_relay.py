"""Relay + local backend for the chat panel (checklist 52, slice 2, v0.101.0)."""
from __future__ import annotations

import json
import threading

import dash
import pytest
from flask import Flask, Response, request
from werkzeug.serving import make_server

from aspire_dash.components import chat_panel, register_chat_panel
from aspire_dash.components.chat_relay import RateLimiter, _DoneSniffer

DONE = {"type": "done", "answer": "Hi", "agent": "athletics_agent", "tools_used": ["athlete_record"]}
CREDS = {"RStudio-Connect-Credentials": json.dumps({"user": "kenny", "groups": ["sport-science"]})}


def sse(o):
    return ("data: " + json.dumps(o) + "\n\n").encode()


def events(raw: bytes):
    return [json.loads(p[5:].strip()) for p in raw.decode().split("\n\n") if p.strip().startswith("data:")]


class FakeUpstream:
    """Stands in for the engine: records each forwarded call, yields scripted SSE chunks."""

    def __init__(self, chunks=None, gate=None):
        self.calls = []
        self.chunks = chunks if chunks is not None else [sse({"type": "thread", "thread_id": "t1"}),
                                                         sse({"type": "token", "text": "Hi"}), sse(DONE)]
        self.gate = gate

    def __call__(self, url, body, timeout):
        self.calls.append((url, body))
        for i, c in enumerate(self.chunks):
            if i == 1 and self.gate is not None:
                assert self.gate.wait(5), "gate never opened"
            yield c


def make_app(prefix=None, url_base=None, **kw):
    args = {}
    if url_base:
        args["url_base_pathname"] = url_base
    if prefix:
        args["requests_pathname_prefix"] = prefix
        args["routes_pathname_prefix"] = "/"
    app = dash.Dash(__name__, **args)
    app.layout = chat_panel(id_prefix="r1", backend=kw.pop("panel_backend", "relay"))
    audits = []
    kw.setdefault("audit", audits.append)
    register_chat_panel(app, id_prefix="r1", **kw)
    return app, audits


def ask(client, path="/api/agent/ask/stream", headers=None, **body):
    body.setdefault("question", "Who is fastest?")
    r = client.post(path, json=body, headers=headers or {})
    r.get_data()                       # consume the stream so the relay finishes (and audits) as a browser would
    return r


# ---- relay ------------------------------------------------------------------------------------------------
def test_relay_streams_and_forwards_contract():
    from aspire_dash.components import chat_relay
    up = FakeUpstream()
    app2, _ = _app_with_upstream(up)
    r = ask(app2.server.test_client(), sport="athletics", thread_id="t0", headers=CREDS)
    assert r.status_code == 200 and r.mimetype == "text/event-stream"
    assert r.headers["Cache-Control"] == "no-cache" and r.headers["X-Accel-Buffering"] == "no"
    assert [e["type"] for e in events(r.data)] == ["thread", "token", "done"]
    url, body = up.calls[0]
    assert url == "http://engine.test/api/agent/ask/stream"
    assert body == {"question": "Who is fastest?", "sport": "athletics", "thread_id": "t0", "user_id": "kenny"}
    assert chat_relay.STREAM_PATH == "api/agent/ask/stream"


def _app_with_upstream(up, prefix=None, url_base=None, **kw):
    """register_chat_panel does not expose `upstream`; mount through register_relay first (idempotent)."""
    from aspire_dash.components.chat_relay import register_relay
    args = {}
    if url_base:
        args["url_base_pathname"] = url_base
    if prefix:
        args["requests_pathname_prefix"] = prefix
        args["routes_pathname_prefix"] = "/"
    app = dash.Dash(__name__, **args)
    audits = []
    kw.setdefault("audit", audits.append)
    register_relay(app, engine_url="http://engine.test/", upstream=up, **kw)
    app.layout = chat_panel(id_prefix="r1")
    register_chat_panel(app, id_prefix="r1")          # second mount is a no-op: the fake stays wired
    return app, audits


def test_relay_is_unbuffered_first_chunk_before_upstream_finishes():
    gate = threading.Event()
    up = FakeUpstream(gate=gate)
    app, _ = _app_with_upstream(up)
    r = app.server.test_client().post("/api/agent/ask/stream", json={"question": "q"}, buffered=False)
    it = iter(r.response)
    first = next(it)                                   # arrives while the upstream is still blocked
    assert b'"thread"' in first and not gate.is_set()
    gate.set()
    rest = b"".join(it)
    assert b'"done"' in rest
    r.close()


@pytest.mark.parametrize("kind", ["root", "connect_prefix", "url_base"])
def test_route_respects_dash_path_prefix(kind):
    up = FakeUpstream()
    if kind == "root":
        app, _ = _app_with_upstream(up)
        path = "/api/agent/ask/stream"
    elif kind == "connect_prefix":     # Connect: requests under /content/abc/, routes at / (proxy strips it)
        app, _ = _app_with_upstream(up, prefix="/content/abc/")
        path = "/api/agent/ask/stream"
    else:                              # url_base_pathname: both prefixes are /content/abc/
        app, _ = _app_with_upstream(up, url_base="/content/abc/")
        path = "/content/abc/api/agent/ask/stream"
    c = app.server.test_client()
    assert ask(c, path=path).status_code == 200
    if kind == "url_base":
        assert ask(c, path="/api/agent/ask/stream").status_code in (404, 405)
    # the page tells the JS the requests prefix (read from #_dash-config)
    cfg = app._config()
    want = "/" if kind == "root" else "/content/abc/"
    assert cfg["requests_pathname_prefix"] == want


def test_identity_from_connect_header_ignores_client_user_id():
    up = FakeUpstream()
    app, audits = _app_with_upstream(up)
    ask(app.server.test_client(), user_id="spoofed-admin", headers=CREDS)
    assert up.calls[0][1]["user_id"] == "kenny" and audits[0]["user"] == "kenny"
    assert "groups" not in audits[0]


def test_identity_anonymous_without_header():
    up = FakeUpstream()
    app, audits = _app_with_upstream(up)
    c = app.server.test_client()
    ask(c, user_id="anon-abc123")
    ask(c)
    assert [b["user_id"] for _, b in up.calls] == ["anon:anon-abc123", "anonymous"]
    assert audits[0]["user"] == "anon:anon-abc123"


def test_custom_user_id_source_and_broken_source():
    up = FakeUpstream()
    app, _ = _app_with_upstream(up, user_id_source=lambda: "svc-user")
    ask(app.server.test_client(), user_id="x", headers=CREDS)
    assert up.calls[0][1]["user_id"] == "svc-user"

    def boom():
        raise RuntimeError("no")
    up2 = FakeUpstream()
    app2, _ = _app_with_upstream(up2, user_id_source=boom)
    ask(app2.server.test_client(), user_id="x")
    assert up2.calls[0][1]["user_id"] == "anon:x"


def test_audit_called_once_with_done_fields():
    up = FakeUpstream()
    app, audits = _app_with_upstream(up)
    ask(app.server.test_client(), question="Q" * 900, sport="squash", headers=CREDS)
    assert len(audits) == 1
    a = audits[0]
    assert a["status"] == "ok" and a["agent"] == "athletics_agent" and a["tools_used"] == ["athlete_record"]
    assert a["sport"] == "squash" and a["thread_id"] == "t1" and a["error"] is None
    assert len(a["question"]) == 500 and isinstance(a["duration_ms"], int)
    assert set(a) >= {"ts", "user", "question", "sport", "thread_id", "status", "agent", "tools_used",
                      "duration_ms", "error"}


def test_audit_error_event_and_unreachable_engine():
    up = FakeUpstream(chunks=[sse({"type": "error", "error": "engine timeout"})])
    app, audits = _app_with_upstream(up)
    ask(app.server.test_client())
    assert audits[0]["status"] == "error" and audits[0]["error"] == "engine timeout"

    def dead(url, body, timeout):
        raise ConnectionRefusedError("down")
        yield b""  # pragma: no cover
    app2, audits2 = _app_with_upstream(dead)
    r = ask(app2.server.test_client())
    assert events(r.data) == [{"type": "error", "error": "engine unreachable: ConnectionRefusedError"}]
    assert audits2[0]["status"] == "error"


def test_default_audit_is_one_structured_log_line(caplog):
    up = FakeUpstream()
    app, _ = _app_with_upstream(up, audit=None)
    with caplog.at_level("INFO", logger="aspire_dash.chat"):
        ask(app.server.test_client(), headers=CREDS)
    lines = [r.getMessage() for r in caplog.records if r.getMessage().startswith("chat_audit ")]
    assert len(lines) == 1
    ev = json.loads(lines[0][len("chat_audit "):])
    assert ev["user"] == "kenny" and ev["status"] == "ok"


@pytest.mark.parametrize("q,msg", [("   ", "empty question"), ("x" * 4001, "question too long")])
def test_empty_and_oversize_rejected_with_sse_error(q, msg):
    up = FakeUpstream()
    app, audits = _app_with_upstream(up)
    r = ask(app.server.test_client(), question=q)
    assert r.status_code == 400 and r.mimetype == "text/event-stream"
    assert events(r.data)[0]["type"] == "error" and msg in events(r.data)[0]["error"]
    assert up.calls == [] and audits[0]["status"] == "rejected"


def test_rate_limit_per_user():
    up = FakeUpstream()
    app, audits = _app_with_upstream(up, rate_limit=3)
    c = app.server.test_client()
    codes = [ask(c, headers=CREDS).status_code for _ in range(4)]
    assert codes == [200, 200, 200, 429]
    r = ask(c, headers=CREDS)
    assert "too many questions" in events(r.data)[0]["error"]
    assert ask(c, user_id="someone-else").status_code == 200      # another user is not blocked
    assert len(up.calls) == 4


def test_rate_limiter_window_slides():
    t = [0.0]
    rl = RateLimiter(2, 60, clock=lambda: t[0])
    assert rl.allow("a") and rl.allow("a") and not rl.allow("a")
    t[0] = 61
    assert rl.allow("a")


def test_sniffer_handles_split_chunks():
    s = _DoneSniffer()
    raw = sse({"type": "token", "text": "a"}) + sse(DONE)
    for i in range(0, len(raw), 7):
        s.feed(raw[i:i + 7])
    s.finish()
    assert s.done["agent"] == "athletics_agent"


def test_real_http_upstream_streams_unbuffered():
    """The stdlib fetcher against a real local HTTP engine: first token relayed before the engine ends."""
    eng = Flask("fake_engine")
    gate = threading.Event()
    seen = {}

    @eng.post("/api/agent/ask/stream")
    def _s():
        seen["body"] = request.get_json()
        seen["accept"] = request.headers.get("Accept")
        seen["enc"] = request.headers.get("Accept-Encoding")

        def g():
            yield sse({"type": "token", "text": "first"})
            gate.wait(5)
            yield sse(DONE)
        return Response(g(), mimetype="text/event-stream")

    srv = make_server("127.0.0.1", 0, eng, threaded=True)
    th = threading.Thread(target=srv.serve_forever, daemon=True)
    th.start()
    try:
        app, audits = make_app(engine_url=f"http://127.0.0.1:{srv.server_port}")
        r = app.server.test_client().post("/api/agent/ask/stream", json={"question": "q"},
                                          headers=CREDS, buffered=False)
        it = iter(r.response)
        assert b"first" in next(it) and not gate.is_set()
        gate.set()
        assert b'"done"' in b"".join(it)
        r.close()
        assert seen["accept"] == "text/event-stream" and seen["enc"] == "identity"
        assert seen["body"]["user_id"] == "kenny"
        assert audits[0]["status"] == "ok"
    finally:
        gate.set()
        srv.shutdown()


def test_chips_relay_uses_server_identity_only():
    eng = Flask("fake_engine")
    seen = {}

    @eng.post("/api/agent/chips")
    def _c():
        seen["body"] = request.get_json()
        return {"chips": [{"label": "x", "question": "y"}]}

    srv = make_server("127.0.0.1", 0, eng, threaded=True)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        app, _ = make_app(engine_url=f"http://127.0.0.1:{srv.server_port}")
        r = app.server.test_client().post("/api/agent/chips", json={"user_id": "spoof"}, headers=CREDS)
        assert r.get_json()["chips"][0]["question"] == "y" and seen["body"] == {"user_id": "kenny"}
    finally:
        srv.shutdown()


# ---- local ------------------------------------------------------------------------------------------------
def test_local_handler_streams_in_process_with_history():
    calls = []

    def handler(question, history, thread_id, user):
        calls.append((question, list(history), thread_id, user))
        yield {"type": "status", "text": "reading SAMS"}
        yield {"type": "token", "text": "ans-" + question}
        yield {"type": "done", "answer": "ans-" + question, "agent": "medical", "tools_used": ["sams"]}

    app, audits = make_app(handler=handler, panel_backend="local")
    c = app.server.test_client()
    r1 = ask(c, question="one", headers=CREDS)
    ev = events(r1.data)
    assert [e["type"] for e in ev] == ["thread", "status", "token", "done"]
    th = ev[0]["thread_id"]
    ask(c, question="two", thread_id=th, headers=CREDS)
    assert calls[0] == ("one", [], th, "kenny")
    assert calls[1][1] == [{"role": "user", "text": "one"}, {"role": "assistant", "text": "ans-one"}]
    assert [a["agent"] for a in audits] == ["medical", "medical"] and audits[0]["status"] == "ok"
    assert set(audits[0]) == {"ts", "user", "question", "sport", "thread_id", "status", "agent", "tools_used",
                              "duration_ms", "error", "backend"}       # nothing from the handler's data
    assert c.post("/api/agent/chips", json={}).get_json() == {"chips": []}


def test_local_handler_exception_is_generic_error():
    def handler(q, h, t, u):
        yield {"type": "status", "text": "x"}
        raise ValueError("patient 123 secret")

    app, audits = make_app(handler=handler)
    r = ask(app.server.test_client())
    err = events(r.data)[-1]
    assert err == {"type": "error", "error": "handler error: ValueError"}
    assert "secret" not in r.data.decode() and audits[0]["status"] == "error"


# ---- panel config ---------------------------------------------------------------------------------------
def _cfg(panel, prefix):
    stack = [panel]
    while stack:
        c = stack.pop()
        if getattr(c, "id", None) == f"{prefix}-config":
            return c.data
        ch = getattr(c, "children", None)
        stack.extend(ch if isinstance(ch, list) else [ch] if ch is not None and not isinstance(ch, str) else [])
    raise AssertionError("no config")


def test_relay_config_hides_engine_url_engine_mode_keeps_it():
    relay = _cfg(chat_panel(engine_url="https://e.test", id_prefix="a"), "a")
    assert relay["backend"] == "relay" and relay["engine_url"] == ""
    eng = _cfg(chat_panel(engine_url="https://e.test/", id_prefix="b", backend="engine"), "b")
    assert eng["backend"] == "engine" and eng["engine_url"] == "https://e.test"


def test_engine_backend_mounts_no_route_and_bad_backend_raises():
    app = dash.Dash(__name__)
    app.layout = chat_panel(id_prefix="e1", backend="engine")
    register_chat_panel(app, id_prefix="e1", backend="engine")
    assert "aspire_chat_relay" not in app.server.view_functions
    with pytest.raises(ValueError):
        chat_panel(backend="direct")
    with pytest.raises(ValueError):
        register_chat_panel(dash.Dash(__name__), backend="local")     # local needs a handler
