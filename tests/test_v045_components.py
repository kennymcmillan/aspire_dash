"""v0.45 promotions: legend_chips, error_banner, section_card, sparkline_figure."""
import pytest


def test_legend_chips_structure():
    from aspire_dash.components import legend_chips
    out = legend_chips([("Within 1 SD", "#dcfce7", "#166534"),
                        ("> +2 SD", "#fecaca", "#991b1b")])
    assert out.className == "legend-chips"
    assert len(out.children) == 2
    chip = out.children[0]
    assert chip.children == "Within 1 SD"
    assert chip.style["backgroundColor"] == "#dcfce7"
    assert chip.style["color"] == "#166534"


def test_error_banner_message_and_hint():
    from aspire_dash.components import error_banner
    out = error_banner("timeout after 30s", title="Inventory unreachable",
                       hint="Check SPORTS_WRITE_API_KEY")
    assert out.className == "error-banner"
    assert out.role == "alert"
    flat = str(out)
    assert "timeout after 30s" in flat
    assert "Inventory unreachable" in flat
    assert "SPORTS_WRITE_API_KEY" in flat


def test_section_card_accent_and_badge():
    from aspire_dash.components import section_card
    from dash import html
    out = section_card("Low stock", html.Div("body"),
                       icon="fa-solid fa-boxes-stacked",
                       badge_text="3 items", accent_color="#dc2626")
    assert "section-card" in out.className
    assert out.style["borderLeft"] == "4px solid #dc2626"
    header = out.children[0]
    assert header.className == "section-header"
    # icon + title + badge
    assert len(header.children) == 3


def test_section_card_minimal():
    from aspire_dash.components import section_card
    out = section_card("Title", "body")
    assert "borderLeft" not in out.style
    assert len(out.children[0].children) == 1  # title only


def test_sparkline_figure_fill_and_padding():
    from aspire_dash.plots import sparkline_figure
    fig = sparkline_figure([10, 12, None, 15], color="#004185")
    tr = fig.data[0]
    assert tr.fill == "tozeroy"
    assert tr.line.color == "#004185"
    lo, hi = fig.layout.yaxis.range
    assert lo < 10 and hi > 15           # padded beyond data
    assert fig.layout.paper_bgcolor == "rgba(0,0,0,0)"  # dark-mode safe


def test_sparkline_figure_no_fill_markers():
    from aspire_dash.plots import sparkline_figure
    fig = sparkline_figure([1, 2, 3], fill=False, height=60)
    assert fig.data[0].mode == "lines+markers"
    assert fig.layout.height == 60
