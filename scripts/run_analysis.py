"""
Main script: run calculations + generate all outputs
"""

import os
import random
import sys
from pathlib import Path
sys.path.append(os.path.dirname(__file__))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import pandas as pd

from config import (SCENARIOS, LAMBDA_NORMAL, LAMBDA_ONLINE, MU_COUNTER, C_COUNTERS_BASE, MU_GATE, C_GATES)
from queue_model import mmc_metrics, littles_law_check, generate_arrivals, simulate_mmc_queue
import visualization

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "passenger_flow_peak_hours.csv"
XLSX_PATH = PROJECT_ROOT / "outputs" / "performance_analysis.xlsx"

SEED = 42

print("=" * 60)
print("Railway Station Passenger Flow – Performance Analysis")
print("=" * 60)

df = pd.read_csv(DATA_PATH)
normal = df[df["Ticket_Type"] == "Normal"]
online = df[df["Ticket_Type"] == "Online"]
n_norm, n_online = len(normal), len(online)
mu_implied = 60.0 / normal["Counter_Service_Min"].mean()

print("\n--- Dataset Statistics ---")
print(f"  Total passengers            : {len(df)}")
print(f"  Normal ticket               : {n_norm} ({n_norm / len(df) * 100:.1f}%)")
print(f"  Online ticket               : {n_online} ({n_online / len(df) * 100:.1f}%)")
print(f"  Window                      : 07:00 - 09:00 (2 hours)")
print(f"  Normal arrival rate λ       : {LAMBDA_NORMAL:.0f} / hour")
print(f"  Online arrival rate λ       : {LAMBDA_ONLINE:.0f} / hour")
print(f"  System throughput           : {len(df) / 2:.0f} passengers/hour")
print(f"  Mean counter service (N)    : {normal['Counter_Service_Min'].mean():.3f} min -> μ ≈ {mu_implied:.1f} / hour")
print(f"  Mean counter wait (N)       : {normal['Counter_Wait_Min'].mean():.2f} min")
print(f"  Mean gate wait (all)        : {df['Gate_Wait_Min'].mean():.2f} min")
print(f"  Mean total time (Normal)    : {normal['Total_Time_Min'].mean():.2f} min")
print(f"  Mean total time (Online)    : {online['Total_Time_Min'].mean():.2f} min")

print("\n--- Scenario Analysis (M/M/c) ---")
for sc in SCENARIOS:
    res = mmc_metrics(sc["lambda"], sc["mu"], sc["c"])
    print(f"\n{sc['name']}")
    print(f"  λ={sc['lambda']}, μ={sc['mu']}, c={sc['c']}")
    print(f"  ρ = {res['rho']}")
    print(f"  Avg Queue Length Lq = {res['Lq']}")
    print(f"  Avg Wait Wq = {res['Wq_min']} min")
    if res["stable"]:
        ll = littles_law_check(sc["lambda"], res["Wq_min"])
        print(f"  Little's Law check: Erlang-C Lq = {res['Lq']} vs λ·Wq = {ll}")

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
sim_wait = normal["Counter_Wait_Min"].mean()
sim_svc = normal["Counter_Service_Min"].mean()
res = mmc_metrics(LAMBDA_NORMAL, MU_COUNTER, C_COUNTERS_BASE)
print(f"  Simulated mean counter wait = {sim_wait:.2f} min vs analytical Wq = {res['Wq_min']:.2f} min "
      f"(difference {abs(sim_wait - res['Wq_min']) / res['Wq_min'] * 100:.1f}%)")
print(f"  Simulated mean service = {sim_svc:.2f} min -> μ ≈ {60 / sim_svc:.1f}/hr (target {MU_COUNTER:.0f})")

print("\n--- Scenario simulation (controlled experiment, same seed per replication) ---")

N_REPS = 20

def run_scenario_sim(sc, seed):
    """One discrete-event M/M/c replication for a scenario (fixed 2-hour window)."""
    lam, mu, c = sc["lambda"], sc["mu"], sc["c"]
    n = round(lam * 2.0)
    rng = random.Random(seed)
    arrivals = generate_arrivals(n, lam, rng)
    sim = simulate_mmc_queue(arrivals, 60.0 / mu, c, rng)
    waits = [w for w, _, _ in sim]
    services = [s for _, s, _ in sim]
    records = []
    for i, (a, (w, s, d)) in enumerate(zip(arrivals, sim), 1):
        records.append({
            "Passenger_ID": f"P{i:03d}",
            "Arrival_Time_min": round(a, 2),
            "Counter_Wait_Min": round(w, 2),
            "Counter_Service_Min": round(s, 2),
            "Counter_Exit_Min": round(d, 2),
        })
    return {
        "records": records,
        "n": n,
        "mean_wait": sum(waits) / n,
        "mean_service": sum(services) / n,
    }

summary_rows = []
per_scenario_sheets = {}
for sc in SCENARIOS:
    a = mmc_metrics(sc["lambda"], sc["mu"], sc["c"])
    rep1 = run_scenario_sim(sc, SEED)
    sim_waits, sim_services = [], []
    for rep in range(N_REPS):
        r = run_scenario_sim(sc, SEED + rep)
        sim_waits.append(r["mean_wait"])
        sim_services.append(r["mean_service"])
    mean_wait = sum(sim_waits) / N_REPS
    mean_service = sum(sim_services) / N_REPS
    summary_rows.append({
        "Scenario": sc["name"],
        "Lambda_per_hr": sc["lambda"],
        "Mu_per_hr": sc["mu"],
        "c_counters": sc["c"],
        "rho_analytical": a["rho"],
        "P_wait": a["P_wait"],
        "Lq_analytical": a["Lq"],
        "Wq_min_analytical": a["Wq_min"],
        "Sim_Mean_Wait_Min": round(mean_wait, 2),
        "Sim_Mean_Service_Min": round(mean_service, 2),
        "Stable": a["stable"],
    })
    per_scenario_sheets[sc["name"]] = pd.DataFrame(rep1["records"])
    print(f"  {sc['name']:<24} λ={sc['lambda']:<3} μ={sc['mu']:<3} c={sc['c']}  "
          f"analytical Wq={a['Wq_min']} min | simulated mean wait (avg {N_REPS} reps)={mean_wait:.2f} min")

summary_df = pd.DataFrame(summary_rows)
print(f"\n  Note: simulated mean wait is the average over {N_REPS} independent 2-hour "
      "replications (queue starts empty each replication).")
print("  Because the finite window includes the transient warm-up, simulated waits sit")
print("  at or below the steady-state M/M/c Wq; the gap grows with utilisation.")
print("\n  Summary (also exported to Excel):")
print(summary_df.to_string(index=False))

with pd.ExcelWriter(XLSX_PATH, engine="openpyxl") as writer:
    summary_df.to_excel(writer, sheet_name="Summary", index=False)
    for sheet_name, sheet_df in per_scenario_sheets.items():
        sheet_df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
print(f"\nSaved: {XLSX_PATH}")

print("\n--- Generating graphs ---")
visualization.plot_utilisation_comparison()
visualization.plot_waiting_vs_counters()
visualization.plot_queue_length_over_time()
visualization.plot_ticket_type_comparison()
visualization.plot_sensitivity_analysis()
visualization.plot_waiting_trend()
visualization.plot_system_flow_diagram()

print("\nAll outputs saved to the 'outputs/' folder.")
print("Dataset is in 'data/passenger_flow_peak_hours.csv'")
