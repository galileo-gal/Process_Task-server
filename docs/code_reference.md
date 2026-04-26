<!-- AUTO-GENERATED FILE. DO NOT EDIT MANUALLY -->
<!-- Generated: 2026-04-26 23:34:03 | Commit: 952e537 -->

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

### `src\core\registry.py`
> Workload registry — maps workload_type strings to actual function calls.

**Functions:**
- `run_workload(workload_type, params)` → `Any` – Execute a workload by name. Top-level so ProcessPoolExecutor can pickle it.

---
## Layer: `scheduler/`

### `src\scheduler\fifo.py`

**Class: `FIFOScheduler`** – First-In First-Out scheduler. Arrival order is preserved strictly.
- `empty()` → `bool` – Returns self._queue.empty()
- `get(timeout=None)` → `Optional[Job]` – Dequeue the next job. Calls job.mark_dequeued() before returning.
- `put(job)` → `None` – Enqueue a job. Calls job.mark_enqueued() before inserting.
- `qsize()` → `int` – Returns self._queue.qsize()
- `stats()` → `dict` – Returns {'scheduler': 'fifo', 'enqueued': self._enqueued_count, 'deq
- `task_done()` → `None` – Signal that a previously dequeued job has been processed.

### `src\scheduler\priority.py`

**Class: `PriorityScheduler`** – Priority-based scheduler. Lower priority integer = higher urgency.
- `empty()` → `bool` – Returns len(self._heap) == 0
- `get(timeout=None)` → `Optional[Job]` – Dequeue the highest-priority job. Calls job.mark_dequeued() before returning.
- `put(job)` → `None` – Enqueue a job. Calls job.mark_enqueued() before inserting.
- `qsize()` → `int` – Returns len(self._heap)
- `stats()` → `dict` – Returns {'scheduler': 'priority', 'enqueued': self._enqueued_count, 

---
## Layer: `dispatch/`

### `src\dispatch\dispatcher.py`

**Class: `Dispatcher`** – Policy-to-mechanism bridge.
- `start()` → `None` – Start the background dispatch loop.
- `stats()` → `dict` – Returns {'running': self._running, **self._scheduler.stats()}
- `stop()` → `None` – Signal the dispatch loop to stop after the current job finishes.
- `submit(job)` → `None` – Enqueue a job into the scheduler. Called by the server layer.

---
## Layer: `executors/`

### `src\executors\async_executor.py`
> Async Executor.

**Class: `AsyncExecutor`** – Runs an asyncio event loop in a background thread.
- `execute(job)` → `None` – Submit job to the event loop. Non-blocking — returns immediately.
- `shutdown()` → `None` – Executes shutdown operation
- `stats()` → `dict` – Returns {'executor': 'async', 'loop_running': self._loop.is_running(

### `src\executors\process_pool.py`
> Process Pool Executor.

**Class: `ProcessPoolExecutor`** – Wraps concurrent.futures.ProcessPoolExecutor with Job lifecycle management.
- `execute(job)` → `None` – Submit job to process pool. Non-blocking — returns immediately.
- `shutdown(wait=True)` → `None` – Executes shutdown operation
- `stats()` → `dict` – Returns {'executor': 'process_pool', 'max_workers': self._max_worker

### `src\executors\thread_pool.py`
> Thread Pool Executor.

**Class: `ThreadPoolExecutor`** – Wraps concurrent.futures.ThreadPoolExecutor with Job lifecycle management.
- `execute(job)` → `None` – Submit job to thread pool. Non-blocking — returns immediately.
- `shutdown(wait=True)` → `None` – Executes shutdown operation
- `stats()` → `dict` – Returns {'executor': 'thread_pool', 'max_workers': self._max_workers

---
## Layer: `servers/`

### `src\servers\fastapi_app.py`
> FastAPI server — async IO executor experiments.

**Class: `RunRequest`** – Executes RunRequest operation

**Functions:**
- `async health()` → `Any` – Returns {'status': 'ok', 'executor': 'async', 'scheduler': SCHEDULER
- `async lifespan(app)` → `Any` – Executes lifespan operation
- `async run_job(req)` → `Any` – Sets self.on_complete on the job instance
- `async stats()` → `Any` – Returns {'status': 'not started'}

### `src\servers\flask_app.py`
> Flask server — baseline, threaded, and multiprocess executor experiments.

**Functions:**
- `health()` → `Any` – Returns (jsonify({'status': 'ok', 'executor': EXECUTOR_TYPE, 'schedu
- `run_job()` → `Any` – Sets self.on_complete on the job instance
- `stats()` → `Any` – Returns (jsonify({'executor': 'baseline', 'scheduler': 'none'}), 200

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
- `file_operations(size_kb, iterations=100)` → `int` – File read/write operations. size_kb: 100-300, iterations: 10-50.
- `sleep_simulation(ms)` → `int` – Simulate network latency. Param range: 100-500ms.

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

### `src\utils\experiment_logger.py`
> Experiment logger — writes completed Job results to a JSONL file.

**Class: `ExperimentLogger`** – Sets self._path on the job instance
- `close()` → `None` – Executes close operation
- `log(job)` → `None` – Append one job record to the JSONL file. Thread-safe.
- `path()` → `str` – Returns self._path

### `src\utils\logger.py`

**Functions:**
- `async_log_execution(func)` → `Any` – Decorator that logs async execution time and errors.
- `log_execution(func)` → `Any` – Decorator that logs execution time and errors.

### `src\utils\metrics.py`

**Functions:**
- `track_request()` → `Any` – Track OS-level metrics with delta computation.
