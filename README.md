# EEI6373 – Performance Modelling Mini Project

**Topic:** Performance Modelling of Passenger Flow at a Major Railway Station during Peak Hours

**Student:** Akila Dhambure Liyanage
**Registration Number:** 320267120

## Project Description
This project analyses passenger flow at a railway station ticket concourse during the morning peak period (07:00 – 09:00) using queueing theory (M/M/c / Erlang-C), a discrete-event simulation, and a simulated passenger-level dataset. It covers the EEI6373 mini-project requirements: system description and performance goals, modelling approach and assumptions, data description, detailed analysis, visualisations, limitations and future work.

> **Important:** The passenger-level dataset is **simulated**. It is not real railway-station observations.

## Folder Structure

```
PM-railway/
├── data/
│   └── passenger_flow_peak_hours.csv      ← Main dataset (400 passengers)
├── scripts/
│   ├── config.py                          ← Parameters & scenarios
│   ├── generate_dataset.py                ← M/M/c discrete-event simulation
│   ├── queue_model.py                     ← M/M/c (Erlang-C) + Little's Law
│   ├── visualization.py                   ← Graphs for the report
│   └── run_analysis.py                    ← Main entry point
├── outputs/
│   ├── performance_analysis.xlsx            ← Summary + one sheet per scenario
│   ├── 01_utilisation_comparison.png
│   ├── 02_waiting_vs_counters.png
│   ├── 03_arrival_intensity.png
│   ├── 04_ticket_type_comparison.png
│   ├── 05_sensitivity_analysis.png
│   ├── 06_waiting_trend.png
│   └── 07_system_flow_diagram.png
├── .gitignore
├── requirements.txt
└── README.md
```

## Dataset Summary

- Peak period: **07:00 – 09:00** (2 hours)
- Total passengers: **400**
  - Normal ticket: **180** → λ ≈ 90 passengers/hour (queue at ticket counters)
  - Online ticket: **220** → λ ≈ 110 passengers/hour (bypass the counters)
- Columns: `Passenger_ID`, `Arrival_Time`, `Ticket_Type`, `Counter_Wait_Min`, `Counter_Service_Min`, `Gate_Wait_Min`, `Gate_Service_Min`, `Boarding_Wait_Min`, `Total_Time_Min`
- The Normal passenger counter waits are produced by an actual FIFO M/M/c discrete-event simulation (c = 3, μ = 40/hour), so the data validate the analytical model (simulated mean wait 1.22 min vs analytical Wq 1.14 min).

## Dataset Statistics (printed by `run_analysis.py`)

- Total passengers: **400** — Normal **180 (45.0%)**, Online **220 (55.0%)**
- Normal arrival rate λ = **90/hour**; Online arrival rate λ = **110/hour**
- System throughput: **200 passengers/hour**
- Mean counter service (Normal): 1.456 min → μ ≈ **41.2/hour** (target 40)
- Mean counter wait (Normal): **1.22 min**; mean gate wait (all): **0.49 min**
- Mean total time: **8.67 min** (Normal) vs **5.88 min** (Online)

## Setup on Windows

### 1. Install Python
Install Python 3.10+ and make sure Python is added to PATH.

```bash
python --version
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install requirements

```bash
pip install -r requirements.txt
```

## How to Run
### Run the full analysis + generate graphs (recommended)

```bash
cd scripts
python run_analysis.py
```

### Only re-generate the dataset

```bash
cd scripts
python generate_dataset.py
```

### Only check the M/M/c calculations

```bash
cd scripts
python queue_model.py
```

## Key Results (M/M/c, matching the report)

| Scenario                  | λ    | μ  | c | ρ       | Wq (min) |
|---------------------------|------|----|---|---------|----------|
| Baseline (Normal Peak)    | 90   | 40 | 3 | 0.750   | 1.14     |
| Busy Morning              | 110  | 40 | 3 | 0.9167  | 5.08     |
| Busy + 5 Counters         | 110  | 40 | 5 | 0.55    | 0.12     |
| Busy + Faster Service     | 110  | 50 | 3 | 0.7333  | 0.81     |

Little's Law (Lq = λ × Wq) is applied as a consistency check and matches within rounding.

## Scenario Results (Excel)

`run_analysis.py` runs the four scenarios as a **controlled experiment** (same seed per
replication; one parameter changed at a time) and exports everything to
`outputs/performance_analysis.xlsx` with:

- **Summary** sheet — analytical ρ, P(wait), Lq, Wq and simulated mean wait/service per scenario.
- One sheet per scenario (`Baseline (Normal Peak)`, `Busy Morning`, `Busy + 5 Counters`,
  `Busy + Faster Service`) — the per-passenger counter simulation records.

The simulated mean wait in the Summary is the average over **20 independent 2-hour
replications** (each queue starts empty). Because the finite window includes the
transient warm-up, simulated waits sit at or below the steady-state M/M/c Wq, and the gap
grows with utilisation (e.g. Busy Morning: simulated ≈ 2.99 min vs steady-state 5.08 min).

## Analytical values used in the report

- λ = 180 normal passengers / 2 hours = **90 / hour**
- μ = 40 passengers/hour per counter → mean service time = **1.5 min**
- Baseline utilisation: ρ = λ/(cμ) = 90/(3×40) = **0.75**
- Busy morning: ρ = 110/(3×40) = **0.9167**
- Five-counter case: ρ = 110/(5×40) = **0.55**
- Entry gates: λ = 200/hour, μ = 100/hour, c = 3 → ρ = **0.667**, Wq = **0.27 min**
- Capacity limit: with c = 3 counters the system is stable only while λ < 120/hour.

## Validation

The simulated dataset is compared against the analytical model in `run_analysis.py`:
- Simulated mean counter wait (Normal) = **1.22 min** vs analytical Wq = **1.14 min** (7.2% difference, finite-sample/warm-up effect).
- Simulated mean service time = **1.46 min** → μ ≈ **41.2/hour** (target 40/hour).

## What the Visualisations Show

1. **07_system_flow_diagram.png** – passenger flow chain: Normal passengers queue at ticket counters, Online passengers bypass them; both proceed through gates, platform and boarding.
2. **01_utilisation_comparison.png** – utilisation of ticket counters (baseline and busy) and entry gates, with the high-congestion threshold.
3. **02_waiting_vs_counters.png** – how adding ticket counters reduces Wq under λ = 110/hour.
4. **03_arrival_intensity.png** – arrival intensity across 07:00 – 09:00 (passengers per 10-minute bin).
5. **06_waiting_trend.png** – average counter waiting time per 10-minute bin over the peak period (Normal passengers), with analytical Wq as reference.
6. **04_ticket_type_comparison.png** – average counter wait, gate wait and total time for Normal vs Online ticket passengers.
7. **05_sensitivity_analysis.png** – Wq vs arrival rate for c = 3, 4 and 5 counters.


