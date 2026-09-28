"""aspire_dash.testing (v0.95): the shared baseline must catch planted bugs and pass a
clean app. Each app runs baseline_problems(app.app, root='.') == []."""
import dash
from dash import Dash, Input, Output, dcc, html

import pytest

from aspire_dash import testing as T


@pytest.fixture(autouse=True)
def _isolated_global_callbacks(monkeypatch):
    """Other test modules (and aspire_dash's own auto-registered popouts) put callbacks
    on Dash's global list; each kit test must only see the app it builds."""
    from dash import _callback
    monkeypatch.setattr(_callback, "GLOBAL_CALLBACK_LIST", [])
    monkeypatch.setattr(dash, "page_registry", {})


def _fresh(tmp_path, src: str):
    (tmp_path / "app_src.py").write_text(src, encoding="utf-8")
    return tmp_path


def test_clean_app_passes(tmp_path):
    app = Dash(__name__)
    app.layout = html.Div([dcc.Input(id="kit-in"), html.Div(id="kit-out")])

    @app.callback(Output("kit-out", "children"), Input("kit-in", "value"))
    def _f(v):
        return v
    root = _fresh(tmp_path, 'html.Div(id="kit-out")')
    assert T.callback_target_problems(app, root=root) == []
    assert T.duplicate_output_problems(app) == []


def test_missing_target_is_caught(tmp_path):
    """Output points at an id nothing creates (renamed/deleted): page would blank."""
    app = Dash(__name__)
    app.layout = html.Div([dcc.Input(id="kit-in2")])

    @app.callback(Output("kit-renamed-away", "children"), Input("kit-in2", "value"))
    def _f(v):
        return v
    probs = T.callback_target_problems(app, root=_fresh(tmp_path, "x = 1"))
    assert any("kit-renamed-away" in p for p in probs)


def test_target_built_in_a_callback_counts_via_source(tmp_path):
    """Components built inside callbacks (not in a static layout) are fine."""
    app = Dash(__name__)
    app.layout = html.Div([dcc.Input(id="kit-in3")])

    @app.callback(Output("kit-dynamic", "children"), Input("kit-in3", "value"))
    def _f(v):
        return v
    root = _fresh(tmp_path, 'def body():\n    return html.Div(id="kit-dynamic")\n')
    assert T.callback_target_problems(app, root=root) == []


def test_duplicate_output_is_caught():
    app = Dash(__name__)
    app.layout = html.Div([dcc.Input(id="kit-a"), dcc.Input(id="kit-b"), html.Div(id="kit-o")])

    @app.callback(Output("kit-o", "children"), Input("kit-a", "value"))
    def _f1(v):
        return v

    @app.callback(Output("kit-o", "children", allow_duplicate=True), Input("kit-b", "value"),
                  prevent_initial_call=True)
    def _f2(v):
        return v
    assert T.duplicate_output_problems(app) == []      # allow_duplicate is fine

    app2 = Dash(__name__)
    app2.layout = app.layout
    app2._callback_list = [dict(s) for s in app._callback_list[:1]] * 1 + [dict(app._callback_list[0])]  # two registrations
    assert any("kit-o.children" in p for p in T.duplicate_output_problems(app2))


def test_page_render_problem_is_caught(monkeypatch):
    def boom():
        raise ValueError("bad page")
    monkeypatch.setattr(dash, "page_registry", {"x": {"path": "/x", "layout": boom}})
    probs = T.page_render_problems()
    assert probs and "/x" in probs[0] and "bad page" in probs[0]
