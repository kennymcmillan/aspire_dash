"""v0.72.0 first-class tooltips on aspire_datatable (tooltip_header /
tooltip_data / tooltip_duration forwarded to dash_table.DataTable)."""
from aspire_dash.tables import aspire_datatable

COLS = [{"name": "Sport", "id": "sport"}, {"name": "RSI", "id": "rsi"}]
DATA = [{"sport": "Fencing", "rsi": 1.2}, {"sport": "Squash", "rsi": 1.4}]


def test_datatable_no_tooltips_by_default():
    t = aspire_datatable("t", DATA, COLS)
    # no tooltip props leak onto the table when the caller passes none
    assert getattr(t, "tooltip_header", None) is None
    assert getattr(t, "tooltip_data", None) is None
    assert getattr(t, "tooltip_duration", None) is None


def test_datatable_tooltip_header_forwarded():
    th = {"rsi": "Reactive Strength Index"}
    t = aspire_datatable("t", DATA, COLS, tooltip_header=th)
    assert t.tooltip_header == th
    assert t.tooltip_duration == 2000            # default forwarded alongside


def test_datatable_tooltip_data_forwarded():
    td = [{"rsi": {"value": "hi", "type": "markdown"}} for _ in DATA]
    t = aspire_datatable("t", DATA, COLS, tooltip_data=td)
    assert t.tooltip_data == td
    assert t.tooltip_duration == 2000


def test_datatable_tooltip_duration_none_is_persistent():
    t = aspire_datatable("t", DATA, COLS,
                         tooltip_header={"rsi": "x"}, tooltip_duration=None)
    assert t.tooltip_duration is None            # stays open until pointer leaves


def test_datatable_tooltip_defaults_still_branded():
    """Adding tooltips does not disturb the Aspire header / zebra styling."""
    t = aspire_datatable("t", DATA, COLS, tooltip_header={"rsi": "x"})
    assert t.style_header["backgroundColor"]      # Aspire-blue header preserved
    assert t.style_as_list_view is True
