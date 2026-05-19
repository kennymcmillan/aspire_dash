"""Structured logging + callback timing for Aspire Dash apps.

Posit Connect captures stdout/stderr per process, so we just need a clean
log format and the ability to flag slow callbacks. This module is
zero-dependency (stdlib only).

Usage at app startup::

    from aspire_dash.observability import configure
    configure()

In any callback::

    from aspire_dash.observability import timed

    @callback(Output(...), Input(...))
    @timed("update_chart")
    def update_chart(...):
        ...

Process-lifetime counters (cache hits, 429s, slow callbacks) are available
via ``get_metrics()`` — wire to a ``/__health`` endpoint if you want to
expose them.

Environment knobs:
  LOG_LEVEL          default INFO
  SLOW_CALLBACK_MS   default 3000  (warn when a @timed callback exceeds this)
"""
from __future__ import annotations

import logging
import os
import time
from collections import Counter
from functools import wraps
from typing import Callable

__all__ = [
    "configure", "timed", "bump", "get_metrics", "reset_metrics",
    "LOG_LEVEL", "SLOW_CALLBACK_MS",
]

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
SLOW_CALLBACK_MS = int(os.environ.get("SLOW_CALLBACK_MS", "3000"))

# Module-level metrics (process-lifetime counters). Visible via get_metrics().
_metrics: Counter = Counter()


def configure() -> None:
    """Configure the root logger once. Safe to call multiple times.

    Format: ``YYYY-MM-DDTHH:MM:SS LEVEL logger.name message``
    Werkzeug request log is quieted to WARNING.
    """
    root = logging.getLogger()
    if getattr(root, "_aspire_dash_configured", False):
        return
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    ))
    root.handlers = [handler]
    root.setLevel(LOG_LEVEL)
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    root._aspire_dash_configured = True  # type: ignore[attr-defined]
    logging.getLogger(__name__).info(
        "aspire_dash logging configured level=%s slow_threshold_ms=%d",
        LOG_LEVEL, SLOW_CALLBACK_MS,
    )


def get_metrics() -> dict[str, int]:
    """Snapshot of process-lifetime counters."""
    return dict(_metrics)


def bump(key: str, n: int = 1) -> None:
    """Increment a named counter. Use for cache hits, 429s, error tallies."""
    _metrics[key] += n


def reset_metrics() -> None:
    """Reset all counters. Mostly useful in tests."""
    _metrics.clear()


def timed(label: str) -> Callable:
    """Decorator: log callback duration; warn when over SLOW_CALLBACK_MS.

    Records three counters per labelled callback:
      - ``callback.{label}.calls``  — every invocation
      - ``callback.{label}.errors`` — exceptions raised
      - ``callback.{label}.slow``   — durations ≥ SLOW_CALLBACK_MS

    Use sparingly — every wrapped callback adds one log line per fire.
    Best for the heavy data-path callbacks (charts, group fetches, exports).
    """
    log = logging.getLogger("aspire_dash.callback")

    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            t0 = time.perf_counter()
            err = None
            try:
                return fn(*args, **kwargs)
            except Exception as e:
                err = e
                raise
            finally:
                dur_ms = (time.perf_counter() - t0) * 1000.0
                bump(f"callback.{label}.calls")
                if err is not None:
                    bump(f"callback.{label}.errors")
                    log.warning("callback=%s dur_ms=%.0f error=%s",
                                 label, dur_ms, type(err).__name__)
                elif dur_ms >= SLOW_CALLBACK_MS:
                    bump(f"callback.{label}.slow")
                    log.warning("callback=%s dur_ms=%.0f (slow > %dms)",
                                 label, dur_ms, SLOW_CALLBACK_MS)
                else:
                    log.debug("callback=%s dur_ms=%.0f", label, dur_ms)
        return wrapper
    return deco
