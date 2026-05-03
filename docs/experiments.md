# Experiment Procedure

## Overview

Experiments are run by starting a server with a specific configuration (executor + scheduler), then load-testing it with Locust for a fixed duration. Results are written to JSONL files and post-processed into CSV and plots.

---

## Prerequisites

```powershell
# Activate venv
.venv\Scripts\activate

# Set Python path (required every new session)
$env:PYTHONPATH = "E:\AI Engineering\Process_Task-server"

# Verify
python -c "from src.core.job import Job; print('OK')"
```

---

## Quick Start — Full Automated Run

Runs all 7 executor+scheduler combinations sequentially:

```powershell
python scripts/run_experiment.py --duration 180 --users 100 --spawn-rate 10
```

| Parameter | Recommended | Notes |
|-----------|------------|-------|
| `--duration` | 180 | Seconds per run |
| `--users` | 100 | Concurrent Locust users |
| `--spawn-rate` | 10 | Users added per second |

Total time: ~25-30 minutes. Monitor RAM in Task Manager.

---

## Manual Single-Run Procedure

**Terminal 1 — start server:**
```powershell
$env:EXECUTOR_TYPE  = "thread"
$env:SCHEDULER_TYPE = "priority"
$env:EXPERIMENT_ID  = "thread_priority_manual"
$env:MAX_WORKERS    = "4"
python src/servers/flask_app.py
```

**Terminal 2 — run load test:**
```powershell
python -m locust -f experiments/locustfile.py `
  --headless --host http://localhost:5000 `
  --users 100 --spawn-rate 10 --run-time 180s
```

**For FastAPI (async executor):**
```powershell
# Terminal 1
$env:SCHEDULER_TYPE = "fifo"
$env:EXPERIMENT_ID  = "async_fifo_manual"
uvicorn src.servers.fastapi_app:app --host 0.0.0.0 --port 8000

# Terminal 2
python -m locust -f experiments/locustfile.py `
  --headless --host http://localhost:8000 `
  --users 100 --spawn-rate 10 --run-time 180s
```

---

## Experiment Matrix

| Run | Executor | Scheduler | Server | Port |
|-----|----------|-----------|--------|------|
| 1 | baseline | fifo | flask | 5000 |
| 2 | thread | fifo | flask | 5000 |
| 3 | thread | priority | flask | 5000 |
| 4 | process | fifo | flask | 5000 |
| 5 | process | priority | flask | 5000 |
| 6 | async | fifo | fastapi | 8000 |
| 7 | async | priority | fastapi | 8000 |

---

## Advanced Phases

### Phase 1 — Stability Check (10 repeated runs)
```powershell
python scripts/run_phase1.py
```
Validates that your environment is stable enough for comparisons.
Pass threshold: coefficient of variation < 10%.

### Phase 3 — Workload Isolation
```powershell
python scripts/run_phase3.py
```
Runs CPU, IO, and memory workloads separately so results are not averaged.

### Phase 4 — Concurrency Scaling
```powershell
python scripts/run_phase4.py
```
Scales users from 1 to 100 to find each executor's breaking point.

### Phase 5 — Scheduler Deep Dive
```powershell
python scripts/run_phase5.py
```
Tests FIFO vs Priority under uniform, bimodal, and mixed priority distributions.

---

## Analysis

After any experiment run:

```powershell
# Aggregate all JSONL into summary.csv
python experiments/analysis/summarize.py

# Generate 5 plots from summary.csv
python experiments/analysis/plot.py
```

Plots are saved to `results/plots/`.

---

## Result File Naming

`results/{experiment_id}.jsonl`

Where `experiment_id` follows the pattern:
`{executor}_{scheduler}_{YYYYMMDD_HHMMSS}`

Example: `thread_priority_20260427_001407.jsonl`

The `summarize.py` script parses executor and scheduler from the filename prefix automatically.

---

## Known Issues

| Issue | Workaround |
|-------|-----------|
| `ml_predict` fails with `No module named 'sklearn'` | Run `pip install scikit-learn` in venv |
| Server fails to start in 15s | Increase `timeout` in runner scripts or check port conflict |
| PYTHONPATH not set | Always set `$env:PYTHONPATH` before running |
| Pre-commit hook fails | Commit via Git Bash, not PowerShell |
