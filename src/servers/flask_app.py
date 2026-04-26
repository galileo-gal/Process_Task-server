# src/servers/flask_app.py
"""
Flask server — baseline, threaded, and multiprocess executor experiments.

Configuration via environment variables:
    EXECUTOR_TYPE   : baseline | thread | process   (default: baseline)
    SCHEDULER_TYPE  : fifo | priority               (default: fifo)
    MAX_WORKERS     : int                           (default: 4)
    EXPERIMENT_ID   : str                           (default: timestamp)

Modes:
    baseline  — workload runs synchronously in the request thread.
                No dispatcher. Represents single-threaded sequential execution.
    thread    — ThreadPoolExecutor + Dispatcher. True concurrent IO; GIL-limited CPU.
    process   — ProcessPoolExecutor + Dispatcher. True CPU parallelism via OS processes.

POST /run
    Body: {"workload_type": str, "params": dict, "priority": int (optional)}
    Returns: full job result dict

GET  /health  — liveness check
GET  /stats   — scheduler + executor queue depths
"""
import os
import threading
import logging

from flask import Flask, request, jsonify

from config.logging_config import setup_logging
from src.core.job import Job
from src.core.registry import run_workload
from src.utils.experiment_logger import ExperimentLogger
from src.utils.metrics import track_request

app = Flask(__name__)

# ── Configuration ─────────────────────────────────────────────────────────────
EXECUTOR_TYPE  = os.getenv("EXECUTOR_TYPE",  "baseline").lower()
SCHEDULER_TYPE = os.getenv("SCHEDULER_TYPE", "fifo").lower()
MAX_WORKERS    = int(os.getenv("MAX_WORKERS", "4"))
EXPERIMENT_ID  = os.getenv("EXPERIMENT_ID",  None)
JOB_TIMEOUT    = float(os.getenv("JOB_TIMEOUT", "30"))  # seconds

# ── Globals (initialised in _setup, not at import time) ───────────────────────
_dispatcher      = None
_executor        = None
_exp_logger      = None


def _setup():
    """
    Create scheduler, executor, dispatcher, and experiment logger.
    Called once inside `if __name__ == '__main__':` to avoid Windows
    multiprocessing spawn re-entry issues.
    """
    global _dispatcher, _executor, _exp_logger

    setup_logging(EXPERIMENT_ID)
    log = logging.getLogger(__name__)

    _exp_logger = ExperimentLogger(experiment_id=EXPERIMENT_ID)

    if EXECUTOR_TYPE == "baseline":
        log.info("Server mode: baseline (synchronous, no dispatcher)")
        return  # baseline runs workloads directly — no dispatcher needed

    # Build scheduler
    if SCHEDULER_TYPE == "priority":
        from src.scheduler.priority import PriorityScheduler
        scheduler = PriorityScheduler()
    else:
        from src.scheduler.fifo import FIFOScheduler
        scheduler = FIFOScheduler()

    # Build executor
    if EXECUTOR_TYPE == "process":
        from src.executors.process_pool import ProcessPoolExecutor
        _executor = ProcessPoolExecutor(max_workers=MAX_WORKERS)
    else:  # thread
        from src.executors.thread_pool import ThreadPoolExecutor
        _executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)

    # Wire dispatcher
    from src.dispatch.dispatcher import Dispatcher
    _dispatcher = Dispatcher(scheduler=scheduler, executor_fn=_executor.execute)
    _dispatcher.start()

    log.info("Server mode: %s | scheduler: %s | workers: %d",
             EXECUTOR_TYPE, SCHEDULER_TYPE, MAX_WORKERS)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/run", methods=["POST"])
def run_job():
    data = request.get_json(silent=True)
    if not data or "workload_type" not in data:
        return jsonify({"error": "Missing required field: workload_type"}), 400

    workload_type = data["workload_type"]
    params        = data.get("params", {})
    priority      = int(data.get("priority", 2))

    # ── Baseline: run synchronously in request thread ─────────────────────────
    if EXECUTOR_TYPE == "baseline":
        job = Job(workload_type=workload_type, params=params, priority=priority)
        job.mark_started()
        with track_request() as metrics:
            try:
                result = run_workload(workload_type, params)
                job.os_metrics = metrics
                job.mark_completed(result=result)
            except KeyError as e:
                job.os_metrics = metrics
                job.mark_completed(error=str(e))
                return jsonify({"error": str(e)}), 400
            except Exception as e:
                job.os_metrics = metrics
                job.mark_completed(error=str(e))
                return jsonify({"error": str(e)}), 500
        if _exp_logger:
            _exp_logger.log(job)
        return jsonify(job.to_dict()), 200

    # ── Threaded / Process: submit to dispatcher, wait for completion ─────────
    event = threading.Event()
    job   = Job(workload_type=workload_type, params=params, priority=priority)

    def _on_complete(completed_job: Job):
        if _exp_logger:
            _exp_logger.log(completed_job)
        event.set()

    job.on_complete = _on_complete
    _dispatcher.submit(job)

    completed = event.wait(timeout=JOB_TIMEOUT)
    if not completed:
        return jsonify({"error": "Job timed out", "job_id": job.job_id}), 504

    if job.error:
        return jsonify(job.to_dict()), 500

    return jsonify(job.to_dict()), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "executor": EXECUTOR_TYPE,
                    "scheduler": SCHEDULER_TYPE}), 200


@app.route("/stats", methods=["GET"])
def stats():
    if _dispatcher:
        return jsonify(_dispatcher.stats()), 200
    return jsonify({"executor": "baseline", "scheduler": "none"}), 200


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # _setup() MUST be called inside this guard.
    # On Windows, ProcessPoolExecutor uses 'spawn' — the module is re-imported
    # in each worker. Anything outside this guard runs in every worker process.
    _setup()
    app.run(host="0.0.0.0", port=5000, threaded=True, debug=False)
