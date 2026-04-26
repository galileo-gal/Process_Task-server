# src/scheduler/fifo.py
import queue
import threading
from typing import Optional
from src.core.job import Job


class FIFOScheduler:
    """First-In First-Out scheduler. Arrival order is preserved strictly."""

    def __init__(self):
        self._queue: queue.Queue[Job] = queue.Queue()
        self._lock = threading.Lock()
        self._enqueued_count = 0
        self._dequeued_count = 0

    def put(self, job: Job) -> None:
        """Enqueue a job. Calls job.mark_enqueued() before inserting."""
        job.mark_enqueued()
        self._queue.put(job)
        with self._lock:
            self._enqueued_count += 1

    def get(self, timeout: Optional[float] = None) -> Optional[Job]:
        """
        Dequeue the next job. Calls job.mark_dequeued() before returning.
        Returns None if queue is empty and timeout expires.
        """
        try:
            job = self._queue.get(timeout=timeout)
            job.mark_dequeued()
            with self._lock:
                self._dequeued_count += 1
            return job
        except queue.Empty:
            return None

    def task_done(self) -> None:
        """Signal that a previously dequeued job has been processed."""
        self._queue.task_done()

    def qsize(self) -> int:
        return self._queue.qsize()

    def empty(self) -> bool:
        return self._queue.empty()

    def stats(self) -> dict:
        with self._lock:
            return {
                "scheduler": "fifo",
                "enqueued": self._enqueued_count,
                "dequeued": self._dequeued_count,
                "queue_depth": self._queue.qsize(),
            }
