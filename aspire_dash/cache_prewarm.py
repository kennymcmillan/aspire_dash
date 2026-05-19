"""Fire-and-forget cache pre-warming for Dash apps.

Pattern: data-bound pages cache via cachetools.TTLCache (or similar)
so the second visit is fast. The FIRST visit pays the latency of the
upstream API call(s). Pre-warming the cache during Dash boot
eliminates that — by the time a user lands on the page, the cache is
populated.

Usage in app.py (after setup_app):

    from aspire_dash.cache_prewarm import cache_prewarm
    from app.data.sams import list_sport_roster, SPORTS

    cache_prewarm(
        name="sams-rosters",
        fns=[(list_sport_roster, (sid,), {}) for sid in SPORTS],
    )

Each entry in fns is (callable, args, kwargs). Calls are made
sequentially in a daemon thread; one slow / failing call doesn't
block the others (errors logged + swallowed). Idempotent — a second
cache_prewarm() with the same name is a no-op until the process
restarts.
"""
from __future__ import annotations

import logging
import threading
from time import monotonic
from typing import Any, Callable, Iterable

log = logging.getLogger("aspire_dash.cache_prewarm")

# Guard set keyed by name — prevents the same prewarm from running
# twice within a single process.
_STARTED: set[str] = set()


def cache_prewarm(
    name: str,
    fns: Iterable[tuple[Callable, tuple, dict] | Callable],
    *,
    sequential: bool = True,
) -> None:
    """Spawn a daemon thread that calls each function once to warm
    whatever cache they populate.

    Parameters
    ----------
    name : str
        Unique name for this prewarm batch (for the idempotency guard
        and log messages). Use a stable string like "sams-rosters".
    fns : iterable
        Each item is either a bare callable (called with no args) OR a
        (callable, args, kwargs) tuple.
    sequential : bool, default True
        Run calls one after another. False → spawn one thread per
        callable (use with care; concurrent SAMS calls can hit rate
        limits).

    Behavior:
      - Returns immediately (work happens in the daemon thread).
      - Idempotent within a single process (re-call with same name
        is a no-op).
      - Daemon thread, so process exit doesn't wait on it.
      - Per-call exceptions are caught + logged; subsequent calls
        still run.
    """
    if name in _STARTED:
        return
    _STARTED.add(name)

    # Normalise each entry to (callable, args, kwargs)
    spec: list[tuple[Callable, tuple, dict]] = []
    for item in fns:
        if callable(item):
            spec.append((item, (), {}))
        else:
            fn, args, kwargs = item  # raises if shape is wrong
            spec.append((fn, args, kwargs))

    def _worker():
        t0 = monotonic()
        for fn, args, kwargs in spec:
            label = f"{fn.__module__}.{fn.__name__}{args!r}"
            try:
                fn(*args, **kwargs)
                log.info("[%s] OK  %s", name, label)
            except Exception as e:  # noqa: BLE001
                log.warning("[%s] FAIL %s: %s", name, label, e)
        log.info("[%s] complete in %.1fs (%d call%s)",
                 name, monotonic() - t0, len(spec),
                 "" if len(spec) == 1 else "s")

    if sequential:
        threading.Thread(target=_worker, name=f"prewarm-{name}",
                          daemon=True).start()
    else:
        # Fan out — one thread per call
        for fn, args, kwargs in spec:
            def _one(fn=fn, args=args, kwargs=kwargs):
                try:
                    fn(*args, **kwargs)
                except Exception as e:  # noqa: BLE001
                    log.warning("[%s] FAIL %s.%s: %s",
                                name, fn.__module__, fn.__name__, e)
            threading.Thread(target=_one,
                              name=f"prewarm-{name}-{fn.__name__}",
                              daemon=True).start()
