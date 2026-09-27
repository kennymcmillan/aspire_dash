"""v0.95: fly toast (no close button) + tables that never cut text (Kenny 2026-09-27)."""
from __future__ import annotations

from pathlib import Path

import dash
from dash import Dash, html

from aspire_dash.components import dispatch_fly_toast, fly_toast, register_fly_toast, render_fly_toast
from aspire_dash.tables import DEFAULT_COL_DEF, DEFAULT_GRID_OPTIONS, aspire_datatable, datatable_autofit

CSS = (Path(__file__).resolve().parents[1] / "aspire_dash" / "assets" / "00_aspire_base.css").read_text(encoding="utf-8")


# ── fly toast ────────────────────────────────────────────────────────────────
def test_fly_toast_host_has_store_and_live_region():
    host = fly_toast()
    ids = {c.id for c in host.children}
    assert ids == {"fly-toast", "fly-toast-trigger"}
    assert host.children[1].className == "fly-toast-host"


def test_render_restarts_per_message_and_has_nothing_to_press():
    a, b = render_fly_toast(dispatch_fly_toast("Preparing…")), render_fly_toast(dispatch_fly_toast("Done", "x", "success"))
    assert a.key != b.key                                         # new key = remount = animation restarts
    assert b.className == "fly-toast fly-toast--success"
    assert "Button" not in str(a) + str(b)
    assert render_fly_toast({"header": "h", "icon": "<x>", "ts": 1}).className.endswith("--primary")
    assert render_fly_toast(None) is dash.no_update


def test_register_fly_toast_wires_trigger_to_host():
    app = Dash(__name__)
    app.layout = html.Div(fly_toast("t-host", "t-trig"))
    register_fly_toast(app, "t-host", "t-trig")
    assert any("t-host.children" in k for k in app.callback_map)


def test_fly_toast_css_flies_out_on_its_own():
    assert "@keyframes fly-toast" in CSS and "visibility: hidden" in CSS
    assert "prefers-reduced-motion" in CSS


# ── DataTable autofit ────────────────────────────────────────────────────────
COLS = [{"name": "Name", "id": "name"}, {"name": "Date of injury", "id": "date"},
        {"name": "Last SAMS comment", "id": "comment"}]
ROWS = [{"name": "Abdulrahman Al-Kuwari", "date": "25-Jul-2026", "comment": "Rehab phase two progressing well"},
        {"name": "Ali", "date": "01-Sep-2026", "comment": "Supercalifragilisticexpialidocious" * 3}]


def _min(fit, cid):
    return int(next(r["minWidth"] for r in fit["style_cell_conditional"] if r["if"]["column_id"] == cid)[:-2])


def test_autofit_min_width_is_longest_word_not_whole_text():
    fit = datatable_autofit(COLS, ROWS)
    assert _min(fit, "name") < _min(fit, "comment")               # "Abdulrahman" vs a huge word
    assert _min(fit, "comment") == 280                            # capped: breaks instead of clipping
    assert fit["style_cell"]["whiteSpace"] == "normal" and fit["style_cell"]["overflowWrap"] == "anywhere"
    assert fit["style_table"]["overflowX"] == "auto"              # scrolls inside its own box


def test_autofit_nowrap_column_fits_whole_text_and_header():
    fit = datatable_autofit(COLS, ROWS, nowrap=("date",))
    date_rule = next(r for r in fit["style_cell_conditional"] if r["if"]["column_id"] == "date")
    assert date_rule["whiteSpace"] == "nowrap"
    assert _min(fit, "date") >= int(len("Date of injury") * 7.6)   # the one-line header fits
    assert {"if": {"column_id": "date"}, "whiteSpace": "nowrap"} in fit["style_header_conditional"]


def test_autofit_header_word_sets_floor_for_empty_column():
    fit = datatable_autofit([{"name": "Tissue classification", "id": "t"}], [])
    assert _min(fit, "t") >= int(len("classification") * 7.6)


def test_aspire_datatable_autofits_by_default_and_keeps_brand_styles():
    t = aspire_datatable("x", ROWS, COLS)
    assert t.style_cell["whiteSpace"] == "normal" and t.style_cell["fontFamily"].startswith("Inter")
    ids = [r["if"]["column_id"] for r in t.style_cell_conditional]
    assert {"name", "date", "comment"} <= set(ids)
    assert t.style_cell_conditional[-1] == {"if": {"column_id": "name"}, "textAlign": "left"}   # brand rule kept
    off = aspire_datatable("y", ROWS, COLS, autofit=False)
    assert "whiteSpace" not in off.style_cell


def test_ag_grid_defaults_never_cut_text():
    assert DEFAULT_COL_DEF["wrapHeaderText"] and DEFAULT_COL_DEF["autoHeaderHeight"]
    assert DEFAULT_GRID_OPTIONS["autoSizeStrategy"] == {"type": "fitCellContents"}
