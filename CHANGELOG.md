# Changelog

All notable changes to this project are documented in this file.

This project follows a **chronological engineering log**, tracking architectural decisions, tooling changes, and experiment-related updates.  
Dates reflect when changes were committed to `main`.

---

## [2026-04-27] – Extended Experiment Run & Full Documentation

### Added
- Advanced experiment phase scripts:
  - `scripts/run_phase1.py` — 10-run stability check with CV analysis
  - `scripts/run_phase2.py` — load sweep using WSL2 `stress-ng` at 4 CPU levels
  - `scripts/run_phase3.py` — workload isolation (CPU / IO / memory groups)
  - `scripts/run_phase4.py` — concurrency scaling (1–100 users, finds breaking point)
  - `scripts/run_phase5.py` — scheduler deep dive with 5 runs per config, priority tier analysis
- Isolated workload locustfiles:
  - `experiments/locustfile_cpu.py`
  - `experiments/locustfile_io.py`
  - `experiments/locustfile_memory.py`
  - `experiments/locustfile_priority_uniform.py`
  - `experiments/locustfile_priority_bimodal.py`
- Completed documentation:
  - `docs/api.md` — full REST API reference with request/response schemas
  - `docs/experiments.md` — experiment procedure, environment setup, known issues
  - `docs/results.md` — extended analysis across two runs (10 users + 100 users)

### Changed
- `requirements.txt` — added `scikit-learn>=1.4.0` explicitly (was missing from recreated venv, causing ml_predict failures in Run 2)
- `docs/results.md` — rewritten to include 100-user extended run findings
- `PROJECT_HANDOFF.md` — updated with all new files, new bugs found, current status

### Fixed
- `ml_predict` workload failures — `scikit-learn` missing from requirements.txt

### Experiment Results — Run 2 (2026-04-27, 100 users, 180s)
- **~2,900 jobs** across 7 configurations
- Priority scheduling IO starvation now clearly visible: +80–212% waiting time vs FIFO at 100 users
- Process executor: 43.6% faster than baseline for CPU workloads (GIL confirmed)
- Async executor: 2× job throughput vs thread/process (3.22 vs 1.78 jobs/s)
- Baseline execution variance CV=67.9% — single-run averages unreliable for baseline
- Process executor most stable: CV=38.9%
- Voluntary context switches 10–50× higher at 100 users vs 10 users
- New bug found: `ml_predict` failing with `No module named 'sklearn'` in fresh venv

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
- Initial results and analysis (`docs/results.md`)

### Changed
- `src/core/job.py` — added `os_metrics: Optional[Dict]` field and `on_complete` callback; updated `to_dict()`
- `src/utils/logger.py` — renamed `args` → `func_args` in `extra=` to avoid `LogRecord` collision
- `src/workloads/cpu_bound.py` — removed `@log_execution` from `fibonacci` to prevent recursive decorator spam
- `src/workloads/io_bound.py` — replaced `/tmp/` with `tempfile.NamedTemporaryFile`; added async variants
- Pre-commit hook — replaced hardcoded Python 3.11 path with venv-relative path

### Fixed
- `PriorityScheduler` heap crash — added `id(job)` as tiebreaker
- `PriorityScheduler` busy-wait — replaced with `threading.Condition.wait(timeout)`
- `registry.py` — lazy import of `ml_simple`
- Windows `ProcessPoolExecutor` spawn guard
- `job.os_metrics` field missing from dataclass

### Experiment Results — Run 1 (2026-04-24, 10 users, 60s)
- **1,150 jobs** across 7 configurations
- Process executor fastest for CPU — GIL confirmed
- Async executor 2× IO throughput
- Priority scheduler: IO waiting time +20–32% vs FIFO (barely visible at 10 users)

---

## [2026-02-11] – Infrastructure Stabilization & Cross-Platform Setup

### Added
- WSL2-based Linux execution environment
- SSH-based GitHub authentication
- `requirements.lock.linux.txt` and `requirements.lock.windows.txt`
- Structured documentation set under `docs/`
- Scheduler module scaffolding
- Dispatcher abstraction
- Core job abstraction

### Fixed
- Git line-ending conflicts
- Broken virtual environment creation
- NumPy build failures on Windows
- Git authentication issues

---

## [2026-02-10] – Project Structure & Architectural Finalization

### Added
- Finalized project directory structure
- Initial workload implementations (CPU, IO, memory, mixed, ML)
- Experiment analysis utilities
- Centralized experiment configuration

### Changed
- Replaced URL-parameter APIs with JSON POST
- Reduced workload sizes to laptop-safe bounds
- Reworked metrics to delta-based measurement

---

## [2026-02-09] – Phase 1 Blueprint & Academic Alignment

### Added
- Phase 1 OS Concurrency Study blueprint
- Week-by-week experiment plan
- OS-level metrics plan using `psutil`

### Changed
- Shifted focus to OS scheduling and concurrency depth
- Reframed ML workloads as inference-only

---

## [2026-02-08] – Initial Repository Setup

### Added
- Initial repository with Flask and FastAPI servers
- Basic executor abstractions
- Logging and metrics utility scaffolding
- Base `.gitignore`

---

## Notes
- Development: Windows 11. Profiling: WSL2 Ubuntu.
- Platform limitations documented as experimental constraints, not omissions.
