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
