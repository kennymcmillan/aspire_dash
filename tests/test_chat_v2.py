"""v0.102.0 chat panel: sport seed vs lock, workspace tabs, trace waterfall, clarify chips, the JSON door.

Asserts on values (config dicts, rendered component props, relayed bytes), never on source text."""
import json
import os
import shutil
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from aspire_dash.components import chat_panel  # noqa: E402


def _walk(c):
    yield c
    ch = getattr(c, "children", None)
    if isinstance(ch, (list, tuple)):
        for x in ch:
            yield from _walk(x)
    elif ch is not None and hasattr(ch, "children"):
        yield from _walk(ch)


def _find(root, cid):
    return next(c for c in _walk(root) if getattr(c, "id", None) == cid)


# ---- slice 1: sport seeds the picker, lock_sport is opt-in ------------------------------------------------

def test_sport_seeds_picker_and_is_not_locked_by_default():
    panel = chat_panel(sport="squash", id_prefix="s1")
    cfg = _find(panel, "s1-config").data
    picker = _find(panel, "s1-sport")
    assert picker.value == "squash"
    assert cfg["sport"] == "squash" and cfg["lock_sport"] is False
    assert not getattr(picker, "disabled", False)


def test_lock_sport_pins_and_disables_the_picker():
    panel = chat_panel(sport="fencing", id_prefix="s2", lock_sport=True)
    assert _find(panel, "s2-config").data["lock_sport"] is True
    assert _find(panel, "s2-sport").disabled is True


def test_lock_sport_without_a_sport_is_a_no_op():
    panel = chat_panel(id_prefix="s3", lock_sport=True)
    assert _find(panel, "s3-config").data["lock_sport"] is False
    assert _find(panel, "s3-sport").value == "athletics"


def test_js_sport_and_json_door_node_suite():
    """Runs tests/js/chat_v2.test.js (pickSport seed/lock, doneFromJson) when node is on PATH."""
    node = shutil.which("node")
    if not node:
        pytest.skip("node not installed")
    js = os.path.join(os.path.dirname(os.path.abspath(__file__)), "js", "chat_v2.test.js")
    r = subprocess.run([node, js], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stdout + r.stderr


# ---- slice 2: workspace tabs, tables + medals, charts, trace waterfall, turn store -------------------------
import dash  # noqa: E402

from aspire_dash.components import register_chat_panel  # noqa: E402
from aspire_dash.components.chat_workspace import (  # noqa: E402
    num, pane_hidden, render_workspace, shape_trace, tab_labels, tables_from_markdown, trace_view)

ANSWER = ("## Qatar 100m: top 3\n\n| Rank | Athlete | PB |\n|---|---|---|\n| 1 | A | 10.12 |\n| 2 | B | 10.31 |\n"
          "| 3 | C | 10.40 |\n| 4 | D | 10.55 |\n\nDone.")
TRACE = {"llm_calls": 1, "llm_ms": 800, "tool_calls": 1, "tool_ms": 300, "cached_tokens": 500,
         "spans": [{"k": "node", "node": "router", "name": "router", "t": 0, "ms": 100, "err": False},
                   {"k": "node", "node": "athletics_agent", "name": "athletics_agent", "t": 100, "ms": 1200, "err": False},
                   {"k": "llm", "node": "athletics_agent", "name": "gpt-x", "t": 120, "ms": 800, "err": False,
                    "in": 2000, "out": 150, "cached": 500, "calls": ["athlete_record"]},
                   {"k": "tool", "node": "athletics_agent", "name": "athlete_record", "t": 950, "ms": 300, "err": True}]}
TURN = {"q": "Qatar 100m top 3", "answer": ANSWER, "agent": "athletics_agent", "tools_used": ["athlete_record"],
        "usage": {"llm_calls": 1, "input_tokens": 2000, "output_tokens": 150, "cost_usd": 0.0042}, "trace": TRACE,
        "ms": 1400}


def test_tables_from_markdown_values():
    tb = tables_from_markdown(ANSWER)
    assert len(tb) == 1
    t = tb[0]
    assert t["title"] == "Qatar 100m: top 3" and t["head"] == ["Rank", "Athlete", "PB"]
    assert t["rows"][0] == ["1", "A", "10.12"] and len(t["rows"]) == 4
    assert t["numeric"] == [0, 2] and t["values"]["2"] == [10.12, 10.31, 10.40, 10.55]
    assert t["chart"] is True
    assert num("2:05.30") == 125.3 and num("1,234") == 1234 and num("-") is None


def _classes(c):
    return [getattr(x, "className", "") or "" for x in _walk(c)]


def test_table_card_uses_data_table_and_medals_for_top3_only():
    tables, charts, trace, counts = render_workspace({"turns": [TURN]})
    assert counts == {"tables": 1, "charts": 1, "trace": 4}
    cls = _classes(tables[0])
    assert any("aspire-data-table" in c for c in cls)
    medals = [c for c in cls if "placement-badge" in c]
    assert len(medals) == 3 and any("place-gold" in c for c in medals) and not any("place-top8" in c for c in medals)


def test_shape_trace_node_rows_nest_llm_and_tool():
    x = shape_trace(TURN)
    assert [(r["kind"], r["depth"], r["name"]) for r in x["rows"]] == [
        ("node", 0, "router"), ("node", 0, "athletics_agent"), ("llm", 1, "gpt-x"), ("err", 1, "athlete_record")]
    assert x["path"] == ["router", "athletics_agent", "athlete_record"]
    assert x["total"] == 1400 and x["fast"] is False
    assert x["kpis"]["llm_calls"] == 1 and x["kpis"]["cached_share"] == 0.25 and x["kpis"]["cost"] == 0.0042
    assert x["rows"][2]["tok"] == "2.0k/150"


def test_trace_view_bars_positioned_by_start_and_duration():
    view = trace_view(TURN)
    bars = [x for x in _walk(view) if (getattr(x, "className", "") or "") == "aspire-chat-tr-bar"]
    assert len(bars) == 4
    # athletics_agent node: t=100 ms, 1200 ms of a 1400 ms run
    assert bars[1].style == {"left": "7.14%", "width": "85.71%"}
    rows = [x for x in _walk(view) if isinstance(x, dash.html.Li)]
    assert [getattr(r, "data-kind") for r in rows] == ["node", "node", "llm", "err"]
    assert "is-child" in rows[2].className and "is-child" not in rows[1].className


def test_trace_falls_back_to_hops_and_fast_path():
    x = shape_trace({"q": "q", "trace": {"hops": ["squash_agent:2916ms", "writer:84ms"]}, "usage": {"llm_calls": 0}})
    assert x["approx"] is True and [r["t"] for r in x["rows"]] == [0, 2916] and x["fast"] is True
    assert trace_view(None) is None and shape_trace(None)["rows"] == []


def test_empty_workspace_has_empty_states_and_no_counts():
    tables, charts, trace, counts = render_workspace(None)
    assert counts == {"tables": 0, "charts": 0, "trace": 0}
    assert "aspire-chat-empty" in tables[0].className and "aspire-chat-empty" in trace.className
    assert tab_labels(counts) == ["Answer", "Tables", "Charts", "Trace"]
    assert tab_labels({"tables": 2, "trace": 4}) == ["Answer", "Tables (2)", "Charts", "Trace (4)"]


def test_pane_hidden_shows_exactly_one():
    assert pane_hidden("trace") == [True, True, True, False]
    assert pane_hidden(None) == [False, True, True, True]


def _cb(app, out_fragment):
    key = next(k for k in app.callback_map if out_fragment in k)
    entry = app.callback_map[key]
    return key, entry, entry["callback"].__wrapped__


def _app(prefix):
    app = dash.Dash(__name__)
    app.layout = chat_panel(id_prefix=prefix)
    register_chat_panel(app, id_prefix=prefix)
    return app


def test_workspace_callback_wiring_and_values():
    app = _app("w1")
    key, entry, fn = _cb(app, "w1-tables.children")
    assert [i["id"] + "." + i["property"] for i in entry["inputs"]] == ["w1-turns.data"]
    for out in ("w1-tables.children", "w1-charts.children", "w1-trace.children", "w1-tabs.children"):
        assert out in key
    tables, charts, trace, tabs = fn({"turns": [TURN], "sel": 0})
    assert [t.label for t in tabs] == ["Answer", "Tables (1)", "Charts (1)", "Trace (4)"]
    assert [t.value for t in tabs] == ["answer", "tables", "charts", "trace"]
    assert "aspire-chat-traceview" in trace.className


def test_pane_and_trace_button_callbacks():
    app = _app("w2")
    key, entry, fn = _cb(app, "w2-pane-answer.hidden")
    assert [i["id"] for i in entry["inputs"]] == ["w2-tabs"]
    assert "w2-debug.hidden" in key
    assert fn("tables") == (True, False, True, True, True)
    key, entry, fn = _cb(app, "w2-tabs.value")
    assert [i["id"] for i in entry["inputs"]] == ["w2-debug-toggle"] and [s["id"] for s in entry["state"]] == ["w2-tabs"]
    assert fn(1, "answer") == "trace" and fn(2, "trace") == "answer"


def test_every_new_output_has_a_layout_component():
    from aspire_dash.testing import baseline_problems
    app = _app("w3")
    assert baseline_problems(app, root=None) == []
