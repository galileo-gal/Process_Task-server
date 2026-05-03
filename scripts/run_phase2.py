# scripts/run_phase2.py
"""
Phase 2: Load Sweep — all executor+scheduler combos under 4 stress levels.
stress-ng runs in WSL2 to simulate background system load.

Prerequisite:
    wsl sudo apt install stress-ng -y

Usage:
    python scripts/run_phase2.py
"""
import os, sys, subprocess, time, requests
from datetime import datetime

PYTHON     = sys.executable
DURATION   = 90
USERS      = 100
SPAWN_RATE = 10

EXPERIMENTS = [
    ("baseline",  "fifo",     "src.servers.flask_app",   5000),
    ("thread",    "fifo",     "src.servers.flask_app",   5000),
    ("thread",    "priority", "src.servers.flask_app",   5000),
    ("process",   "fifo",     "src.servers.flask_app",   5000),
    ("process",   "priority", "src.servers.flask_app",   5000),
    ("async",     "fifo",     "src.servers.fastapi_app", 8000),
    ("async",     "priority", "src.servers.fastapi_app", 8000),
]

STRESS_LEVELS = [
    ("idle",   0),
    ("low",    25),
    ("medium", 50),
    ("high",   75),
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


def start_stress(cpu_pct):
    if cpu_pct == 0: return None
    wsl_cmd = f"stress-ng --cpu 1 --cpu-load {cpu_pct} --timeout {DURATION + 30}s"
    proc = subprocess.Popen(["wsl", "bash", "-c", wsl_cmd],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    return proc


def stop_stress(proc):
    if proc:
        proc.terminate()
        try: proc.wait(timeout=5)
        except Exception: proc.kill()


def run_one(executor, scheduler, module, port, stress_label):
    ts            = datetime.now().strftime("%Y%m%d_%H%M%S")
    experiment_id = f"phase2_{stress_label}_{executor}_{scheduler}_{ts}"
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
    subprocess.run([PYTHON, "-m", "locust", "-f", "experiments/locustfile.py",
        "--headless", "--host", f"http://localhost:{port}",
        "--users", str(USERS), "--spawn-rate", str(SPAWN_RATE),
        "--run-time", f"{DURATION}s"])
    server.terminate()
    try: server.wait(timeout=5)
    except Exception: server.kill()
    print(f"  Done → results/{experiment_id}.jsonl")


def main():
    os.makedirs("results", exist_ok=True)
    print(f"Phase 2: {len(STRESS_LEVELS) * len(EXPERIMENTS)} runs | {USERS} users | {DURATION}s each")
    for stress_label, stress_pct in STRESS_LEVELS:
        print(f"\n{'='*60}\nSTRESS: {stress_label} ({stress_pct}% CPU via WSL stress-ng)")
        stress_proc = start_stress(stress_pct)
        for executor, scheduler, module, port in EXPERIMENTS:
            print(f"\n  {executor}+{scheduler} | {stress_label}")
            run_one(executor, scheduler, module, port, stress_label)
            time.sleep(3)
        stop_stress(stress_proc)
        print(f"Cooling down 10s...")
        time.sleep(10)
    print("\nPhase 2 complete. Run summarize.py and plot.py.")


if __name__ == "__main__":
    main()
