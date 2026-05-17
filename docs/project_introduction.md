# OS Concurrency Study — Project Introduction

## What is this?

An HTTP server built to **measure** Operating Systems concepts — not just implement them.

Most OS projects stop at "it works." This one asks: *by how much, and why?*

It accepts jobs over HTTP, schedules them using FIFO or Priority policy, executes them via threads, processes, or async — then records OS-level metrics for every single job: CPU time consumed, context switches triggered, memory allocated, and exact time spent waiting in the scheduler queue.

The result is a controlled experiment that produces real data on questions like:

- Does Python's GIL actually hurt thread performance for CPU tasks? (**Yes. 43.6% slower than process.*)
- Does Priority scheduling starve low-priority jobs at scale? (**Yes. +212% waiting time at 100 users.**)
- Is async actually faster for IO? (**Yes. 2× the throughput of threads.**)

---

## Skills Demonstrated

**Operating Systems:** Scheduling policies, GIL mechanics, process/thread/async concurrency models, context switches, IPC, voluntary vs involuntary preemption

**Software Engineering:** Clean layered architecture, separation of concerns, thread-safe data structures, cross-platform compatibility, pre-commit hooks, structured logging

**Systems Programming:** psutil delta-based OS metric collection, multiprocessing pickling constraints, asyncio event loop bridging across threads

**Data Engineering:** JSONL logging, pandas aggregation, matplotlib visualization, statistical analysis (CV, p95/p99, Welch's t-test)

**DevOps:** Automated experiment runner, Locust load testing, virtual environment management across Windows and WSL2

---

## Architecture in One Diagram

```
HTTP Request
     ↓
  Server Layer          (Flask / FastAPI)
     ↓
  Scheduler             (FIFO or Priority)
     ↓
  Dispatcher            ← measures waiting time here
     ↓
  Executor              (Thread / Process / Async)
     ↓
  Workload              (CPU / IO / Memory / Mixed / ML)
     ↓
  psutil Metrics        → JSONL Log → CSV → Charts
```

Each layer has one responsibility. The scheduler never executes. The executor never schedules. The dispatcher makes waiting time independently observable.

---

## Key Results

| Finding | Data |
|---------|------|
| GIL cost on CPU workloads | Process 43.6% faster than baseline |
| Priority starvation at 100 users | IO waiting time +212% vs FIFO |
| Async IO throughput | 2× jobs/second vs thread/process |
| Most stable executor | Process (CV=38.9% vs baseline CV=67.9%) |

---

## Documentation

| | |
|-|-|
| [`docs/architecture.md`](docs/architecture.md) | System design and layer responsibilities |
| [`docs/api.md`](docs/api.md) | REST API reference |
| [`docs/experiments.md`](docs/experiments.md) | How to reproduce experiments |
| [`docs/results.md`](docs/results.md) | Full analysis with charts |
| [`docs/technical_report.md`](docs/technical_report.md) | STAR-format challenge report |

---

*Built for CSE-323 Operating Systems — North South University, Spring 2026*
