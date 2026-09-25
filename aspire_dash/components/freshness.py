"""'Data as of HH:MM' header badge (v0.92). Pairs with aspire_data.cache (>= 0.22.0):
every ttl_cache records when its data was fetched, and the badge shows the OLDEST
still-cached fetch, so a coach can see at a glance how fresh the screen is. If
anything ever goes stale again, it is visible instead of silent.

    from aspire_dash.components import header, data_as_of_badge, register_data_as_of
    header(title="Squad", right_content=data_as_of_badge())
    register_data_as_of(app)                       # all ttl_cache readers
    register_data_as_of(app, fns=(aerobic, vald))  # or just this page's readers

Times are shown in Asia/Qatar whatever the server clock is.
"""
from __future__ import annotations

import datetime as _dt
from zoneinfo import ZoneInfo

from dash import Input, Output, dcc, html

DEFAULT_ID = "aspire-data-as-of"
_QATAR = ZoneInfo("Asia/Qatar")


def data_as_of_badge(id: str = DEFAULT_ID, every_s: int = 60):
    """The badge + its refresh tick. Place it in ``header(right_content=...)``."""
    return html.Span([
        html.Span("", id=id, className="aspire-asof", title=""),
        dcc.Interval(id=f"{id}-tick", interval=every_s * 1000, n_intervals=0),
    ])


def data_as_of_text(ts: float | None, *, now: float | None = None,
                    stale_after: int = 3600, tz=_QATAR) -> tuple[str, str, str]:
    """(text, className, title) for an epoch fetch time. Pure, for tests."""
    if ts is None:
        return ("Live data", "aspire-asof",
                "Nothing cached yet: this page reads straight from the source.")
    now = now if now is not None else _dt.datetime.now(tz).timestamp()
    t = _dt.datetime.fromtimestamp(ts, tz)
    age = max(0, int(now - ts))
    stale = age > stale_after
    mins = age // 60
    ago = "just now" if mins < 1 else f"{mins} min ago" if mins < 90 else f"{mins // 60} h ago"
    title = (f"Oldest data on this page was fetched {ago}. Live data refreshes every "
             "15 min on its own; use Refresh for the latest now.")
    return (f"Data as of {t:%H:%M}", "aspire-asof aspire-asof--stale" if stale else "aspire-asof",
            title)


def register_data_as_of(app, id: str = DEFAULT_ID, fns=(), stale_after: int = 3600):
    """Wire the badge. ``fns``: the ttl_cache readers behind this screen (default:
    every ttl_cache in the process). Needs aspire_data >= 0.22.0; without it the
    badge stays blank rather than failing the app."""

    @app.callback(Output(id, "children"), Output(id, "className"), Output(id, "title"),
                  Input(f"{id}-tick", "n_intervals"))
    def _asof(_n):
        try:
            from aspire_data.cache import data_as_of
        except ImportError:
            return "", "aspire-asof", ""
        return data_as_of_text(data_as_of(*fns), stale_after=stale_after)

    return _asof
