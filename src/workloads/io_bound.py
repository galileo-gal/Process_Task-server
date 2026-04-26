# src/workloads/io_bound.py
import asyncio
import os
import tempfile
import time

from src.utils.logger import log_execution, async_log_execution


@log_execution
def file_operations(size_kb: int, iterations: int = 100) -> int:
    """File read/write operations. size_kb: 100-300, iterations: 10-50."""
    data = b"x" * (size_kb * 1024)

    with tempfile.NamedTemporaryFile(delete=False) as f:
        tmp_path = f.name

    try:
        for _ in range(iterations):
            with open(tmp_path, "wb") as f:
                f.write(data)
            with open(tmp_path, "rb") as f:
                _ = f.read()
    finally:
        os.unlink(tmp_path)

    return iterations


@log_execution
def sleep_simulation(ms: int) -> int:
    """Simulate network latency. Param range: 100-500ms."""
    time.sleep(ms / 1000.0)
    return ms


@async_log_execution
async def async_file_operations(size_kb: int, iterations: int = 100) -> int:
    """Async file operations using aiofiles."""
    import aiofiles
    data = b"x" * (size_kb * 1024)

    with tempfile.NamedTemporaryFile(delete=False) as f:
        tmp_path = f.name

    try:
        for _ in range(iterations):
            async with aiofiles.open(tmp_path, "wb") as f:
                await f.write(data)
            async with aiofiles.open(tmp_path, "rb") as f:
                _ = await f.read()
    finally:
        os.unlink(tmp_path)

    return iterations


@async_log_execution
async def async_sleep(ms: int) -> int:
    """Async sleep simulation."""
    await asyncio.sleep(ms / 1000.0)
    return ms
