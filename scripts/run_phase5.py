# scripts/run_phase5.py
"""
Phase 5: Scheduler Deep Dive — measures starvation under different priority distributions.
Fixes executor to process (most stable). 5 runs per configuration.

Usage:
    python scripts/run_phase5.py
"""
import json, os, sys, subprocess, time, requests, statistics
from datetime import datetime

PYTHON     = sys.executable
DURATION   = 120
USERS      = 100
SPAWN_RATE = 10
RUNS_EACH  = 5

PRIORITY_SCENARIOS = [
    ("uniform",  "experiments/locustfile_priority_uniform.py"),
    ("bimodal",  "experiments/locustfile_priority_bimodal.py"),
    ("mixed",    "experiments/locustfile.py"),
]
SCHEDULERS = ["fifo", "priority"]


def wait_for_server(port, timeout=15):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            if requests.get(f"http://localhost:{port}/health", timeout=2).status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


def run_one(scheduler, scenario_name, locustfile, run_id):
    ts            = datetime.now().strftime("%Y%m%d_%H%M%S")
    experiment_id = f"phase5_{scenario_name}_{scheduler}_r{run_id:02d}_{ts}"
    env = os.environ.copy()
    env.update({"EXECUTOR_TYPE": "process", "SCHEDULER_TYPE": scheduler,
                "EXPERIMENT_ID": experiment_id, "MAX_WORKERS": "4"})
    server = subprocess.Popen([PYTHON, "-m", "src.servers.flask_app"], env=env)
    if not wait_for_server(5000):
        print(f"  SKIP: server failed"); server.terminate(); return None
    subprocess.run([PYTHON, "-m", "locust", "-f", locustfile,
        "--headless", "--host", "http://localhost:5000",
        "--users", str(USERS), "--spawn-rate", str(SPAWN_RATE),
        "--run-time", f"{DURATION}s"])
    server.terminate()
    try: server.wait(timeout=5)
    except Exception: server.kill()
    return f"results/{experiment_id}.jsonl"


def analyze_by_priority(files):
    data = {}
    for path in [f for f in files if f and os.path.exists(f)]:
        with open(path) as f:
            for line in f:
                try:
                    r = json.loads(line)
                    if r.get("error") or not r.get("waiting_time"): continue
                    p = r.get("priority", "?")
                    data.setdefault(p, []).append(r["waiting_time"])
                except Exception:
                    continue
    print("\n  Waiting time breakdown by priority tier:")
    for p in sorted(data.keys()):
        vals = data[p]
        if len(vals) < 2: continue
        mean = statistics.mean(vals)
        p95  = sorted(vals)[int(len(vals) * 0.95)]
        print(f"    priority={p}: mean={mean:.5f}s  p95={p95:.5f}s  n={len(vals)}")


def main():
    os.makedirs("results", exist_ok=True)
    total = len(PRIORITY_SCENARIOS) * len(SCHEDULERS) * RUNS_EACH
    print(f"Phase 5: {total} runs | process executor | {USERS} users | {DURATION}s | {RUNS_EACH} runs each")
    for scenario_name, locustfile in PRIORITY_SCENARIOS:
        print(f"\n{'='*60}\nSCENARIO: {scenario_name.upper()}")
        for scheduler in SCHEDULERS:
            print(f"\n  Scheduler: {scheduler}")
            files = []
            for run_id in range(1, RUNS_EACH + 1):
                files.append(run_one(scheduler, scenario_name, locustfile, run_id))
                time.sleep(3)
            analyze_by_priority(files)
    print("\nPhase 5 complete.")


if __name__ == "__main__":
    main()
