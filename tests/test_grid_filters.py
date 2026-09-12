"""Slice 3 — AG Grid filterModel -> safe WHERE, new operators, OR within a column, grid sort,
the plain-English sentence, and counted distinct values (no network)."""
from __future__ import annotations

from aspire_dash import grid_filters as F

COLS = ["Name", "World_Ranking", "Country", "Start_Date"]


def test_text_filter_types():
    m = {"Name": {"filterType": "text", "type": "contains", "filter": "O'Br"}}
    w, warn = F.compile_where_report(F.from_grid_model(m, COLS), COLS)
    assert w == "Name LIKE '%O''Br%'" and not warn
    m = {"Name": {"filterType": "text", "type": "notContains", "filter": "x"}}
    assert F.compile_where(F.from_grid_model(m, COLS), COLS) == "Name NOT LIKE '%x%'"
    m = {"Name": {"filterType": "text", "type": "endsWith", "filter": "son"}}
    assert F.compile_where(F.from_grid_model(m, COLS), COLS) == "Name LIKE '%son'"
    m = {"Name": {"filterType": "text", "type": "blank"}}
    assert F.compile_where(F.from_grid_model(m, COLS), COLS) == "(Name IS NULL OR Name = '')"
    m = {"Name": {"filterType": "text", "type": "notBlank"}}
    assert F.compile_where(F.from_grid_model(m, COLS), COLS) == "(Name IS NOT NULL AND Name <> '')"


def test_number_filter_types_and_range():
    m = {"World_Ranking": {"filterType": "number", "type": "lessThanOrEqual", "filter": 20}}
    assert F.compile_where(F.from_grid_model(m, COLS), COLS) == "World_Ranking <= 20"
    m = {"World_Ranking": {"filterType": "number", "type": "inRange", "filter": 5, "filterTo": 10}}
    assert F.compile_where(F.from_grid_model(m, COLS), COLS) == "World_Ranking BETWEEN 5 AND 10"


def test_date_filter_types():
    m = {"Start_Date": {"filterType": "date", "type": "greaterThan", "dateFrom": "2025-01-01 00:00:00", "dateTo": None}}
    assert F.compile_where(F.from_grid_model(m, COLS), COLS) == "Start_Date > '2025-01-01 00:00:00'"
    m = {"Start_Date": {"filterType": "date", "type": "inRange", "dateFrom": "2025-01-01 00:00:00", "dateTo": "2025-06-30 00:00:00"}}
    assert F.compile_where(F.from_grid_model(m, COLS), COLS) == \
        "Start_Date BETWEEN '2025-01-01 00:00:00' AND '2025-06-30 00:00:00'"
    # a single day matches the whole day whatever time is stored
    m = {"Start_Date": {"filterType": "date", "type": "equals", "dateFrom": "2025-03-04 00:00:00", "dateTo": None}}
    assert F.compile_where(F.from_grid_model(m, COLS), COLS) == \
        "Start_Date BETWEEN '2025-03-04 00:00:00' AND '2025-03-04 23:59:59'"


def test_combined_conditions_and_or_within_column():
    m = {"Country": {"filterType": "text", "operator": "OR",
                     "conditions": [{"filterType": "text", "type": "equals", "filter": "EGY"},
                                    {"filterType": "text", "type": "equals", "filter": "PAK"}]},
         "World_Ranking": {"filterType": "number", "type": "lessThan", "filter": 50}}
    w = F.compile_where(F.from_grid_model(m, COLS), COLS)
    assert w == "(Country = 'EGY' OR Country = 'PAK') AND World_Ranking < 50"
    # older two-condition form, AND
    m = {"World_Ranking": {"filterType": "number", "operator": "AND",
                           "condition1": {"filterType": "number", "type": "greaterThan", "filter": 1},
                           "condition2": {"filterType": "number", "type": "lessThan", "filter": 9}}}
    assert F.compile_where(F.from_grid_model(m, COLS), COLS) == "World_Ranking > 1 AND World_Ranking < 9"


def test_unknown_column_from_grid_is_warned_not_emitted():
    m = {"evil": {"filterType": "text", "type": "equals", "filter": "x"}}
    w, warn = F.compile_where_report(F.from_grid_model(m, COLS), COLS)
    assert w == "" and warn and "evil" in warn[0]


def test_in_and_not_in_accept_lists():
    w = F.compile_where([{"column": "Country", "op": "in", "value": ["EGY", "PAK"]}], COLS)
    assert w == "Country IN ('EGY','PAK')"
    w = F.compile_where([{"column": "Country", "op": "not in", "value": ["EGY"]}], COLS)
    assert w == "Country NOT IN ('EGY')"


def test_sort_from_grid_and_sentence():
    assert F.sort_from_grid([{"colId": "Name"}, {"colId": "World_Ranking", "sort": "desc", "sortIndex": 0}]) == ("World_Ranking", True)
    assert F.sort_from_grid(None) == (None, False)
    s = F.sentence([{"column": "Country", "op": "in", "value": ["EGY", "PAK"]},
                    {"column": "World_Ranking", "op": "<=", "value": 20},
                    {"column": "Name", "any": [{"op": "contains", "value": "a"}, {"op": "starts with", "value": "B"}]}])
    assert s == "Country is EGY or PAK, and World_Ranking <= 20, and Name contains a or starts with B"


