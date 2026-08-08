"""Generate graphs for the Mini Project report Requires: matplotlib, pandas"""

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

GATE_LAMBDA = TOTAL_PASSENGERS / 2.0  

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
    df["hour_min"] = df["Arrival_Time"].dt.strftime("%H:%M")
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
    avg = df.groupby("Ticket_Type")[["Counter_Wait_Min", "Gate_Wait_Min", "Total_Time_Min"]].mean()

    fig, ax = plt.subplots(figsize=(8, 5))
    avg.plot(kind="bar", ax=ax, edgecolor="black")
    ax.set_ylabel("Average Time (minutes)")
    ax.set_title("Average Times by Ticket Type")
    ax.set_xticklabels(avg.index, rotation=0)
    ax.legend(["Counter Wait", "Gate Wait", "Total Time"])
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

def plot_waiting_trend():
    df = pd.read_csv(DATA_PATH)
    df = df[df["Ticket_Type"] == "Normal"].copy()
    df["Arrival_Time"] = pd.to_datetime(df["Arrival_Time"], format="%H:%M:%S")
    df = df.sort_values("Arrival_Time")
    df["bin"] = df["Arrival_Time"].dt.floor("10min")
    trend = df.groupby("bin")["Counter_Wait_Min"].mean()

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(trend.index.strftime("%H:%M"), trend.values, marker="o", color="#c0392b", linewidth=2)
    ax.axhline(1.14, color="gray", linestyle="--", label="Analytical Wq = 1.14 min")
    ax.set_xlabel("Time")
    ax.set_ylabel("Average counter wait (min)")
    ax.set_title("Average Counter Waiting Time over Peak Period (Normal passengers)")
    ax.tick_params(axis="x", rotation=45)
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "06_waiting_trend.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved: {path}")

def plot_system_flow_diagram():
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis("off")

    def box(x, y, w, h, text, fc="#ecf0f1"):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08",
                                    fc=fc, ec="#2c3e50", lw=1.5))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=9)

    def arrow(x1, y1, x2, y2, text=""):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2),
                                     arrowstyle="-|>", mutation_scale=18,
                                     color="#2c3e50", lw=1.6))
        if text:
            ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.12, text,
                    ha="center", va="bottom", fontsize=8, color="#7f8c8d")

    ax.text(6, 7.6, "Railway Station Passenger Flow (07:00 – 09:00)", ha="center", fontsize=13, weight="bold")

    box(0.3, 5.4, 2.2, 1.2, "Passengers arrive\nλ = 200 / hour", fc="#d5f5e3")
    box(3.4, 6.2, 2.2, 1.2, "Ticket counters\nM/M/c, c = 3\nμ = 40 / hr, λ = 90 / hr", fc="#fdebd0")
    box(3.4, 2.2, 2.2, 1.2, "Online tickets\nbypass counter\nλ = 110 / hr", fc="#d6eaf8")
    box(6.6, 4.6, 2.2, 1.2, "Entry gates\nc = 3, μ = 100 / hr\nλ = 200 / hr", fc="#e8daef")
    box(9.4, 4.6, 2.2, 1.2, "Platform wait\n+ boarding\n(mean 5 min)", fc="#fadbd8")

    arrow(2.5, 6.0, 3.4, 6.6, "Normal (180)")
    arrow(2.5, 6.0, 3.4, 2.8, "Online (220)")
    arrow(5.6, 6.6, 6.6, 5.6)
    arrow(5.6, 2.8, 6.6, 5.2)
    arrow(8.8, 5.2, 9.4, 5.2)
    arrow(11.6, 5.2, 11.9, 5.2)
    ax.text(11.55, 5.0, "Exit", ha="center", va="top", fontsize=9)

    fig.tight_layout()
    path = os.path.join(OUTPUT_DIR, "07_system_flow_diagram.png")
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
    plot_waiting_trend()
    plot_system_flow_diagram()
    print("Done.")
