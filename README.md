# **OS Concurrency Study – Adaptive Task Execution Server**

## 📌 Project Overview

This project is an **Operating Systems–focused concurrency study** that analyzes how different **execution models** and **scheduling policies** behave under diverse workloads.

Instead of treating concurrency as a black box, the project explicitly separates:

* **Scheduling policy** (FIFO vs Priority)
* **Execution mechanism** (threads, processes, async)
* **Workload characteristics** (CPU, IO, memory, mixed, ML)

The goal is to **measure, compare, and explain OS-level behavior** such as waiting time, throughput, CPU utilization, context switching, and fairness.

---

## 🎯 Objectives

* Compare **single-threaded, multi-threaded, multi-process, and async** servers
* Analyze **FIFO vs Priority scheduling** within the server
* Study the **GIL impact** on CPU-bound workloads
* Measure **OS-level metrics** using `psutil`
* Produce **reproducible experiments** with structured results

---

## 🧠 Key OS Concepts Covered

* Concurrency vs Parallelism
* Scheduling policies (FIFO, Priority)
* Waiting time, turnaround time, starvation
* Thread vs process overhead
* GIL effects in CPython
* Async IO vs blocking execution
* Context switches and CPU utilization

---

## 🏗️ High-Level Architecture

```
Client Request
     ↓
Server (/run endpoint)
     ↓
Scheduler (FIFO / Priority)
     ↓
Dispatcher
     ↓
Executor (Thread / Process / Async)
     ↓
Workload Execution
     ↓
Metrics Collection (psutil)
     ↓
Experiment Logs → Analysis → Report
```

---

## 📂 Project Structure (Simplified)

```
src/
├── core/          # Job abstraction
├── scheduler/     # FIFO & Priority scheduling policies
├── dispatch/      # Scheduler → Executor bridge
├── executors/     # Thread, Process, Async execution backends
├── servers/       # Flask (baseline/thread/process), FastAPI (async)
├── workloads/     # CPU, IO, Memory, Mixed, ML workloads
├── utils/         # Metrics, logging, experiment logging

experiments/
├── analysis/      # Summarization & plotting scripts

results/           # Experiment outputs (JSONL, CSV, plots)
docs/              # Architecture, API, experiments, results docs
config/            # Experiment & logging configuration
```

---

## ⚙️ Workloads Implemented

* **CPU-bound**: Fibonacci, matrix multiplication
* **IO-bound**: File operations, sleep simulation
* **Memory-bound**: Large array allocation & processing
* **Mixed**: CPU → IO and IO → CPU
* **ML (lightweight)**: Predict-only Linear Regression (model loaded once)

All workloads are **parameterized** to allow controlled scaling.

---

## 🧩 Scheduling Policies

* **FIFO**: Fair, simple baseline
* **Priority**: Task-based priority scheduling

  * CPU = High
  * ML = Medium
  * IO = Low

Metrics analyzed:

* Waiting time
* Tail latency (p95/p99)
* Starvation indicators
* Fairness (variation in waiting time)

---

## 📊 Metrics Collected

Per request:

* Latency (execution time)
* Waiting time (scheduler delay)
* CPU time (user/system)
* Memory usage (RSS delta)
* Context switch deltas

All raw data is stored as **JSONL** for reproducibility.

---

## 🧪 Experiments

* Load testing via **Locust**
* Controlled experiment matrix (users, workload types, scheduler, executor)
* Results summarized into CSV and plotted

See: `docs/experiments.md`

---

## 🖥️ Platform Notes

* Primary development: **Windows**
* OS-level analysis enhanced via **WSL2 (Ubuntu)**
* `psutil` used for profiling
* `perf` noted as future work due to WSL limitations

---

## 🚀 Setup (Quick)

```bash
git clone <repo-url>
cd Process_Task-server
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Run server:

```bash
python src/servers/flask_app.py
# or
uvicorn src.servers.fastapi_app:app
```

---

## 📘 Documentation

* `docs/architecture.md` – system design & flow
* `docs/api.md` – API contract
* `docs/experiments.md` – experiment execution
* `docs/results.md` – interpreting outputs
* `docs/README.md` – documentation index (start here for detailed docs)
---

## 📌 Status

**Phase 1: Active**

* Workloads ✔
* Scheduling ✔
* Baseline & threaded servers ✔
* Metrics & logging ✔

---

## 👨‍🏫 Academic Context

This project is designed as an **OS course project**, emphasizing **analysis and reasoning** over raw performance, and is structured to be **viva-defensible**.

---
