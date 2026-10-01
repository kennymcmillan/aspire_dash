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
