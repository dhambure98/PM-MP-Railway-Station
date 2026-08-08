"""
Generate graphs for the Mini Project report
Requires: matplotlib, pandas
"""

import os
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from queue_model import mmc_metrics
from config import LAMBDA_NORMAL, MU_COUNTER, C_COUNTERS_BASE, MU_GATE, C_GATES, TOTAL_PASSENGERS

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "outputs"
DATA_PATH = PROJECT_ROOT / "data" / "passenger_flow_peak_hours.csv"
os.makedirs(OUTPUT_DIR, exist_ok=True)

GATE_LAMBDA = TOTAL_PASSENGERS / 2.0  # all passengers pass the gates in 2 hours

def plot_utilisation_comparison():
    rho_base = mmc_metrics(LAMBDA_NORMAL, MU_COUNTER, C_COUNTERS_BASE)["rho"]
    rho_busy = mmc_metrics(110, MU_COUNTER, C_COUNTERS_BASE)["rho"]
    rho_gate = GATE_LAMBDA / (C_GATES * MU_GATE)
    labels = [f"Ticket Counters\n(λ={LAMBDA_NORMAL:.0f}, c={C_COUNTERS_BASE})",
              "Ticket Counters\n(Busy λ=110)",
              f"Entry Gates\n(λ={GATE_LAMBDA:.0f}, c={C_GATES})"]
    rhos = [rho_base, rho_busy, rho_gate]
    colors = ["#e74c3c", "#c0392b", "#3498db"]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, rhos, color=colors, edgecolor="black")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Utilisation (ρ)")
    ax.set_title("Utilisation Comparison – Peak Period")
    ax.axhline(0.85, color="orange", linestyle="--", label="High congestion threshold")
    for bar, val in zip(bars, rhos):
        ax.text(bar.get_x() + bar.get_width()/2, val + 0.02, f"{val:.2f}", ha="center")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "01_utilisation_comparison.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved: {path}")

def plot_waiting_vs_counters():
    lam = 110
    mu = 40
    counters = [2, 3, 4, 5, 6]
    wqs = []
    for c in counters:
        res = mmc_metrics(lam, mu, c)
        wqs.append(res["Wq_min"] if res["stable"] else 30)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(counters, wqs, marker="o", linewidth=2, color="#2980b9")
    ax.set_xlabel("Number of Ticket Counters (c)")
    ax.set_ylabel("Average Waiting Time Wq (minutes)")
    ax.set_title("Waiting Time vs Number of Ticket Counters\n(λ = 110 passengers/hour)")
    ax.grid(True, alpha=0.3)
    for x, y in zip(counters, wqs):
        ax.annotate(f"{y:.1f} min", (x, y), textcoords="offset points", xytext=(0,8), ha="center")
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "02_waiting_vs_counters.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved: {path}")

def plot_queue_length_over_time():
    df = pd.read_csv(DATA_PATH)
    df["Arrival_Time"] = pd.to_datetime(df["Arrival_Time"], format="%H:%M:%S")
    df = df.sort_values("Arrival_Time")

    # Approximate cumulative queue proxy using rolling count of recent arrivals
    df["hour_min"] = df["Arrival_Time"].dt.strftime("%H:%M")
    # Simple bin by 10-minute intervals
    df["bin"] = df["Arrival_Time"].dt.floor("10min")
    counts = df.groupby("bin").size()

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(counts.index.strftime("%H:%M"), counts.values, marker="o", color="#8e44ad")
    ax.set_xlabel("Time")
    ax.set_ylabel("Passengers arriving per 10 min")
    ax.set_title("Arrival Intensity during Peak Period (07:00 – 09:00)")
    ax.tick_params(axis="x", rotation=45)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "03_arrival_intensity.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved: {path}")

def plot_ticket_type_comparison():
    df = pd.read_csv(DATA_PATH)
    avg = df.groupby("Ticket_Type")[["Counter_Wait_Min", "Entry_Wait_Min", "Total_Time_Min"]].mean()

    fig, ax = plt.subplots(figsize=(8, 5))
    avg.plot(kind="bar", ax=ax, edgecolor="black")
    ax.set_ylabel("Average Time (minutes)")
    ax.set_title("Average Times by Ticket Type")
    ax.set_xticklabels(avg.index, rotation=0)
    ax.legend(["Counter Wait", "Entry Wait", "Total Time"])
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "04_ticket_type_comparison.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved: {path}")

def plot_sensitivity_analysis():
    lam_range = list(range(70, 141, 5))
    mu = 40
    fig, ax = plt.subplots(figsize=(9, 5))
    for c in (3, 4, 5):
        wqs = []
        for lam in lam_range:
            res = mmc_metrics(lam, mu, c)
            wqs.append(res["Wq_min"] if res["stable"] else 30)
        ax.plot(lam_range, wqs, marker="o", label=f"c = {c} counters")
    ax.set_xlabel("Arrival rate λ (passengers/hour)")
    ax.set_ylabel("Average waiting time Wq (minutes)")
    ax.set_title("Sensitivity: Wq vs Arrival Rate for Different Counter Counts")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "05_sensitivity_analysis.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved: {path}")

if __name__ == "__main__":
    print("Generating visualisations...")
    plot_utilisation_comparison()
    plot_waiting_vs_counters()
    plot_queue_length_over_time()
    plot_ticket_type_comparison()
    plot_sensitivity_analysis()
    print("Done.")
