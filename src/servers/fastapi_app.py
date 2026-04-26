# src/servers/fastapi_app.py
"""
FastAPI server — async IO executor experiments.

Configuration via environment variables:
    SCHEDULER_TYPE  : fifo | priority   (default: fifo)
    EXPERIMENT_ID   : str               (default: timestamp)
    JOB_TIMEOUT     : float seconds     (default: 30)

This server always uses AsyncExecutor. The executor runs its own event loop
in a background thread. Completion signals are bridged back to FastAPI's
event loop via asyncio.Future + loop.call_soon_threadsafe().

POST /run
    Body: {"workload_type": str, "params": dict, "priority": int (optional)}
    Returns: full job result dict

GET  /health
GET  /stats
"""
import asyncio
import os
import logging

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import Any, Dict, Optional

from config.logging_config import setup_logging
from src.core.job import Job
from src.utils.experiment_logger import ExperimentLogger

# ── Configuration ─────────────────────────────────────────────────────────────
SCHEDULER_TYPE = os.getenv("SCHEDULER_TYPE", "fifo").lower()
EXPERIMENT_ID  = os.getenv("EXPERIMENT_ID",  None)
JOB_TIMEOUT    = float(os.getenv("JOB_TIMEOUT", "30"))

# ── Globals ───────────────────────────────────────────────────────────────────
_dispatcher  = None
_executor    = None
_exp_logger  = None


# ── Lifespan (replaces deprecated @app.on_event) ──────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    global _dispatcher, _executor, _exp_logger

    setup_logging(EXPERIMENT_ID)
    log = logging.getLogger(__name__)

    _exp_logger = ExperimentLogger(experiment_id=EXPERIMENT_ID)

    if SCHEDULER_TYPE == "priority":
        from src.scheduler.priority import PriorityScheduler
        scheduler = PriorityScheduler()
    else:
        from src.scheduler.fifo import FIFOScheduler
        scheduler = FIFOScheduler()

    from src.executors.async_executor import AsyncExecutor
    from src.dispatch.dispatcher import Dispatcher

    _executor   = AsyncExecutor()
    _dispatcher = Dispatcher(scheduler=scheduler, executor_fn=_executor.execute)
    _dispatcher.start()

    log.info("FastAPI server started | scheduler: %s", SCHEDULER_TYPE)

    yield  # server is running

    # Shutdown
    _dispatcher.stop()
    _executor.shutdown()
    if _exp_logger:
        _exp_logger.close()
    log.info("FastAPI server shut down.")


app = FastAPI(title="OS Concurrency Study — Async Server", lifespan=lifespan)


# ── Request / Response schemas ────────────────────────────────────────────────
class RunRequest(BaseModel):
    workload_type: str
    params: Dict[str, Any] = {}
    priority: Optional[int] = 2


# ── Routes ────────────────────────────────────────────────────────────────────
@app.post("/run")
async def run_job(req: RunRequest):
    loop = asyncio.get_running_loop()
    future: asyncio.Future = loop.create_future()

    job = Job(
        workload_type=req.workload_type,
        params=req.params,
        priority=req.priority,
    )

    def _on_complete(completed_job: Job):
        """
        Called by executor (in its own thread) when job finishes.
        Bridges result back to this coroutine's event loop safely.
        """
        if _exp_logger:
            _exp_logger.log(completed_job)

        if completed_job.error:
            exc = Exception(completed_job.error)
            loop.call_soon_threadsafe(future.set_exception, exc)
        else:
            loop.call_soon_threadsafe(future.set_result, completed_job)

    job.on_complete = _on_complete
    _dispatcher.submit(job)

    try:
        completed_job = await asyncio.wait_for(future, timeout=JOB_TIMEOUT)
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504,
                            detail={"error": "Job timed out", "job_id": job.job_id})
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})

    return JSONResponse(content=completed_job.to_dict(), status_code=200)


@app.get("/health")
async def health():
    return {"status": "ok", "executor": "async", "scheduler": SCHEDULER_TYPE}


@app.get("/stats")
async def stats():
    if _dispatcher:
        return _dispatcher.stats()
    return {"status": "not started"}
