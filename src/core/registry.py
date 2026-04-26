# src/core/registry.py
"""
Workload registry — maps workload_type strings to actual function calls.

Single source of truth used by all three executors.
run_workload() is a top-level function (not a lambda) so it is picklable
and safe to use with ProcessPoolExecutor.

ml_simple is imported lazily (inside the ml_predict branch only) to avoid
triggering model training at import time in every executor and worker process.
"""
from src.workloads.cpu_bound import fibonacci, matrix_multiply, prime_check
from src.workloads.io_bound import file_operations, sleep_simulation
from src.workloads.memory_bound import numpy_allocation, array_operations, list_processing
from src.workloads.mixed import cpu_then_io, io_then_cpu


def run_workload(workload_type: str, params: dict):
    """
    Execute a workload by name. Top-level so ProcessPoolExecutor can pickle it.

    Returns the raw workload result.
    Raises KeyError for unknown workload_type.
    Raises TypeError if required params are missing.
    """
    if workload_type == "cpu_fibonacci":
        return fibonacci(params["n"])
    elif workload_type == "cpu_matrix":
        return matrix_multiply(params["size"])
    elif workload_type == "cpu_prime":
        return prime_check(params["limit"])
    elif workload_type == "io_file":
        return file_operations(params["size_kb"], params.get("iterations", 100))
    elif workload_type == "io_sleep":
        return sleep_simulation(params["ms"])
    elif workload_type == "memory_numpy":
        return numpy_allocation(params["mb"])
    elif workload_type == "memory_array":
        return array_operations(params["mb"])
    elif workload_type == "memory_list":
        return list_processing(params.get("size", 2_000_000))
    elif workload_type == "mixed_cpu_io":
        return cpu_then_io(params["cpu_param"], params["io_ms"])
    elif workload_type == "mixed_io_cpu":
        return io_then_cpu(params["io_ms"], params["cpu_param"])
    elif workload_type == "ml_predict":
        # Lazy import — model training runs once per process, only when first needed
        from src.workloads.ml_simple import predict_batch
        return predict_batch(params["n_samples"])
    else:
        raise KeyError(f"Unknown workload_type: '{workload_type}'")


# Async variants — imported separately to avoid loading aiofiles at registry import
ASYNC_WORKLOAD_TYPES = {"io_file_async", "io_sleep_async"}
