"""
Generate simulated passenger flow dataset for Railway Station Peak Hour Analysis
Peak period: 07:00 - 09:00 (2 hours)
"""

import csv
import random
from datetime import datetime, timedelta

random.seed(42)  # for reproducibility

# Configuration (matches report assumptions)
START_TIME = datetime(2026, 8, 8, 7, 0, 0)
END_TIME = datetime(2026, 8, 8, 9, 0, 0)
DURATION_HOURS = 2.0

# Target numbers
NUM_NORMAL = 180          # → λ_normal ≈ 90 / hour
NUM_ONLINE = 220          # online passengers
TOTAL = NUM_NORMAL + NUM_ONLINE

# Service parameters (minutes)
COUNTER_MEAN_SERVICE = 1.5      # → μ ≈ 40 / hour
GATE_MEAN_SERVICE = 0.4
BOARDING_MEAN_WAIT = 5.0

def random_exponential(mean):
    return random.expovariate(1.0 / mean)

def generate_arrival_times(n, start, end):
    """Generate roughly uniform arrivals with some clustering for realism"""
    times = []
    total_seconds = (end - start).total_seconds()
    for _ in range(n):
        # slight morning peak bias
        offset = random.betavariate(2, 2) * total_seconds
        times.append(start + timedelta(seconds=offset))
    times.sort()
    return times

def main():
    normal_arrivals = generate_arrival_times(NUM_NORMAL, START_TIME, END_TIME)
    online_arrivals = generate_arrival_times(NUM_ONLINE, START_TIME, END_TIME)

    records = []
    pid = 1

    # Normal ticket passengers
    for arr in normal_arrivals:
        counter_wait = max(0.1, random_exponential(2.0))      # higher wait
        counter_service = max(0.3, random_exponential(COUNTER_MEAN_SERVICE))
        entry_wait = max(0.05, random_exponential(0.6))
        boarding_wait = max(1.0, random_exponential(BOARDING_MEAN_WAIT))
        total = counter_wait + counter_service + entry_wait + boarding_wait

        records.append({
            "Passenger_ID": f"P{pid:03d}",
            "Arrival_Time": arr.strftime("%H:%M:%S"),
            "Ticket_Type": "Normal",
            "Counter_Wait_Min": round(counter_wait, 2),
            "Counter_Service_Min": round(counter_service, 2),
            "Entry_Wait_Min": round(entry_wait, 2),
            "Boarding_Wait_Min": round(boarding_wait, 2),
            "Total_Time_Min": round(total, 2)
        })
        pid += 1

    # Online ticket passengers (skip counter mostly)
    for arr in online_arrivals:
        counter_wait = 0.0
        counter_service = 0.0
        entry_wait = max(0.05, random_exponential(0.35))
        boarding_wait = max(1.0, random_exponential(BOARDING_MEAN_WAIT))
        total = entry_wait + boarding_wait

        records.append({
            "Passenger_ID": f"P{pid:03d}",
            "Arrival_Time": arr.strftime("%H:%M:%S"),
            "Ticket_Type": "Online",
            "Counter_Wait_Min": 0.0,
            "Counter_Service_Min": 0.0,
            "Entry_Wait_Min": round(entry_wait, 2),
            "Boarding_Wait_Min": round(boarding_wait, 2),
            "Total_Time_Min": round(total, 2)
        })
        pid += 1

    # Sort by arrival time
    records.sort(key=lambda r: r["Arrival_Time"])

    # Re-assign sequential IDs after sorting
    for i, r in enumerate(records, 1):
        r["Passenger_ID"] = f"P{i:03d}"

    out_path = "/home/workdir/artifacts/railway_performance_modelling/data/passenger_flow_peak_hours.csv"
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

if __name__ == "__main__":
    main()
