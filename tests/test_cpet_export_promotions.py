"""v0.58 promotions from DASH_Vyntus — identity export helpers + lactate markers."""
from aspire_dash.components.print_export import identity_columns, identity_filename_slug
from aspire_dash.sports_science import lactate_curve


def test_identity_columns_full():
    cols = identity_columns({"player_id": 5, "mrn": "M1", "full_name": "A B",
                             "sport": "Athletics", "date_of_birth": "2010-01-01",
                             "age": 14}, "2026-06-15")
    assert list(cols) == ["Player_ID", "MRN", "Athlete", "Sport", "DOB", "Age", "Test_Date"]
    assert cols["Player_ID"] == 5 and cols["Test_Date"] == "2026-06-15"


def test_identity_columns_stable_when_empty():
    cols = identity_columns(None, "2026-06-15")
    assert list(cols) == ["Player_ID", "MRN", "Athlete", "Sport", "DOB", "Age", "Test_Date"]
    assert cols["Athlete"] == "" and cols["Test_Date"] == "2026-06-15"


def test_identity_columns_age_zero_preserved():
    assert identity_columns({"age": 0}, None)["Age"] == 0


def test_filename_slug():
    assert identity_filename_slug({"full_name": "Amir Omuash"}, "2026-06-15") == "Amir_Omuash_2026-06-15"
    assert identity_filename_slug({"full_name": "O'Brien-Smith"}, None) == "O_Brien_Smith"
    assert identity_filename_slug(None, "2026-06-15") == ""


def test_lactate_curve_markers_drawn():
    fig = lactate_curve(
        {"T": {"speed": [12, 13, 14], "la": [1.2, 2.1, 4.0], "hr": [140, 150, 165]}},
        markers=[(13.0, "LT2", "#000"), (None, "skip", "#000")], as_graph=False)
    # vlines are layout shapes; the valid (non-None) marker is drawn, the None skipped
    assert len(fig.layout.shapes) >= 1
    assert any(getattr(a, "text", "") == "LT2" for a in fig.layout.annotations)
