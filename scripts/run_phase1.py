# scripts/run_phase1.py
"""
Phase 1: Stability Check — runs process+fifo 10 times to measure variance.
Pass threshold: coefficient of variation < 10%.

Usage:
    python scripts/run_phase1.py
"""
import json, os, sys, subprocess, time, requests, statistics
from datetime import datetime

PYTHON     = sys.executable
RUNS       = 10
DURATION   = 60
USERS      = 50
SPAWN_RATE = 5


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


def run_once(run_id):
    ts            = datetime.now().strftime("%Y%m%d_%H%M%S")
    experiment_id = f"phase1_process_fifo_run{run_id:02d}_{ts}"
    env = os.environ.copy()
    env.update({"EXECUTOR_TYPE": "process", "SCHEDULER_TYPE": "fifo",
                "EXPERIMENT_ID": experiment_id, "MAX_WORKERS": "4"})
    server = subprocess.Popen([PYTHON, "-m", "src.servers.flask_app"], env=env)
    if not wait_for_server(5000):
        print(f"  Run {run_id}: server failed"); server.terminate(); return None
    subprocess.run([PYTHON, "-m", "locust", "-f", "experiments/locustfile.py",
        "--headless", "--host", "http://localhost:5000",
        "--users", str(USERS), "--spawn-rate", str(SPAWN_RATE),
        "--run-time", f"{DURATION}s"], capture_output=True)
    server.terminate()
    try: server.wait(timeout=5)
    except subprocess.TimeoutExpired: server.kill()
    return f"results/{experiment_id}.jsonl"


def analyze(files):
    exec_times, total_times = [], []
    for path in [f for f in files if f and os.path.exists(f)]:
        with open(path) as f:
            for line in f:
                try:
                    r = json.loads(line)
                    if not r.get("error"):
                        if r.get("execution_time"): exec_times.append(r["execution_time"])
                        if r.get("total_time"):     total_times.append(r["total_time"])
                except Exception:
                    continue
    print("\n── Phase 1 Stability Results ──────────────────────────────")
    for label, data in [("execution_time", exec_times), ("total_time", total_times)]:
        if len(data) < 2: continue
        mean   = statistics.mean(data)
        stddev = statistics.stdev(data)
        pct    = stddev / mean * 100 if mean > 0 else 0
        p95    = sorted(data)[int(len(data) * 0.95)]
        print(f"\n{label}:")
        print(f"  mean={mean:.4f}s  stdev={stddev:.4f}s  CV={pct:.1f}%")
        print(f"  min={min(data):.4f}s  max={max(data):.4f}s  p95={p95:.4f}s")
        verdict = "⚠ HIGH VARIANCE — environment noisy (>10%)" if pct > 10 else "✓ STABLE (<10%)"
        print(f"  {verdict}")


def main():
    os.makedirs("results", exist_ok=True)
    print(f"Phase 1: {RUNS} stability runs | process+fifo | {USERS} users | {DURATION}s each")
    files = []
    for i in range(1, RUNS + 1):
        print(f"\nRun {i}/{RUNS}...")
        files.append(run_once(i))
        time.sleep(3)
    analyze(files)


if __name__ == "__main__":
    main()
