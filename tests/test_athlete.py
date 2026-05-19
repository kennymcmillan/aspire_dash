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
