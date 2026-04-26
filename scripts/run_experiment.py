# scripts/run_experiment.py
"""
Automated experiment runner — runs all 7 combinations sequentially.

Usage:
    python scripts/run_experiment.py
    python scripts/run_experiment.py --duration 60 --users 10 --spawn-rate 2

After completion:
    python experiments/analysis/summarize.py
    python experiments/analysis/plot.py
"""
import argparse
import os
import subprocess
import sys
import time
import requests
from datetime import datetime

EXPERIMENTS = [
    # (executor,  scheduler,   server_module,             port)
    ("baseline",  "fifo",     "src.servers.flask_app",   5000),
    ("thread",    "fifo",     "src.servers.flask_app",   5000),
    ("thread",    "priority", "src.servers.flask_app",   5000),
    ("process",   "fifo",     "src.servers.flask_app",   5000),
    ("process",   "priority", "src.servers.flask_app",   5000),
    ("async",     "fifo",     "src.servers.fastapi_app", 8000),
    ("async",     "priority", "src.servers.fastapi_app", 8000),
]

PYTHON = sys.executable


def wait_for_server(port: int, timeout: int = 15) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = requests.get(f"http://localhost:{port}/health", timeout=2)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


def run_one(executor, scheduler, module, port, duration, users, spawn_rate):
    ts            = datetime.now().strftime("%Y%m%d_%H%M%S")
    experiment_id = f"{executor}_{scheduler}_{ts}"

    print(f"\n{'='*60}")
    print(f"  {experiment_id}")
    print(f"{'='*60}")

    env = os.environ.copy()
    env.update({
        "EXECUTOR_TYPE":  executor,
        "SCHEDULER_TYPE": scheduler,
        "EXPERIMENT_ID":  experiment_id,
        "MAX_WORKERS":    "4",
    })

    if "fastapi" in module:
        server_cmd = [PYTHON, "-m", "uvicorn", f"{module}:app",
                      "--host", "0.0.0.0", "--port", str(port)]
    else:
        server_cmd = [PYTHON, "-m", module]

    server = subprocess.Popen(server_cmd, env=env)
    print(f"  Server PID {server.pid} starting...")

    if not wait_for_server(port):
        print("  ERROR: server did not start in 15s — skipping.")
        server.terminate()
        return

    print(f"  Server ready on :{port}")

    locust_cmd = [
        PYTHON, "-m", "locust",
        "-f", "experiments/locustfile.py",
        "--headless",
        "--host",       f"http://localhost:{port}",
        "--users",      str(users),
        "--spawn-rate", str(spawn_rate),
        "--run-time",   f"{duration}s",
    ]
    print(f"  Locust: {users} users × {duration}s")
    subprocess.run(locust_cmd)

    server.terminate()
    try:
        server.wait(timeout=5)
    except subprocess.TimeoutExpired:
        server.kill()

    print(f"  Done → results/{experiment_id}.jsonl")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration",   type=int, default=60)
    parser.add_argument("--users",      type=int, default=10)
    parser.add_argument("--spawn-rate", type=int, default=2)
    args = parser.parse_args()

    os.makedirs("results", exist_ok=True)
    os.makedirs("logs",    exist_ok=True)

    print(f"{len(EXPERIMENTS)} experiments | {args.duration}s each | {args.users} users")

    for exp in EXPERIMENTS:
        run_one(*exp, args.duration, args.users, args.spawn_rate)
        time.sleep(3)

    print("\n" + "="*60)
    print("All done. Next:")
    print("  python experiments/analysis/summarize.py")
    print("  python experiments/analysis/plot.py")


if __name__ == "__main__":
    main()
