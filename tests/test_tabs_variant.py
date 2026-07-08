"""v0.72.0 segmented "pill" tab bar for aspire_tabs (+ underline variant)."""
from aspire_dash.components import aspire_tabs
from aspire_dash.theme import ACCENT

TABS = [{"label": "Growth", "value": "gm"}, {"label": "Physical", "value": "phys"}]


def test_aspire_tabs_default_is_pill():
    t = aspire_tabs("id-tabs", TABS)
    assert t.className == "aspire-tabs"
    assert "--underline" not in t.className
    # segmented band container on the tab row (inline so it renders w/o the CSS)
    assert t.style["background"] == "#eef2f7"
    assert t.style["borderRadius"] == "10px"
    # selected tab is a filled navy pill
    first = t.children[0]
    assert first.selected_style["background"] == ACCENT == "#004185"
    assert first.selected_style["color"] == "#ffffff"
    assert "borderBottom" not in first.selected_style


def test_aspire_tabs_underline_variant_reproduces_legacy():
    t = aspire_tabs("id-tabs", TABS, variant="underline")
    assert "aspire-tabs--underline" in t.className
    assert t.parent_style["borderBottom"].endswith("#e2e8f0")
    first = t.children[0]
    # underline indicator lives on the tab's bottom border, not a filled bg
    assert "3px solid" in first.selected_style["borderBottom"]
    assert first.selected_style["background"] == "transparent"


def test_aspire_tabs_value_and_children_preserved():
    tabs = [{"label": "A", "value": "a", "children": "body-a"},
            {"label": "B", "value": "b"}]
    t = aspire_tabs("x", tabs, value="b")
    assert t.value == "b"
    assert t.children[0].children == "body-a"
    assert t.children[0].value == "a"


def test_aspire_tabs_default_value_is_first():
    t = aspire_tabs("x", TABS)
    assert t.value == "gm"
