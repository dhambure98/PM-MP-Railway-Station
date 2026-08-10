import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

from queue_model import generate_arrivals, simulate_mmc_queue

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


def main():
    normal_arrivals = generate_arrivals(NUM_NORMAL, LAMBDA_NORMAL)
    online_arrivals = generate_arrivals(NUM_ONLINE, LAMBDA_ONLINE)
    normal_sim = simulate_mmc_queue(normal_arrivals, SERVICE_MEAN_MIN, C_COUNTERS)

    records = []

    # Normal ticket passengers -> M/M/c queue simulation
    for arr_min, (wait, svc, _dep) in zip(normal_arrivals, normal_sim):
        gate_wait = max(0.05, random_exponential(0.6))
        gate_service = max(0.05, random_exponential(GATE_MEAN_SERVICE))
        boarding_wait = max(1.0, random_exponential(BOARDING_MEAN_WAIT))
        total = wait + svc + gate_wait + gate_service + boarding_wait
        records.append({
            "Passenger_ID": "",
            "Arrival_Time": (START_TIME + timedelta(minutes=arr_min)).strftime("%H:%M:%S"),
            "Ticket_Type": "Normal",
            "Counter_Wait_Min": round(wait, 2),
            "Counter_Service_Min": round(svc, 2),
            "Gate_Wait_Min": round(gate_wait, 2),
            "Gate_Service_Min": round(gate_service, 2),
            "Boarding_Wait_Min": round(boarding_wait, 2),
            "Total_Time_Min": round(total, 2),
        })

    # Online ticket passengers -> bypass the ticket counter
    for arr_min in online_arrivals:
        gate_wait = max(0.05, random_exponential(0.35))
        gate_service = max(0.05, random_exponential(GATE_MEAN_SERVICE))
        boarding_wait = max(1.0, random_exponential(BOARDING_MEAN_WAIT))
        total = gate_wait + gate_service + boarding_wait
        records.append({
            "Passenger_ID": "",
            "Arrival_Time": (START_TIME + timedelta(minutes=arr_min)).strftime("%H:%M:%S"),
            "Ticket_Type": "Online",
            "Counter_Wait_Min": 0.0,
            "Counter_Service_Min": 0.0,
            "Gate_Wait_Min": round(gate_wait, 2),
            "Gate_Service_Min": round(gate_service, 2),
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
            "Gate_Wait_Min", "Gate_Service_Min",
            "Boarding_Wait_Min", "Total_Time_Min"
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
