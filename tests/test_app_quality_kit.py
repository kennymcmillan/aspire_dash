"""v0.100 app-quality kit: section_tabs, fold, page_head, setup_app(quality=True).

The kit's assets are copied to EVERY app by setup_app() (like all shared assets),
so the contract tested here is: without the opt-in they are inert (CSS part B
only matches under .aspire-quality, the JS gates on it, section_tabs/fold CSS only
matches classes that existing components never render), and an app that does not
opt in gets the same index page, header and layout as before.
"""
import importlib
import re
import subprocess
import sys
from pathlib import Path

import dash
import dash_bootstrap_components as dbc
import pytest
from dash import Dash, html

from aspire_dash import _ASSETS_DIR, _quality_index_string, setup_app
from aspire_dash.components import fold, header, page_head, section_tabs, sidebar
from aspire_dash.layouts import page_layout

NEW_ASSETS = ("05_aspire_quality.css", "aspire_section_tabs.js", "aspire_quality.js")


def _walk(node):
    yield node
    kids = getattr(node, "children", None)
    if kids is None:
        return
    for k in kids if isinstance(kids, (list, tuple)) else [kids]:
        if hasattr(k, "to_plotly_json"):
            yield from _walk(k)


# ---------- components ----------

def test_section_tabs_renders_every_pane_and_defaults_to_first():
    t = section_tabs("t1", [("One", "a", html.P("A")), ("Two", "b", html.P("B")), ("Gone", "c", None)])
    assert isinstance(t, dbc.Tabs)
    assert t.id == "t1" and t.active_tab == "a"
    assert "aspire-section-tabs" in t.className and "aspire-section-tabs--main" in t.className
    assert [tab.tab_id for tab in t.children] == ["a", "b"]          # None children skipped
    assert all(tab.label_class_name == "aspire-section-tab" for tab in t.children)


def test_section_tabs_sub_active_and_icon():
    t = section_tabs("t2", [("One", "a", html.P("A"), None), ("Two", "b", html.P("B"), "/assets/x.svg")],
                     active="b", sub=True)
    assert t.active_tab == "b"
    assert "aspire-section-tabs--sub" in t.className and "--main" not in t.className
    plain, icon = t.children
    assert "--icon" not in plain.label_class_name
    assert "aspire-section-tab--icon" in icon.label_class_name
    assert icon.label_style == {"--aspire-tab-icon": "url('/assets/x.svg')"}


def test_section_tabs_empty_is_harmless():
    assert isinstance(section_tabs("t3", [("x", "x", None)]), html.Div)


def test_fold_is_a_closed_details_with_title_and_icon():
    f = fold("About", html.P("body"), icon="fa-solid fa-circle-info")
    assert isinstance(f, html.Details) and f.className == "aspire-fold" and f.open is False
    summary, body = f.children
    assert isinstance(summary, html.Summary)
    assert any(isinstance(n, html.I) and "fa-circle-info" in n.className for n in _walk(summary))
    assert any(isinstance(n, html.Span) and n.children == "About" for n in _walk(summary))
    assert body.className == "aspire-fold__body"
    assert fold("x", "y", open=True).open is True


def test_page_head_has_h1_lead_and_right_slot():
    h = page_head("Squad", lead="Who is fit", right=html.Button("Export"))
    nodes = list(_walk(h))
    assert any(isinstance(n, html.H1) and n.children == "Squad" for n in nodes)
    assert any(isinstance(n, html.P) and n.children == "Who is fit" for n in nodes)
    assert any(getattr(n, "className", "") == "aspire-page-head__right" for n in nodes)
    bare = page_head("Squad")
    assert not any(isinstance(n, html.P) for n in _walk(bare))
    assert not any(getattr(n, "className", "") == "aspire-page-head__right" for n in _walk(bare))


def test_header_subtitle_has_stable_id_and_is_hidden_when_empty():
    def sub(h):
        return next(n for n in _walk(h) if getattr(n, "id", None) == "aspire-page-subtitle")
    empty = sub(header(title="T"))
    assert empty.style.get("display") == "none" and not empty.children
    full = sub(header(title="T", subtitle="S"))
    assert full.children == "S" and "display" not in full.style


# ---------- opt-in mechanism ----------

def test_new_assets_ship_with_the_library():
    for f in NEW_ASSETS:
        assert (Path(_ASSETS_DIR) / f).is_file(), f


def test_setup_app_without_opt_in_leaves_app_unchanged(tmp_path):
    """Existing-app smoke: assets are copied (harmlessly, see module doc), but the index
    page, update_title and the layout carry no opt-in marker."""
    app = Dash(__name__, assets_folder=str(tmp_path / "assets"))
    before_index, before_title = app.index_string, app.config.update_title
    setup_app(app)
    assert app.index_string == before_index
    assert app.config.update_title == before_title
    for f in NEW_ASSETS:
        assert (tmp_path / "assets" / f).is_file()
    layout = page_layout(sidebar(title="X", nav_items=[{"label": "H", "href": "/"}]), header(title="X"))
    assert "aspire-quality" not in str(layout.to_plotly_json())


def test_setup_app_quality_marks_html_and_sets_label(tmp_path):
    app = Dash(__name__, assets_folder=str(tmp_path / "assets"))
    setup_app(app, quality=True, loading_label='My "App"')
    html_tag = re.search(r"<html[^>]*>", app.index_string).group(0)
    assert 'class="aspire-quality"' in html_tag and 'lang="en"' in html_tag
    assert "--aspire-loading-label:\"My 'App'\"" in app.index_string
    assert app.config.update_title is None
    setup_app(app, quality=True, loading_label="Again")             # idempotent
    assert app.index_string.count("aspire-quality") == 1
    assert app.index_string.count("--aspire-loading-label") == 1


def test_quality_index_string_keeps_existing_html_attrs():
    out = _quality_index_string('<html lang="ar" class="dark"><head></head></html>')
    tag = re.search(r"<html[^>]*>", out).group(0)
    assert 'class="dark aspire-quality"' in tag and 'lang="ar"' in tag and 'lang="en"' not in tag


def test_opt_in_css_is_scoped_to_the_class():
    """Every rule in PART B of the CSS must sit under .aspire-quality (the skip link only
    exists when the gated JS creates it), so non-opted apps are untouched."""
    css = (Path(_ASSETS_DIR) / "05_aspire_quality.css").read_text(encoding="utf-8")
    part_b = css.split("PART B: opt-in", 1)[1]
    part_b = re.sub(r"/\*.*?\*/", "", part_b, flags=re.S)
    part_b = re.sub(r"@keyframes[^{]*\{(?:[^{}]*\{[^}]*\})*[^}]*\}", "", part_b)
    selectors = []
    for m in re.finditer(r"([^{}]+)\{", part_b):
        sel = m.group(1).strip()
        if not sel or sel.startswith("@media"):
            continue
        selectors += [s.strip() for s in sel.split(",")]
    assert selectors, "parsed no selectors"
    bad = [s for s in selectors if ".aspire-quality" not in s and not s.startswith(".aspire-skip")]
    assert bad == [], bad


def test_part_a_css_only_targets_new_component_classes():
    css = (Path(_ASSETS_DIR) / "05_aspire_quality.css").read_text(encoding="utf-8")
    part_a = re.sub(r"/\*.*?\*/", "", css.split("PART B: opt-in", 1)[0], flags=re.S)
    selectors = []
    for m in re.finditer(r"([^{}]+)\{", part_a):
        sel = m.group(1).strip()
        if sel.startswith("@media"):
            continue
        selectors += [s.strip() for s in sel.split(",")]
    allowed = (":root", "html.dark")
    bad = [s for s in selectors
           if not (s.startswith(allowed) or ".aspire-section-tab" in s or ".aspire-fold" in s or ".aspire-page-head" in s)]
    assert bad == [], bad


def test_quality_js_is_gated_and_tabs_js_is_class_scoped():
    q = (Path(_ASSETS_DIR) / "aspire_quality.js").read_text(encoding="utf-8")
    assert 'if (!on()) { return; }' in q and 'classList.contains("aspire-quality")' in q
    t = (Path(_ASSETS_DIR) / "aspire_section_tabs.js").read_text(encoding="utf-8")
    assert 'var SEL = ".aspire-section-tabs";' in t
    # no global selector work outside SEL apart from measuring the header
    assert "querySelectorAll(\".nav-link" not in t


# ---------- scaffold ----------

@pytest.fixture
def _isolated_dash(monkeypatch):
    from dash import _callback
    monkeypatch.setattr(_callback, "GLOBAL_CALLBACK_LIST", [])
    monkeypatch.setattr(dash, "page_registry", {})


def test_scaffold_opts_in_and_passes_baseline(tmp_path, monkeypatch, _isolated_dash):
    from aspire_dash import testing as T
    monkeypatch.chdir(tmp_path)
    r = subprocess.run([sys.executable, "-m", "aspire_dash", "new", "qk_app", "--title", "QK App"],
                       capture_output=True, text=True, timeout=60,
                       cwd=str(tmp_path), env={**__import__("os").environ,
                                               "PYTHONPATH": str(Path(__file__).resolve().parents[1])})
    assert r.returncode == 0, r.stderr
    app_dir = tmp_path / "qk_app"
    app_src = (app_dir / "app.py").read_text(encoding="utf-8")
    assert 'setup_app(app, quality=True, loading_label="QK App")' in app_src
    home = (app_dir / "pages" / "home.py").read_text(encoding="utf-8")
    assert "section_tabs(" in home and "sub=True" in home and "fold(" in home and "page_head(" in home

    monkeypatch.chdir(app_dir)
    monkeypatch.syspath_prepend(str(app_dir))
    for mod in list(sys.modules):
        if mod == "app" or mod.startswith("pages"):
            sys.modules.pop(mod, None)
    mod = importlib.import_module("app")
    try:
        assert "aspire-quality" in mod.app.index_string
        assert T.baseline_problems(mod.app, root=str(app_dir)) == []
    finally:
        for m in list(sys.modules):
            if m == "app" or m.startswith("pages"):
                sys.modules.pop(m, None)
