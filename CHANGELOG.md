# Changelog

All notable changes to the OS Concurrency Study – Adaptive Task Execution Server project will be documented in this
file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [0.4.0] - 2024-01-XX

### Added

- Comprehensive documentation structure in `docs/` directory
    - `docs/architecture.md` – System design and component flow
    - `docs/api.md` – API endpoint specifications
    - `docs/experiments.md` – Experiment execution guidelines
    - `docs/results.md` – Results interpretation guide
    - `docs/README.md` – Documentation index
- Experiment infrastructure with YAML configuration (`config/experiment.yaml`)
- Results directory structure for JSONL, CSV, and plot outputs
- Analysis scripts in `experiments/analysis/` for data summarization and visualization

### Changed

- Enhanced README.md with complete project overview, architecture diagram, and setup instructions
- Organized project structure with clear separation of concerns

---

## [0.3.0] - 2024-01-XX

### Added

- Metrics collection system using `psutil` for OS-level profiling
    - Per-request latency tracking
    - Waiting time measurement
    - CPU time (user/system) monitoring
    - Memory usage (RSS delta) tracking
    - Context switch delta measurement
- Structured logging configuration (`config/logging_config.py`)
- Experiment logging utilities in `src/utils/`
- JSONL-based raw data storage for reproducibility

---

## [0.2.0] - 2024-01-XX

### Added

- Multiple server implementations:
    - Flask baseline server (single-threaded)
    - Flask threaded server (multi-threaded)
    - Flask process server (multi-process)
    - FastAPI async server (asynchronous)
- Executor implementations in `src/executors/`:
    - Thread-based executor
    - Process-based executor
    - Async executor
- Dispatcher layer (`src/dispatch/`) bridging scheduler and executors
- Load testing integration with Locust

---

## [0.1.0] - 2024-01-XX

### Added

- Core job abstraction in `src/core/`
- Scheduling policies in `src/scheduler/`:
    - FIFO (First-In-First-Out) scheduler
    - Priority-based scheduler with configurable priorities
- Workload implementations in `src/workloads/`:
    - CPU-bound workloads (Fibonacci, matrix multiplication)
    - IO-bound workloads (file operations, sleep simulation)
    - Memory-bound workloads (large array processing)
    - Mixed workloads (CPU→IO and IO→CPU)
    - ML workloads (lightweight Linear Regression prediction)
- Parameterized workload configuration for controlled scaling
- Project structure with organized directories:
    - `src/` for source code
    - `config/` for configuration files
    - `logs/` for log outputs
    - `experiments/` for experiment scripts
    - `results/` for experiment outputs

### Changed

- Initial project setup with virtual environment support
- Requirements specification in `requirements.txt`

---

## [0.0.1] - 2024-01-XX

### Added

- Initial project repository structure
- Basic README with project concept
- Git repository initialization
- `.gitkeep` files for empty directories (`logs/`)
