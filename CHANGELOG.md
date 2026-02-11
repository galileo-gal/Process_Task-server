# Changelog

All notable changes to this project are documented in this file.

This project follows a **chronological engineering log**, tracking architectural decisions, tooling changes, and experiment-related updates.  
Dates reflect when changes were committed to `main`.

---

## [Unreleased]
### Planned
- FIFO vs Priority scheduling implementation inside dispatcher
- Scheduling policy benchmarking under mixed workloads
- Waiting-time, starvation, and fairness analysis
- Final experiment aggregation and report writing

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
