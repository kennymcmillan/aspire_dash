"""Squad-relative z-score engine — pure math, no Dash deps.

Generic helpers for "compute and colour-code each athlete's standing vs the
group". Born in the ``DASH_Anthro`` ISAK app (phantom-stratagem skinfold z-
scores) but written generically so it can drive any squad-comparison view:

- ``compute_squad_z_scores(athletes, measurement_keys)`` returns the per-
  athlete z matrix + per-key mean/SD + 3 ready-to-display insight strings.
- ``z_score(value, mu, sigma)`` and ``z_score_color(z, inverted)`` are
  building blocks if you want to colour cells in a custom table.
- ``INVERTED_MEASURES`` flags keys where lower is better (skinfolds, fat
  mass) so the 7-bucket colour scale flips automatically.
- ``Z_SCORE_MEASURES`` is the default ISAK metadata table the heatmap +
  radar in ``aspire_dash.anthropometric`` render against. Pass a custom
  list for non-anthro domains.

Domain-independent: nothing in here knows about ISAK or anthropometry
beyond the labels in the optional ``Z_SCORE_MEASURES`` list. The engine
works on any ``{id, name, values: {key: float|None}}`` shape and any
iterable of measurement keys.

Used by ``aspire_dash.anthropometric.zscore_heatmap`` and
``aspire_dash.anthropometric.zscore_radar_figure`` — those modules re-
import the colour helper + INVERTED_MEASURES from here.
"""
from __future__ import annotations

import math
from typing import Iterable

__all__ = [
    "INVERTED_MEASURES",
    "Z_SCORE_MEASURES",
    "is_inverted",
    "z_score",
    "z_score_color",
    "compute_squad_z_scores",
]


# Measures where LOWER is better (skinfolds, %BF, fat mass).
# The 7-bucket colour helper flips its sign when the key is in this set.
INVERTED_MEASURES = {
    "sf_triceps", "sf_subscapular", "sf_biceps", "sf_iliacCrest",
    "sf_supraspinale", "sf_abdominal", "sf_frontThigh", "sf_medialCalf",
    "sumOf8", "sumOf4", "percentBodyFat", "fatMass",
}

# Default ISAK measurement metadata for ``zscore_heatmap``. Order matters —
# group blocks come from this list. Apps that drive the heatmap with a
# different domain should pass their own list with the same shape:
# ``{key, label, unit, group}``.
Z_SCORE_MEASURES = [
    {"key": "bodyMass", "label": "Body Mass", "unit": "kg", "group": "Basic"},
    {"key": "stature", "label": "Stature", "unit": "cm", "group": "Basic"},
    {"key": "sumOf8", "label": "Sum of 8 SF", "unit": "mm", "group": "Calculated"},
    {"key": "percentBodyFat", "label": "Body Fat", "unit": "%", "group": "Calculated"},
    {"key": "fatFreeMass", "label": "FFM", "unit": "kg", "group": "Calculated"},
    {"key": "fatMass", "label": "Fat Mass", "unit": "kg", "group": "Calculated"},
    {"key": "sf_triceps", "label": "Triceps", "unit": "mm", "group": "Skinfolds"},
    {"key": "sf_subscapular", "label": "Subscapular", "unit": "mm", "group": "Skinfolds"},
    {"key": "sf_biceps", "label": "Biceps", "unit": "mm", "group": "Skinfolds"},
    {"key": "sf_iliacCrest", "label": "Iliac Crest", "unit": "mm", "group": "Skinfolds"},
    {"key": "sf_supraspinale", "label": "Supraspinale", "unit": "mm", "group": "Skinfolds"},
    {"key": "sf_abdominal", "label": "Abdominal", "unit": "mm", "group": "Skinfolds"},
    {"key": "sf_frontThigh", "label": "Front Thigh", "unit": "mm", "group": "Skinfolds"},
    {"key": "sf_medialCalf", "label": "Medial Calf", "unit": "mm", "group": "Skinfolds"},
    {"key": "g_armRelaxed", "label": "Arm Relaxed", "unit": "cm", "group": "Girths"},
    {"key": "g_armFlexed", "label": "Arm Flexed", "unit": "cm", "group": "Girths"},
    {"key": "g_calf", "label": "Calf", "unit": "cm", "group": "Girths"},
    {"key": "b_humerus", "label": "Humerus", "unit": "cm", "group": "Breadths"},
    {"key": "b_femur", "label": "Femur", "unit": "cm", "group": "Breadths"},
]


def _mean(vals):
    vals = [v for v in vals if v is not None and not (isinstance(v, float) and math.isnan(v))]
    if not vals:
        return 0.0
    return sum(vals) / len(vals)


def _sd(vals):
    vals = [v for v in vals if v is not None and not (isinstance(v, float) and math.isnan(v))]
    if len(vals) < 2:
        return 0.0
    m = _mean(vals)
    var = sum((v - m) ** 2 for v in vals) / (len(vals) - 1)
    return math.sqrt(var)


def is_inverted(key: str) -> bool:
    """Return True if higher is worse for this measurement key.

    Used by ``z_score_color`` to flip the colour scale so that good
    standings always render green regardless of metric direction.
    """
    return key in INVERTED_MEASURES


def z_score(value: float, mu: float, sigma: float):
    """Standard z-score with a guard for near-zero variance.

    Returns ``None`` when ``sigma < 0.01`` so callers can render a
    blank cell rather than an inf/NaN. Otherwise ``(value - mu) / sigma``.
    """
    if sigma < 0.01:
        return None
    return (value - mu) / sigma


def compute_squad_z_scores(athletes, measurement_keys: Iterable[str]):
    """Compute per-athlete z-scores against the squad's own mean+SD.

    Parameters
    ----------
    athletes : list[dict]
        ``[{"id": ..., "name": ..., "values": {key: float|None}}, ...]``.
        Must contain at least 3 athletes — otherwise an explanatory
        insight is returned and the matrix is empty.
    measurement_keys : Iterable[str]
        Which keys inside each athlete's ``values`` dict to z-score.

    Returns
    -------
    dict with three top-level keys:
        ``matrix``   — ``{athlete_id: {key: z|None}}``
        ``stats``    — ``{key: {"mean": float, "sd": float, "n": int}}``
        ``insights`` — ``list[str]`` of 0..N human-readable headline lines
    """
    measurement_keys = list(measurement_keys)
    if len(athletes) < 3:
        return {
            "matrix": {},
            "stats": {},
            "insights": ["Z-score analysis requires at least 3 athletes in the squad."],
        }

    stats = {}
    for key in measurement_keys:
        valid = [a["values"].get(key) for a in athletes]
        valid = [v for v in valid if v is not None]
        stats[key] = {"mean": _mean(valid), "sd": _sd(valid), "n": len(valid)}

    matrix = {}
    for a in athletes:
        matrix[a["id"]] = {}
        for key in measurement_keys:
            v = a["values"].get(key)
            if v is None:
                matrix[a["id"]][key] = None
            else:
                matrix[a["id"]][key] = z_score(v, stats[key]["mean"], stats[key]["sd"])

    insights = _generate_insights(athletes, matrix, stats)
    return {"matrix": matrix, "stats": stats, "insights": insights}


def _generate_insights(athletes, matrix, stats):
    """Three default headline insights for the ISAK domain.

    Safe on any input — gracefully skips keys that aren't present in the
    supplied measurement metadata. Callers can ignore the ``insights``
    list and roll their own narrative if they're not in the anthro
    domain.
    """
    out = []
    if stats.get("sumOf8", {}).get("n", 0) >= 3:
        best = min(
            ((a["values"].get("sumOf8"), a["name"]) for a in athletes if a["values"].get("sumOf8") is not None),
            default=None,
        )
        if best:
            out.append(f"{best[1]} has the lowest Sum of 8 Skinfolds ({best[0]:.1f} mm)")

    if stats.get("fatFreeMass", {}).get("n", 0) >= 3:
        best = max(
            ((a["values"].get("fatFreeMass"), a["name"]) for a in athletes if a["values"].get("fatFreeMass") is not None),
            default=None,
        )
        if best:
            out.append(f"{best[1]} has the highest fat-free mass ({best[0]:.1f} kg)")

    if stats.get("percentBodyFat", {}).get("n", 0) >= 3:
        above = [a for a in athletes if (matrix.get(a["id"], {}).get("percentBodyFat") or 0) > 1]
        if above:
            s = "s" if len(above) > 1 else ""
            out.append(f"{len(above)} athlete{s} above +1 SD for body fat percentage")

    s8 = stats.get("sumOf8", {})
    if s8.get("sd", 0) > 0 and s8.get("mean", 0) > 0:
        cv = (s8["sd"] / s8["mean"]) * 100
        label = "homogeneous" if cv < 15 else "moderately variable" if cv < 25 else "highly variable"
        out.append(f"Squad Sum of 8 SF profiles are {label} (CV = {cv:.0f}%)")

    return out


def z_score_color(z, inverted: bool = False):
    """Return ``(bg, text)`` hex colours for a 7-bucket diverging scale.

    Buckets (effective z, where inverted = -z):
        z >= +2       deep green / white
        +1 .. +2      pale green / dark green
        +0.5 .. +1    very pale green / mid green
        -0.5 .. +0.5  near-white slate / dark slate text (within ±0.5 SD)
        -1 .. -0.5    very pale red / dark red
        -2 .. -1      pale red / dark red
        z <= -2       deep red / white
        None          neutral slate / muted text (no data)

    Pass ``inverted=True`` for measurements where lower is better — the
    colour scale flips so "good" always reads green.
    """
    if z is None:
        return ("#f8fafc", "#94a3b8")
    eff = -z if inverted else z
    if eff >= 2:
        return ("#065f46", "white")
    if eff >= 1:
        return ("#d1fae5", "#065f46")
    if eff >= 0.5:
        return ("#ecfdf5", "#047857")
    if eff > -0.5:
        return ("#f8fafc", "#475569")
    if eff > -1:
        return ("#fef2f2", "#991b1b")
    if eff > -2:
        return ("#fee2e2", "#991b1b")
    return ("#991b1b", "white")
