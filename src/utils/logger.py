# src/utils/logger.py
import logging
import time
from functools import wraps

def log_execution(func):
    """Decorator that logs execution time and errors."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            duration = time.perf_counter() - start
            logger.info("execution_success", extra={
                "function": func.__name__,
                "duration_ms": round(duration * 1000, 2),
                "func_args": str(args)[:100]
            })
            return result
        except Exception as e:
            duration = time.perf_counter() - start
            logger.error("execution_failed", extra={
                "function": func.__name__,
                "duration_ms": round(duration * 1000, 2),
                "error": str(e)
            })
            raise
    return wrapper

def async_log_execution(func):
    """Decorator that logs async execution time and errors."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        start = time.perf_counter()
        try:
            result = await func(*args, **kwargs)
            duration = time.perf_counter() - start
            logger.info("execution_success", extra={
                "function": func.__name__,
                "duration_ms": round(duration * 1000, 2)
            })
            return result
        except Exception as e:
            duration = time.perf_counter() - start
            logger.error("execution_failed", extra={
                "function": func.__name__,
                "duration_ms": round(duration * 1000, 2),
                "error": str(e)
            })
            raise
    return wrapper
