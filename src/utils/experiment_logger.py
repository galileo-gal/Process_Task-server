# src/utils/experiment_logger.py
"""
Experiment logger — writes completed Job results to a JSONL file.

Each line is one JSON record (one job). JSONL is used because:
- Append-safe under concurrent writes (one atomic line per job)
- Easy to stream and post-process with pandas / jq
- No schema lock-in

Usage:
    logger = ExperimentLogger(experiment_id="exp_01")
    logger.log(job)        # call after job.mark_completed()
    logger.close()
"""
import json
import logging
import os
import threading
from datetime import datetime
from src.core.job import Job

logger = logging.getLogger(__name__)


class ExperimentLogger:

    def __init__(self, experiment_id: str = None, log_dir: str = "results"):
        os.makedirs(log_dir, exist_ok=True)
        exp_id = experiment_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self._path = os.path.join(log_dir, f"{exp_id}.jsonl")
        self._lock = threading.Lock()
        self._file = open(self._path, "a", encoding="utf-8")
        logger.info("ExperimentLogger writing to %s", self._path)

    def log(self, job: Job) -> None:
        """Append one job record to the JSONL file. Thread-safe."""
        record = job.to_dict()
        line = json.dumps(record, default=str)
        with self._lock:
            self._file.write(line + "\n")
            self._file.flush()

    def close(self) -> None:
        with self._lock:
            self._file.close()
        logger.info("ExperimentLogger closed (%s)", self._path)

    @property
    def path(self) -> str:
        return self._path
