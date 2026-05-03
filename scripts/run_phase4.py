# scripts/run_phase4.py
"""
Phase 4: Concurrency Scaling — finds breaking point for each executor.
Scales users: 1, 2, 4, 8, 16, 32, 64, 100.

Usage:
    python scripts/run_phase4.py
"""
import json, os, sys, subprocess, time, requests
from datetime import datetime

PYTHON      = sys.executable
DURATION    = 60
USER_LEVELS = [1, 2, 4, 8, 16, 32, 64, 100]

EXECUTORS = [
    ("thread",  "fifo", "src.servers.flask_app",   5000),
    ("process", "fifo", "src.servers.flask_app",   5000),
    ("async",   "fifo", "src.servers.fastapi_app", 8000),
]


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


def run_one(executor, scheduler, module, port, users):
    ts            = datetime.now().strftime("%Y%m%d_%H%M%S")
    experiment_id = f"phase4_{executor}_{scheduler}_u{users:03d}_{ts}"
    spawn_rate    = min(users, 10)
    env = os.environ.copy()
    env.update({"EXECUTOR_TYPE": executor, "SCHEDULER_TYPE": scheduler,
                "EXPERIMENT_ID": experiment_id, "MAX_WORKERS": "4"})
    if "fastapi" in module:
        server_cmd = [PYTHON, "-m", "uvicorn", f"{module}:app",
                      "--host", "0.0.0.0", "--port", str(port)]
    else:
        server_cmd = [PYTHON, "-m", module]
    server = subprocess.Popen(server_cmd, env=env)
    if not wait_for_server(port):
        print(f"  SKIP: server failed"); server.terminate(); return None
    subprocess.run([PYTHON, "-m", "locust", "-f", "experiments/locustfile.py",
        "--headless", "--host", f"http://localhost:{port}",
        "--users", str(users), "--spawn-rate", str(spawn_rate),
        "--run-time", f"{DURATION}s"])
    server.terminate()
    try: server.wait(timeout=5)
    except Exception: server.kill()
    return f"results/{experiment_id}.jsonl"


def throughput(path):
    if not path or not os.path.exists(path): return 0
    count = sum(1 for line in open(path)
                if line.strip() and not json.loads(line).get("error"))
    return count / DURATION


def main():
    os.makedirs("results", exist_ok=True)
    print(f"Phase 4: Concurrency scaling | {DURATION}s per run")
    print(f"\n{'Executor':<12} {'Users':>6} {'Jobs/s':>8} {'p_ratio':>8}")
    print("-" * 38)
    results = {}
    for executor, scheduler, module, port in EXECUTORS:
        results[executor] = {}
        for users in USER_LEVELS:
            path = run_one(executor, scheduler, module, port, users)
            rps  = throughput(path)
            results[executor][users] = rps
            baseline_rps = results[executor].get(1, rps)
            ratio = rps / baseline_rps if baseline_rps > 0 else 1.0
            print(f"{executor:<12} {users:>6} {rps:>8.2f} {ratio:>8.1f}x")
            time.sleep(3)
    print("\nPhase 4 complete.")


if __name__ == "__main__":
    main()
