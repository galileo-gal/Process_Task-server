# src/scheduler/priority.py
import heapq
import threading
from typing import Optional
from src.core.job import Job


class PriorityScheduler:
    """
    Priority-based scheduler. Lower priority integer = higher urgency.
    Convention: 1=high, 2=medium, 3=low (matches Job.priority defaults).

    Tiebreaking within the same priority level is by arrival time (created_at),
    so earlier-arriving jobs run first — preserving FIFO fairness within a tier.

    If created_at also ties (same millisecond), id(job) is used as final
    tiebreaker so Python never attempts to compare Job objects directly,
    which would raise TypeError since Job has no __lt__.
    """

    def __init__(self):
        self._heap: list = []
        self._lock = threading.Lock()
        self._not_empty = threading.Condition(self._lock)
        self._enqueued_count = 0
        self._dequeued_count = 0

    def put(self, job: Job) -> None:
        """
        Enqueue a job. Calls job.mark_enqueued() before inserting.
        Heap key: (priority, created_at, id(job), job) — fully stable ordering.
        """
        job.mark_enqueued()
        with self._not_empty:
            heapq.heappush(self._heap, (job.priority, job.created_at, id(job), job))
            self._enqueued_count += 1
            self._not_empty.notify()

    def get(self, timeout: Optional[float] = None) -> Optional[Job]:
        """
        Dequeue the highest-priority job. Calls job.mark_dequeued() before returning.
        Blocks up to `timeout` seconds if the queue is empty (matching FIFOScheduler
        behaviour). Returns None if still empty after timeout.
        """
        with self._not_empty:
            if not self._heap:
                self._not_empty.wait(timeout=timeout)
            if not self._heap:
                return None
            _, _, _, job = heapq.heappop(self._heap)
            self._dequeued_count += 1

        job.mark_dequeued()
        return job

    def qsize(self) -> int:
        with self._lock:
            return len(self._heap)

    def empty(self) -> bool:
        with self._lock:
            return len(self._heap) == 0

    def stats(self) -> dict:
        with self._lock:
            return {
                "scheduler": "priority",
                "enqueued": self._enqueued_count,
                "dequeued": self._dequeued_count,
                "queue_depth": len(self._heap),
            }
