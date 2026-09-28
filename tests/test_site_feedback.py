"""aspire_dash.site_feedback (v0.96): button/drawer, triage grid, callbacks (no network, fake store)."""
from __future__ import annotations

from collections import OrderedDict
from contextvars import copy_context

import dash
import pandas as pd
import pytest
from dash._callback_context import context_value
from dash._utils import AttributeDict

import aspire_dash.site_feedback as sf

COLS = ["id", "created_utc", "app", "page", "page_path", "category", "note", "status", "status_on",
        "status_by", "by"]


class FakeStore:
    app = "demo"

    def __init__(self):
        self.rows, self.last_error, self.added, self.status_calls = [], "", [], []

    def load(self, fresh=False):
        return pd.DataFrame(self.rows, columns=COLS)

    def pending(self):
        return 0

    def add(self, page, note, *, by="", category="", page_path=""):
        row = dict.fromkeys(COLS, "")
        row.update(id=f"r{len(self.rows)}", created_utc="2026-09-28 05:00", app=self.app, page=page,
                   page_path=page_path, category=category, note=note.strip(), status="Open", by=by)
        self.rows.insert(0, row)
        self.added.append(row)
        return row

    def set_status(self, rid, status, *, by=""):
        self.status_calls.append((rid, status))
        for r in self.rows:
            if r["id"] == rid:
                r["status"] = status
        return True


@pytest.fixture
def store(monkeypatch):
    monkeypatch.delenv("RSTUDIO_PRODUCT", raising=False)
    monkeypatch.delenv("CONNECT_CONTENT_GUID", raising=False)
    monkeypatch.setattr(dash, "page_registry", OrderedDict([
        ("pages.home", {"path": "/", "name": "Current Injuries"}),
        ("pages.admin", {"path": "/admin", "name": "Report recipients"})]))
    s = FakeStore()
    sf._CFG.clear()
    sf._CFG.update(store=s, extra_pages=("Ask Medical",), categories=("Bug", "Idea"),
                   can_triage=sf.default_can_triage, notice="No athlete details.",
                   toast_trigger="fly-toast-trigger", feedback_href="/feedback", inbox=None)
    return s


def run(fn, *args, inputs_list=None, triggered=None):
    def inner():
        context_value.set(AttributeDict(triggered_inputs=triggered or [{"prop_id": "x.n_clicks", "value": 1}],
                                        inputs_list=inputs_list or []))
        return fn(*args)
    return copy_context().run(inner)


def test_page_for_path_uses_the_registry(store):
    assert sf.page_for_path("/admin") == "Report recipients"
    assert sf.page_for_path("/") == "Current Injuries"
    assert sf.page_for_path("/nope") == "Whole site" and sf.page_for_path(None) == "Current Injuries"


def test_open_prefills_the_current_page(store):
    opts, value, cats, notice, href, msg = run(sf._open, 1, "/admin")
    assert value == "Report recipients" and opts == ["Current Injuries", "Report recipients", "Ask Medical",
                                                     "Whole site"]
    assert cats == ["Bug", "Idea"] and notice == "No athlete details." and msg == ""
    assert all(x is dash.no_update for x in run(sf._open, 0, "/admin"))       # mount fire: nothing


def test_save_adds_one_request_and_closes_the_drawer(store):
    note, cls, msg, toast = run(sf._save, 1, "Report recipients", "Idea", "  Make ticks bigger ", "/admin")
    assert (note, cls, msg) == ("", "sfb-drawer", "") and toast["header"] == "Thanks, saved"
    assert store.added[0]["note"] == "Make ticks bigger" and store.added[0]["page_path"] == "/admin"
    assert store.added[0]["category"] == "Idea"
    assert run(sf._save, 2, "X", None, "   ", "/")[2] == "Write what should change first."
    assert all(x is dash.no_update for x in run(sf._save, 0, "X", None, "hi", "/"))
    assert len(store.added) == 1


def test_save_failure_is_shown_not_raised(store):
    def boom(*a, **k):
        raise RuntimeError("pin down")
    store.add = boom
    assert "Could not save (RuntimeError)" in run(sf._save, 1, "P", None, "note", "/")[2]


def _boxes(done: dict):
    """The Done tick boxes as Dash sends them: {row id: ticked?}."""
    return [[{"id": {"type": "sfb-done", "id": rid}, "property": "value", "value": ["done"] if on else []}
             for rid, on in done.items()]]


def test_tick_saves_only_the_one_change_and_refuses_a_stale_page(store):
    """v0.98: a Done tick box per request (Kenny 2026-09-28: 'I need a way to tick if done or not')."""
    for n in ("a", "b", "c"):
        store.add("P", n)
    ids = [r["id"] for r in store.rows]
    same = {i: False for i in ids}
    assert run(sf._status, None, inputs_list=_boxes(same))[0] is dash.no_update        # re-render: no write
    count, toast = run(sf._status, None, inputs_list=_boxes({**same, ids[1]: True}))
    assert store.status_calls == [(ids[1], "Done")] and toast == {**toast, "header": "Saved", "msg": "Marked done."}
    assert count.startswith("2 open · 1 done")
    count, toast = run(sf._status, None, inputs_list=_boxes(same))                     # untick it again
    assert store.status_calls[-1] == (ids[1], "Open") and toast["msg"] == "Marked not done."
    stale = run(sf._status, None, inputs_list=_boxes({ids[0]: True, ids[1]: True, ids[2]: False}))
    assert stale[1]["header"] == "Page out of date" and len(store.status_calls) == 2


def test_unticked_box_leaves_an_in_progress_request_alone(store):
    store.add("P", "x")
    store.rows[0]["status"] = "In progress"
    assert run(sf._status, None, inputs_list=_boxes({store.rows[0]["id"]: False}))[0] is dash.no_update
    assert store.status_calls == []


def test_non_triage_users_cannot_tick_and_see_chips(store, monkeypatch):
    store.add("P", "x")
    monkeypatch.setenv("RSTUDIO_PRODUCT", "CONNECT")
    monkeypatch.setenv("ADMIN_USERS", "kenneth.mcmillan@aspire.qa")
    rid = store.rows[0]["id"]
    res = run(sf._status, None, inputs_list=_boxes({rid: True}))
    assert res[1]["header"] == "Not allowed" and store.status_calls == []
    grid = str(sf._rows(store.load(), "Open", "This app"))
    assert "sfb-done" not in grid and "sfb-chip--open" in grid


def test_triage_users_get_a_tick_box_per_row(store):
    store.add("P", "open one")
    store.add("Q", "done one")
    store.rows[0]["status"], store.rows[0]["status_on"] = "Done", "2026-09-28 06:00"
    grid = str(sf._rows(store.load(), "All", "This app"))
    assert grid.count("sfb-done-input") == 2 and "28-Sep-2026 09:00" in grid       # Done on (Qatar)
    assert "value=['done']" in grid and "value=[]" in grid


def test_default_can_triage(monkeypatch):
    monkeypatch.delenv("RSTUDIO_PRODUCT", raising=False)
    monkeypatch.delenv("CONNECT_CONTENT_GUID", raising=False)
    assert sf.default_can_triage("")                                   # local development
    monkeypatch.setenv("RSTUDIO_PRODUCT", "CONNECT")
    monkeypatch.setenv("ADMIN_USERS", "Kenneth.Mcmillan@aspire.qa")
    assert sf.default_can_triage("kenneth.mcmillan") and sf.default_can_triage("KENNETH.MCMILLAN@ASPIRE.QA")
    assert not sf.default_can_triage("physio@aspire.qa") and not sf.default_can_triage("")


def test_grid_filters_open_done_all_and_inbox_shows_the_app(store):
    store.add("P", "open one")
    store.add("Q", "done one")
    store.rows[0]["status"] = "Done"
    lst, count = sf._render("Open", "This app")
    assert "open one" in str(lst) and "done one" not in str(lst) and count.startswith("1 open · 1 done")
    assert "done one" in str(sf._render("Done", "This app")[0]) and "open one" not in str(sf._render("Done", "This app")[0])
    assert "sfb-row--done" in str(sf._rows(store.load(), "All", "This app"))
    inbox = pd.DataFrame([{**dict.fromkeys(COLS, ""), "id": "z", "app": "strength-rota", "note": "from rota",
                           "status": "Open"}])
    sf._CFG["inbox"] = lambda: inbox
    lst, _ = sf._render("Open", "All apps")
    assert "strength-rota" in str(lst) and "from rota" in str(lst) and "sfb-done" not in str(lst)
    sf._CFG["inbox"] = None
    lst, _ = sf._render("Open", "All apps")                           # no inbox configured: this app only
    assert "from rota" not in str(lst)


def test_page_opens_on_all_when_nothing_is_open(store):
    """10 requests all done showed an empty 'No open requests.' with no tick boxes (2026-09-28)."""
    store.add("P", "x")
    assert "value='Open'" in str(sf.site_feedback_page())
    store.rows[0]["status"] = "Done"
    assert "value='All'" in str(sf.site_feedback_page())


def test_layout_pieces_render(store):
    assert "sfb-fab" in str(sf.site_feedback_button()) and "sfb-drawer" in str(sf.site_feedback_button())
    page = str(sf.site_feedback_page())
    assert "sfb-filter" in page and "'display': 'none'" in page         # no inbox: scope toggle hidden
    sf._CFG["inbox"] = lambda: pd.DataFrame(columns=COLS)
    assert "'display': 'none'" not in str(sf.site_feedback_page())
    assert sf._when("2026-09-28 05:21") == "28-Sep-2026 08:21"


def test_register_wires_callbacks_once_in_a_real_app(store):
    app = dash.Dash(__name__)
    sf._REGISTERED["done"] = False
    sf.register_site_feedback(store, toast_trigger="fly-toast-trigger")
    sf.register_site_feedback(store, toast_trigger="fly-toast-trigger")          # idempotent
    outs = " ".join(k for k in dash._callback.GLOBAL_CALLBACK_MAP)
    assert "sfb-list.children" in outs and "sfb-page.options" in outs and "sfb-drawer.className" in outs
    assert app is not None


def test_css_lets_the_app_move_the_button():
    """04_site_feedback.css loads AFTER app CSS: a :root default there overrode the app's --sfb-bottom and
    put the pill under the medical app's chat button (e2e, 2026-09-28). Fallbacks live in var() only."""
    from pathlib import Path
    css = (Path(sf.__file__).parent / "assets" / "04_site_feedback.css").read_text(encoding="utf-8")
    rules = css.split("*/", 1)[1]
    assert "--sfb-bottom:" not in rules and "var(--sfb-bottom, 24px)" in rules
