"""v0.48 v12_helpers residual glow-up — class contract for the ported parts."""
from __future__ import annotations


def test_athlete_card_avatar_and_link():
    from aspire_dash.v12_helpers import athlete_card
    with_photo = athlete_card("Ali Turki", photo_url="https://x/p.jpg")
    avatar = with_photo.children[0].children[0]
    assert avatar.className == "amc-avatar"
    initials = athlete_card("Ali Turki").children[0].children[0]
    assert initials.className == "amc-avatar amc-avatar--initials"
    assert initials.children == "AT"
    body = athlete_card("Ali Turki").children[0].children[1]
    assert body.className == "amc-body"
    linked = athlete_card("Ali Turki", href="/athlete/1")
    assert linked.className == "card-link"


def test_athlete_card_rings_md_avatar_and_rings_row():
    from aspire_dash.v12_helpers import athlete_card_rings
    rings = [{"value": 72, "pct": 72, "label": "Recovery"}]
    card = athlete_card_rings("Mo Hosny", rings)
    avatar = card.children[0].children[0]
    assert avatar.className == "amc-avatar amc-avatar--md amc-avatar--initials"
    assert card.children[1].className == "amc-rings"
    linked = athlete_card_rings("Mo Hosny", rings, href="/x")
    assert linked.className == "card-link"


def test_metric_ring_classes_keep_dynamic_size_and_colour():
    from aspire_dash.v12_helpers import metric_ring
    out = metric_ring(68, pct=68, label="Recovery", tone="good", size=80)
    assert out.className == "metric-ring"
    box = out.children[0]
    assert box.className == "metric-ring__box"
    assert box.style == {"width": "80px", "height": "80px"}
    img, centre = box.children
    assert img.className == "metric-ring__img"
    assert centre.className == "metric-ring__centre"
    val = centre.children
    assert val.className == "metric-ring__value"
    assert "fontSize" in val.style and "color" in val.style
    assert out.children[1].className == "metric-ring__label"


def test_athlete_card_v2_link_uses_card_link():
    from aspire_dash.v12_helpers import athlete_card_v2
    linked = athlete_card_v2("Ali", rings=[], href="/a")
    assert linked.className == "card-link"
