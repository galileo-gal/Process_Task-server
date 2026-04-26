# src/workloads/memory_bound.py - UPDATED
import numpy as np
from src.utils.logger import log_execution

@log_execution
def numpy_allocation(mb: int) -> float:
    """Allocate numpy array. Param range: 50-300MB."""
    elements = (mb * 1024 * 1024) // 8  # 8 bytes per float64
    arr = np.zeros(elements)
    return arr.sum()

@log_execution
def array_operations(mb: int) -> float:
    """Array allocation + operations. Param range: 50-300MB."""
    elements = (mb * 1024 * 1024) // 8
    arr = np.random.rand(elements)
    result = arr * 2.0
    return result.sum()

@log_execution
def list_processing(size: int = 2_000_000) -> int:
    """Process large Python list. Max 3M elements for safety."""
    data = list(range(size))
    result = [x * 2 for x in data if x % 2 == 0]
    return len(result)