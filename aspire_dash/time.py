"""Time-window controls and date helpers.

Patterns lifted from medical-dashboard, sams-training-dashboard,
sams-attendance-dashboard, and aspire-nutrition where each app had
reimplemented period pills, week snapping, and "X to Y" labels.

Usage::

    from aspire_dash.time import (
        period_pill_filter, period_mode_to_dates,
        sunday_of, format_period_label,
    )

    # Layout
    period_pill_filter("period-mode", value="month")

    # Callback
    start, end = period_mode_to_dates(mode)
    label = format_period_label(start, end, mode)
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Iterable

from dash import dcc, html


# ── Period pill filter ─────────────────────────────────────────────────────
DEFAULT_MODES: list[dict] = [
    {"label": "Week",   "value": "week"},
    {"label": "Month",  "value": "month"},
    {"label": "12mo",   "value": "12mo"},
    {"label": "Custom", "value": "custom"},
]


def period_pill_filter(
    id: str,
    value: str = "month",
    modes: Iterable[dict] | None = None,
    label: str | None = "Period",
):
    """Connected pill-button radio group for time-window selection.

    Renders a `dcc.RadioItems` styled by the `.period-pills` class
    (defined in 00_aspire_base.css). The Aspire-blue active pill,
    slate inactive labels, and connected pill aesthetic all come
    from the shared CSS — no per-app styling needed.

    Parameters
    ----------
    id : str
        Component id for the RadioItems (use this in your callbacks).
    value : str
        Initial selected mode (default ``"month"``).
    modes : iterable of dict or None
        Options to render. Defaults to Week / Month / 12mo / Custom.
        Each dict needs ``{"label", "value"}``.
    label : str or None
        Uppercase eyebrow label rendered above the pills. Pass ``None``
        to render the pills bare.
    """
    options = list(modes) if modes is not None else DEFAULT_MODES
    children = []
    if label:
        children.append(html.Div(
            label,
            style={
                "fontSize": "10px", "fontWeight": "700",
                "color": "#64748b", "textTransform": "uppercase",
                "letterSpacing": "0.4px", "marginBottom": "4px",
            },
        ))
    children.append(dcc.RadioItems(
        id=id,
        options=options,
        value=value,
        className="period-pills",
        inline=True,
    ))
    return html.Div(children)


# ── Date snapping helpers ──────────────────────────────────────────────────

def sunday_of(d: date) -> date:
    """Snap any date to the Sunday that starts its Sun..Sat week.

    Python weekday: Mon=0, Sun=6. Days since Sunday = (weekday + 1) % 7.
    """
    return d - timedelta(days=(d.weekday() + 1) % 7)


def monday_of(d: date) -> date:
    """Snap any date to the Monday that starts its Mon..Sun week."""
    return d - timedelta(days=d.weekday())


def first_of_month(d: date) -> date:
    """First day of the month containing d."""
    return d.replace(day=1)


def to_date(v) -> date:
    """Coerce ``v`` to a ``date`` — accepts ``date``, ``datetime``, or ISO string."""
    if isinstance(v, date):
        return v
    return date.fromisoformat(str(v)[:10])


def date_range(start, end) -> list[str]:
    """Inclusive list of ISO date strings from start to end."""
    s, e = to_date(start), to_date(end)
    return [(s + timedelta(i)).isoformat() for i in range((e - s).days + 1)]


# ── Period mode → start/end ────────────────────────────────────────────────

def period_mode_to_dates(
    mode: str,
    today: date | None = None,
    week_starts_on: str = "sunday",
) -> tuple[date, date]:
    """Convert a mode string to an inclusive (start, end) date pair.

    Modes:
        - ``"week"``    : current Sun..Sat (or Mon..Sun if week_starts_on='monday')
        - ``"month"``   : 1st of the current month through today
        - ``"12mo"``    : today minus 365 days through today
        - ``"ytd"``     : Jan 1 of the current year through today
        - ``"custom"``  : (today, today) — callers should swap in their
                          own DatePickerRange values

    Parameters
    ----------
    mode : str
    today : date or None
        Override for testing. Defaults to ``date.today()``.
    week_starts_on : "sunday" | "monday"
        Used only for ``"week"`` mode.
    """
    today = today or date.today()
    mode = (mode or "").lower()
    if mode == "week":
        start = sunday_of(today) if week_starts_on == "sunday" else monday_of(today)
        return start, start + timedelta(days=6)
    if mode == "month":
        return first_of_month(today), today
    if mode == "12mo":
        return today - timedelta(days=365), today
    if mode == "ytd":
        return date(today.year, 1, 1), today
    return today, today


# ── Label formatting ───────────────────────────────────────────────────────

def format_period_label(
    start: date | str,
    end: date | str,
    mode: str | None = None,
) -> str:
    """Render a human-friendly period label.

    Examples::

        format_period_label(date(2026,5,17), date(2026,5,23), "week")
        # "Sun 17 May – Sat 23 May 2026"

        format_period_label("2026-05-01", "2026-05-20", "month")
        # "1 – 20 May 2026"

        format_period_label("2025-05-20", "2026-05-20", "12mo")
        # "20 May 2025 – 20 May 2026"
    """
    s, e = to_date(start), to_date(end)
    if mode == "week":
        return f"{s.strftime('%a %d %b')} – {e.strftime('%a %d %b %Y')}"
    if mode == "month" and s.year == e.year and s.month == e.month:
        return f"{s.day} – {e.day} {e.strftime('%b %Y')}"
    if s.year == e.year:
        return f"{s.strftime('%d %b')} – {e.strftime('%d %b %Y')}"
    return f"{s.strftime('%d %b %Y')} – {e.strftime('%d %b %Y')}"


def days_ago_chip_label(days: int, label: str = "") -> str:
    """Render a tabular-nums-friendly "<label> · <N>d ago" string.

    For freshness banners and last-updated chips. Handles 0 / 1 / never.
    """
    prefix = f"{label} · " if label else ""
    if days is None or days >= 9999:
        return f"{prefix}never"
    if days == 0:
        return f"{prefix}today"
    if days == 1:
        return f"{prefix}1d ago"
    return f"{prefix}{int(days)}d ago"
