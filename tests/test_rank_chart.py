"""0.108: rank over time (promoted from High Management Overview). Mock records only."""
import pytest

from aspire_dash.components import (rank_over_time, rank_over_time_figure, rank_series_from_record,
                                    rank_titles_from_record)

SQUASH = {"squash": {"ranking_history": [{"date": "01 Oct 2023", "rank": 40}, {"date": "01 Oct 2023", "rank": 40},
                                         {"date": "01 Jan 2025", "rank": 9}, {"date": "01 Oct 2026", "rank": 12},
                                         {"date": "bad", "rank": 5}, {"date": "01 Feb 2024", "rank": None}],
                     "honours": {"titles": 2, "wins": [{"date": "2025-01-10", "tournament": "Open A"},
                                                       {"date": None, "tournament": "No date"}]}}}


def test_squash_series_dedupes_drops_bad_rows_and_sorts():
    s = rank_series_from_record("squash", SQUASH)
    assert s == {"World (PSA)": [("2023-10-01", 40), ("2025-01-01", 9), ("2026-10-01", 12)]}


def test_titles_come_from_honours_wins_with_dates_only():
    assert rank_titles_from_record("squash", SQUASH) == [("2025-01-10", "Open A")]


def test_fencing_best_rank_per_season_and_board():
    rec = {"fencing": {"ranking_history": [
        {"season": "2024", "rank": 80, "band": "Senior", "weapon": "Foil", "source": "FIE"},
        {"season": "2024", "rank": 55, "band": "Senior", "weapon": "Foil", "source": "FIE"},
        {"season": "2025", "rank": 30, "band": "Senior", "weapon": "Foil", "source": "FIE"},
        {"season": "x", "rank": 1}]}}
    assert rank_series_from_record("fencing", rec) == {"Senior Foil (FIE)": [("2024-07-01", 55), ("2025-07-01", 30)]}


def test_tabletennis_iso_weeks_and_padel_boards():
    tt = {"tabletennis": {"ranking_history": [{"year": 2026, "week": 2, "rank": 300, "event_name": "MS", "category": "Senior"},
                                              {"year": 2026, "week": 99, "rank": 280, "event_name": "MS", "category": "Senior"}]}}
    s = rank_series_from_record("tabletennis", tt)
    assert s == {"MS (Senior)": [("2026-01-05", 300), ("2026-12-21", 280)]}
    pd = {"padel": {"ranking_history_by_group": {"FIP": [{"date": "2026-01-01", "rank": 70}], "Empty": []}}}
    assert rank_series_from_record("padel", pd) == {"FIP": [("2026-01-01", 70)]}


def test_unranked_sport_and_empty_payload_give_nothing():
    assert rank_series_from_record("athletics", SQUASH) == {}
    assert rank_series_from_record("squash", {}) == {}
    assert rank_over_time({}) is None


def test_figure_is_linear_with_best_rank_on_top():
    fig = rank_over_time_figure(rank_series_from_record("squash", SQUASH), [("2025-01-10", "Open A")])
    y = fig.layout.yaxis
    assert y.type == "linear"
    lo, hi = y.range
    assert lo == pytest.approx(42.0) and hi == 0.5          # worst (40) x 1.05 at the bottom, #1 ceiling on top
    texts = [a.text for a in fig.layout.annotations]
    assert "<b>Career high #9</b>" in texts and "<b>#12 now</b>" in texts
    star = [t for t in fig.data if t.name == "Title"][0]
    assert list(star.y) == [9]                                # the main line's rank at the title date


def test_career_high_now_gets_one_label():
    fig = rank_over_time_figure({"W": [("2024-01-01", 20), ("2025-01-01", 6)]})
    assert [a.text for a in fig.layout.annotations] == ["<b>Career high #6, now</b>"]


def test_max_lines_keeps_the_most_recent_boards():
    s = {"old": [("2019-01-01", 5)], "mid": [("2023-01-01", 9)], "new": [("2026-01-01", 3)], "newer": [("2026-06-01", 4)]}
    fig = rank_over_time_figure(s, max_lines=2)
    assert [t.name for t in fig.data if t.mode == "lines"] == ["newer", "new"]


def test_section_note_mentions_stars_only_with_titles():
    s = rank_series_from_record("squash", SQUASH)
    assert rank_over_time(s).children[2].children == "Best rank on top."
    assert rank_over_time(s, [("2025-01-10", "A")]).children[2].children == "Best rank on top. Stars are titles."
