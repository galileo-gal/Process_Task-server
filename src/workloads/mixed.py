# src/workloads/mixed.py - NEW FILE
from src.workloads.cpu_bound import fibonacci
from src.workloads.io_bound import sleep_simulation
from src.utils.logger import log_execution

@log_execution
def cpu_then_io(cpu_param: int, io_ms: int) -> tuple:
    """Execute CPU workload followed by IO. cpu_param: fib(n), io_ms: sleep duration."""
    cpu_result = fibonacci(cpu_param)
    io_result = sleep_simulation(io_ms)
    return (cpu_result, io_result)

@log_execution
def io_then_cpu(io_ms: int, cpu_param: int) -> tuple:
    """Execute IO workload followed by CPU."""
    io_result = sleep_simulation(io_ms)
    cpu_result = fibonacci(cpu_param)
    return (io_result, cpu_result)