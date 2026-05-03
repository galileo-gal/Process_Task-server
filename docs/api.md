# API Reference

**Base URLs:**
- Flask server: `http://localhost:5000`
- FastAPI server: `http://localhost:8000`

---

## POST /run

Submit a job for execution.

**Request body (JSON):**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `workload_type` | string | Yes | One of the workload keys below |
| `params` | object | Yes | Workload-specific parameters |
| `priority` | int | No | 1=high, 2=medium, 3=low. Default: 2 |

**Workload types and required params:**

| `workload_type` | Required params | Safe ranges |
|-----------------|----------------|-------------|
| `cpu_fibonacci` | `n: int` | 28–33 |
| `cpu_matrix` | `size: int` | 200–500 |
| `cpu_prime` | `limit: int` | 10000–60000 |
| `io_sleep` | `ms: int` | 100–500 |
| `io_file` | `size_kb: int`, `iterations: int` | 100–400, 10–50 |
| `memory_numpy` | `mb: int` | 50–200 |
| `memory_array` | `mb: int` | 50–200 |
| `memory_list` | `size: int` | 500000–2000000 |
| `mixed_cpu_io` | `cpu_param: int`, `io_ms: int` | 28–31, 100–300 |
| `mixed_io_cpu` | `io_ms: int`, `cpu_param: int` | 100–300, 28–31 |
| `ml_predict` | `n_samples: int` | 1000–5000 |

**Example request:**
```json
{
  "workload_type": "cpu_fibonacci",
  "params": {"n": 30},
  "priority": 1
}
```

**Response (200 OK):**
```json
{
  "job_id": "a1b2c3d4",
  "workload_type": "cpu_fibonacci",
  "params": {"n": 30},
  "priority": 1,
  "waiting_time": 0.0023,
  "execution_time": 0.312,
  "total_time": 0.3143,
  "error": null,
  "os_metrics": {
    "duration_s": 0.309,
    "cpu_user_delta_s": 0.297,
    "cpu_system_delta_s": 0.016,
    "ctx_voluntary_delta": 236,
    "ctx_involuntary_delta": 0,
    "memory_mb": 58.4,
    "memory_delta_mb": 0.33
  }
}
```

**Error responses:**

| Status | Meaning |
|--------|---------|
| 400 | Missing `workload_type` or unknown workload |
| 500 | Workload raised an exception |
| 504 | Job timed out (default: 30s) |

---

## GET /health

Liveness check.

**Response (200):**
```json
{"status": "ok", "executor": "thread", "scheduler": "fifo"}
```

---

## GET /stats

Current scheduler and executor queue depth.

**Response (200):**
```json
{
  "running": true,
  "scheduler": "fifo",
  "enqueued": 142,
  "dequeued": 139,
  "queue_depth": 3
}
```

For baseline mode: `{"executor": "baseline", "scheduler": "none"}`

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `EXECUTOR_TYPE` | `baseline` | `baseline` / `thread` / `process` |
| `SCHEDULER_TYPE` | `fifo` | `fifo` / `priority` |
| `MAX_WORKERS` | `4` | Thread/process pool size |
| `EXPERIMENT_ID` | timestamp | Prefix for result JSONL filename |
| `JOB_TIMEOUT` | `30` | Seconds before 504 response |
