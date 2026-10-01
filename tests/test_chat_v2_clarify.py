"""v0.102.0 clarify chips: the engine's `clarify` block over the SSE done event and the JSON door, the chips'
reply text and sport, and the relay's JSON-door conversion. A fake engine at the relay's upstream seam returns
a clarify payload and a trace. Asserts on values."""
import json
import os
import sys

import dash
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from aspire_dash.components import chat_panel, register_chat_panel  # noqa: E402
from aspire_dash.components.chat import chips_from_done, clarify_reply  # noqa: E402
from aspire_dash.components.chat_relay import json_door_events, register_relay  # noqa: E402

CLARIFY_DONE = {
    "type": "done", "answer": "Which sport do you mean for 'Ali': Squash, Padel?", "agent": "parameter_finder",
    "tools_used": ["resolve_athlete"], "thread_id": "th-1",
    "trace": {"spans": [{"k": "node", "node": "parameter_finder", "name": "parameter_finder", "t": 0, "ms": 40}]},
    "clarify": {"question": "Which sport do you mean for 'Ali': Squash, Padel?", "attr": "sport",
                "options": [{"label": "Squash", "aspire_id": 4242, "sport": "squash", "tracked": True},
                            {"label": "Padel", "aspire_id": None, "sport": "padel", "tracked": False}]},
    "suggestions": [{"label": "Squash", "question": "Ali PB (aspire_id 4242)", "aspire_id": 4242, "sport": "squash"},
                    {"label": "Padel", "question": "Ali PB (padel)", "sport": "padel"},
                    {"label": "Ali's last 5", "question": "Ali last 5 results", "aspire_id": 77, "sport": "squash"}],
}


class FakeEngine:
    """Upstream seam fake. mode 'sse': thread, status, token, done. mode 'json': ONE JSON object (the
    /api/agent/ask door), split across two chunks so the relay must buffer it. Both carry clarify + trace."""

    def __init__(self):
        self.mode, self.calls = "sse", []

    def __call__(self, url, body, timeout):
        self.calls.append(body)
        if self.mode == "json":
            raw = json.dumps({k: v for k, v in CLARIFY_DONE.items() if k != "type"}).encode()
            yield raw[:20]
            yield raw[20:]
            return
        for ev in ({"type": "thread", "thread_id": "th-1"}, {"type": "status", "text": "resolving"},
                   {"type": "token", "text": CLARIFY_DONE["answer"]}, CLARIFY_DONE):
            yield ("data: " + json.dumps(ev) + "\n\n").encode()


@pytest.fixture
def fake_engine():
    return FakeEngine()


def _relay_app(engine, audits):
    app = dash.Dash(__name__)
    register_relay(app, engine_url="http://engine.test", upstream=engine, audit=audits.append)
    app.layout = chat_panel(id_prefix="c1")
    return app


def _events(raw: bytes):
    return [json.loads(p[5:].strip()) for p in raw.decode().split("\n\n") if p.strip().startswith("data:")]


def test_clarify_options_render_as_reply_buttons_then_deduped_suggestions():
    chips = chips_from_done(CLARIFY_DONE)
    block, rest = chips[0], chips[1:]
    assert "aspire-chat-clarify" in block.className
    q, *buttons = block.children
    assert q.children == CLARIFY_DONE["clarify"]["question"]
    assert [(b.children, getattr(b, "data-question"), getattr(b, "data-sport")) for b in buttons] == [
        ("Squash", "Squash (aspire_id 4242)", "squash"), ("Padel", "Padel", "padel")]
    assert getattr(buttons[0], "data-aspire-id") == "4242" and not hasattr(buttons[1], "data-aspire-id")
    # both option suggestions are dropped as repeats; the unrelated one stays with its id + sport
    assert [(c.children, getattr(c, "data-question"), getattr(c, "data-sport"), getattr(c, "data-aspire-id"))
            for c in rest] == [("Ali's last 5", "Ali last 5 results", "squash", "77")]


def test_clarify_reply_text_binds_by_id_else_label():
    assert clarify_reply({"label": "Squash", "aspire_id": 4242}) == "Squash (aspire_id 4242)"
    assert clarify_reply({"label": " QAT ", "aspire_id": None}) == "QAT"


def test_no_clarify_keeps_plain_suggestions():
    chips = chips_from_done({"suggestions": [{"label": "L", "question": "Q?"}]})
    assert [(c.children, getattr(c, "data-question")) for c in chips] == [("L", "Q?")]
    assert chips_from_done({"clarify": {"question": "x", "options": []}}) == []


def test_relay_sse_done_carries_clarify_and_trace(fake_engine):
    audits = []
    app = _relay_app(fake_engine, audits)
    r = app.server.test_client().post("/api/agent/ask/stream", json={"question": "Ali PB", "thread_id": "th-1"})
    evs = _events(r.get_data())
    assert [e["type"] for e in evs] == ["thread", "status", "token", "done"]
    assert evs[-1]["clarify"]["options"][0]["aspire_id"] == 4242 and evs[-1]["trace"]["spans"][0]["k"] == "node"
    assert audits[-1]["status"] == "ok" and audits[-1]["agent"] == "parameter_finder"


def test_relay_json_door_becomes_thread_plus_done_and_chip_replies_on_same_thread(fake_engine):
    audits = []
    fake_engine.mode = "json"
    app = _relay_app(fake_engine, audits)
    client = app.server.test_client()
    evs = _events(client.post("/api/agent/ask/stream", json={"question": "Ali PB"}).get_data())
    assert [e["type"] for e in evs] == ["thread", "done"]
    assert evs[0]["thread_id"] == "th-1"
    assert evs[1]["clarify"] == CLARIFY_DONE["clarify"] and evs[1]["answer"] == CLARIFY_DONE["answer"]
    assert audits[-1]["status"] == "ok" and audits[-1]["thread_id"] == "th-1"
    assert audits[-1]["tools_used"] == ["resolve_athlete"]
    # the chip's reply goes back on the SAME thread with the option's sport (what aspire-chat.js posts)
    reply = chips_from_done(evs[1])[0].children[1]
    client.post("/api/agent/ask/stream", json={"question": getattr(reply, "data-question"), "thread_id": "th-1",
                                               "sport": getattr(reply, "data-sport")}).get_data()
    assert fake_engine.calls[-1] == {"question": "Squash (aspire_id 4242)", "sport": "squash", "thread_id": "th-1",
                                     "user_id": "anonymous"}


def test_json_door_error_and_garbage():
    assert json_door_events(b'{"error": "boom"}') == [{"type": "error", "error": "boom"}]
    assert json_door_events(b"{nope")[0]["type"] == "error"
    assert json_door_events(b'{"answer": "a"}') == [{"type": "done", "answer": "a"}]


def test_chips_callback_wiring_renders_clarify():
    app = dash.Dash(__name__)
    app.layout = chat_panel(id_prefix="w4")
    register_chat_panel(app, id_prefix="w4")
    key = next(k for k in app.callback_map if "w4-chips.children" in k)
    entry = app.callback_map[key]
    assert [i["id"] + "." + i["property"] for i in entry["inputs"]] == ["w4-last.data"]
    assert "w4-debug.children" in key
    chips, raw = entry["callback"].__wrapped__(CLARIFY_DONE)
    assert "aspire-chat-clarify" in chips[0].className and json.loads(raw)["agent"] == "parameter_finder"
    assert entry["callback"].__wrapped__(None)[1] == ""
