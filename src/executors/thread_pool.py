# src/executors/thread_pool.py
"""
Thread Pool Executor.

Concurrency model: multiple threads share one process.
GIL impact: CPU-bound workloads do NOT run in true parallel here —
threads take turns holding the GIL. IO-bound workloads benefit because
the GIL is released during IO waits.

This is the primary executor for baseline and threaded server experiments.
"""
import logging
import threading
from concurrent.futures import ThreadPoolExecutor as _ThreadPoolExecutor
from src.core.job import Job
from src.core.registry import run_workload
from src.utils.metrics import track_request

logger = logging.getLogger(__name__)


class ThreadPoolExecutor:
    """Wraps concurrent.futures.ThreadPoolExecutor with Job lifecycle management."""

    def __init__(self, max_workers: int = 4):
        self._pool = _ThreadPoolExecutor(max_workers=max_workers)
        self._max_workers = max_workers
        self._active = 0
        self._lock = threading.Lock()
        logger.info("ThreadPoolExecutor ready (max_workers=%d)", max_workers)

    def execute(self, job: Job) -> None:
        """
        Submit job to thread pool. Non-blocking — returns immediately.
        mark_completed() is called inside the worker thread via future callback.
        """
        with self._lock:
            self._active += 1

        future = self._pool.submit(self._run, job)
        future.add_done_callback(lambda f: self._on_done(f, job))

    def _run(self, job: Job):
        """Worker function — runs inside a thread from the pool."""
        with track_request() as metrics:
            result = run_workload(job.workload_type, job.params)
            job.os_metrics = metrics  # inside block — set even if exception occurs (finally runs)
        return result

    def _on_done(self, future, job: Job) -> None:
        """Called when the future completes (success or exception)."""
        with self._lock:
            self._active -= 1
        try:
            result = future.result()
            job.mark_completed(result=result)
            logger.debug("Job %s completed (type=%s)", job.job_id, job.workload_type)
        except Exception as e:
            job.mark_completed(error=str(e))
            logger.error("Job %s failed: %s", job.job_id, e)

    def shutdown(self, wait: bool = True) -> None:
        self._pool.shutdown(wait=wait)
        logger.info("ThreadPoolExecutor shut down.")

    def stats(self) -> dict:
        with self._lock:
            return {
                "executor": "thread_pool",
                "max_workers": self._max_workers,
                "active_jobs": self._active,
            }
