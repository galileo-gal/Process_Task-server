<!-- AUTO-GENERATED FILE. DO NOT EDIT MANUALLY -->
<!-- Generated: 2026-02-13 11:59:52 | Commit: 645b906 -->

# Code Reference – Process_Task-server

**Grouped by architecture layer. Regenerate:** `python scripts/generate_code_reference.py`

---
## Layer: `core/`

### `src\core\job.py`

**Class: `Job`** – Job abstraction for workload execution with scheduling metadata.
- `mark_completed(result=None, error=None)` → `Any` – Sets self.completed_at on the job instance
- `mark_dequeued()` → `Any` – Sets self.dequeued_at on the job instance
- `mark_enqueued()` → `Any` – Sets self.enqueued_at on the job instance
- `mark_started()` → `Any` – Sets self.started_at on the job instance
- `to_dict()` → `Dict[str, Any]` – Serializes job to dict for logging/JSONL output.

---
## Layer: `workloads/`

### `src\workloads\cpu_bound.py`

**Functions:**
- `fibonacci(n)` → `int` – Recursive fibonacci. Param range: 28-36 for laptop safety.
- `matrix_multiply(size)` → `float` – Matrix multiplication. Param range: 200-800 for laptop safety.
- `prime_check(limit)` → `int` – Count primes up to limit. Param range: 10000-100000.

### `src\workloads\io_bound.py`

**Functions:**
- `async async_file_operations(size_kb, iterations=100)` → `int` – Async file operations using aiofiles.
- `async async_sleep(ms)` → `int` – Async sleep simulation.
- `file_operations(size_kb, iterations=100)` → `int` – File read/write operations. size_kb: 100-1000, iterations: 10-100.
- `sleep_simulation(ms)` → `int` – Simulate network latency. Param range: 100-2000ms.

### `src\workloads\memory_bound.py`

**Functions:**
- `array_operations(mb)` → `float` – Array allocation + operations. Param range: 50-300MB.
- `list_processing(size=2000000)` → `int` – Process large Python list. Max 3M elements for safety.
- `numpy_allocation(mb)` → `float` – Allocate numpy array. Param range: 50-300MB.

### `src\workloads\mixed.py`

**Functions:**
- `cpu_then_io(cpu_param, io_ms)` → `tuple` – Execute CPU workload followed by IO. cpu_param: fib(n), io_ms: sleep duration.
- `io_then_cpu(io_ms, cpu_param)` → `tuple` – Execute IO workload followed by CPU.

### `src\workloads\ml_simple.py`

**Functions:**
- `predict_batch(n_samples)` → `float` – Predict only (no training). Param range: 1000-10000 samples.

---
## Layer: `utils/`

### `src\utils\logger.py`

**Functions:**
- `async async_log_execution(func)` → `Any` – Decorator that logs async execution time and errors.Decorator that logs async execution time and errors.
- `log_execution(func)` → `Any` – Decorator that logs execution time and errors.

### `src\utils\metrics.py`

**Functions:**
- `track_request()` → `Any` – Track OS-level metrics with delta computation.
