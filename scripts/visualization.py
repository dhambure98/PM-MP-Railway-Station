"""
Generate graphs for the Mini Project report
Requires: matplotlib, pandas
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
from queue_model import mmc_metrics

OUTPUT_DIR = "/home/workdir/artifacts/railway_performance_modelling/outputs"
DATA_PATH = "/home/workdir/artifacts/railway_performance_modelling/data/passenger_flow_peak_hours.csv"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def plot_utilisation_comparison():
    labels = ["Ticket Counters\n(c=3, λ=90)", "Ticket Counters\n(Busy λ=110)", "Entry Gates\n(approx)"]
    rhos = [0.75, 0.92, 0.30]  # illustrative gate util
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

if __name__ == "__main__":
    print("Generating visualisations...")
    plot_utilisation_comparison()
    plot_waiting_vs_counters()
    plot_queue_length_over_time()
    plot_ticket_type_comparison()
    print("Done.")
