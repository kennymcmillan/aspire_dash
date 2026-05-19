"""Smoke: every component-returning function returns a Dash component."""
from conftest import is_dash_component


def test_sidebar_returns_component():
    from aspire_dash.components import sidebar
    out = sidebar(title="Test", nav_items=[
        {"label": "Home", "href": "/", "icon": "fa-solid fa-house"},
    ])
    assert is_dash_component(out)


def test_topnav_returns_component():
    """Topnav uses dash.get_relative_path which needs a Dash app context;
    smoke-import the function rather than call it without a context."""
    from aspire_dash.components import topnav
    assert callable(topnav)


def test_header_returns_component():
    from aspire_dash.components import header
    out = header(title="Title")
    assert is_dash_component(out)


def test_hamburger_button_returns_component():
    from aspire_dash.components import hamburger_button
    assert is_dash_component(hamburger_button())


def test_card_wraps_children():
    from aspire_dash.components import card
    out = card(["one", "two"])
    assert is_dash_component(out)


def test_summary_card():
    from aspire_dash.components import summary_card
    out = summary_card(label="Latest", value="42.0", sub="cm")
    assert is_dash_component(out)


def test_graph_card_with_figure():
    import plotly.graph_objects as go
    from aspire_dash.components import graph_card
    fig = go.Figure()
    out = graph_card(figure=fig, title="My Chart")
    assert is_dash_component(out)


def test_toast_returns_component():
    from aspire_dash.components import toast
    assert is_dash_component(toast("my-toast"))


def test_badge_pill_variants():
    from aspire_dash.components import badge
    assert is_dash_component(badge("New", color="success"))
    assert is_dash_component(badge("Pill", color="primary", pill=True))


def test_toggle_group_builds_buttons():
    from aspire_dash.components import toggle_group
    out = toggle_group(
        "my-toggle",
        options=[{"label": "1W", "value": "week"},
                  {"label": "1M", "value": "month"}],
        value="week",
    )
    assert is_dash_component(out)


def test_dark_mode_toggle():
    from aspire_dash.components import dark_mode_toggle
    assert is_dash_component(dark_mode_toggle())


def test_print_header_footer():
    from aspire_dash.components import print_header, print_footer
    assert is_dash_component(print_header(title="Print Title"))
    assert is_dash_component(print_footer(text="Confidential"))


def test_export_buttons():
    from aspire_dash.components import export_buttons
    out = export_buttons("my-export")
    assert is_dash_component(out)


def test_empty_state_with_and_without_hint():
    from aspire_dash.components import empty_state
    assert is_dash_component(empty_state(text="Nothing here"))
    assert is_dash_component(empty_state(text="Nothing", hint="Pick X first"))


def test_filter_bar_wraps_children():
    from aspire_dash.components import filter_bar
    assert is_dash_component(filter_bar(["a", "b"]))


# ── v0.5+/0.6+ additions ────────────────────────────────────────────────────

def test_kpi_tile_renders():
    from aspire_dash.components import kpi_tile
    out = kpi_tile(label="Latest", value=42.0, unit="cm")
    assert is_dash_component(out)


def test_status_pill_renders():
    try:
        from aspire_dash.components import status_pill
    except ImportError:
        import pytest
        pytest.skip("status_pill not in this version")
    # Real signature: status_pill(status, label=None, palette=None, size='md')
    assert is_dash_component(status_pill("ok", label="Healthy"))
    # None status should also render (defensive default)
    assert is_dash_component(status_pill(None))


# ── v0.7 additions ──────────────────────────────────────────────────────────

def test_confirm_modal_renders():
    from aspire_dash.components import confirm_modal
    out = confirm_modal("delete-x", title="Delete?", body="Are you sure?")
    assert is_dash_component(out)


def test_file_upload_card_renders():
    from aspire_dash.components import file_upload_card
    out = file_upload_card("upload-x", label="Drop CSV", accept=".csv")
    assert is_dash_component(out)


def test_connect_user_chip_renders():
    from aspire_dash.components import connect_user_chip
    assert is_dash_component(connect_user_chip())
    assert is_dash_component(connect_user_chip(default="kenny"))


def test_linear_step_card_states():
    from aspire_dash.components import linear_step_card
    for state in ("active", "complete", "pending"):
        out = linear_step_card(1, "Step", "desc", state=state)
        assert is_dash_component(out)


def test_aspire_tabs_renders():
    from aspire_dash.components import aspire_tabs
    out = aspire_tabs("tabs-x", [
        {"label": "A", "value": "a"}, {"label": "B", "value": "b"},
    ])
    assert is_dash_component(out)


def test_freshness_banner_renders():
    from aspire_dash.components import freshness_banner
    out = freshness_banner([
        {"label": "Athletics", "days": 2},
        {"label": "Padel", "days": 60},
        {"label": "Squash", "days": None},
    ])
    assert is_dash_component(out)


def test_kpi_stat_renders():
    from aspire_dash.components import kpi_stat
    out = kpi_stat("Days lost", 234, sub="last 12 months")
    assert is_dash_component(out)
