"""Regression: kpi_tile/_fmt_value must not crash on non-numeric values
(ranks, country, week labels, decimal ACWR shown as pre-formatted strings)."""
from aspire_dash.components.kpi import _fmt_value, kpi_strip


def test_fmt_value_numbers_and_strings():
    assert _fmt_value(None) == "—"
    assert _fmt_value(1234) == "1,234"
    assert _fmt_value(0) == "0"
    assert _fmt_value("28") == "28"
    assert _fmt_value("Qatar") == "Qatar"
    assert _fmt_value("0.81") == "0.81"
    assert _fmt_value(True) == "True"   # bool is not treated as the int 1


def test_kpi_strip_with_text_values_does_not_crash():
    kpi_strip([{"label": "Country", "value": "Qatar", "unit": ""},
               {"label": "ACWR", "value": "0.81", "unit": ""}])
