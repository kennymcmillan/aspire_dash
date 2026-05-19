"""Lightweight summary statistics for Aspire Dash dashboards.

A single `compute_stats(values)` helper used across athlete-monitoring apps
to render the standard 5-stat row (Latest / Mean / Std Dev / Change / N).
"""
from __future__ import annotations

from typing import Iterable

import numpy as np

__all__ = ["compute_stats"]


def compute_stats(values: Iterable[float]) -> dict:
    """Return mean, std, cv, min, max, n for a list of values.

    All numerics are returned as plain Python floats so the dict is
    JSON-serialisable (useful for `dcc.Store`).
    """
    vals = list(values)
    if not vals:
        return {"mean": 0.0, "std": 0.0, "cv": 0.0,
                "min": 0.0, "max": 0.0, "n": 0}
    m = float(np.mean(vals))
    s = float(np.std(vals))
    return {
        "mean": m,
        "std": s,
        "cv": (s / m * 100) if m != 0 else 0.0,
        "min": float(np.min(vals)),
        "max": float(np.max(vals)),
        "n": len(vals),
    }
