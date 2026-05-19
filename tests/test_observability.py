"""Observability module — counters, timed decorator, configure()."""
import logging
import time

import pytest


@pytest.fixture(autouse=True)
def _reset():
    from aspire_dash import observability
    observability._metrics.clear()
    yield
    observability._metrics.clear()


def test_configure_idempotent():
    from aspire_dash.observability import configure
    configure(); configure(); configure()
    root = logging.getLogger()
    assert getattr(root, "_aspire_dash_configured", False)


def test_bump_increments():
    from aspire_dash.observability import bump, get_metrics
    bump("x")
    bump("x", 4)
    bump("y")
    m = get_metrics()
    assert m["x"] == 5
    assert m["y"] == 1


def test_reset_metrics_clears():
    from aspire_dash.observability import bump, reset_metrics, get_metrics
    bump("x")
    reset_metrics()
    assert get_metrics() == {}


def test_timed_counts_calls():
    from aspire_dash.observability import timed, get_metrics

    @timed("demo")
    def f(x):
        return x + 1

    f(1); f(2)
    m = get_metrics()
    assert m["callback.demo.calls"] == 2


def test_timed_counts_errors():
    from aspire_dash.observability import timed, get_metrics

    @timed("blowup")
    def f():
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        f()
    m = get_metrics()
    assert m["callback.blowup.errors"] == 1


def test_timed_flags_slow():
    from aspire_dash import observability
    original = observability.SLOW_CALLBACK_MS
    observability.SLOW_CALLBACK_MS = 10
    try:
        @observability.timed("slow")
        def f():
            time.sleep(0.05)

        f()
        m = observability.get_metrics()
        assert m["callback.slow.slow"] == 1
    finally:
        observability.SLOW_CALLBACK_MS = original


def test_timed_preserves_metadata():
    from aspire_dash.observability import timed

    @timed("named")
    def fn():
        """my docstring"""
        return 1

    assert fn.__name__ == "fn"
    assert "my docstring" in (fn.__doc__ or "")
