"""
Main script: run calculations + generate all outputs
"""

import os
import sys
sys.path.append(os.path.dirname(__file__))

from config import SCENARIOS, LAMBDA_NORMAL, MU_COUNTER, C_COUNTERS_BASE
from queue_model import mmc_metrics, littles_law_check
import visualization

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

print("\n--- Generating graphs ---")
visualization.plot_utilisation_comparison()
visualization.plot_waiting_vs_counters()
visualization.plot_queue_length_over_time()
visualization.plot_ticket_type_comparison()

print("\nAll outputs saved to the 'outputs/' folder.")
print("Dataset is in 'data/passenger_flow_peak_hours.csv'")
