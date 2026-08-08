# EEI6373 – Performance Modelling Mini Project

**Topic:** Performance Modelling of Passenger Flow at a Major Railway Station during Peak Hours

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
│   ├── 01_utilisation_comparison.png
│   ├── 02_waiting_vs_counters.png
│   ├── 03_arrival_intensity.png
│   ├── 04_ticket_type_comparison.png
│   └── 05_sensitivity_analysis.png
├── docs/
│   └── report.md                          ← Formal report (all required sections)
├── .gitignore
├── requirements.txt
└── README.md
```

## Dataset Summary

- Peak period: **07:00 – 09:00** (2 hours)
- Total passengers: **400**
  - Normal ticket: **180** → λ ≈ 90 passengers/hour (queue at ticket counters)
  - Online ticket: **220** → λ ≈ 110 passengers/hour (bypass the counters)
- Columns: `Passenger_ID`, `Arrival_Time`, `Ticket_Type`, `Counter_Wait_Min`, `Counter_Service_Min`, `Entry_Wait_Min`, `Boarding_Wait_Min`, `Total_Time_Min`
- The Normal passenger counter waits are produced by an actual FIFO M/M/c discrete-event simulation (c = 3, μ = 40/hour), so the data validate the analytical model (simulated mean wait 1.22 min vs analytical Wq 1.14 min).

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

1. **01_utilisation_comparison.png** – utilisation of ticket counters (baseline and busy) and entry gates, with the high-congestion threshold.
2. **02_waiting_vs_counters.png** – how adding ticket counters reduces Wq under λ = 110/hour.
3. **03_arrival_intensity.png** – arrival intensity across 07:00 – 09:00 (passengers per 10-minute bin).
4. **04_ticket_type_comparison.png** – average counter wait, entry wait and total time for Normal vs Online ticket passengers.
5. **05_sensitivity_analysis.png** – Wq vs arrival rate for c = 3, 4 and 5 counters.

## Report

The full formal report with all required sections (system description & goals, modelling approach & assumptions, data & methodology, detailed analysis & findings, visualisations, limitations & future extensions, references) is in **`docs/report.md`**.

## Notes for the Viva

- λ = 180 / 2 hours = **90 passengers/hour**; μ = **40 passengers/hour** per counter (1.5 min mean service time).
- Little's Law is used as a consistency check between Lq and Wq.
- **Ticket counters are the main bottleneck** for Normal ticket passengers (Baseline ρ = 0.75; Busy Morning ρ = 0.917 → Wq grows from 1.14 to 5.08 min).
- Adding counters (c = 5) or faster service (μ = 50) both cut Wq below 1 min; c = 5 keeps Wq under 0.3 min even at λ = 130/hour.
- **Online ticket passengers largely bypass the counter queue** (total time 5.0 vs 8.7 min for Normal).
- Limitations: simulated data, steady-state M/M/c assumptions, no balking/reneging, homogeneous service times.

## Academic Integrity

The assignment states that use of AI/plagiarism or other academic misconduct can result in zero marks. Use this repository as a modelling/implementation aid, understand every section, and write/verify your own final submission and explanations.
