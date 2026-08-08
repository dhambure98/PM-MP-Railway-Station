"""
Generate simulated passenger flow dataset for Railway Station Peak Hour Analysis
Peak period: 07:00 - 09:00 (2 hours)

Normal (ticket-counter) passengers are produced by a FIFO M/M/c discrete-event
simulation (c = 3 counters, service mean 1.5 min => mu = 40/hour, arrival rate
90/hour) so the simulated counter wait converges to the analytical Erlang-C
result (Wq ~ 1.14 min). Online passengers bypass the ticket counters entirely.
"""

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)  # for reproducibility

START_TIME = datetime(2026, 8, 8, 7, 0, 0)

# Target numbers (lambda in passengers/hour)
NUM_NORMAL = 180
NUM_ONLINE = 220
LAMBDA_NORMAL = 90.0
LAMBDA_ONLINE = 110.0

# Queue parameters for the ticket counter (M/M/c)
C_COUNTERS = 3
SERVICE_MEAN_MIN = 1.5   # => mu = 40 passengers/hour

# Downstream phases (descriptive data, not part of the M/M/c validation)
GATE_MEAN_SERVICE = 0.4
BOARDING_MEAN_WAIT = 5.0


def random_exponential(mean):
    return random.expovariate(1.0 / mean)


def generate_arrivals(n, rate_per_hour):
    """Poisson-process arrivals with a fixed count and fixed window.

    Sorted uniform order statistics over [0, total_min] are statistically
    equivalent to conditioning a Poisson process on exactly N arrivals, so the
    arrival rate stays rate_per_hour and the span is exactly 2 hours.
    """
    total_min = n * 60.0 / rate_per_hour
    return sorted(random.uniform(0.0, total_min) for _ in range(n))


def simulate_mmc_queue(arrival_times_min, service_mean_min, c):
    """FIFO M/M/c event simulation -> list of (wait, service, departure) in minutes."""
    free = [0.0] * c
    results = []
    for a in arrival_times_min:
        server = min(range(c), key=lambda i: free[i])
        start = max(a, free[server])
        wait = start - a
        svc = random_exponential(service_mean_min)
        dep = start + svc
        free[server] = dep
        results.append((wait, svc, dep))
    return results


def main():
    normal_arrivals = generate_arrivals(NUM_NORMAL, LAMBDA_NORMAL)
    online_arrivals = generate_arrivals(NUM_ONLINE, LAMBDA_ONLINE)
    normal_sim = simulate_mmc_queue(normal_arrivals, SERVICE_MEAN_MIN, C_COUNTERS)

    records = []

    # Normal ticket passengers -> M/M/c queue simulation
    for arr_min, (wait, svc, _dep) in zip(normal_arrivals, normal_sim):
        entry_wait = max(0.05, random_exponential(0.6))
        boarding_wait = max(1.0, random_exponential(BOARDING_MEAN_WAIT))
        total = wait + svc + entry_wait + boarding_wait
        records.append({
            "Passenger_ID": "",
            "Arrival_Time": (START_TIME + timedelta(minutes=arr_min)).strftime("%H:%M:%S"),
            "Ticket_Type": "Normal",
            "Counter_Wait_Min": round(wait, 2),
            "Counter_Service_Min": round(svc, 2),
            "Entry_Wait_Min": round(entry_wait, 2),
            "Boarding_Wait_Min": round(boarding_wait, 2),
            "Total_Time_Min": round(total, 2),
        })

    # Online ticket passengers -> bypass the ticket counter
    for arr_min in online_arrivals:
        entry_wait = max(0.05, random_exponential(0.35))
        boarding_wait = max(1.0, random_exponential(BOARDING_MEAN_WAIT))
        total = entry_wait + boarding_wait
        records.append({
            "Passenger_ID": "",
            "Arrival_Time": (START_TIME + timedelta(minutes=arr_min)).strftime("%H:%M:%S"),
            "Ticket_Type": "Online",
            "Counter_Wait_Min": 0.0,
            "Counter_Service_Min": 0.0,
            "Entry_Wait_Min": round(entry_wait, 2),
            "Boarding_Wait_Min": round(boarding_wait, 2),
            "Total_Time_Min": round(total, 2),
        })

    # Sort by arrival time and assign sequential IDs
    records.sort(key=lambda r: r["Arrival_Time"])
    for i, r in enumerate(records, 1):
        r["Passenger_ID"] = f"P{i:03d}"

    project_root = Path(__file__).resolve().parent.parent
    data_dir = project_root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    out_path = data_dir / "passenger_flow_peak_hours.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "Passenger_ID", "Arrival_Time", "Ticket_Type",
            "Counter_Wait_Min", "Counter_Service_Min",
            "Entry_Wait_Min", "Boarding_Wait_Min", "Total_Time_Min"
        ])
        writer.writeheader()
        writer.writerows(records)

    print(f"Generated {len(records)} records")
    print(f"Normal: {NUM_NORMAL}, Online: {NUM_ONLINE}")
    print(f"Saved to: {out_path}")

    # Quick validation vs the analytical model
    sim_wait = sum(w for w, _, _ in normal_sim) / NUM_NORMAL
    sim_svc = sum(s for _, s, _ in normal_sim) / NUM_NORMAL
    print(f"Normal counter mean wait (simulated): {sim_wait:.3f} min")
    print(f"Normal counter mean service (simulated): {sim_svc:.3f} min "
          f"(target 1.500 -> mu = {60 / sim_svc:.2f}/hr, target 40)")


if __name__ == "__main__":
    main()
