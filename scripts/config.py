# Peak period
PEAK_START = "07:00"
PEAK_END = "09:00"
DURATION_HOURS = 2.0

# From simulated dataset
NUM_NORMAL_PASSENGERS = 180
NUM_ONLINE_PASSENGERS = 220
TOTAL_PASSENGERS = 400

# Analytical model parameters (used in report)
LAMBDA_NORMAL = 90.0          # passengers per hour (180 / 2)
LAMBDA_ONLINE = 110.0         # passengers per hour (220 / 2)
MU_COUNTER = 40.0             # passengers per hour per counter
C_COUNTERS_BASE = 3

# Entry gates (for comparison)
MU_GATE = 100.0
C_GATES = 3

# Scenarios for what-if analysis
SCENARIOS = [
    {"name": "Baseline (Normal Peak)", "lambda": 90, "mu": 40, "c": 3},
    {"name": "Busy Morning", "lambda": 110, "mu": 40, "c": 3},
    {"name": "Busy + 5 Counters", "lambda": 110, "mu": 40, "c": 5},
    {"name": "Busy + Faster Service", "lambda": 110, "mu": 50, "c": 3},
]
