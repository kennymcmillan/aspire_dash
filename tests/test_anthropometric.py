"""v0.47 anthropometric glow-up — class contract for the 3 ported components."""
from __future__ import annotations


def test_snapshot_card_classes():
    from aspire_dash.anthropometric import athlete_snapshot_card
    out = athlete_snapshot_card("Snapshot", [
        {"label": "Body Mass", "value": "83.5", "unit": "kg"},
        {"label": "Stature", "value": "184.6", "unit": "cm"},
    ], accent="gold")
    assert out.className == "card snapshot-card accent-gold"
    header, body = out.children
    assert header.className == "snapshot-card__header"
    assert body.className == "snapshot-card__body"
    row = body.children[0]
    assert row.className == "snapshot-card__row"
    labels = [c.className for c in row.children]
    assert labels == ["snapshot-card__label", "snapshot-card__value",
                      "snapshot-card__unit"]


def test_limb_symmetry_tones():
    from aspire_dash.anthropometric import limb_symmetry_bar
    good = limb_symmetry_bar("Calf girth", 38.0, 38.1)
    assert "sym-good" in good.className
    warn = limb_symmetry_bar("Thigh", 50.0, 47.5)        # ~95%
    assert "sym-warn" in warn.className
    bad = limb_symmetry_bar("Arm", 30.0, 25.0)           # ~83%
    assert "sym-danger" in bad.className
    track = good.children[1]
    assert track.className == "limb-sym__track"
    left, right = track.children
    assert left.className == "limb-sym__left"
    assert "width" in left.style                          # widths stay dynamic
    assert right.className == "limb-sym__right"


def test_zscore_heatmap_classes_and_dynamic_cells():
    from aspire_dash.anthropometric import zscore_heatmap
    athletes = [{"id": 1, "name": "Ali Turki"}, {"id": 2, "name": "Mo Hosny"}]
    measures = [{"key": "stature", "label": "Stature", "unit": "cm",
                 "group": "Size"},
                {"key": "triceps", "label": "Triceps", "unit": "mm",
                 "group": "Skinfolds"}]
    matrix = {1: {"stature": 1.2, "triceps": -0.4},
              2: {"stature": None, "triceps": 0.9}}
    raw = {1: {"stature": 184.0, "triceps": 8.2},
           2: {"stature": None, "triceps": 11.0}}
    stats = {"stature": {"mean": 178.0, "sd": 5.0, "n": 2},
             "triceps": {"mean": 9.5, "sd": 1.4, "n": 2}}
    out = zscore_heatmap(athletes, measures, matrix, raw, stats)
    assert out.className == "zscore-heatmap"
    legend, wrap = out.children
    assert legend.className == "zscore-heatmap__legend"
    assert wrap.className == "zscore-table-wrap"
    table = wrap.children
    assert table.className == "zscore-table"
    header = table.children[0]
    assert header.children[0].className == "zscore-table__measure-h"
    group_row = table.children[1]
    assert group_row.children[0].className == "zscore-table__group"
    data_row = table.children[2]
    z_cell = data_row.children[3]
    assert z_cell.className == "zscore-table__cell"
    assert "backgroundColor" in z_cell.style              # z colour stays dynamic
