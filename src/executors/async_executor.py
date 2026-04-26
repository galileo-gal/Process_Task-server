# src/executors/async_executor.py
"""
Async Executor.

Concurrency model: single-threaded event loop (asyncio).
Best for: IO-bound workloads — many tasks wait concurrently without blocking.
CPU workloads: offloaded to a thread pool via loop.run_in_executor() to avoid
blocking the event loop (a CPU-bound coroutine would starve all other tasks).

The event loop runs in a dedicated background thread so the synchronous
dispatcher can call execute() normally.
"""
import asyncio
import logging
import threading
from src.core.job import Job
from src.core.registry import run_workload, ASYNC_WORKLOAD_TYPES
from src.utils.metrics import track_request

logger = logging.getLogger(__name__)


class AsyncExecutor:
    """
    Runs an asyncio event loop in a background thread.
    execute() submits coroutines to that loop from any thread.
    """

    def __init__(self):
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(
            target=self._loop.run_forever,
            daemon=True,
            name="async-executor-loop"
        )
        self._thread.start()
        logger.info("AsyncExecutor event loop started.")

    def execute(self, job: Job) -> None:
        """
        Submit job to the event loop. Non-blocking — returns immediately.
        The coroutine runs inside the dedicated event loop thread.
        """
        asyncio.run_coroutine_threadsafe(self._run(job), self._loop)

    async def _run(self, job: Job) -> None:
        """
        Coroutine that executes the job.

        - Async workloads (io_file_async, io_sleep_async): awaited directly.
        - All other workloads: run in a thread executor to avoid blocking the loop.
        """
        with track_request() as metrics:
            try:
                if job.workload_type in ASYNC_WORKLOAD_TYPES:
                    result = await self._run_async_workload(job)
                else:
                    # Offload sync/CPU work to thread pool so the loop stays free
                    result = await self._loop.run_in_executor(
                        None,  # uses default ThreadPoolExecutor
                        run_workload,
                        job.workload_type,
                        job.params
                    )
                job.os_metrics = metrics
                job.mark_completed(result=result)
                logger.debug("Job %s completed async (type=%s)", job.job_id, job.workload_type)
            except Exception as e:
                job.os_metrics = metrics
                job.mark_completed(error=str(e))
                logger.error("Job %s failed async: %s", job.job_id, e)

    async def _run_async_workload(self, job: Job):
        """Route to native async workload functions."""
        from src.workloads.io_bound import async_file_operations, async_sleep

        if job.workload_type == "io_file_async":
            return await async_file_operations(
                job.params["size_kb"],
                job.params.get("iterations", 100)
            )
        elif job.workload_type == "io_sleep_async":
            return await async_sleep(job.params["ms"])
        else:
            raise KeyError(f"Unknown async workload_type: '{job.workload_type}'")

    def shutdown(self) -> None:
        self._loop.call_soon_threadsafe(self._loop.stop)
        self._thread.join(timeout=5)
        logger.info("AsyncExecutor shut down.")

    def stats(self) -> dict:
        return {
            "executor": "async",
            "loop_running": self._loop.is_running(),
        }
