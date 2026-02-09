
# System Architecture

## 1. Purpose and Scope

This project is designed as an **application-level Operating Systems concurrency study**.  
The architecture explicitly separates **scheduling policy** from **execution mechanism** to allow controlled observation and analysis of OS-level behavior such as waiting time, responsiveness, fairness, and overhead.

**In scope:**
- Application-level scheduling (FIFO vs Priority)
- Threads, processes, and async execution models
- Waiting time, latency, throughput, context switches
- GIL impact in CPython
- OS profiling using `psutil`

**Out of scope:**
- Kernel modification
- Custom OS schedulers
- Hardware-level microarchitectural tuning

This scope ensures the system remains **safe, reproducible, and academically appropriate** for an OS course project.

---

## 2. Architectural Overview

The system follows a **layered architecture** where each layer has a single, well-defined responsibility:

```

Client
↓
Server Layer
↓
Scheduler (Policy)
↓
Dispatcher (Policy → Mechanism Bridge)
↓
Executor (Mechanism)
↓
Workload Execution
↓
Metrics Collection & Logging

```


## 3. Core Architectural Layers

### 3.1 Server Layer

**Responsibility:**
- Accept client requests via a REST API
- Validate input and workload parameters
- Construct a Job abstraction
- Submit jobs to the scheduler

The server layer **does not decide execution order** and **does not execute workloads directly**.  
It acts as an entry point and orchestration layer.

Two server implementations exist:
- **Flask server**: baseline, threaded, and multiprocess modes
- **FastAPI server**: async IO-focused execution

---

### 3.2 Job Abstraction (Core Layer)

Each request is converted into a **Job object**, which encapsulates all information required for scheduling and execution.

A Job includes:
- Unique job identifier
- Workload type and parameters
- Priority (if applicable)
- Arrival and enqueue timestamps
- Sequence number for deterministic ordering

This abstraction enables:
- Precise waiting-time measurement
- Stable scheduling behavior
- Clean separation between request handling and execution

---

### 3.3 Scheduler Layer (Policy)

**Responsibility:**
- Decide *which job runs next*
- Maintain ordering according to a scheduling policy
- Track enqueue and dequeue times

The scheduler **never executes jobs**.

Implemented policies:
- **FIFO**: First-In–First-Out (baseline fairness)
- **Priority**: Task-priority–based ordering with starvation detection

By isolating scheduling here, the system can compare policies **without changing execution logic**.

---

### 3.4 Dispatcher Layer (Policy → Mechanism Bridge)

The dispatcher is the **most critical architectural component**.

**Responsibility:**
- Pull jobs from the scheduler
- Measure waiting time
- Submit jobs to the selected executor

This layer ensures that:
- Scheduling decisions are respected
- Waiting time is measured *before* execution
- Executors remain policy-agnostic

Without this layer, scheduling analysis would be superficial.

---

### 3.5 Executor Layer (Mechanism)

Executors define **how** jobs are executed, not **which** job runs next.

Supported executors:
- **Thread Pool Executor**
  - Concurrency via threads
  - Subject to CPython GIL
- **Process Pool Executor**
  - True parallelism
  - Higher memory and IPC overhead
- **Async Executor**
  - Event-loop–based, non-blocking IO
  - CPU tasks explicitly offloaded

Executors are interchangeable and configured externally.

---

### 3.6 Workload Layer

Workloads represent **pure computation or IO logic**.

Characteristics:
- No server logic
- No scheduling logic
- No metrics logic
- Fully parameterized

Workload categories:
- CPU-bound
- IO-bound
- Memory-bound
- Mixed (CPU + IO)
- Lightweight ML (predict-only)

This isolation ensures workload behavior is the **independent variable** in experiments.

---

### 3.7 Metrics and Logging Layer

Metrics are collected using `psutil` at execution boundaries.

Collected data includes:
- Execution latency
- Scheduler waiting time
- CPU time (user/system)
- Memory usage deltas
- Context switch deltas

All metrics are logged in **JSONL format** for reproducibility and post-processing.

---

## 4. Execution Flow (Step-by-Step)

1. Client sends a `/run` request
2. Server validates input and creates a Job
3. Job is submitted to the scheduler
4. Scheduler enqueues job according to policy
5. Dispatcher dequeues the next job
6. Waiting time is computed
7. Job is submitted to the executor
8. Workload executes
9. Metrics are collected
10. Results and metrics are logged

This flow ensures that **scheduling delay and execution time are independently observable**.

---

## 5. Scheduling vs Execution: Explicit Separation

A central design goal is to distinguish:

- **Scheduling (policy):**  
  *Which job should run next?*

- **Execution (mechanism):**  
  *How is the job executed?*

This mirrors classical OS design principles and allows:
- Fair comparison of FIFO vs Priority
- Consistent executor behavior across policies
- Clean analysis of waiting time and starvation

---

## 6. Concurrency Models in Context

- **Threads:** efficient for IO, limited CPU scalability due to GIL
- **Processes:** CPU scalability with higher overhead
- **Async:** best for high-concurrency IO workloads

The architecture allows these models to be compared **under identical scheduling and workload conditions**.

---

## 7. Design Rationale

Key architectural decisions:
- Decoupling policy from mechanism for clarity
- Dispatcher layer to make scheduling measurable
- Parameterized workloads for controlled experiments
- JSONL logging for reproducibility
- Configuration-driven experimentation

These choices prioritize **observability, correctness, and academic defensibility** over raw performance.

---

## 8. Platform Considerations

- Primary development on Windows
- OS-level analysis enhanced using WSL2 (Linux kernel)
- `psutil` used for portable profiling
- Linux `perf` noted as future work due to virtualization limits

Platform limitations are explicitly documented and acknowledged.

---

## 9. Summary

This architecture enables a structured and defensible study of OS-level concurrency by:
- Making scheduling explicit
- Isolating execution mechanisms
- Enforcing clean abstraction boundaries
- Supporting reproducible experimentation

The system is intentionally engineered for **analysis and explanation**, not just execution.
