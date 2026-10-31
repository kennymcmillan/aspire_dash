import dash_bootstrap_components as dbc

import aspire_dash


def test_icon_font_comes_from_a_cors_enabled_cdn():
    # use.fontawesome.com serves its webfonts without Access-Control-Allow-Origin,
    # so browsers refuse them and every icon renders as a box (2026-10-31)
    assert dbc.icons.FONT_AWESOME not in aspire_dash.STYLESHEETS
    assert aspire_dash.FONT_AWESOME in aspire_dash.STYLESHEETS
    assert aspire_dash.FONT_AWESOME.startswith("https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.7.2/")
