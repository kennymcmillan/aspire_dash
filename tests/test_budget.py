"""budget module — currency formatters + components."""
from conftest import is_dash_component


def test_fmt_currency_basic():
    from aspire_dash.budget import fmt_currency
    assert fmt_currency(1234.5).startswith(("$", "QAR", "Q", "QR")) \
        or "1,234" in fmt_currency(1234.5) \
        or "1234" in fmt_currency(1234.5)


def test_fmt_k_abbreviation():
    from aspire_dash.budget import fmt_k
    s = fmt_k(12500)
    assert "12" in s
    # Should use 'K' or 'k' suffix at this magnitude
    assert any(c in s.lower() for c in ("k",))


def test_fmt_m_abbreviation():
    from aspire_dash.budget import fmt_m
    s = fmt_m(2_500_000)
    assert "2" in s
    assert "m" in s.lower()


def test_fmt_pct_basic():
    from aspire_dash.budget import fmt_pct
    s = fmt_pct(0.42)
    assert "42" in s and "%" in s


def test_variance_card():
    from aspire_dash.budget import variance_card
    out = variance_card("Q1 Spend", actual=8000, target=10000)
    assert is_dash_component(out)


def test_variance_card_higher_is_worse():
    """For 'spend' metrics where over-target is bad."""
    from aspire_dash.budget import variance_card
    out = variance_card("Q1 Spend", actual=12000, target=10000,
                          higher_is_better=False)
    assert is_dash_component(out)


def test_utilisation_card():
    from aspire_dash.budget import utilisation_card
    out = utilisation_card("Camp Days", used=750, total=1000)
    assert is_dash_component(out)


def test_rollup_chips_with_dict_list():
    from aspire_dash.budget import rollup_chips
    out = rollup_chips([
        {"label": "Salaries", "value": 50000},
        {"label": "Travel",   "value": 10000},
    ])
    assert is_dash_component(out)
