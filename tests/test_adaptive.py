"""aspire_dash.adaptive — the promoted Roshan-Newell engine, validated cell-for-cell
against the original R (golden tables under tests/adaptive_golden/)."""
import csv
import os

import numpy as np

from aspire_dash.adaptive import em_f, k_factor

GOLD = os.path.join(os.path.dirname(__file__), "adaptive_golden")


def _frame(p):
    with open(os.path.join(GOLD, p), newline="") as f:
        return [(int(float(r["player"])), float(r["Biomarker"])) for r in csv.DictReader(f)]


def _gold(p):
    with open(os.path.join(GOLD, p), newline="") as f:
        return list(csv.DictReader(f))


def _check(tol_alpha, gold_file):
    pop, sampl = _frame("pop_frame.csv"), _frame("sampl_frame.csv")
    got = em_f(pop, sampl, "two", tol_alpha, 0.95)
    gold = _gold(gold_file)
    assert len(got) == len(gold)
    for g, r in zip(got, gold):
        assert abs(g["LAR"] - float(r["LAR"])) < 1e-6
        assert abs(g["UAR"] - float(r["UAR"])) < 1e-6


def test_golden_alpha_005():
    _check(0.05, "golden_em_a005.csv")


def test_golden_alpha_010():
    _check(0.10, "golden_em_a010.csv")


def test_k_factor_matches_golden():
    assert abs(k_factor(56, 0.05, 0.95, side=2) - 2.3521) < 1e-3
    assert abs(k_factor(56, 0.05, 0.95, side=1) - 2.0378) < 1e-3


def test_static_then_adaptive_narrows():
    pop = [(2, 34), (2, 35), (2, 36), (3, 40), (3, 41), (3, 42), (4, 29), (4, 30), (4, 31)]
    tbl = em_f(pop, [(1, 35), (1, 35.5), (1, 36), (1, 35), (1, 34.8)], "two", 0.10, 0.95)
    assert tbl[0]["LAR"] == tbl[1]["LAR"]        # cold-start static band on pts 1-2
    assert (tbl[2]["UAR"] - tbl[2]["LAR"]) < (tbl[0]["UAR"] - tbl[0]["LAR"])
    for r in tbl:
        assert r["LAR"] <= r["UAR"]
