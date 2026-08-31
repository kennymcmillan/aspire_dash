"""M7: ChatPanel layout, pure helpers, and callback registration (no engine, no browser)."""
import os
import sys

import dash
from dash import html

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from aspire_dash.components import chat_panel, chips_from_done, register_chat_panel, trace_text  # noqa: E402
from aspire_dash.components.chat import _ids  # noqa: E402


def _walk(c):
    yield c
    ch = getattr(c, "children", None)
    if isinstance(ch, (list, tuple)):
        for x in ch:
            yield from _walk(x)
    elif ch is not None and hasattr(ch, "children"):
        yield from _walk(ch)


def test_layout_carries_every_id_once_and_the_engine_config():
    panel = chat_panel(engine_url="https://example.test/", sport="squash", id_prefix="p1")
    ids = [getattr(c, "id", None) for c in _walk(panel) if getattr(c, "id", None)]
    for k, v in _ids("p1").items():
        assert ids.count(v) == 1, (k, v, ids.count(v))
    store = next(c for c in _walk(panel) if getattr(c, "id", None) == "p1-config")
    assert store.data == {"engine_url": "https://example.test", "sport": "squash", "prefix": "p1"}
    thread = next(c for c in _walk(panel) if getattr(c, "id", None) == "p1-thread")
    assert thread.storage_type == "session"
    assert chat_panel(thread_scope="memory", id_prefix="p2").children[1].storage_type == "memory"


def test_chips_from_done_max_four_with_question_in_data_attr():
    done = {"suggestions": [{"label": f"L{i}", "question": f"Q{i}?", "why": "w"} for i in range(6)] + [{"label": ""}]}
    chips = chips_from_done(done)
    assert len(chips) == 4 and all(isinstance(c, html.Button) for c in chips)
    assert chips[0].children == "L0" and getattr(chips[0], "data-question") == "Q0?"
    assert chips_from_done(None) == [] and chips_from_done({}) == []


def test_trace_text_keeps_only_trace_fields():
    t = trace_text({"answer": "long", "agent": "athletics_agent", "tools_used": ["athlete_context"], "thread_id": "t1"})
    assert "athletics_agent" in t and "athlete_context" in t and "long" not in t
    assert trace_text(None) == ""


def test_register_wires_clientside_and_server_callbacks():
    app = dash.Dash(__name__)
    app.layout = chat_panel(id_prefix="p3")
    register_chat_panel(app, id_prefix="p3")
    outputs = " ".join(app.callback_map.keys())
    for out in ("p3-stream-state.data", "p3-input.value", "p3-chips.children", "p3-debug.hidden", "p3-thread.data"):
        assert out in outputs, out
