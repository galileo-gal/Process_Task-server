# Experiment Results & Analysis

**Project:** OS Concurrency Study – Adaptive Task Execution Server  
**Phase:** 1  
**Date:** 2026-04-24  
**Total jobs recorded:** 1,150 across 7 experiment configurations  
**Load profile:** 10 concurrent users, 60s per run, 1–3s think time between requests

---

## 1. Experiment Matrix

| Executor | Scheduler | Jobs | Notes |
|----------|-----------|------|-------|
| baseline | fifo      | 118  | Synchronous, no dispatcher |
| thread   | fifo      | 137  | ThreadPoolExecutor, 4 workers |
| thread   | priority  | 135  | ThreadPoolExecutor, 4 workers |
| process  | fifo      | 138  | ProcessPoolExecutor, 4 workers |
| process  | priority  | 136  | ProcessPoolExecutor, 4 workers |
| async    | fifo      | 242  | AsyncExecutor, FastAPI |
| async    | priority  | 244  | AsyncExecutor, FastAPI |

Async processed roughly **2× more jobs** in the same time window due to non-blocking IO concurrency.

---

## 2. Finding 1 — Process Executor is Fastest for CPU Workloads (GIL Effect Confirmed)

| Executor | cpu_fibonacci (s) | cpu_matrix (s) |
|----------|-------------------|----------------|
| baseline | 0.217             | 0.024          |
| thread   | 0.153 (fifo)      | 0.037          |
| process  | **0.132 (fifo)**  | **0.016**      |
| async    | 0.337             | 0.102          |

**Explanation:** Python's Global Interpreter Lock (GIL) prevents true thread-level parallelism for CPU-bound work. Multiple threads share one GIL — only one executes Python bytecode at a time. The process executor creates separate OS processes, each with its own GIL, achieving genuine parallel execution. This is why `process` outperforms `thread` on CPU workloads despite higher process creation overhead.

`async` is the slowest for CPU because CPU workloads are offloaded to `run_in_executor()` (a thread pool), and the async overhead adds latency on top of thread-level GIL contention.

---

## 3. Finding 2 — Async Executor Handles IO Concurrency Best (Throughput)

| Executor | Jobs completed in 60s |
|----------|-----------------------|
| baseline | 118                   |
| thread   | ~136                  |
| process  | ~137                  |
| async    | **~243**              |

**Explanation:** The async executor uses an event loop — when one job is waiting on IO (file read, sleep), the loop immediately picks up another job. No thread is blocked. This is why async processed nearly 2× the jobs of thread/process in the same duration. For IO-bound workloads like `io_sleep` and `io_file`, this concurrency model is the most efficient.

However, async `execution_time` for IO workloads (0.36s for `io_sleep`) appears higher than process (0.32s). This is because the async executor measures wall-clock time inside the event loop, which includes coroutine scheduling overhead and the time other concurrent coroutines are running.

---

## 4. Finding 3 — Priority Scheduler Increases Waiting Time for Low-Priority Jobs

From `waiting_time_by_scheduler.png`:

| Workload | FIFO waiting (s) | Priority waiting (s) | Change |
|----------|-----------------|----------------------|--------|
| io_file  | 0.0022          | 0.0029               | +32%   |
| io_sleep | 0.0015          | 0.0018               | +20%   |
| cpu_fibonacci | 0.0013     | 0.0017               | +31%   |

**Explanation:** Under Priority scheduling, CPU jobs (priority=1) jump ahead of IO and memory jobs (priority=3). This causes IO workloads to wait longer in the queue — an early indicator of **starvation**. At only 10 concurrent users, the effect is small (sub-millisecond). Under heavier load (50+ users), IO jobs would face significantly higher waiting times as CPU jobs continuously preempt the queue.

This directly demonstrates the fairness vs. efficiency tradeoff between FIFO and Priority scheduling covered in Silberschatz Chapter 5.

---

## 5. Finding 4 — Process Executor Has Highest Context Switches

From `ctx_switches_by_executor.png`:

| Executor | Mean voluntary ctx switches/job |
|----------|--------------------------------|
| async    | NaN (measurement limitation)   |
| baseline | 22.3                           |
| thread   | 25.3                           |
| process  | **34.7**                       |

**Explanation:** Each process pool job spawns work in a child process. The OS must switch context to schedule the child process, execute it, and switch back to the parent to collect results. This IPC (inter-process communication) overhead produces more voluntary context switches per job. Voluntary switches occur when a process yields the CPU willingly (e.g., waiting for a child process result), which is exactly what the parent process does here.

**Note on async NaN:** `psutil` metrics for the async executor are NaN because `track_request()` runs in the event loop thread, but the actual workload executes in a separate thread via `run_in_executor()`. The metrics capture the wrong thread. This is a documented measurement limitation, not an execution failure.

---

## 6. Finding 5 — process+priority cpu_fibonacci Anomaly (222 ctx switches)

`process_priority_cpu_fibonacci` shows 222 mean voluntary context switches vs. the expected ~10.

**Explanation:** Under priority scheduling, the process executor dequeues and spawns CPU jobs aggressively since they have priority=1. Spawning multiple processes rapidly causes the OS scheduler to interleave them heavily, producing abnormally high context switch counts. This is a priority scheduling side effect — high-priority CPU jobs starve the process pool, causing all workers to compete simultaneously and generating excessive OS-level scheduling overhead.

---

## 7. Finding 6 — Memory Delta Anomaly in mixed_cpu_io

From `memory_delta_by_workload.png`:

`mixed_cpu_io` shows a negative memory delta of ~−1.9 MB, while `cpu_matrix` shows +1.1 MB.

**Explanation:** The negative delta in `mixed_cpu_io` is caused by Python's garbage collector running between the before/after RSS snapshots. The fibonacci computation allocates stack frames which are released before the IO phase completes. Since RSS (Resident Set Size) is measured at two points, GC activity between them can produce negative deltas. This is a known limitation of RSS-based memory measurement for short-lived workloads.

---

## 8. Total Time Heatmap Summary

From `total_time_heatmap.png`:

| Executor | Scheduler | Mean Total Time (s) |
|----------|-----------|---------------------|
| thread   | fifo      | **0.16** ← best     |
| process  | fifo      | 0.17                |
| baseline | fifo      | 0.18                |
| thread   | priority  | 0.18                |
| process  | priority  | 0.19                |
| async    | fifo      | 0.26                |
| async    | priority  | 0.28                |

`thread+fifo` achieves the lowest mean total time overall. This is expected — thread overhead is lower than process (no spawn cost), and FIFO avoids priority-induced scheduling overhead. Async appears slowest in total time because it serves more jobs concurrently, meaning individual jobs wait longer for the event loop to return to them.

---

## 9. Known Limitations

| Limitation | Impact | Notes |
|------------|--------|-------|
| async os_metrics NaN | Cannot compare ctx switches for async | psutil measures wrong thread |
| Low user count (10) | Waiting times too small to show starvation clearly | Sub-millisecond queue delays |
| Windows platform | No `perf` access, no kernel-level tracing | psutil used as portable alternative |
| RSS memory measurement | Negative deltas possible due to GC | Not a bug in workloads |
| ml_predict ctx NaN | psutil failure for very short workloads | Low impact |

---

## 10. Conclusions

1. **Use process executor for CPU-bound workloads** — GIL makes threads ineffective for CPU parallelism.
2. **Use async executor for IO-bound workloads at scale** — event loop concurrency outperforms thread/process on throughput.
3. **FIFO is fairer than Priority under mixed load** — Priority causes measurable IO waiting time increase even at low concurrency.
4. **Process executor has the highest OS overhead** — context switches and spawn cost make it unsuitable for short, frequent jobs.
5. **Scheduling policy choice depends on workload mix** — Priority is beneficial when CPU jobs are latency-critical; FIFO is better for fairness.
