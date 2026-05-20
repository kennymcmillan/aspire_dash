"""stats + timeseries — pure-Python helpers, easy to cover."""


# ── stats ──────────────────────────────────────────────────────────────────

def test_compute_stats_empty():
    from aspire_dash.stats import compute_stats
    s = compute_stats([])
    assert s["mean"] == 0.0
    assert s["n"] == 0


def test_compute_stats_basic():
    from aspire_dash.stats import compute_stats
    s = compute_stats([10, 20, 30])
    assert abs(s["mean"] - 20.0) < 1e-6
    assert s["std"] > 0
    assert s["min"] == 10
    assert s["max"] == 30
    assert s["n"] == 3


def test_compute_stats_zero_mean_safe_cv():
    """Avoid ZeroDivisionError when mean is 0."""
    from aspire_dash.stats import compute_stats
    s = compute_stats([0, 0, 0])
    assert s["cv"] == 0.0


def test_compute_stats_negative_values():
    """CMJ Countermovement Depth is stored as negative cm."""
    from aspire_dash.stats import compute_stats
    s = compute_stats([-30.0, -25.0, -28.0])
    assert s["mean"] < 0
    assert s["min"] == -30.0
    assert s["max"] == -25.0


# ── timeseries: chart-overlay builders ─────────────────────────────────────

def test_build_sd_traces_returns_5_traces():
    from aspire_dash.timeseries import build_sd_traces
    stats = {"mean": 20.0, "std": 5.0}
    out = build_sd_traces(["d1", "d2", "d3"], [10, 20, 30], stats)
    assert len(out) == 5  # ±2SD outer + ±1SD inner + mean line


def test_build_sd_traces_zero_std_empty():
    from aspire_dash.timeseries import build_sd_traces
    out = build_sd_traces(["d1"], [10], {"mean": 10, "std": 0})
    assert out == []


def test_build_4pt_ma_needs_window_points():
    from aspire_dash.timeseries import build_4pt_ma_traces
    assert build_4pt_ma_traces(["d1", "d2"], [1, 2]) == []
    out = build_4pt_ma_traces([f"d{i}" for i in range(4)], [1, 2, 3, 4])
    assert len(out) == 3  # upper band, lower band, rolling mean


def test_build_acute_traces_flags_outliers():
    from aspire_dash.timeseries import build_acute_traces
    dates = [f"d{i}" for i in range(5)]
    values = [10, 10.5, 10.2, 10.8, 50.0]  # last is huge outlier
    out = build_acute_traces(dates, values)
    # upper, lower, rolling mean + acute marker = 4
    assert len(out) == 4
    # Marker is named 'Acute' (not 'Alert') and is AMBER (not red) so users
    # don't mistake an acute-trend-break for an outside-±2 SD outlier.
    acute_marker = out[-1]
    assert acute_marker.name == "Acute"
    line_color = (acute_marker.marker.line.color or "").lower()
    # Should not be red (#ef4444 or any 'rgb(239,68,68)' variant)
    assert "239" not in line_color and "#ef" not in line_color, \
        f"acute marker should be amber, not red: {line_color}"


def test_build_acute_traces_uses_amber_not_red():
    """Regression: red dots used to fire on rolling ±1.5 SD which is
    tighter than the ±2 SD bands shown — users saw 'red dot inside band'
    and thought the chart was broken. Acute now uses amber."""
    from aspire_dash.timeseries import build_acute_traces, DEFAULT_COLORS
    dates = [f"d{i}" for i in range(6)]
    values = [10, 10.2, 10.1, 10.3, 12.0, 9.8]  # mild deviation
    out = build_acute_traces(dates, values)
    for tr in out:
        if getattr(tr, "name", "") == "Acute":
            color = tr.marker.line.color
            assert color == DEFAULT_COLORS["alert_amber"], \
                f"acute marker must be alert_amber, got {color}"


def test_build_main_line_trace_default_linear_not_spline():
    """Regression: spline shape was distorting discrete test data."""
    from aspire_dash.timeseries import build_main_line_trace
    tr = build_main_line_trace(["d1", "d2"], [10, 20])
    assert tr.line.shape == "linear"


# ── timeseries: session aggregator ─────────────────────────────────────────

def test_aggregate_sessions_max_for_trend_up():
    from aspire_dash.timeseries import aggregate_sessions
    rows = [
        {"date": "2026-01-01", "value": 30.0},
        {"date": "2026-01-01", "value": 32.0},  # same date — max wins
        {"date": "2026-01-15", "value": 28.0},
    ]
    out = aggregate_sessions(rows, trend_direction="up")
    assert out[0] == {"date": "2026-01-01", "value": 32.0}
    assert out[1]["value"] == 28.0


def test_aggregate_sessions_min_for_trend_down():
    """Contraction Time, Contact Time: lower=better → min wins."""
    from aspire_dash.timeseries import aggregate_sessions
    rows = [
        {"date": "2026-01-01", "value": 0.85},
        {"date": "2026-01-01", "value": 0.72},  # faster → keep
    ]
    out = aggregate_sessions(rows, trend_direction="down")
    assert out[0]["value"] == 0.72


def test_aggregate_sessions_none_defaults_to_max():
    from aspire_dash.timeseries import aggregate_sessions
    rows = [{"date": "2026-01-01", "value": 30.0},
             {"date": "2026-01-01", "value": 32.0}]
    out = aggregate_sessions(rows, trend_direction=None)
    assert out[0]["value"] == 32.0


def test_aggregate_sessions_sorts_output():
    from aspire_dash.timeseries import aggregate_sessions
    rows = [
        {"date": "2026-03-15", "value": 3.0},
        {"date": "2026-01-15", "value": 1.0},
        {"date": "2026-02-15", "value": 2.0},
    ]
    out = aggregate_sessions(rows)
    assert [r["date"] for r in out] == [
        "2026-01-15", "2026-02-15", "2026-03-15",
    ]
