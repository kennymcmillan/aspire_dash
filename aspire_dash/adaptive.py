"""Roshan & Newell Bayesian adaptive reference ranges - faithful Python port.

Line-for-line port of the original R engine (John_Jump: EM.R, EMsourcecodes.R,
tolerance.R) validated cell-for-cell against R output (see tests/test_golden.py).
Pure numpy + scipy, no R, no network - so it runs in-process in any Dash app and
wraps into a FastAPI /compute-ranges service.

Structure (mirrors the R):
  k_factor / normtol_int  <- tolerance.R  (cold-start static tolerance band, Howe HE)
  SemaState + fit_sema / fit_sema_ar <- EMsourcecodes.R  (streaming EM, CDSS T1/T2/T3)
  em_f  <- EM.R  (orchestrator: points 1-2 = static band, 3+ = adaptive band)

Contract per EM.f: sample points 1 and 2 take the population tolerance interval;
points 3..n take the streaming SEMA posterior-predictive band
  s.mean +/- qnorm(1 - alpha/2) * s.sd
computed from the target's first (j-1) observations, BEFORE ingesting point j.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.stats import norm, nct, chi2

__all__ = ["k_factor", "normtol_int", "SemaState", "em_f", "adaptive_range_table"]


# ---------------------------------------------------------------------------
# tolerance.R : K.factor + normtol.int  (cold-start static tolerance interval)
# ---------------------------------------------------------------------------

def k_factor(n: int, alpha: float = 0.05, P: float = 0.99, side: int = 1,
             f: float | None = None) -> float:
    """Normal tolerance factor. side=1 exact (noncentral t); side=2 Howe 'HE'.
    Verbatim port of tolerance.R K.factor (only the code paths the app reaches)."""
    if f is None:
        f = n - 1
    if side == 1:
        z_p = norm.ppf(P)
        ncp = np.sqrt(n) * z_p
        t_a = nct.ppf(1 - alpha, df=f, nc=ncp)
        return float(t_a / np.sqrt(n))
    # side == 2, method "HE" (Howe 1969) - tolerance.R lines 32-53
    chi_a = chi2.ppf(alpha, f)
    z_p = norm.ppf((1 + P) / 2)
    z_a = norm.ppf((2 - alpha) / 2)
    df_cut = n ** 2 * (1 + 1 / z_a ** 2)
    V = 1 + z_a ** 2 / n + ((3 - z_p ** 2) * z_a ** 4) / (6 * n ** 2)
    K1 = z_p * np.sqrt(V * (1 + (n * V / (2 * f)) * (1 + 1 / z_a ** 2)))
    G = (f - 2 - chi_a) / (2 * (n + 1) ** 2)
    K2 = z_p * np.sqrt(((f * (1 + 1 / n)) / chi_a) * (1 + G))
    if f > df_cut:
        K = K1
    else:
        K = K2
        if np.isnan(K):
            K = 0.0
    return float(K)


def normtol_int(x, alpha: float = 0.05, P: float = 0.99, side: int = 1,
                log_norm: bool = False) -> dict:
    """Two-/one-sided normal tolerance interval. Port of tolerance.R normtol.int."""
    x = np.asarray([float(v) for v in x], dtype=float)
    if log_norm:
        x = np.log(x)
    x_bar = float(np.mean(x))
    s = float(np.std(x, ddof=1))
    n = len(x)
    K = k_factor(n=n, alpha=alpha, P=P, side=side)
    lower, upper = x_bar - s * K, x_bar + s * K
    if log_norm:
        lower, upper, x_bar = np.exp(lower), np.exp(upper), np.exp(x_bar)
    return {"alpha": alpha, "P": P, "x_bar": x_bar, "lower": lower, "upper": upper}


# ---------------------------------------------------------------------------
# EMsourcecodes.R : streaming EM approximation (SEMA), random intercept
# ---------------------------------------------------------------------------

def _update_average(oldmean, obs, n):
    return oldmean + (obs - oldmean) / n


@dataclass
class _Ind:
    mean_y_j: float
    hatmu_j: float
    n_j: int
    hatnu_j: float
    mean_ysq: float


@dataclass
class SemaState:
    n: int = 0
    J: int = 0
    T1: float = 0.0
    T2: float = 0.0
    T3: dict = field(default_factory=dict)       # id -> T3_i
    sigmasq: dict = field(default_factory=dict)  # id -> sigma^2_i
    individual: dict = field(default_factory=dict)  # id -> _Ind
    mu: float = 0.0        # parameters[1]
    tausq: float = 1.0     # parameters[2]
    order: list = field(default_factory=list)     # id insertion order (last = target)

    def _step(self, id_, obs, *, first_ever):
        # mu_hat: obs for the very first observation ever, else the model mean
        mu_hat = obs if first_ever else self.mu
        self.n += 1
        if id_ not in self.individual:            # add new person
            self.J += 1
            self.individual[id_] = _Ind(mean_y_j=obs, hatmu_j=0.0, n_j=0,
                                        hatnu_j=0.0, mean_ysq=obs ** 2)
            self.T3[id_] = 0.0
            self.sigmasq[id_] = 1.0
            self.order.append(id_)
        row = self.individual[id_]
        tausq = self.tausq
        sigmasq_i = self.sigmasq[id_]
        # subtract previous contributions from the CDSS
        self.T1 -= row.hatmu_j
        self.T2 -= (row.hatmu_j ** 2 + row.hatnu_j)
        self.T3[id_] -= (row.mean_ysq - 2 * row.mean_y_j * row.hatmu_j
                         + row.hatmu_j ** 2 + row.hatnu_j) * row.n_j
        # update individual moments
        row.n_j += 1
        row.mean_y_j = _update_average(row.mean_y_j, obs, row.n_j)
        row.mean_ysq = _update_average(row.mean_ysq, obs ** 2, row.n_j)
        # individual parameters (rho uses sigma^2_i from BEFORE this re-estimation)
        rho = tausq / (tausq + sigmasq_i / row.n_j)
        row.hatmu_j = rho * row.mean_y_j + (1 - rho) * mu_hat
        row.hatnu_j = tausq * (1 - rho)
        # add updated contributions
        self.T1 += row.hatmu_j
        self.T2 += (row.hatmu_j ** 2 + row.hatnu_j)
        self.T3[id_] += (row.mean_ysq - 2 * row.mean_y_j * row.hatmu_j
                         + row.hatmu_j ** 2 + row.hatnu_j) * row.n_j
        # model parameters
        self.mu = self.T1 / self.J
        self.tausq = self.T2 / self.J - self.mu ** 2
        self.sigmasq[id_] = self.T3[id_] / row.n_j

    def fit_sema(self, id_, obs, first_ever=False):
        """State-only streaming update (EMsourcecodes.R fitSema)."""
        self._step(id_, obs, first_ever=first_ever)

    def adaptive_band(self, tol_por, side="two"):
        """Posterior-predictive band for the LAST individual (the target), computed
        from current state BEFORE the next obs is ingested (fitSema.AR range block).
        `tol_por` here is EM.f's alpha (= 1 - original coverage)."""
        last = self.order[-1]
        row = self.individual[last]
        sig = self.sigmasq[last]
        num = (row.n_j * row.mean_y_j) / sig + self.mu / self.tausq
        den = (row.n_j / sig) + 1 / self.tausq
        s_mean = num / den
        s_sd = np.sqrt(1 / den + sig)
        if side == "two":
            z = norm.ppf(1 - tol_por / 2)
            return s_mean - z * s_sd, s_mean + z * s_sd
        z = norm.ppf(1 - tol_por)
        if side == "low":
            return s_mean - z * s_sd, np.nan
        return np.nan, s_mean + z * s_sd

    def fit_sema_ar(self, id_, obs, tol_por, side="two"):
        """Adaptive-range then state update (EMsourcecodes.R fitSema.AR)."""
        band = self.adaptive_band(tol_por, side=side)  # BEFORE ingesting obs
        self._step(id_, obs, first_ever=False)
        return band


# ---------------------------------------------------------------------------
# EM.R : orchestrator
# ---------------------------------------------------------------------------

def em_f(pop, sampl, side="two", tol_alpha=0.05, tol_por=0.95):
    """Faithful port of EM.f. `pop`/`sampl` are lists of (player, biomarker) in the
    order to stream (Time-sorted upstream). Returns list of dicts
    {test_time, LAR, value, UAR, alpha}. Sample = the target; its player id must be
    distinct from pop ids. Points 1-2 use the population tolerance interval; 3+ use
    the streaming SEMA band. `tol_alpha` = 1 - confidence; `tol_por` = coverage."""
    alpha = 1 - tol_por  # EM.R line 10
    pop_tol_values = [float(b) for (_p, b) in pop]           # full pop for tol band
    stream_pop = [(p, float(b)) for (p, b) in pop if p != 1]  # exclude player 1
    sampl = [(p, float(b)) for (p, b) in sampl]

    st = SemaState()
    for i, (pid, obs) in enumerate(stream_pop):
        st.fit_sema(pid, obs, first_ever=(i == 0))
    tid = sampl[0][0]
    st.fit_sema(tid, sampl[0][1])   # sample obs 1 (state only)
    st.fit_sema(tid, sampl[1][1])   # sample obs 2 (state only)

    # static tolerance band for points 1 and 2
    ti = normtol_int(pop_tol_values, alpha=tol_alpha, P=(1 - alpha), side=(2 if side == "two" else 1))
    if side == "two":
        static = (ti["lower"], ti["upper"])
    elif side == "low":
        static = (ti["lower"], np.nan)
    else:
        static = (np.nan, ti["upper"])

    rows = [
        {"test_time": 1, "LAR": static[0], "value": sampl[0][1], "UAR": static[1], "alpha": alpha},
        {"test_time": 2, "LAR": static[0], "value": sampl[1][1], "UAR": static[1], "alpha": alpha},
    ]
    for j in range(2, len(sampl)):  # points 3..n (0-indexed j>=2)
        lar, uar = st.fit_sema_ar(tid, sampl[j][1], tol_por=alpha, side=side)
        rows.append({"test_time": j + 1, "LAR": lar, "value": sampl[j][1],
                     "UAR": uar, "alpha": alpha})
    return rows


def adaptive_range_table(target_values, population_series, side="two",
                         tol_alpha=0.05, tol_por=0.95):
    """App-facing convenience: target as a plain value list (date-sorted), population
    as {athlete_key: [values...]}. Assigns the target player id 1 and pop ids 2.. ,
    then runs em_f. Returns the per-observation band table."""
    pop = []
    for k, (_key, vals) in enumerate(population_series.items(), start=2):
        for v in vals:
            if v is not None and not (isinstance(v, float) and np.isnan(v)):
                pop.append((k, float(v)))
    sampl = [(1, float(v)) for v in target_values
             if v is not None and not (isinstance(v, float) and np.isnan(v))]
    if len(sampl) < 2 or not pop:
        return []
    return em_f(pop, sampl, side=side, tol_alpha=tol_alpha, tol_por=tol_por)
