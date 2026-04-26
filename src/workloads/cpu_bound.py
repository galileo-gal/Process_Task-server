# src/workloads/cpu_bound.py - UPDATED with parameterization
import math
import numpy as np
from src.utils.logger import log_execution


def fibonacci(n: int) -> int:
    """Recursive fibonacci. Param range: 28-36 for laptop safety."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

@log_execution
def matrix_multiply(size: int) -> float:
    """Matrix multiplication. Param range: 200-800 for laptop safety."""
    a = np.random.rand(size, size)
    b = np.random.rand(size, size)
    result = np.dot(a, b)
    return float(result[0, 0])  # Return sample value

@log_execution
def prime_check(limit: int) -> int:
    """Count primes up to limit. Param range: 10000-100000."""
    count = 0
    for n in range(2, limit):
        is_prime = True
        for i in range(2, int(math.sqrt(n)) + 1):
            if n % i == 0:
                is_prime = False
                break
        if is_prime:
            count += 1
    return count
