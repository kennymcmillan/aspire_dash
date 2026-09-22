"""v0.90 hover-out popouts promoted from endurance-dashboard.

Covers the test-history column chart (chips + leader lines + best ring) and the
modal / hover-card BUILDERS returning the right Dash components. Deterministic,
no network, no Dash app needed."""
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dcc, html

from aspire_dash.charts import history_figure, _repel_1d
from aspire_dash.components import (history_trigger, history_modal,
                                    hovercard_graph, render_card, HOVERCARD_ARROW)

VALUE_BOX = "#0a5ba8"   # the navy chip bg history_figure boxes each value in


# ── history_figure ───────────────────────────────────────────────────────────

def _chip_annotations(fig):
    return [a for a in fig.layout.annotations if a.bgcolor == VALUE_BOX]


def test_history_figure_boxes_a_value_chip_on_every_bar():
    series = [("2026-01-01", 30.0), ("2026-03-01", 32.0), ("2026-06-01", 35.0)]
    fig = history_figure(series, unit="cm", title="CMJ")
    chips = _chip_annotations(fig)
    assert len(chips) == 3                          # one chip per bar
    assert [c.text for c in chips] == ["30.0", "32.0", "35.0"]
    assert all(c.font.color == "white" for c in chips)


def test_history_figure_one_bar_trace_best_test_gold_ringed():
    series = [("2026-01-01", 30.0), ("2026-03-01", 35.0), ("2026-06-01", 32.0)]
    fig = history_figure(series, unit="cm", title="CMJ")
    bars = [t for t in fig.data if t.type == "bar"]
    assert len(bars) == 1
    # best (max) is index 1; it carries the gold ring (width 2.5) and gold colour
    widths = list(bars[0].marker.line.width)
    assert widths[1] == 2.5 and max(widths) == 2.5 and widths.count(2.5) == 1
    assert bars[0].marker.line.color[1].lower() == "#fbb800"   # GOLD token


def test_history_figure_lower_is_better_rings_the_minimum():
    series = [("2026-01-01", 12.0), ("2026-03-01", 11.5), ("2026-06-01", 12.2)]
    fig = history_figure(series, unit="s", lower_is_better=True, title="Sprint")
    bars = [t for t in fig.data if t.type == "bar"][0]
    widths = list(bars.marker.line.width)
    assert widths.index(2.5) == 1                   # the fastest (min) test is best


def test_history_figure_draws_a_leader_line_when_labels_collide():
    # mean and the benchmark coincide -> the right-margin labels must fan out, which
    # draws a diagonal leader line (y0 != y1) back to the rule's true height.
    series = [("2026-01-01", 10.0), ("2026-03-01", 10.0), ("2026-06-01", 10.0)]
    fig = history_figure(series, unit="cm", title="X", benchmarks=[("PB", 10.0)])
    leaders = [s for s in fig.layout.shapes if s.type == "line" and s.y0 != s.y1]
    assert len(leaders) >= 1


def test_history_figure_empty_series_shows_placeholder():
    fig = history_figure([], unit="cm", title="CMJ")
    assert any("No test history" in (a.text or "") for a in fig.layout.annotations)
    assert not [t for t in fig.data if t.type == "bar"]


def test_history_figure_unit_none_does_not_crash():
    fig = history_figure([("2026-01-01", 5.0), ("2026-02-01", 6.0)], unit=None)
    assert [t for t in fig.data if t.type == "bar"]


def test_repel_1d_spreads_close_values_by_at_least_the_gap():
    out = _repel_1d([1.0, 1.0, 1.0], lo=0.0, hi=10.0, gap=1.0)
    assert out[1] - out[0] >= 1.0 - 1e-9
    assert out[2] - out[1] >= 1.0 - 1e-9


# ── history modal + trigger builders ─────────────────────────────────────────

def test_history_trigger_is_a_clickable_pattern_card():
    node = history_trigger("cmj", html.Div("card body"))
    assert isinstance(node, html.Div)
    assert node.className == "hist-clickable"
    assert node.id == {"type": "hist-card", "index": "cmj"}
    assert node.n_clicks == 0


def test_history_modal_returns_store_plus_modal():
    figures = {"cmj": {"title": "CMJ", "label": "CMJ", "unit": "cm",
                       "series": [("2026-01-01", 30.0)]}}
    node = history_modal(figures)
    assert isinstance(node, html.Div)
    store, modal = node.children
    assert isinstance(store, dcc.Store) and store.id == "hist-fig-store"
    assert store.data == figures
    assert isinstance(modal, dbc.Modal) and modal.id == "hist-modal"
    assert modal.is_open is False


# ── hover card builders ──────────────────────────────────────────────────────

def _fig_with_line():
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[1, 2, 3], y=[10, 11, 12], mode="lines+markers"))
    return fig


def test_hovercard_graph_wraps_graph_card_and_tooltip():
    metas = [{"name": "A"}, {"name": "B"}, {"name": "C"}]
    node = hovercard_graph(_fig_with_line(), index="cmj", metas=metas, title="CMJ")
    assert isinstance(node, html.Div) and node.className == "hovercard-wrap"
    card, tip = node.children
    assert isinstance(tip, dcc.Tooltip)
    assert tip.id == {"type": "hovercard-tip", "index": "cmj"}
    # default arrow is the on-brand navy, not a red
    assert tip.background_color == HOVERCARD_ARROW == "#003566"


def test_hovercard_graph_arrow_color_param_overrides_default():
    node = hovercard_graph(_fig_with_line(), index="x", metas=[{"name": "A"}],
                           arrow_color="#123456")
    _, tip = node.children
    assert tip.background_color == "#123456" and tip.border_color == "#123456"


def test_hovercard_graph_stamps_customdata_on_the_line_trace():
    fig = _fig_with_line()
    metas = [{"name": "A"}, {"name": "B"}, {"name": "C"}]
    hovercard_graph(fig, index="cmj", metas=metas)
    cd = fig.data[0].customdata
    assert cd is not None and len(cd) == 3
    # each point carries its meta dict (plotly may wrap each in a 1-tuple/row)
    first = cd[0][0] if isinstance(cd[0], (list, tuple)) else cd[0]
    assert first == {"name": "A"}


def test_render_card_builds_the_branded_card():
    meta = {"name": "Jane Doe", "date": "2026-06-01",
            "headline": {"label": "CMJ", "value": "35.0", "unit": "cm", "delta": "+2.0"},
            "rows": [{"label": "RSI", "value": "1.3", "delta": "+0.1"}]}
    card = render_card(meta)
    assert isinstance(card, html.Div) and card.className == "hover-card"


def test_render_card_accepts_a_json_string():
    import json
    card = render_card(json.dumps({"name": "X", "headline": {"label": "L", "value": "1"}}))
    assert card.className == "hover-card"
