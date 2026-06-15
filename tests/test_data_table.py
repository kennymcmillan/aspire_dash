"""sports.data_table — structural tests for the promoted data-grid assembler."""
from aspire_dash.sports import data_table


def _classes(node):
    return (getattr(node, "className", "") or "").split()


def test_wrapper_and_header():
    tbl = data_table(["Rank", "Fencer"], [["1", "Foconi"]])
    assert "aspire-data-table" in _classes(tbl)
    header = tbl.children[0]
    assert "aspire-data-row" in _classes(header)
    assert "is-header" in _classes(header)
    # header labels land in cells
    assert [c.children for c in header.children] == ["Rank", "Fencer"]


def test_rows_render_positional_cells():
    tbl = data_table(["A", "B"], [["a1", "b1"], ["a2", "b2"]])
    body = tbl.children[1:]
    assert len(body) == 2
    assert [c.children for c in body[0].children] == ["a1", "b1"]
    # data rows are NOT headers
    assert "is-header" not in _classes(body[0])


def test_highlight_predicate_marks_rows():
    rows = [["1", "QAT"], ["2", "ITA"], ["3", "QAT"]]
    tbl = data_table(["R", "Nat"], rows, highlight=lambda i, row: row[1] == "QAT")
    body = tbl.children[1:]
    assert "is-highlight" in _classes(body[0])
    assert "is-highlight" not in _classes(body[1])
    assert "is-highlight" in _classes(body[2])


def test_highlight_index_iterable():
    tbl = data_table(["R"], [["1"], ["2"], ["3"]], highlight={1})
    body = tbl.children[1:]
    assert "is-highlight" not in _classes(body[0])
    assert "is-highlight" in _classes(body[1])


def test_column_align_and_width_applied():
    tbl = data_table(
        [{"label": "Rank", "width": "70px"}, {"label": "Pts", "align": "right", "grow": 3}],
        [["1", "198.0"]],
    )
    rank_cell, pts_cell = tbl.children[1].children
    assert rank_cell.style["flex"] == "0 0 70px"
    assert rank_cell.style["maxWidth"] == "70px"
    assert pts_cell.style["textAlign"] == "right"
    assert pts_cell.style["flex"] == "3"


def test_per_cell_override_merges_style_and_value():
    tbl = data_table(
        ["Δ"],
        [[{"value": "▲5", "align": "right", "style": {"color": "#16a34a"}}]],
    )
    cell = tbl.children[1].children[0]
    assert cell.children == "▲5"
    assert cell.style["color"] == "#16a34a"
    assert cell.style["textAlign"] == "right"


def test_float_grow_preserved():
    tbl = data_table(
        [{"label": "A", "grow": 1.5}, {"label": "B", "grow": 0.8}],
        [["a", "b"]],
    )
    a_cell, b_cell = tbl.children[1].children
    assert a_cell.style["flex"] == "1.5"
    assert b_cell.style["flex"] == "0.8"


def test_wrap_column_opts_out_of_ellipsis():
    tbl = data_table(
        [{"label": "Tight"}, {"label": "Rich", "wrap": True}],
        [["x", "y"]],
    )
    tight, rich = tbl.children[1].children
    assert "whiteSpace" not in tight.style          # default: clamped by CSS
    assert rich.style["whiteSpace"] == "normal"     # wrap: opted out
    assert rich.style["overflow"] == "visible"


def test_short_row_pads_missing_cells():
    tbl = data_table(["A", "B", "C"], [["only_a"]])
    cells = tbl.children[1].children
    assert len(cells) == 3
    assert cells[0].children == "only_a"
    assert cells[1].children == ""
