"""athlete module — avatar, profile header, picker."""
from conftest import is_dash_component


def test_athlete_avatar_renders():
    from aspire_dash.athlete import athlete_avatar
    out = athlete_avatar(photo_url=None, name="John Doe")
    assert is_dash_component(out)


def test_athlete_avatar_with_image():
    from aspire_dash.athlete import athlete_avatar
    out = athlete_avatar(
        photo_url="https://example.com/photo.jpg",
        name="Jane Smith",
    )
    assert is_dash_component(out)


def test_athlete_avatar_size_variants():
    from aspire_dash.athlete import athlete_avatar
    for size in ("sm", "md", "lg"):
        assert is_dash_component(athlete_avatar(name="X", size=size))


def test_athlete_profile_header():
    from aspire_dash.athlete import athlete_profile_header
    # Permissive: just confirm callable, accepts a few common kwargs
    import inspect
    sig = inspect.signature(athlete_profile_header)
    # Build kwargs from whatever the function accepts
    common = {"name": "John Doe", "sport": "Athletics", "subtitle": "Endurance"}
    kwargs = {k: v for k, v in common.items() if k in sig.parameters}
    out = athlete_profile_header(**kwargs) if kwargs else athlete_profile_header()
    assert is_dash_component(out)


def test_athlete_picker_renders():
    from aspire_dash.athlete import athlete_picker
    # Default args — empty sports list
    out = athlete_picker()
    assert is_dash_component(out)


def test_picker_store_id_constant():
    from aspire_dash.athlete import PICKER_STORE_ID
    assert isinstance(PICKER_STORE_ID, str)


# ── athlete_options_with_recency ────────────────────────────────────────────

def test_athlete_options_with_recency_sorts_recent_first():
    from aspire_dash.athlete import athlete_options_with_recency
    profiles = [
        {"profileId": "old",    "fullName": "Old Athlete"},
        {"profileId": "recent", "fullName": "Recent Athlete"},
        {"profileId": "none",   "fullName": "Bob Stale"},
    ]
    dates = {
        "old":    "2025-08-01",
        "recent": "2026-04-15",
        # 'none' missing
    }
    out = athlete_options_with_recency(profiles, dates)
    assert [o["value"] for o in out] == ["recent", "old", "none"]
    # Date appears in label of athletes with data
    assert "Apr" in out[0]["label"]
    # No date → clean label
    assert "(" not in out[2]["label"]


def test_athlete_options_with_recency_no_dates_falls_back_to_alphabetical():
    from aspire_dash.athlete import athlete_options_with_recency
    profiles = [
        {"profileId": "z", "fullName": "Zeta Athlete"},
        {"profileId": "a", "fullName": "Alpha Athlete"},
    ]
    out = athlete_options_with_recency(profiles, last_test_dates={})
    assert [o["value"] for o in out] == ["a", "z"]


def test_athlete_options_with_recency_custom_id_field():
    """Works with SAMS (playerId) / Whoop (user_id) / etc."""
    from aspire_dash.athlete import athlete_options_with_recency
    profiles = [
        {"playerId": 123, "fullName": "Joe"},
        {"playerId": 456, "fullName": "Jane"},
    ]
    dates = {123: "2026-04-15", 456: "2026-01-01"}
    out = athlete_options_with_recency(profiles, dates, id_field="playerId")
    assert [o["value"] for o in out] == [123, 456]


def test_athlete_options_with_recency_custom_date_format():
    from aspire_dash.athlete import athlete_options_with_recency
    profiles = [{"profileId": "p1", "fullName": "X"}]
    dates = {"p1": "2026-04-15"}
    out = athlete_options_with_recency(profiles, dates, label_date_fmt="%Y-%m-%d")
    assert "2026-04-15" in out[0]["label"]


def test_athlete_options_with_recency_malformed_date_falls_to_no_date_bucket():
    """A bad date string shouldn't crash — athlete falls to no-date bucket."""
    from aspire_dash.athlete import athlete_options_with_recency
    profiles = [
        {"profileId": "broken", "fullName": "Aaa"},
        {"profileId": "good",   "fullName": "Zzz"},
    ]
    dates = {"broken": "not-a-date", "good": "2026-04-15"}
    out = athlete_options_with_recency(profiles, dates)
    # good comes first (has valid date), broken falls to bucket-1
    assert out[0]["value"] == "good"


def test_athlete_options_with_recency_empty_inputs():
    from aspire_dash.athlete import athlete_options_with_recency
    assert athlete_options_with_recency([], {}) == []
    assert athlete_options_with_recency([], None) == []


# ── athlete_id_card (v0.37) ───────────────────────────────────────────────

def _full_payload() -> dict:
    return {
        "player_id": 12345, "full_name": "Mahmoud Tarek",
        "mrn": "MRN-99", "sport": "Athletics", "sport_id": 1,
        "target_event": "100m", "date_of_birth": "2008-04-15",
        "is_target": True, "photo_url": "https://example.com/p.jpg",
    }


def test_athlete_id_card_renders_full_payload():
    from aspire_dash.athlete import athlete_id_card
    card = athlete_id_card(_full_payload())
    rep = repr(card)
    for needle in ["Mahmoud Tarek", "Athletics", "100m", "2008-04-15",
                   "MRN-99", "12345", "TARGET", "is-target", "yrs",
                   "athlete-id-card__pill"]:
        assert needle in rep, f"missing {needle!r}"


def test_athlete_id_card_empty_state():
    from aspire_dash.athlete import athlete_id_card
    for empty in (None, {}, {"player_id": None}):
        rep = repr(athlete_id_card(empty))
        assert "is-empty" in rep
        assert "No athlete picked" in rep


def test_athlete_id_card_non_target_omits_target_styling():
    from aspire_dash.athlete import athlete_id_card
    p = _full_payload()
    p["is_target"] = False
    p["pathway"] = "Development"
    rep = repr(athlete_id_card(p))
    assert "TARGET" not in rep
    assert "is-target" not in rep


def test_athlete_id_card_pathway_target_triggers_styling():
    """is_target can be missing; pathway='Target' alone should fire it."""
    from aspire_dash.athlete import athlete_id_card
    p = _full_payload()
    p.pop("is_target")
    p["pathway"] = "Target"
    rep = repr(athlete_id_card(p))
    assert "is-target" in rep
    assert "TARGET" in rep


def test_athlete_id_card_skips_missing_pills():
    """Only fields actually present should render. SAMS ID is the only
    identity pill that's guaranteed (player_id gates the empty state)."""
    from aspire_dash.athlete import athlete_id_card
    rep = repr(athlete_id_card({
        "player_id": 99, "full_name": "Solo", "sport": "Padel",
    }))
    assert "Padel" in rep
    assert "pill-sport" in rep
    assert "pill-event" not in rep
    assert "DOB" not in rep
    assert "MRN" not in rep
    assert "SAMS ID" in rep  # always rendered — player_id is present


def test_athlete_id_card_photo_fallback():
    from aspire_dash.athlete import athlete_id_card
    p = _full_payload()
    p.pop("photo_url")
    rep = repr(athlete_id_card(p))
    assert "athlete-id-card__photo-fallback" in rep
    assert "fa-user" in rep


def test_athlete_id_card_age_decimal():
    from aspire_dash.athlete import athlete_id_card, _athlete_id_card_fractional_age
    p = _full_payload()
    rep = repr(athlete_id_card(p))
    expected = _athlete_id_card_fractional_age(p["date_of_birth"])
    assert expected is not None
    assert f"{expected:.1f} yrs" in rep


def test_athlete_id_card_fractional_age_robust():
    from aspire_dash.athlete import _athlete_id_card_fractional_age as f
    assert f(None) is None
    assert f("") is None
    assert f("not-a-date") is None
    assert f("2010-01-21") > 15.0
