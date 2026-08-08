"""
Simple M/M/c calculations for the Railway Station project
"""

import math
import sys
from math import factorial

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

def erlang_c(c, rho):
    """Probability of waiting (Erlang-C)"""
    if rho >= 1:
        return 1.0
    a = c * rho
    sum_term = sum([(a ** k) / factorial(k) for k in range(c)])
    last = (a ** c) / factorial(c) / (1 - rho)
    return last / (sum_term + last)

def mmc_metrics(lam, mu, c):
    """
    Returns utilisation, P(wait), Lq, Wq (in minutes), L, W
    """
    if c * mu <= lam:
        return {
            "rho": lam / (c * mu),
            "P_wait": 1.0,
            "Lq": float("inf"),
            "Wq_min": float("inf"),
            "L": float("inf"),
            "W_min": float("inf"),
            "stable": False
        }

    rho = lam / (c * mu)
    Pw = erlang_c(c, rho)
    Wq_hour = Pw / (c * mu - lam)
    Lq = lam * Wq_hour
    W_hour = Wq_hour + 1/mu
    L = lam * W_hour

    return {
        "rho": round(rho, 4),
        "P_wait": round(Pw, 4),
        "Lq": round(Lq, 3),
        "Wq_min": round(Wq_hour * 60, 2),
        "L": round(L, 3),
        "W_min": round(W_hour * 60, 2),
        "stable": True
    }

def littles_law_check(lam, Wq_min):
    """Lq should ≈ λ * (Wq in hours)"""
    Wq_hour = Wq_min / 60.0
    return round(lam * Wq_hour, 3)

if __name__ == "__main__":
    # Demo matching the report
    print("=== Baseline (λ=90, μ=40, c=3) ===")
    r = mmc_metrics(90, 40, 3)
    print(r)
    print("Little's Law Lq check:", littles_law_check(90, r["Wq_min"]))

    print("\n=== Busy (λ=110, μ=40, c=3) ===")
    r2 = mmc_metrics(110, 40, 3)
    print(r2)

    print("\n=== Busy + 5 counters ===")
    r3 = mmc_metrics(110, 40, 5)
    print(r3)
