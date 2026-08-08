"""
Main script: run calculations + generate all outputs
"""

import os
import sys
from pathlib import Path
sys.path.append(os.path.dirname(__file__))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import pandas as pd

from config import SCENARIOS, LAMBDA_NORMAL, MU_COUNTER, C_COUNTERS_BASE, MU_GATE, C_GATES
from queue_model import mmc_metrics, littles_law_check
import visualization

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "passenger_flow_peak_hours.csv"

print("=" * 60)
print("Railway Station Passenger Flow – Performance Analysis")
print("=" * 60)

print("\n--- Scenario Analysis (M/M/c) ---")
for sc in SCENARIOS:
    res = mmc_metrics(sc["lambda"], sc["mu"], sc["c"])
    print(f"\n{sc['name']}")
    print(f"  λ={sc['lambda']}, μ={sc['mu']}, c={sc['c']}")
    print(f"  ρ = {res['rho']}")
    print(f"  Avg Queue Length Lq = {res['Lq']}")
    print(f"  Avg Wait Wq = {res['Wq_min']} min")
    if res["stable"]:
        print(f"  Little's Law check Lq ≈ {littles_law_check(sc['lambda'], res['Wq_min'])}")

print("\n--- Sensitivity Analysis (arrival rate sweep) ---")
print(f"{'λ (/hr)':>8} {'ρ(c=3)':>9} {'Wq min (c=3)':>14} {'Lq (c=3)':>10} {'Wq min (c=5)':>14}")
for lam in range(70, 131, 10):
    r3 = mmc_metrics(lam, MU_COUNTER, C_COUNTERS_BASE)
    r5 = mmc_metrics(lam, MU_COUNTER, 5)
    rho3 = f"{r3['rho']:.4f}"
    wq3 = r3["Wq_min"] if r3["stable"] else "inf"
    lq3 = r3["Lq"] if r3["stable"] else "inf"
    wq5 = r5["Wq_min"] if r5["stable"] else "inf"
    print(f"{lam:>8} {rho3:>9} {wq3!s:>14} {lq3!s:>10} {wq5!s:>14}")

print("\n--- Entry Gate comparison (all 400 passengers pass gates) ---")
lam_gate = 400.0 / 2.0
rg = mmc_metrics(lam_gate, MU_GATE, C_GATES)
print(f"  Gate λ = {lam_gate:.0f}/hr, μ = {MU_GATE}/hr, c = {C_GATES}")
print(f"  Gate ρ = {rg['rho']}")
print(f"  Gate Wq = {rg['Wq_min']} min")

print("\n--- Validation: simulated data vs analytical model (Normal) ---")
df = pd.read_csv(DATA_PATH)
n = df[df["Ticket_Type"] == "Normal"]
sim_wait = n["Counter_Wait_Min"].mean()
sim_svc = n["Counter_Service_Min"].mean()
res = mmc_metrics(LAMBDA_NORMAL, MU_COUNTER, C_COUNTERS_BASE)
print(f"  Simulated mean counter wait = {sim_wait:.2f} min vs analytical Wq = {res['Wq_min']:.2f} min "
      f"(difference {abs(sim_wait - res['Wq_min']) / res['Wq_min'] * 100:.1f}%)")
print(f"  Simulated mean service = {sim_svc:.2f} min -> μ ≈ {60 / sim_svc:.1f}/hr (target {MU_COUNTER:.0f})")

print("\n--- Generating graphs ---")
visualization.plot_utilisation_comparison()
visualization.plot_waiting_vs_counters()
visualization.plot_queue_length_over_time()
visualization.plot_ticket_type_comparison()
visualization.plot_sensitivity_analysis()

print("\nAll outputs saved to the 'outputs/' folder.")
print("Dataset is in 'data/passenger_flow_peak_hours.csv'")
