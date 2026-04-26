# src/dispatch/dispatcher.py
import threading
import logging
from typing import Callable, Union
from src.core.job import Job
from src.scheduler.fifo import FIFOScheduler
from src.scheduler.priority import PriorityScheduler

logger = logging.getLogger(__name__)

SchedulerType = Union[FIFOScheduler, PriorityScheduler]


class Dispatcher:
    """
    Policy-to-mechanism bridge.

    Responsibilities:
    - Accept jobs from the server layer via submit()
    - Dequeue jobs from the scheduler in policy order
    - Hand jobs to the executor callable
    - Waiting time is recorded by the scheduler (via job.mark_dequeued)

    The dispatcher is executor-agnostic: it calls executor_fn(job) and expects
    the executor to handle thread/process/async dispatch internally.
    """

    def __init__(self, scheduler: SchedulerType, executor_fn: Callable[[Job], None]):
        """
        Args:
            scheduler:    A FIFOScheduler or PriorityScheduler instance.
            executor_fn:  Callable that accepts a Job and executes it.
                          Called in the dispatch loop thread.
        """
        self._scheduler = scheduler
        self._executor_fn = executor_fn
        self._running = False
        self._thread: threading.Thread | None = None

    def submit(self, job: Job) -> None:
        """Enqueue a job into the scheduler. Called by the server layer."""
        self._scheduler.put(job)
        logger.debug("Submitted job %s (type=%s, priority=%d)",
                     job.job_id, job.workload_type, job.priority)

    def start(self) -> None:
        """Start the background dispatch loop."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True, name="dispatcher")
        self._thread.start()
        logger.info("Dispatcher started (scheduler=%s)",
                    type(self._scheduler).__name__)

    def stop(self) -> None:
        """Signal the dispatch loop to stop after the current job finishes."""
        self._running = False
        logger.info("Dispatcher stop requested.")

    def _loop(self) -> None:
        """
        Dispatch loop: continuously dequeue and execute jobs while running.
        Blocks on get() with a short timeout to allow clean shutdown.
        """
        while self._running:
            job = self._scheduler.get(timeout=0.1)
            if job is None:
                continue
            try:
                job.mark_started()
                self._executor_fn(job)
            except Exception as e:
                job.mark_completed(error=str(e))
                logger.error("Job %s failed: %s", job.job_id, e)

    def stats(self) -> dict:
        return {
            "running": self._running,
            **self._scheduler.stats(),
        }
