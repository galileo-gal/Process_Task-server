# scripts/run_phase3.py
"""
Phase 3: Workload Isolation — runs each workload group separately.
Prevents CPU/IO/Memory results from being averaged together.

Usage:
    python scripts/run_phase3.py
"""
import os, sys, subprocess, time, requests
from datetime import datetime

PYTHON     = sys.executable
DURATION   = 90
USERS      = 100
SPAWN_RATE = 10

EXECUTORS = [
    ("baseline",  "fifo",     "src.servers.flask_app",   5000),
    ("thread",    "fifo",     "src.servers.flask_app",   5000),
    ("thread",    "priority", "src.servers.flask_app",   5000),
    ("process",   "fifo",     "src.servers.flask_app",   5000),
    ("process",   "priority", "src.servers.flask_app",   5000),
    ("async",     "fifo",     "src.servers.fastapi_app", 8000),
    ("async",     "priority", "src.servers.fastapi_app", 8000),
]

WORKLOAD_GROUPS = [
    ("cpu",    "experiments/locustfile_cpu.py"),
    ("io",     "experiments/locustfile_io.py"),
    ("memory", "experiments/locustfile_memory.py"),
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


def run_one(executor, scheduler, module, port, group_name, locustfile):
    ts            = datetime.now().strftime("%Y%m%d_%H%M%S")
    experiment_id = f"phase3_{group_name}_{executor}_{scheduler}_{ts}"
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
        print(f"  SKIP: server failed"); server.terminate(); return
    subprocess.run([PYTHON, "-m", "locust", "-f", locustfile,
        "--headless", "--host", f"http://localhost:{port}",
        "--users", str(USERS), "--spawn-rate", str(SPAWN_RATE),
        "--run-time", f"{DURATION}s"])
    server.terminate()
    try: server.wait(timeout=5)
    except Exception: server.kill()
    print(f"  Done → results/{experiment_id}.jsonl")


def main():
    os.makedirs("results", exist_ok=True)
    print(f"Phase 3: {len(WORKLOAD_GROUPS) * len(EXECUTORS)} runs | {USERS} users | {DURATION}s each")
    for group_name, locustfile in WORKLOAD_GROUPS:
        print(f"\n{'='*60}\nWORKLOAD GROUP: {group_name.upper()}")
        for executor, scheduler, module, port in EXECUTORS:
            print(f"\n  {executor}+{scheduler} | {group_name}")
            run_one(executor, scheduler, module, port, group_name, locustfile)
            time.sleep(3)
    print("\nPhase 3 complete.")


if __name__ == "__main__":
    main()
