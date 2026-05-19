"""time module — date arithmetic + period dropdown helpers."""
from datetime import date

import pytest


def test_to_date_accepts_str_and_date():
    from aspire_dash.time import to_date
    assert to_date("2026-05-19") == date(2026, 5, 19)
    assert to_date(date(2026, 5, 19)) == date(2026, 5, 19)


def test_monday_of_returns_monday():
    from aspire_dash.time import monday_of
    # 2026-05-19 is a Tuesday
    out = monday_of(date(2026, 5, 19))
    assert out.weekday() == 0
    assert out == date(2026, 5, 18)


def test_sunday_of_returns_sunday():
    from aspire_dash.time import sunday_of
    out = sunday_of(date(2026, 5, 19))
    assert out.weekday() == 6


def test_first_of_month():
    from aspire_dash.time import first_of_month
    assert first_of_month(date(2026, 5, 19)) == date(2026, 5, 1)


def test_date_range_inclusive():
    """date_range returns ISO date strings (inclusive on both ends)."""
    from aspire_dash.time import date_range
    rng = list(date_range(date(2026, 1, 1), date(2026, 1, 3)))
    assert rng == ["2026-01-01", "2026-01-02", "2026-01-03"]


@pytest.mark.parametrize("mode", ["today", "yesterday", "this_week", "last_week",
                                    "this_month", "last_month"])
def test_period_mode_to_dates_returns_tuple(mode):
    from aspire_dash.time import period_mode_to_dates
    out = period_mode_to_dates(mode)
    assert isinstance(out, tuple) and len(out) == 2
    fr, to = out
    # Both should be date or date-like, and fr <= to
    assert fr <= to


def test_format_period_label_safe_default():
    from aspire_dash.time import format_period_label
    s = format_period_label(date(2026, 1, 1), date(2026, 1, 7))
    assert isinstance(s, str) and s


def test_format_time_ago_buckets():
    """v0.7: relative time bucketing (5m / 3h / 2d / 6w → 1mo / 2y)."""
    from datetime import datetime, timedelta
    from aspire_dash.time import format_time_ago
    now = datetime(2026, 5, 20, 12, 0, 0)
    assert format_time_ago(now - timedelta(seconds=30), now=now) == "just now"
    assert format_time_ago(now - timedelta(minutes=5), now=now) == "5m ago"
    assert format_time_ago(now - timedelta(hours=3), now=now) == "3h ago"
    assert format_time_ago(now - timedelta(days=2), now=now) == "2d ago"
    assert format_time_ago(now - timedelta(weeks=2), now=now) == "2w ago"
    assert format_time_ago(None, now=now) == "—"
    assert format_time_ago("", now=now) == "—"
    assert format_time_ago("not-a-date", now=now) == "—"
