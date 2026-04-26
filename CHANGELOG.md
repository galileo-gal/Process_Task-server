# Changelog

All notable changes to this project are documented in this file.

This project follows a **chronological engineering log**, tracking architectural decisions, tooling changes, and experiment-related updates.  
Dates reflect when changes were committed to `main`.

---

## [2026-04-24] – Phase 1 Complete: Full Experiment Run & Analysis

### Added
- Full scheduler implementations:
  - `src/scheduler/fifo.py` — thread-safe FIFO using `queue.Queue`
  - `src/scheduler/priority.py` — heap-based priority scheduler with `threading.Condition` blocking and stable `id(job)` tiebreaker
- Dispatcher bridge (`src/dispatch/dispatcher.py`) connecting scheduler policy to executor mechanism
- Three executor backends:
  - `src/executors/thread_pool.py` — `concurrent.futures.ThreadPoolExecutor` with Job lifecycle callbacks
  - `src/executors/process_pool.py` — `concurrent.futures.ProcessPoolExecutor` with picklable top-level worker function
  - `src/executors/async_executor.py` — asyncio event loop in background thread; CPU tasks offloaded via `run_in_executor()`
- Workload registry (`src/core/registry.py`) — single picklable dispatch table for all executors
- Flask server (`src/servers/flask_app.py`) — baseline, thread, and process modes via `EXECUTOR_TYPE` env var
- FastAPI server (`src/servers/fastapi_app.py`) — async mode with `asyncio.Future` + `loop.call_soon_threadsafe()` bridge
- Experiment logger (`src/utils/experiment_logger.py`) — thread-safe JSONL append writer
- Centralized logging (`config/logging_config.py`) — JSON file handler + human-readable console handler
- Locust load test (`experiments/locustfile.py`) — 8 workload tasks with realistic priority and weight distribution
- Automated experiment runner (`scripts/run_experiment.py`) — runs all 7 configurations sequentially
- Analysis pipeline:
  - `experiments/analysis/summarize.py` — flattens JSONL → `summary.csv`
  - `experiments/analysis/plot.py` — 5 charts from `summary.csv`
- Experiment results and analysis (`docs/results.md`) — 10 findings grounded in real experiment data

### Changed
- `src/core/job.py` — added `os_metrics: Optional[Dict]` field and `on_complete` callback; updated `to_dict()`
- `src/utils/logger.py` — fixed duplicate docstring; renamed `args` → `func_args` in `extra=` to avoid `LogRecord` collision
- `src/workloads/cpu_bound.py` — removed `@log_execution` from `fibonacci` to prevent recursive decorator spam
- `src/workloads/io_bound.py` — replaced `/tmp/` path with `tempfile.NamedTemporaryFile` for Windows compatibility; added async variants
- `requirements.txt` — added `pandas`, `matplotlib`, `aiofiles`, `pydantic`
- Pre-commit hook — replaced hardcoded Python 3.11 path with venv-relative path

### Fixed
- `PriorityScheduler` heap crash — added `id(job)` as tiebreaker so `Job` objects are never compared directly (`TypeError`)
- `PriorityScheduler` busy-wait — replaced immediate `None` return with `threading.Condition.wait(timeout)` to match FIFO blocking behaviour
- `registry.py` — lazy import of `ml_simple` to prevent model training at import time in every worker process
- Windows `ProcessPoolExecutor` spawn guard — executor initialisation moved inside `if __name__ == '__main__':` in Flask server

### Experiment Results Summary (2026-04-24)
- **1,150 jobs** recorded across 7 configurations
- Process executor fastest for CPU (`cpu_fibonacci`: 0.132s vs thread 0.153s vs baseline 0.217s) — GIL effect confirmed
- Async executor highest throughput for IO (~243 jobs/60s vs ~137 for thread/process)
- Priority scheduler increases IO waiting time by 20–32% vs FIFO at 10 concurrent users
- Process executor highest context switches (mean 34.7/job) due to IPC overhead
- Known limitation: async `os_metrics` NaN due to psutil measuring wrong thread

---

## [Unreleased]
### Planned
- Phase 2: higher concurrency experiments (50+ users) to observe starvation clearly
- Aging mechanism in Priority scheduler to prevent indefinite IO starvation
- WSL2 `perf` integration for kernel-level context switch tracing
- SJF scheduling with ML-based burst time predictor (deferred from Phase 1)

---

## [2026-02-11] – Infrastructure Stabilization & Cross-Platform Setup

### Added
- WSL2-based Linux execution environment for OS-level experiments
- SSH-based GitHub authentication for reliable cross-platform Git operations
- `requirements.lock.linux.txt` and `requirements.lock.windows.txt` for platform-specific dependency tracking
- Structured documentation set under `docs/`:
  - `architecture.md`
  - `api.md`
  - `experiments.md`
  - `results.md`
- Scheduler module scaffolding:
  - `src/scheduler/fifo.py`
  - `src/scheduler/priority.py`
- Dispatcher abstraction (`src/dispatch/dispatcher.py`) to decouple scheduling from execution
- Core job abstraction (`src/core/job.py`) to unify task metadata (type, priority, timestamps)

### Changed
- Normalized line endings to **LF** across the repository using `.gitattributes`
- Updated `requirements.txt` to support ML workloads:
  - Added `scikit-learn`, `scipy`, `joblib`
  - Constrained `numpy` to `<2.0` for cross-platform compatibility
- Refactored logging utilities for structured, experiment-safe logging
- Refined metrics collection utilities for OS-oriented measurements (CPU time, context switches)

### Fixed
- Git line-ending conflicts between Windows and Linux environments
- Broken virtual environment creation on Windows and WSL
- NumPy build failures on Windows due to missing compilers
- Git permission and authentication issues (HTTPS → SSH migration)
- Accidental nested repository creation during WSL setup

---

## [2026-02-10] – Project Structure & Architectural Finalization

### Added
- Finalized project directory structure separating:
  - workloads
  - schedulers
  - executors
  - servers
  - utilities
- Initial workload implementations:
  - CPU-bound workloads
  - IO-bound workloads
  - Memory-bound workloads
  - Mixed workloads
  - ML inference workload (predict-only)
- Experiment analysis utilities:
  - `experiments/analysis/plot.py`
  - `experiments/analysis/summarize.py`
- Centralized experiment configuration (`config/experiment.yaml`)

### Changed
- Replaced URL-parameter APIs with JSON POST-based execution
- Reduced workload sizes to laptop-safe bounds
- Reworked metrics to use **delta-based** measurement (before/after snapshots)

---

## [2026-02-09] – Phase 1 Blueprint & Academic Alignment

### Added
- Phase 1 OS Concurrency Study blueprint
- Week-by-week experiment plan covering:
  - Baseline execution
  - Multi-threading
  - Multi-processing
  - Async IO
- Explicit scheduling policy requirement (FIFO vs Priority)
- OS-level metrics plan using `psutil` (Windows/WSL compatible)

### Changed
- Shifted focus from capstone-style breadth to **OS scheduling and concurrency depth**
- Explicitly scoped async workloads to IO-only tasks
- Reframed ML workloads as inference-only to avoid training bias

---

## [2026-02-08] – Initial Repository Setup

### Added
- Initial repository with Flask and FastAPI servers
- Basic executor abstractions (thread, process, async)
- Logging and metrics utility scaffolding
- Base `.gitignore` for Python, logs, and build artifacts

---

## Notes
- This project is intentionally developed across **Windows (development)** and **Linux/WSL (execution & profiling)** environments.
- Platform-specific limitations (e.g., `perf` availability) are documented explicitly and treated as experimental constraints, not omissions.

---
