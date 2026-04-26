# src/executors/process_pool.py
"""
Process Pool Executor.

Concurrency model: each job runs in a separate OS process.
GIL impact: none — each process has its own GIL, so CPU-bound workloads
run in true parallel. Cost: higher memory overhead and IPC serialization
(job params serialized via pickle to send to worker process).

Constraint: only picklable arguments can be sent to worker processes.
run_workload() is a top-level function in registry.py — it is picklable.
job.params must contain only basic Python types (str, int, float, dict, list).

Metrics note: track_request() runs inside the worker process. The metrics
dict is returned alongside the result and attached to the job in the main process.
"""
import logging
import threading
from concurrent.futures import ProcessPoolExecutor as _ProcessPoolExecutor
from src.core.job import Job
from src.core.registry import run_workload

logger = logging.getLogger(__name__)


def _worker(workload_type: str, params: dict) -> tuple:
    """
    Top-level worker function — must be defined at module level to be picklable.
    Returns (result, metrics_dict).
    """
    import psutil
    import time

    process = psutil.Process()
    cpu_start = process.cpu_times()
    ctx_start = process.num_ctx_switches()
    mem_start = process.memory_info().rss / 1024 / 1024
    wall_start = time.perf_counter()

    result = run_workload(workload_type, params)

    wall_end = time.perf_counter()
    cpu_end = process.cpu_times()
    ctx_end = process.num_ctx_switches()
    mem_end = process.memory_info().rss / 1024 / 1024

    metrics = {
        "duration_s": round(wall_end - wall_start, 3),
        "cpu_user_delta_s": round(cpu_end.user - cpu_start.user, 3),
        "cpu_system_delta_s": round(cpu_end.system - cpu_start.system, 3),
        "ctx_voluntary_delta": ctx_end.voluntary - ctx_start.voluntary,
        "ctx_involuntary_delta": ctx_end.involuntary - ctx_start.involuntary,
        "memory_mb": round(mem_end, 2),
        "memory_delta_mb": round(mem_end - mem_start, 2),
    }
    return result, metrics


class ProcessPoolExecutor:
    """Wraps concurrent.futures.ProcessPoolExecutor with Job lifecycle management."""

    def __init__(self, max_workers: int = 2):
        # Default 2 workers — process overhead is high, don't overcommit on laptop
        self._pool = _ProcessPoolExecutor(max_workers=max_workers)
        self._max_workers = max_workers
        self._active = 0
        self._lock = threading.Lock()
        logger.info("ProcessPoolExecutor ready (max_workers=%d)", max_workers)

    def execute(self, job: Job) -> None:
        """
        Submit job to process pool. Non-blocking — returns immediately.
        Sends only (workload_type, params) — both are picklable.
        mark_completed() is called back in the main process via future callback.
        """
        with self._lock:
            self._active += 1

        future = self._pool.submit(_worker, job.workload_type, job.params)
        future.add_done_callback(lambda f: self._on_done(f, job))

    def _on_done(self, future, job: Job) -> None:
        with self._lock:
            self._active -= 1
        try:
            result, metrics = future.result()
            job.os_metrics = metrics
            job.mark_completed(result=result)
            logger.debug("Job %s completed in worker process (type=%s)",
                         job.job_id, job.workload_type)
        except Exception as e:
            job.mark_completed(error=str(e))
            logger.error("Job %s failed in worker process: %s", job.job_id, e)

    def shutdown(self, wait: bool = True) -> None:
        self._pool.shutdown(wait=wait)
        logger.info("ProcessPoolExecutor shut down.")

    def stats(self) -> dict:
        with self._lock:
            return {
                "executor": "process_pool",
                "max_workers": self._max_workers,
                "active_jobs": self._active,
            }
