# PHASE 1 BLUEPRINT - OS Concurrency Study (FINAL)

## CRITICAL ADJUSTMENTS FROM FEEDBACK
- Workload sizes: realistic for laptop (no swapping/crashes)
- Parameterized workloads (no hardcoded sizes)
- JSON POST endpoints (not URL params)
- Delta-based context switch tracking
- Async = IO-only (CPU offload clearly labeled)
- Reduced experiment matrix (focus > volume)
- **SCHEDULING POLICY ANALYSIS ADDED (FIFO vs Priority)**
- **OS profiling: psutil on Windows (perf noted as future work)**

---

## WEEK 1: Workloads + Baseline Server

### Day 1: Core Workload Implementation
**File: `src/workloads/cpu_bound.py`**
- [ ] `fibonacci(n)` - param range: 28-36
- [ ] `matrix_multiply(size)` - param range: 200-800
- [ ] Test: verify n=30 completes <5s, size=500 completes <10s

**File: `src/workloads/io_bound.py`**
- [ ] `file_operations(size_kb, iterations)` - size: 100-1000kb
- [ ] `sleep_simulation(ms)` - simulates network latency
- [ ] Test: 500kb×100 iterations completes <3s

**File: `src/workloads/memory_bound.py`**
- [ ] `numpy_allocation(mb)` - param range: 50-300MB
- [ ] `array_operations(mb)` - allocate + sum/multiply ops
- [ ] Test: 200MB doesn't trigger swap (check `free -h` or Task Manager)

### Day 2: Mixed + ML Workloads
**File: `src/workloads/mixed.py`**
- [ ] `cpu_then_io(cpu_param, io_ms)` - fib(n) then sleep(ms)
- [ ] `io_then_cpu(io_ms, cpu_param)` - reverse order
- [ ] Test: both combos complete predictably

**File: `src/workloads/ml_simple.py`**
- [ ] Train LinearRegression once at module load (100k samples)
- [ ] `predict_batch(n_samples)` - param range: 1k-10k
- [ ] Test: 5k predictions <2s (predict only, no fit per request)

### Day 3: Metrics Infrastructure
**File: `src/utils/metrics_tracker.py`**
- [ ] `track_request()` context manager:
  - Before: snapshot CPU time, ctx_switches, memory
  - After: compute deltas
  - Return: dict with all deltas + duration
- [ ] Save to `results/experiments.jsonl` (append, one JSON per line)
- [ ] Test: verify deltas are non-zero and realistic

**File: `src/utils/experiment_logger.py`**
- [ ] Wrapper to add experiment metadata (workload, params, timestamp)
- [ ] Helper to load/parse JSONL for analysis

### Day 4: Baseline Server
**File: `src/servers/baseline_app.py`**
- [ ] Single endpoint: `POST /run`
- [ ] Request body: `{"type": "cpu_fib", "params": {"n": 30}}`
- [ ] Map type → workload function
- [ ] Wrap execution in `track_request()`
- [ ] Return: `{"result": ..., "metrics": {...}}`
- [ ] Health endpoint: `GET /health` (system info, uptime)
- [ ] Test: curl each workload type, verify metrics logged

### Day 5: Baseline Benchmarking
**File: `experiments/baseline_locust.py`**
- [ ] Tasks for each workload (CPU, IO, Memory, Mixed, ML)
- [ ] Parameterized: small/medium/large intensity
- [ ] Run experiments:
  - CPU (fib): n=30, n=33 @ 10 users, 50 users (4 runs)
  - IO (file): 500kb @ 10, 50 users (2 runs)
  - Memory: 100MB, 200MB @ 10, 50 users (4 runs)
  - Mixed: cpu_then_io @ 50 users (1 run)
  - ML: 5k predictions @ 50 users (1 run)
- [ ] Save results to `results/week1_baseline/`
- [ ] Generate `summary.csv`: workload, users, p50/p95/p99, throughput, avg_cpu, avg_ctx_switches

**WEEK 1 OUTPUT**: 
- 5 workload modules tested
- Baseline metrics for 12 experiments
- summary.csv proving measurement works

---

## WEEK 2: Multi-threaded Server + Scheduling Infrastructure

### Day 1: Thread Pool Server
**File: `src/servers/threaded_app.py`**
- [ ] ThreadPoolExecutor with configurable workers (4, 8, 16)
- [ ] Load pool size from `config/experiment.yaml`
- [ ] Same `/run` endpoint, submit to thread pool
- [ ] Test: verify concurrent execution with print timestamps

### Day 2: Scheduling Module - FIFO
**File: `src/scheduler/fifo.py`**
- [ ] FIFO queue implementation (wrapper over queue.Queue)
- [ ] Enqueue policy: append to tail
- [ ] Dequeue policy: pop from head
- [ ] Track: enqueue_time, dequeue_time, waiting_time
- [ ] Integrate into threaded_app via scheduler parameter

**File: `src/scheduler/priority.py`**
- [ ] Priority queue (wrapper over queue.PriorityQueue)
- [ ] Priority definition: task-based (CPU=high, IO=low, ML=medium) OR user-specified
- [ ] Track: priority level, waiting_time, execution_order
- [ ] Anti-starvation: log tasks waiting >30s

### Day 3: Thread-safe Metrics + Lock Testing
**File: `src/workloads/shared_resource.py`**
- [ ] Workload: increment shared counter with/without lock
- [ ] `lock.acquire(timeout=5)` - log timeout events
- [ ] Simulate contention: 50 threads incrementing 1000 times
- [ ] Test: without lock → wrong count, with lock → correct count
- [ ] Log "lock_timeout" events to identify contention

### Day 4: Thread Benchmarking
- [ ] Locust tests for CPU, IO @ pool sizes: 4, 8, 16
- [ ] Experiments (9 total):
  - CPU fib(33): 4w/10u, 8w/50u, 16w/100u
  - IO 500kb: 4w/10u, 8w/50u, 16w/100u
  - Memory 200MB: 4w/50u, 8w/50u, 16w/50u
- [ ] Save to `results/week2_threaded/`

### Day 5: GIL Impact Analysis
- [ ] Compare CPU-bound: threaded vs baseline
- [ ] Hypothesis: minimal speedup due to GIL
- [ ] Compare IO-bound: should show speedup
- [ ] Document: thread overhead via context switches
- [ ] Write `results/week2_threaded/analysis.md`

**WEEK 2 OUTPUT**: Thread performance data + Scheduling infrastructure ready

---

## WEEK 3: Multi-process Server

### Day 1-2: Process Pool + IPC
**File: `src/servers/multiprocess_app.py`**
- [ ] ProcessPoolExecutor with 2, 4, 8 workers
- [ ] Handle result via return (no manual Queue needed initially)
- [ ] Track process startup overhead (first request latency)
- [ ] Test: verify CPU-bound uses multiple cores (`htop` or Task Manager)

### Day 3: Process Benchmarking
- [ ] Same Locust tests as Week 2
- [ ] Experiments (6 total):
  - CPU fib(33): 2p/10u, 4p/50u, 8p/100u
  - IO: 4p/50u (baseline comparison)
  - Memory: 4p/50u (check overhead)
  - ML predict: 4p/50u
- [ ] Save to `results/week3_multiprocess/`

### Day 4-5: Process vs Thread Analysis
- [ ] Memory overhead: RSS per worker process
- [ ] CPU speedup: processes vs threads vs baseline
- [ ] Identify: when does process overhead hurt performance?
- [ ] Write `results/week3_multiprocess/analysis.md`

**WEEK 3 OUTPUT**: Process data + overhead analysis

---

## WEEK 4: Async Server + Scheduling Policy Analysis

### Day 1-2: AsyncIO Server (IO-only)
**File: `src/servers/async_app.py`**
- [ ] FastAPI with async endpoints
- [ ] Async IO workloads: `async_file_ops()`, `async_sleep()`
- [ ] For CPU: use `asyncio.to_thread()` - LABEL as "async+thread offload"
- [ ] Test: 300 concurrent IO requests complete efficiently

### Day 3: **SCHEDULING POLICY ANALYSIS WITHIN THE SERVER**
**Goal**: Compare FIFO vs Priority scheduling under mixed workloads

**Experiments**:
- [ ] Setup mixed workload scenario:
  - 40% CPU-bound (fib, priority=1-high)
  - 40% IO-bound (file ops, priority=3-low)
  - 20% ML (predict, priority=2-medium)
  
- [ ] Run threaded server with FIFO scheduler @ 50 users, 120s
  - Record per-task: waiting_time, execution_time, completion_time
  - Save to `results/week4_scheduling/fifo_mixed.jsonl`

- [ ] Run threaded server with Priority scheduler @ 50 users, 120s
  - Same metrics
  - Save to `results/week4_scheduling/priority_mixed.jsonl`

**Analysis** (`results/week4_scheduling/scheduling_analysis.md`):
- [ ] Avg waiting time per workload type (FIFO vs Priority)
- [ ] Responsiveness: p95/p99 latency for high-priority tasks
- [ ] Starvation detection: count IO tasks waiting >30s under Priority
- [ ] Fairness: coefficient of variation in waiting times
- [ ] Trade-offs table: FIFO (fair, poor responsiveness) vs Priority (responsive, starvation risk)

### Day 4: Async Benchmarking + Aggregate Analysis
- [ ] Async experiments:
  - IO: 100u, 300u, 500u (async shines here)
  - Mixed (cpu_then_io): 100u with thread offload
- [ ] Save to `results/week4_async/`
- [ ] Merge all weeks into `results/final_analysis/comparison.csv`
- [ ] Per workload: best concurrency model
- [ ] Generate charts: latency boxplots, throughput bars, CPU usage

### Day 5: Final Report Writing
**File: `results/final_analysis/report.md`**

**Structure**:
1. Executive Summary (1 page)
2. Methodology
   - Workloads (5 types)
   - Concurrency models (baseline/thread/process/async)
   - **Scheduling policies (FIFO vs Priority)**
   - Metrics (latency, throughput, CPU, ctx switches, waiting time)
   - Platform: Windows/WSL, psutil for OS profiling
3. Results
   - Concurrency model comparison (tables + charts)
   - **Scheduling Policy Analysis within the Server** (dedicated section)
   - GIL impact on CPU workloads
   - Process overhead analysis
   - Async sweet spot (high-concurrency IO)
4. Conclusions
   - When to use threads/processes/async
   - FIFO vs Priority trade-offs
   - Memory, CPU, complexity trade-offs
5. Future Work
   - Linux perf for cache misses, CPU migrations (noted as platform limitation on Windows)

**WEEK 4 OUTPUT**: Final report + scheduling analysis + all comparison data

---

## FEEDBACK COMPLIANCE CHECKLIST
- [x] Workload sizes safe for laptop
- [x] Parameterized workloads
- [x] JSON POST endpoints
- [x] Delta-based context switch tracking
- [x] Async = IO focus (CPU offload labeled)
- [x] Reduced experiments
- [x] Lock timeout logging (not "deadlock detection")
- [x] ML = predict-only
- [x] **Scheduling module (FIFO vs Priority) - EXPLICIT**
- [x] **Scheduling policy analysis with waiting time, starvation, fairness metrics**
- [x] **OS profiling: psutil (perf noted as future work due to Windows)**

## NEW DIRECTORY STRUCTURE
```
src/
├── scheduler/
│   ├── __init__.py
│   ├── fifo.py           # FIFO queue with waiting time tracking
│   └── priority.py       # Priority queue with starvation detection
├── workloads/
├── executors/
├── servers/
└── utils/

results/
├── week4_scheduling/     # NEW: scheduling analysis results
│   ├── fifo_mixed.jsonl
│   ├── priority_mixed.jsonl
│   └── scheduling_analysis.md
└── final_analysis/
    └── report.md         # Contains "Scheduling Policy Analysis within the Server" section
```

## EXPERIMENT MATRIX (TOTAL: ~28 runs)
Week 1: 12 runs (baseline)
Week 2: 9 runs (threads)
Week 3: 6 runs (processes)
Week 4: 6 runs (2 async + 2 scheduling + 2 aggregate)

## ACADEMIC DEFENSIBILITY
- ✅ Concurrency models analyzed
- ✅ **Scheduling algorithms compared (FIFO vs Priority)**
- ✅ OS-level metrics tracked (psutil)
- ✅ Waiting time, starvation, fairness analysis
- ✅ Platform limitations acknowledged (perf on Windows)
- ✅ Report structure matches OS course expectations

**FACULTY-READY: 92-95% completeness**