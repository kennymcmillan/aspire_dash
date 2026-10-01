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
    panel = chat_panel(engine_url="https://example.test/", sport="squash", id_prefix="p1", backend="engine")
    ids = [getattr(c, "id", None) for c in _walk(panel) if getattr(c, "id", None)]
    for k, v in _ids("p1").items():
        assert ids.count(v) == 1, (k, v, ids.count(v))
    store = next(c for c in _walk(panel) if getattr(c, "id", None) == "p1-config")
    assert store.data["engine_url"] == "https://example.test" and store.data["sport"] == "squash"
    assert store.data["prefix"] == "p1" and store.data["thread_scope"] == "session"
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
    for out in ("p3-stream-state.data", "p3-input.value", "p3-chips.children", "p3-debug.hidden", "p3-thread.data",
                "p3-last.data"):
        assert out in outputs, out


# ---- v0.100.0 (checklist 52, slice 1) -------------------------------------------------------------------

def _all_ids(c):
    return [getattr(x, "id", None) for x in _walk(c) if getattr(x, "id", None)]


def test_two_panels_on_one_page_have_disjoint_ids():
    a, b = _ids("left"), _ids("right")
    assert set(a) == set(b) and "stop" in a
    assert not set(a.values()) & set(b.values())
    page = html.Div([chat_panel(id_prefix="left"), chat_panel(id_prefix="right")])
    ids = _all_ids(page)
    assert len(ids) == len(set(ids)), "duplicate id across two panels"
    app = dash.Dash(__name__)
    app.layout = page
    register_chat_panel(app, id_prefix="left")
    register_chat_panel(app, id_prefix="right")
    outs = " ".join(app.callback_map.keys())
    assert "left-input.value" in outs and "right-input.value" in outs


def test_starters_render_as_chips_and_go_to_config():
    panel = chat_panel(id_prefix="s1", starters=["Top 5 sprinters?", {"label": "Squash", "question": "Latest squash results?",
                                                                    "why": "w"}, {"bad": 1}, "", 7])
    chips = next(c for c in _walk(panel) if getattr(c, "id", None) == "s1-chips").children
    assert [c.children for c in chips] == ["Top 5 sprinters?", "Squash"]
    assert getattr(chips[1], "data-question") == "Latest squash results?" and chips[1].title == "w"
    cfg = next(c for c in _walk(panel) if getattr(c, "id", None) == "s1-config").data
    assert [s["question"] for s in cfg["starters"]] == ["Top 5 sprinters?", "Latest squash results?"]


def test_new_kwargs_default_safely():
    panel = chat_panel(id_prefix="d1")
    chips = next(c for c in _walk(panel) if getattr(c, "id", None) == "d1-chips").children
    assert chips == []
    cfg = next(c for c in _walk(panel) if getattr(c, "id", None) == "d1-config").data
    assert cfg["starters"] == [] and cfg["welcome"]                 # default welcome text present
    assert chat_panel(id_prefix="d2", welcome=None).children[0].data["welcome"] == ""
    stop = next(c for c in _walk(panel) if getattr(c, "id", None) == "d1-stop")
    assert stop.hidden is True and getattr(stop, "data-action") == "stop"
    root = panel
    assert getattr(root, "data-prefix") == "d1" and "aspire-chat" in root.className


def test_messages_node_is_js_owned_no_dash_output():
    app = dash.Dash(__name__)
    app.layout = chat_panel(id_prefix="m1")
    register_chat_panel(app, id_prefix="m1")
    assert "m1-messages.children" not in " ".join(app.callback_map.keys())


def test_md_renderer_node_suite():
    """Runs tests/js/md.test.js (escape-first, safe links, code, lists, tables) when node is on PATH."""
    import shutil
    import subprocess

    import pytest
    node = shutil.which("node")
    if not node:
        pytest.skip("node not installed")
    js = os.path.join(os.path.dirname(os.path.abspath(__file__)), "js", "md.test.js")
    r = subprocess.run([node, js], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stdout + r.stderr
