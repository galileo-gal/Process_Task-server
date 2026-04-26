# src/utils/metrics.py - UPDATED with delta tracking
import psutil
import time
import logging
from contextlib import contextmanager
from typing import Dict


@contextmanager
def track_request():
    """Track OS-level metrics with delta computation."""
    logger = logging.getLogger(__name__)
    process = psutil.Process()

    # Snapshot BEFORE
    cpu_times_start = process.cpu_times()
    ctx_switches_start = process.num_ctx_switches()
    mem_start = process.memory_info().rss / 1024 / 1024  # MB
    wall_start = time.perf_counter()

    metrics = {}

    try:
        yield metrics
    finally:
        # Snapshot AFTER
        wall_end = time.perf_counter()
        cpu_times_end = process.cpu_times()
        ctx_switches_end = process.num_ctx_switches()
        mem_end = process.memory_info().rss / 1024 / 1024

        # Compute DELTAS
        metrics['duration_s'] = round(wall_end - wall_start, 3)
        metrics['cpu_user_delta_s'] = round(cpu_times_end.user - cpu_times_start.user, 3)
        metrics['cpu_system_delta_s'] = round(cpu_times_end.system - cpu_times_start.system, 3)
        metrics['ctx_voluntary_delta'] = ctx_switches_end.voluntary - ctx_switches_start.voluntary
        metrics['ctx_involuntary_delta'] = ctx_switches_end.involuntary - ctx_switches_start.involuntary
        metrics['memory_mb'] = round(mem_end, 2)
        metrics['memory_delta_mb'] = round(mem_end - mem_start, 2)

        logger.info("request_metrics", extra=metrics)