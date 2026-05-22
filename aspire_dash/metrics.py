"""Athlete-monitoring metrics — z-scores, moving averages, adaptive ranges.

Foundation for every longitudinal-monitoring chart in the portfolio:
- Anthropometric growth curves (LMS percentile bands)
- VALD jump-height adaptive ranges (Roshan-Newell)
- Endurance load ACWR (acute:chronic workload ratio)
- HRV / RHR baselines (Whoop / Firstbeat / SAMS-medical)

All helpers are pandas-friendly. Pass a Series in, get a Series/dict out.
No hidden state. Caller controls window sizes + thresholds.
"""
from __future__ import annotations

import math
from typing import Iterable

import numpy as np
import pandas as pd


# ── 1. Standard deviation scores ───────────────────────────────────────────

def sds(value, mean: float, sd: float) -> float:
    """Standard deviation score = (value - mean) / sd.

    Scalar or vectorised — passes through pandas Series unchanged.

        >>> sds(180, mean=175, sd=8)
        0.625

    Returns 0.0 when sd is 0 or NaN.
    """
    if sd is None or (isinstance(sd, float) and (math.isnan(sd) or sd == 0)):
        return 0.0
    return (value - mean) / sd


def sds_series(series: pd.Series, *, baseline_window: int = 28) -> pd.Series:
    """SDS of each point relative to the rolling baseline (mean+sd) of the
    previous `baseline_window` observations. The first `baseline_window`
    rows return NaN (insufficient history)."""
    s = pd.Series(series, dtype="float64")
    rolling = s.shift(1).rolling(window=baseline_window, min_periods=baseline_window)
    return (s - rolling.mean()) / rolling.std()


# ── 2. Moving averages (rolling + EWMA) ────────────────────────────────────

def moving_average(series, window: int = 7) -> pd.Series:
    """Simple rolling mean. NaN-tolerant — uses `min_periods=1` so the
    first `window-1` rows still produce a number based on whatever's
    available so far. Good for visual sparklines.

        >>> moving_average([1, 2, 3, 4, 5], window=3).tolist()
        [1.0, 1.5, 2.0, 3.0, 4.0]
    """
    return pd.Series(series, dtype="float64").rolling(
        window=window, min_periods=1,
    ).mean()


def exponential_moving_average(series, span: int = 7) -> pd.Series:
    """EWMA — weights recent observations more heavily. Use for ACWR-style
    'acute load' calculations or RHR baselines that should adapt to
    training changes faster than a fixed-window SMA."""
    return pd.Series(series, dtype="float64").ewm(
        span=span, adjust=False,
    ).mean()


# ── 3. ACWR (acute:chronic workload ratio) ─────────────────────────────────

ACWR_SWEET_SPOT = (0.8, 1.3)   # generally accepted load-management zone
ACWR_DANGER     = 1.5          # injury risk threshold


def acwr(series, *, acute: int = 7, chronic: int = 28,
          method: str = "rolling") -> pd.Series:
    """Acute-to-chronic workload ratio.

    `method='rolling'` — flat SMA over both windows (most published).
    `method='ewma'`    — exponentially weighted (Williams et al.).

        >>> acwr([100]*30).iloc[-1]   # steady load → ratio of 1.0
        1.0
    """
    s = pd.Series(series, dtype="float64")
    if method == "ewma":
        a = exponential_moving_average(s, span=acute)
        c = exponential_moving_average(s, span=chronic)
    else:
        a = s.rolling(window=acute,   min_periods=acute).mean()
        c = s.rolling(window=chronic, min_periods=chronic).mean()
    return a / c


def acwr_zone(ratio: float) -> str:
    """Classify an ACWR value into a load-management zone.

    Returns: 'low' | 'ok' | 'high' | 'danger'.
    """
    if ratio is None or pd.isna(ratio): return "ok"
    if ratio < 0.5:                       return "low"
    if ratio < ACWR_SWEET_SPOT[0]:        return "low"
    if ratio <= ACWR_SWEET_SPOT[1]:       return "ok"
    if ratio < ACWR_DANGER:               return "high"
    return "danger"


# ── 4. Adaptive reference ranges (Roshan-Newell Bayesian) ──────────────────

def adaptive_range(series: pd.Series, *,
                    window: int = 7, k: float = 1.96) -> pd.DataFrame:
    """Rolling adaptive reference band: mean ± k·SD over the previous
    `window` observations. Returns a DataFrame with columns
    `[mean, lower, upper]` aligned to the input index.

    `k=1.96` covers ~95% of expected variability (normal-distribution).
    `k=1.0`  is the 1-SD band shown on VALD jump-height trend.

    Designed for the line-with-shaded-band charts (already used by
    `firstbeat.add_acwr_zones`).

        >>> df = adaptive_range(pd.Series([8, 9, 10, 11, 12, 11, 10, 9]))
        >>> df[["mean", "lower", "upper"]].tail(1)
    """
    s = pd.Series(series, dtype="float64")
    rolling = s.shift(1).rolling(window=window, min_periods=max(3, window // 2))
    m = rolling.mean()
    sd = rolling.std()
    return pd.DataFrame({
        "mean":  m,
        "lower": m - k * sd,
        "upper": m + k * sd,
    }, index=s.index)


# ── 5. LMS percentile bands (anthropometric) ───────────────────────────────

def lms_to_percentile(value: float, L: float, M: float, S: float) -> float:
    """Cole-Green LMS → percentile (CDC / WHO growth charts).

    L = skewness   M = median   S = coefficient of variation
    Returns percentile (0-100).
    """
    if not all(np.isfinite([value, L, M, S])) or M <= 0 or S <= 0:
        return float("nan")
    if abs(L) < 1e-6:
        z = math.log(value / M) / S
    else:
        z = ((value / M) ** L - 1) / (L * S)
    from scipy.stats import norm  # lazy — only needed for percentile output
    return float(norm.cdf(z) * 100)


def percentile_to_value(percentile: float, L: float, M: float, S: float) -> float:
    """Inverse LMS — what value sits at percentile P given L/M/S?
    Used to draw the 3rd/15th/50th/85th/97th percentile bands."""
    from scipy.stats import norm
    if not all(np.isfinite([percentile, L, M, S])) or not 0 < percentile < 100:
        return float("nan")
    z = norm.ppf(percentile / 100)
    if abs(L) < 1e-6:
        return M * math.exp(S * z)
    return M * ((1 + L * S * z) ** (1 / L))


# ── 6. Coefficient of variation, z, percentile rank ────────────────────────

def coefficient_of_variation(series) -> float:
    """SD / mean — unit-free spread. Returns NaN if mean is 0."""
    s = pd.Series(series, dtype="float64").dropna()
    if s.mean() == 0 or len(s) < 2: return float("nan")
    return s.std() / s.mean()


def z_score(value, *, sample: Iterable[float] | None = None,
             mean: float | None = None, sd: float | None = None) -> float:
    """Z-score against either a `sample` or explicit `mean`+`sd`.

        >>> z_score(95, sample=[80, 85, 90, 95, 100])
        1.41...
        >>> z_score(95, mean=90, sd=5)
        1.0
    """
    if sample is not None:
        s = pd.Series(sample, dtype="float64").dropna()
        mean = s.mean()
        sd = s.std()
    return sds(value, mean=mean, sd=sd)


def percentile_rank(value, sample: Iterable[float]) -> float:
    """Percentile rank of `value` within `sample` (0-100)."""
    s = pd.Series(sample, dtype="float64").dropna()
    if not len(s): return float("nan")
    return float((s < value).mean() * 100)
