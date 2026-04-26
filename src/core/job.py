# src/core/job.py
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional
from datetime import datetime
import uuid


@dataclass
class Job:
    """Job abstraction for workload execution with scheduling metadata."""

    workload_type: str
    params: Dict[str, Any]
    priority: int = 2  # 1=high, 2=medium, 3=low
    job_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    # Timestamps for lifecycle tracking
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())
    enqueued_at: Optional[float] = None
    dequeued_at: Optional[float] = None
    started_at: Optional[float] = None
    completed_at: Optional[float] = None

    # Results
    result: Optional[Any] = None
    error: Optional[str] = None

    # Metrics
    waiting_time: Optional[float] = None   # dequeued_at - enqueued_at
    execution_time: Optional[float] = None  # completed_at - started_at
    total_time: Optional[float] = None      # completed_at - created_at

    # OS-level metrics snapshot (populated by executor after workload completes)
    os_metrics: Optional[Dict[str, Any]] = None

    # Optional completion callback — called at the end of mark_completed().
    # Used by the server layer to signal a waiting request thread/coroutine.
    # Excluded from to_dict() — not serializable.
    # Must NOT be sent to worker processes (ProcessPool passes only params, not Job).
    on_complete: Optional[Callable[["Job"], None]] = field(default=None, repr=False)

    def mark_enqueued(self):
        self.enqueued_at = datetime.now().timestamp()

    def mark_dequeued(self):
        self.dequeued_at = datetime.now().timestamp()
        if self.enqueued_at:
            self.waiting_time = self.dequeued_at - self.enqueued_at

    def mark_started(self):
        self.started_at = datetime.now().timestamp()

    def mark_completed(self, result=None, error=None):
        self.completed_at = datetime.now().timestamp()
        self.result = result
        self.error = error
        if self.started_at:
            self.execution_time = self.completed_at - self.started_at
        if self.created_at:
            self.total_time = self.completed_at - self.created_at
        if self.on_complete:
            self.on_complete(self)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes job to dict for logging/JSONL output."""
        return {
            "job_id": self.job_id,
            "workload_type": self.workload_type,
            "params": self.params,
            "priority": self.priority,
            "waiting_time": self.waiting_time,
            "execution_time": self.execution_time,
            "total_time": self.total_time,
            "error": self.error,
            "os_metrics": self.os_metrics,
        }
