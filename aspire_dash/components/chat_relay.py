"""Server-side relay for the chat panel (checklist 52, slice 2, v0.101.0).

The browser never calls the engine. The Dash app's own Flask server mounts

    POST <routes_pathname_prefix>api/agent/ask/stream   the question -> SSE answer
    POST <routes_pathname_prefix>api/agent/chips        "your athletes" chips (relay mode only)

and either forwards to the engine (`backend="relay"`) or runs an in-process handler (`backend="local"`).

Identity comes from Posit Connect, never from the client: Connect sets the `RStudio-Connect-Credentials`
request header to JSON `{"user": "...", "groups": [...]}` for a signed-in viewer
(https://docs.posit.co/connect/user/dash/, "User meta-data"). With the header present the client-sent
`user_id` is ignored. With no header (local dev, or Connect content open to anonymous viewers) the user is
`anon:<client id>` (or `anonymous`), so it can never collide with a real Connect username.

Audit: `audit(event)` is called ONCE per request, after the stream ends (or is rejected), with
`{ts, user, question (first 500 chars), sport, thread_id, status, agent, tools_used, duration_ms, error}`.
status = ok | error | aborted | incomplete | rejected. agent/tools_used come from the final `done` event,
parsed on the fly without buffering the stream. The default writes one JSON line via
`logging.getLogger("aspire_dash.chat").info`. PII: the event holds the Connect username and the question
text, nothing else (no groups, no answer text, no history, no handler data). If questions may hold
private data, pass your own `audit` that drops or hashes `question`.

Guards: empty or >4000-char question -> 400 with an SSE error event; more than `rate_limit` questions per
user per 60 s (in-memory, per process) -> 429 with an SSE error event.
"""
from __future__ import annotations

import json
import logging
import threading
import time
import urllib.error
import urllib.request
import uuid
from collections import OrderedDict, deque
from typing import Callable, Iterable, Iterator

log = logging.getLogger("aspire_dash.chat")

STREAM_PATH = "api/agent/ask/stream"
CHIPS_PATH = "api/agent/chips"
MAX_QUESTION = 4000
AUDIT_QUESTION_CHARS = 500
BACKENDS = ("relay", "engine", "local")


def sse(obj: dict) -> str:
    return "data: " + json.dumps(obj, ensure_ascii=False) + "\n\n"


def connect_identity() -> str | None:
    """The Connect username from `RStudio-Connect-Credentials`, or None (no header / bad JSON / no request).
    Same header as `aspire_dash.site_feedback.connect_viewer`, which returns '' instead of None."""
    from aspire_dash.site_feedback import connect_viewer
    return connect_viewer() or None


def default_audit(event: dict) -> None:
    log.info("chat_audit %s", json.dumps(event, ensure_ascii=False, default=str))


class RateLimiter:
    """Sliding window: at most `limit` hits per `window` seconds per key. In-memory, per process."""

    def __init__(self, limit: int = 20, window: float = 60.0, clock: Callable[[], float] = time.monotonic):
        self.limit, self.window, self.clock = limit, window, clock
        self._hits: dict[str, deque] = {}
        self._lock = threading.Lock()

    def allow(self, key: str) -> bool:
        if not self.limit or self.limit <= 0:
            return True
        now = self.clock()
        with self._lock:
            q = self._hits.setdefault(key, deque())
            while q and now - q[0] >= self.window:
                q.popleft()
            if len(q) >= self.limit:
                return False
            q.append(now)
            if len(self._hits) > 5000:       # drop idle keys so the dict cannot grow forever
                for k in [k for k, v in self._hits.items() if not v]:
                    self._hits.pop(k, None)
            return True


class History:
    """Per (user, thread) transcript for backend='local': last `turns` messages, at most `threads` threads
    (LRU). Lives in the app process only; it never leaves the app."""

    def __init__(self, turns: int = 20, threads: int = 500):
        self.turns, self.threads = turns, threads
        self._d: OrderedDict = OrderedDict()
        self._lock = threading.Lock()

    def get(self, user: str, thread: str) -> list[dict]:
        with self._lock:
            h = self._d.get((user, thread))
            if h is None:
                return []
            self._d.move_to_end((user, thread))
            return list(h)

    def add(self, user: str, thread: str, role: str, text: str) -> None:
        with self._lock:
            h = self._d.setdefault((user, thread), deque(maxlen=self.turns))
            h.append({"role": role, "text": text})
            self._d.move_to_end((user, thread))
            while len(self._d) > self.threads:
                self._d.popitem(last=False)


class _DoneSniffer:
    """Watches relayed SSE bytes for the final done/error event without holding the stream back.
    Keeps only the trailing partial event in memory."""

    def __init__(self):
        self.buf = ""
        self.done: dict | None = None
        self.error: str | None = None
        self.thread_id: str | None = None
        self.started = False          # set once the first SSE bytes are relayed (JSON-door detection)

    def feed(self, chunk: bytes) -> None:
        self.buf += chunk.decode("utf-8", "replace")
        *events, self.buf = self.buf.replace("\r\n", "\n").split("\n\n")
        for e in events:
            self.event(e)

    def event(self, raw: str) -> None:
        line = raw.strip()
        if not line.startswith("data:"):
            return
        try:
            ev = json.loads(line[5:].strip())
        except ValueError:
            return
        self.observe(ev)

    def observe(self, ev) -> None:
        if not isinstance(ev, dict):
            return
        t = ev.get("type")
        if t == "done":
            self.done = ev
        elif t == "error":
            self.error = str(ev.get("error") or "engine error")
        elif t == "thread" and ev.get("thread_id"):
            self.thread_id = str(ev["thread_id"])

    def finish(self) -> None:
        if self.buf.strip():
            self.event(self.buf)
            self.buf = ""


def _upstream(url: str, body: dict, timeout: float) -> Iterator[bytes]:
    """POST json to the engine and yield SSE bytes as they arrive (read1 = whatever is available, so
    tokens are not held for a full buffer). Stdlib only: no `requests` dependency."""
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST", headers={
        "Content-Type": "application/json", "Accept": "text/event-stream", "Accept-Encoding": "identity"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        while True:
            chunk = r.read1(65536)
            if not chunk:
                break
            yield chunk


def json_door_events(raw: bytes) -> list[dict]:
    """v0.102.0: an engine reply that is ONE JSON object (the `/api/agent/ask` JSON door shape: answer, agent,
    tools_used, usage, trace, suggestions, clarify, thread_id) -> the SSE events the browser expects:
    a thread event (when it names one) and a done event; `{error}` with no answer -> an error event."""
    try:
        obj = json.loads(raw.decode("utf-8", "replace"))
    except ValueError:
        return [{"type": "error", "error": "engine sent malformed JSON"}]
    if not isinstance(obj, dict):
        return [{"type": "error", "error": "engine sent an unexpected JSON reply"}]
    if obj.get("error") and not obj.get("answer"):
        return [{"type": "error", "error": str(obj["error"])[:300]}]
    evs = [{"type": "thread", "thread_id": obj["thread_id"]}] if obj.get("thread_id") else []
    return evs + [dict(obj, type="done")]


def _clean_id(v, n: int = 128) -> str | None:
    if v is None:
        return None
    s = str(v).strip()[:n]
    return s or None


def register_relay(app, *, backend: str = "relay", engine_url: str | None = None,
                   handler: Callable[..., Iterable[dict]] | None = None,
                   user_id_source: Callable[[], str | None] | None = None,
                   audit: Callable[[dict], None] | None = None, rate_limit: int = 20,
                   timeout: float = 180.0, upstream: Callable[[str, dict, float], Iterable[bytes]] | None = None):
    """Mount the relay routes on `app.server` under `app.config.routes_pathname_prefix`. Idempotent per app
    (two panels on one page share it; the first registration's settings win). Returns the route rules."""
    from flask import Response, jsonify, request, stream_with_context

    if backend not in ("relay", "local"):
        raise ValueError(f"register_relay backend must be 'relay' or 'local', not {backend!r}")
    if backend == "local" and handler is None:
        raise ValueError("backend='local' needs handler=callable(question, history, thread_id, user)")
    server = app.server
    prefix = (app.config.get("routes_pathname_prefix") or "/").rstrip("/") + "/"
    rule, chips_rule = prefix + STREAM_PATH, prefix + CHIPS_PATH
    if "aspire_chat_relay" in server.view_functions:
        return rule, chips_rule
    engine = (engine_url or "").rstrip("/")
    who = user_id_source or connect_identity
    record = audit or default_audit
    limiter = RateLimiter(rate_limit)
    history = History()
    fetch = upstream or _upstream

    def identity(body: dict) -> str:
        try:
            u = _clean_id(who(), 256)
        except Exception:  # noqa: BLE001  a broken identity source must not open the door
            log.exception("chat relay: user_id_source failed")
            u = None
        if u:
            return u                                     # header wins; the client's user_id is ignored
        cid = _clean_id(body.get("user_id"), 64)
        return f"anon:{cid}" if cid else "anonymous"

    def write_audit(ev: dict) -> None:
        try:
            record(ev)
        except Exception:  # noqa: BLE001
            log.exception("chat relay: audit callable failed")

    def reject(status: int, msg: str, base: dict) -> Response:
        write_audit(dict(base, status="rejected", error=msg, duration_ms=0))
        return Response(sse({"type": "error", "error": msg}), status=status, mimetype="text/event-stream")

    @server.route(rule, methods=["POST"], endpoint="aspire_chat_relay")
    def _ask_stream():
        body = request.get_json(silent=True) or {}
        q = str(body.get("question") or "").strip()
        user = identity(body)
        sport = _clean_id(body.get("sport"), 32)
        thread = _clean_id(body.get("thread_id"))
        base = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "user": user, "question": q[:AUDIT_QUESTION_CHARS],
                "sport": sport, "thread_id": thread, "backend": backend, "agent": None, "tools_used": []}
        if not q:
            return reject(400, "empty question", base)
        if len(q) > MAX_QUESTION:
            return reject(400, f"question too long (max {MAX_QUESTION} characters)", base)
        if not limiter.allow(user):
            return reject(429, f"too many questions: limit {rate_limit} a minute, try again shortly", base)
        t0 = time.monotonic()
        sniff = _DoneSniffer()
        state = {"status": None}

        def finish():
            sniff.finish()
            if state["status"] is None:
                state["status"] = "ok" if sniff.done else "error" if sniff.error else "incomplete"
            d = sniff.done or {}
            write_audit(dict(base, thread_id=sniff.thread_id or thread, status=state["status"],
                             agent=d.get("agent"), tools_used=list(d.get("tools_used") or []),
                             duration_ms=int((time.monotonic() - t0) * 1000), error=sniff.error))

        def gen_relay():
            fwd = {"question": q, "sport": sport, "thread_id": thread, "user_id": user}
            door = None                       # JSON door: the engine answered with one JSON object, not SSE
            try:
                for chunk in fetch(engine + "/" + STREAM_PATH, fwd, timeout):
                    if not chunk:
                        continue
                    if door is None and not sniff.started and chunk.lstrip()[:1] == b"{":
                        door = bytearray()
                    if door is not None:
                        door += chunk
                        continue
                    sniff.started = True
                    sniff.feed(chunk)
                    yield chunk
                if door is not None:
                    for ev in json_door_events(bytes(door)):
                        sniff.observe(ev)
                        yield sse(ev)
            except GeneratorExit:            # client went away; after a done/error it is not an abort
                if not (sniff.done or sniff.error):
                    state["status"] = "aborted"
                raise
            except urllib.error.HTTPError as e:
                sniff.error = f"engine HTTP {e.code}"
                yield sse({"type": "error", "error": sniff.error})
            except Exception as e:  # noqa: BLE001
                sniff.error = f"engine unreachable: {type(e).__name__}"
                yield sse({"type": "error", "error": sniff.error})
            finally:
                finish()

        def gen_local():
            th = thread or f"local-{uuid.uuid4().hex[:12]}"
            past = history.get(user, th)
            try:
                if not thread:
                    ev = {"type": "thread", "thread_id": th}
                    sniff.observe(ev)
                    yield sse(ev)
                answer = []
                for ev in handler(q, past, th, user):
                    if not isinstance(ev, dict):
                        continue
                    sniff.observe(ev)
                    if ev.get("type") == "token":
                        answer.append(str(ev.get("text") or ""))
                    yield sse(ev)
                if sniff.done:
                    history.add(user, th, "user", q)
                    history.add(user, th, "assistant", str(sniff.done.get("answer") or "".join(answer)))
            except GeneratorExit:            # client went away; after a done/error it is not an abort
                if not (sniff.done or sniff.error):
                    state["status"] = "aborted"
                raise
            except Exception as e:  # noqa: BLE001  never echo handler internals (may hold private data)
                log.exception("chat relay: local handler failed")
                sniff.error = f"handler error: {type(e).__name__}"
                yield sse({"type": "error", "error": sniff.error})
            finally:
                if not sniff.thread_id:
                    sniff.thread_id = th
                finish()

        gen = gen_relay if backend == "relay" else gen_local
        return Response(stream_with_context(gen()), mimetype="text/event-stream",
                        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

    @server.route(chips_rule, methods=["POST"], endpoint="aspire_chat_chips")
    def _chips():
        # local mode has no engine memory; relay mode asks the engine for the SERVER-derived user only
        if backend != "relay":
            return jsonify({"chips": []})
        user = identity(request.get_json(silent=True) or {})
        try:
            req = urllib.request.Request(engine + "/" + CHIPS_PATH, data=json.dumps({"user_id": user}).encode(),
                                         method="POST", headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as r:
                return Response(r.read(), mimetype="application/json")
        except Exception:  # noqa: BLE001
            return jsonify({"chips": []})

    return rule, chips_rule
