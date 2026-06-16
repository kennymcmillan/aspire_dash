"""sports.data_table — structural tests for the promoted data-grid assembler."""
from aspire_dash.sports import data_table


def _classes(node):
    return (getattr(node, "className", "") or "").split()


def _table(node):
    """data_table returns a horizontal-scroll wrapper containing the
    .aspire-data-table div (header + rows). Tests assert against the inner div."""
    assert "aspire-data-table-scroll" in _classes(node)
    return node.children


def test_wrapper_and_header():
    tbl = data_table(["Rank", "Fencer"], [["1", "Foconi"]])
    table = _table(tbl)
    assert "aspire-data-table" in _classes(table)
    header = table.children[0]
    assert "aspire-data-row" in _classes(header)
    assert "is-header" in _classes(header)
    assert [c.children for c in header.children] == ["Rank", "Fencer"]


def test_rows_render_positional_cells():
    body = _table(data_table(["A", "B"], [["a1", "b1"], ["a2", "b2"]])).children[1:]
    assert len(body) == 2
    assert [c.children for c in body[0].children] == ["a1", "b1"]
    assert "is-header" not in _classes(body[0])


def test_highlight_predicate_marks_rows():
    rows = [["1", "QAT"], ["2", "ITA"], ["3", "QAT"]]
    body = _table(data_table(["R", "Nat"], rows, highlight=lambda i, row: row[1] == "QAT")).children[1:]
    assert "is-highlight" in _classes(body[0])
    assert "is-highlight" not in _classes(body[1])
    assert "is-highlight" in _classes(body[2])


def test_highlight_index_iterable():
    body = _table(data_table(["R"], [["1"], ["2"], ["3"]], highlight={1})).children[1:]
    assert "is-highlight" not in _classes(body[0])
    assert "is-highlight" in _classes(body[1])


def test_column_align_and_width_applied():
    tbl = data_table(
        [{"label": "Rank", "width": "70px"}, {"label": "Pts", "align": "right", "grow": 3}],
        [["1", "198.0"]],
    )
    rank_cell, pts_cell = _table(tbl).children[1].children
    assert rank_cell.style["flex"] == "0 0 70px"
    assert rank_cell.style["maxWidth"] == "70px"
    assert pts_cell.style["textAlign"] == "right"
    assert pts_cell.style["flex"] == "3"


def test_per_cell_override_merges_style_and_value():
    tbl = data_table(["Δ"], [[{"value": "▲5", "align": "right", "style": {"color": "#16a34a"}}]])
    cell = _table(tbl).children[1].children[0]
    assert cell.children == "▲5"
    assert cell.style["color"] == "#16a34a"
    assert cell.style["textAlign"] == "right"


def test_float_grow_preserved():
    tbl = data_table([{"label": "A", "grow": 1.5}, {"label": "B", "grow": 0.8}], [["a", "b"]])
    a_cell, b_cell = _table(tbl).children[1].children
    assert a_cell.style["flex"] == "1.5"
    assert b_cell.style["flex"] == "0.8"


def test_wrap_column_opts_out_of_ellipsis():
    tbl = data_table([{"label": "Tight"}, {"label": "Rich", "wrap": True}], [["x", "y"]])
    tight, rich = _table(tbl).children[1].children
    assert "whiteSpace" not in tight.style
    assert rich.style["whiteSpace"] == "normal"
    assert rich.style["overflow"] == "visible"


def test_row_class_adds_per_row_modifier():
    rows = [["available"], ["pending"], ["available"]]
    body = _table(data_table(["X"], rows,
                             row_class=lambda i, row: "is-dim" if row[0] == "pending" else "")).children[1:]
    assert "is-dim" not in _classes(body[0])
    assert "is-dim" in _classes(body[1])
    assert "is-dim" not in _classes(body[2])


def test_row_class_composes_with_highlight():
    tbl = data_table(["X"], [["a"], ["b"]], highlight={0}, row_class=lambda i, row: "is-dim")
    first = _table(tbl).children[1]
    assert "is-highlight" in _classes(first)
    assert "is-dim" in _classes(first)


def test_short_row_pads_missing_cells():
    cells = _table(data_table(["A", "B", "C"], [["only_a"]])).children[1].children
    assert len(cells) == 3
    assert cells[0].children == "only_a"
    assert cells[1].children == ""


# ── Responsiveness (v0.63 — the fix for the narrow-viewport cramming) ──────────

def test_scroll_wrapper_present():
    tbl = data_table(["A", "B"], [["a", "b"]])
    assert "aspire-data-table-scroll" in _classes(tbl)   # outer wrapper scrolls


def test_wide_table_gets_min_width():
    # 10 flex columns -> a min-width well past a phone/tablet, so it scrolls
    cols = [{"label": f"C{i}"} for i in range(10)]
    table = _table(data_table(cols, [["x"] * 10]))
    mw = table.style["minWidth"]
    assert mw.endswith("px") and int(mw[:-2]) >= 800


def test_min_width_sums_fixed_column_widths():
    tbl = data_table([{"label": "A", "width": "200px"}, {"label": "B", "width": "100px"}], [["a", "b"]])
    assert _table(tbl).style["minWidth"] == "300px"
