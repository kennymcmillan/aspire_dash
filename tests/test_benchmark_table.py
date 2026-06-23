"""benchmark_table + percentile_badge: the tabular age-band benchmarking view.

Consumes aspire_data.benchmarks.best_pb_by_ageband(with_percentile=True) rows.
Pure composition over data_table + color_badge (no new CSS).
"""
from __future__ import annotations

from dash.development.base_component import Component

from aspire_dash.sports import benchmark_table, percentile_badge
from aspire_dash.theme import SEMANTIC_PALETTE


def _rows():
    return [
        {"age_band_label": "12.5 - 13.5", "mark": 5.50, "date": "2023-04-01",
         "n": 2, "percentile": 48},
        {"age_band_label": "13.5 - 14.5", "mark": 6.00, "date": "2024-01-01",
         "n": 1, "percentile": 92},
    ]


def _texts(node):
    """All text leaves in a Dash component tree."""
    acc = []

    def rec(n):
        if n is None:
            return
        if isinstance(n, (str, int, float)):
            acc.append(str(n))
        elif isinstance(n, (list, tuple)):
            for c in n:
                rec(c)
        elif isinstance(n, Component):
            rec(getattr(n, "children", None))

    rec(node)
    return acc


# ---------- percentile_badge tones ----------

def test_badge_tone_by_tier():
    assert percentile_badge(92).style["backgroundColor"] == SEMANTIC_PALETTE["gold"]["bg"]
    assert percentile_badge(80).style["backgroundColor"] == SEMANTIC_PALETTE["success"]["bg"]
    assert percentile_badge(60).style["backgroundColor"] == SEMANTIC_PALETTE["info"]["bg"]
    assert percentile_badge(40).style["backgroundColor"] == SEMANTIC_PALETTE["warning"]["bg"]
    assert percentile_badge(10).style["backgroundColor"] == SEMANTIC_PALETTE["danger"]["bg"]


def test_badge_text_and_missing():
    assert percentile_badge(78).children == "78th"
    miss = percentile_badge(None)
    assert miss.children == "—"
    assert miss.style["backgroundColor"] == SEMANTIC_PALETTE["neutral"]["bg"]


# ---------- benchmark_table ----------

def test_table_renders_bands_dates_and_percentiles():
    texts = _texts(benchmark_table(_rows()))
    for expect in ("Age band", "Best PB", "Date", "Tests", "Percentile",
                   "12.5 - 13.5", "13.5 - 14.5", "Apr 2023", "Jan 2024",
                   "5.50", "6.00", "48th", "92th"):
        assert expect in texts, f"missing {expect!r}"


def test_time_value_format():
    rows = [{"age_band_label": "15.5 - 16.5", "mark": 110.0,
             "date": "2026-03-01", "n": 3, "percentile": 75}]
    texts = _texts(benchmark_table(rows, value_format="time", value_label="Best time"))
    assert "1:50.00" in texts
    assert "Best time" in texts


def test_show_tests_false_drops_column():
    texts = _texts(benchmark_table(_rows(), show_tests=False))
    assert "Tests" not in texts
    assert "Percentile" in texts
