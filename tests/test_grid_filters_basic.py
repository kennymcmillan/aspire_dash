"""Filter compiler — allowlist + injection safety + operator handling."""
from __future__ import annotations

from aspire_dash import grid_filters as F

COLS = ["Name", "World_Ranking", "Country"]


def test_unknown_column_dropped():
    assert F.compile_where([{"column": "evil", "op": "=", "value": "x"}], COLS) == ""


def test_unknown_op_dropped():
    assert F.compile_where([{"column": "Name", "op": "REGEXP", "value": "x"}], COLS) == ""


def test_scalar_equals_and_quote_escaping():
    w = F.compile_where([{"column": "Name", "op": "=", "value": "O'Brien"}], COLS)
    assert w == "Name = 'O''Brien'"


def test_backslash_escaped():
    w = F.compile_where([{"column": "Name", "op": "=", "value": "a\\"}], COLS)
    assert w == "Name = 'a\\\\'"


def test_injection_stays_inside_literal():
    w = F.compile_where([{"column": "Name", "op": "=",
                          "value": "x'; DROP TABLE users; --"}], COLS)
    # the whole payload is a single escaped string literal; quotes doubled
    assert w.startswith("Name = '")
    assert w.endswith("'")
    assert w.count("'") % 2 == 0  # balanced -> cannot break out
    assert "DROP TABLE" in w      # present, but harmless (inside the literal)


def test_numeric_op_requires_number():
    assert F.compile_where([{"column": "World_Ranking", "op": ">", "value": "abc"}], COLS) == ""
    assert F.compile_where([{"column": "World_Ranking", "op": ">", "value": "10"}], COLS) \
        == "World_Ranking > 10"


def test_contains_and_starts_with():
    assert F.compile_where([{"column": "Country", "op": "contains", "value": "QA"}], COLS) \
        == "Country LIKE '%QA%'"
    assert F.compile_where([{"column": "Country", "op": "starts with", "value": "QA"}], COLS) \
        == "Country LIKE 'QA%'"


def test_in_list():
    w = F.compile_where([{"column": "Country", "op": "in", "value": "QAT, EGY ,FRA"}], COLS)
    assert w == "Country IN ('QAT','EGY','FRA')"


def test_multiple_clauses_anded():
    w = F.compile_where([
        {"column": "Country", "op": "=", "value": "QAT"},
        {"column": "World_Ranking", "op": "<=", "value": "20"},
    ], COLS)
    assert w == "Country = 'QAT' AND World_Ranking <= 20"


def test_plain_identifiers_are_not_backticked():
    # Slice 0 / X1: the REST paged route rejects backticks (where_guard), so a plain
    # identifier must be emitted bare. Bare is safe because the column is allowlisted.
    w = F.compile_where([{"column": "Country", "op": "=", "value": "QAT"}], COLS)
    assert "`" not in w


def test_odd_identifier_is_backticked():
    cols = ["World Ranking", "ok-col"]
    w = F.compile_where([{"column": "World Ranking", "op": "=", "value": "1"}], cols)
    assert w.startswith("`World Ranking` = ")
    assert F.needs_tool_route(w)


def test_range_ops_accept_iso_dates():
    cols = ["Start_Date", "World_Ranking"]
    w = F.compile_where([{"column": "Start_Date", "op": ">=", "value": "2025-01-01"}], cols)
    assert w == "Start_Date >= '2025-01-01'"
    w = F.compile_where([{"column": "Start_Date", "op": "<", "value": "2025-06-30 23:59:59"}], cols)
    assert w == "Start_Date < '2025-06-30 23:59:59'"
    # still no free text through a range op
    assert F.compile_where([{"column": "Start_Date", "op": ">", "value": "yesterday"}], cols) == ""


def test_report_names_every_dropped_clause():
    where, warnings = F.compile_where_report([
        {"column": "Country", "op": "=", "value": "QAT"},          # kept
        {"column": "nope", "op": "=", "value": "x"},               # unknown column
        {"column": "World_Ranking", "op": ">", "value": "abc"},    # bad number
        {"column": "Name", "op": "in", "value": " , "},            # empty list
    ], COLS)
    assert where == "Country = 'QAT'"
    assert len(warnings) == 3
    assert any("nope" in w for w in warnings)
    assert any("World_Ranking" in w and "abc" in w for w in warnings)
    assert any("Name" in w for w in warnings)
    # the plain wrapper still returns just the string
    assert F.compile_where([{"column": "Country", "op": "=", "value": "QAT"}], COLS) == where


def test_value_length_capped():
    w = F.compile_where([{"column": "Name", "op": "=", "value": "z" * 500}], COLS)
    inner = w.split("'", 1)[1].rstrip("'")
    assert len(inner) <= F.MAX_VALUE_LEN
