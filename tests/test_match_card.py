"""Tests for aspire_dash.sports.match_card (ported from SAMS .match-card)."""
from dash.development.base_component import Component
from aspire_dash.sports import match_card, _flag_emoji


def all_classes(node):
    out = []

    def walk(n):
        if isinstance(n, Component):
            cn = getattr(n, "className", None)
            if cn:
                out.append(cn)
            walk(getattr(n, "children", None))
        elif isinstance(n, (list, tuple)):
            for x in n:
                walk(x)
    walk(node)
    return out


def test_win_auto_outcome_and_set_shading():
    card = match_card(
        {"name": "Abdulla Al-Tamimi", "country": "QAT", "sets": [11, 9, 11, 11], "total": 3},
        {"name": "Mohamed Samir", "country": "EGY", "sets": [8, 11, 7, 9], "total": 1},
        title="Qatar Squash Open 2026",
        meta=[("fa-solid fa-location-dot", "Doha"), "Quarter-Final"],
        tags=["PSA World Tour", "2026-03-14"],
    )
    cls = all_classes(card)
    assert "match-card is-win" in cls           # outcome inferred from totals
    assert "match-card__player is-focus" in cls  # focus athlete bolded
    assert "match-card__total" in cls
    assert any("match-card__set is-won" in c for c in cls)  # per-set winner shading
    assert any("match-card__outcome win" in c for c in cls)


def test_loss_and_neutral():
    loss = match_card({"name": "A B", "country": "QAT", "total": 2},
                      {"name": "C D", "country": "CHN", "total": 3})
    assert "match-card is-loss" in all_classes(loss)

    neutral = match_card({"name": "Pair A", "country": "QAT"},
                         {"name": "Pair B", "country": "QAT"}, title="Padel League")
    assert "match-card is-neutral" in all_classes(neutral)


def test_explicit_outcome_and_score_override():
    card = match_card({"name": "X"}, {"name": "Y"}, outcome="win", score="3–0")
    assert "match-card is-win" in all_classes(card)


def test_initials_fallback_when_no_photo():
    card = match_card({"name": "Ahmed Khalil"}, {"name": "Bo Li"})
    assert any("match-card__avatar--initials" in c for c in all_classes(card))


def test_flag_emoji():
    assert _flag_emoji("QAT") == "\U0001F1F6\U0001F1E6"  # 🇶🇦
    assert _flag_emoji("EGY") == "\U0001F1EA\U0001F1EC"  # 🇪🇬
    assert _flag_emoji(None) == ""
    assert _flag_emoji("ZZZ") == ""
