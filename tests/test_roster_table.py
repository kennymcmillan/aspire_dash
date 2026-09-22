"""roster_table: the standard athlete-roster/directory table (v0.89)."""
import pandas as pd
from dash import dcc, html

from aspire_dash.tables import roster_table

ROWS = [
    {"name": "Ali", "grp": "Dev 1", "nat": "Qatar", "code": "QAT", "pid": 3230},
    {"name": "Sam", "grp": "Dev 2", "nat": None, "code": None, "pid": None},
]
COLS = [
    {"key": "name", "label": "Athlete",
     "link": lambda r: f"/a?id={r['pid']}" if r["pid"] else None},
    {"key": "grp", "label": "Squad"},
    {"key": "nat", "label": "Nationality", "flag": "code"},
    {"key": "pid", "label": "SAMS ID", "align": "center"},
]


def _table(div):
    """The html.Table inside the returned .card wrapper."""
    return div.children


def _rows(div):
    thead, tbody = _table(div).children
    return tbody.children  # list of html.Tr


def _cells(tr):
    return [td.children for td in tr.children]


def test_returns_div_with_table_and_headers():
    out = roster_table(ROWS, COLS)
    assert isinstance(out, html.Div)
    thead, tbody = _table(out).children
    headers = [th.children for th in thead.children.children]
    assert headers == ["Athlete", "Squad", "Nationality", "SAMS ID"]
    assert "tbl-scroll" in out.className          # sticky-scroll box by default


def test_link_column_renders_dcc_link_with_href():
    out = roster_table(ROWS, COLS)
    name_cell = _cells(_rows(out)[0])[0]          # row 0, Athlete column
    assert isinstance(name_cell, dcc.Link)
    assert name_cell.href == "/a?id=3230"
    assert name_cell.className == "heat-athlete-link"


def test_link_falsy_href_falls_back_to_plain_text():
    out = roster_table(ROWS, COLS)
    name_cell = _cells(_rows(out)[1])[0]          # row 1 has pid=None -> no link
    assert name_cell == "Sam"


def test_flag_column_and_missing_value_render():
    out = roster_table(ROWS, COLS)
    nat0 = _cells(_rows(out)[0])[2]               # QAT -> flag image + name span
    assert isinstance(nat0, html.Span)
    nat1 = _cells(_rows(out)[1])[2]               # None nationality -> en dash
    assert nat1 == "–"


def test_missing_value_is_en_dash():
    out = roster_table(ROWS, COLS)
    pid1 = _cells(_rows(out)[1])[3]               # pid=None
    assert pid1 == "–"


def test_align_sets_text_align():
    out = roster_table(ROWS, COLS)
    pid_td = _rows(out)[0].children[3]            # SAMS ID column, align=center
    assert pid_td.style == {"textAlign": "center"}


def test_custom_cell_and_format():
    cols = [
        {"key": "grp", "format": lambda v: v.upper()},
        {"key": "name", "cell": lambda r: html.B(r["name"])},
    ]
    out = roster_table([ROWS[0]], cols)
    grp, name = _cells(_rows(out)[0])
    assert grp == "DEV 1"
    assert isinstance(name, html.B) and name.children == "Ali"


def test_dataframe_input_supported():
    out = roster_table(pd.DataFrame(ROWS), COLS)
    assert len(_rows(out)) == 2


def test_empty_data_returns_empty_state_not_table():
    out = roster_table([], COLS, empty_text="No athletes")
    assert "No athletes" in str(out)
    # not a table wrapper
    assert getattr(out, "className", "") != "card tbl-scroll"
