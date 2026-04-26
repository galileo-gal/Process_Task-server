# experiments/locustfile.py
"""
Locust load test for OS Concurrency Study.

Run against Flask (baseline/thread/process):
    locust -f experiments/locustfile.py --host=http://localhost:5000

Run against FastAPI (async):
    locust -f experiments/locustfile.py --host=http://localhost:8000

Headless (scripted):
    locust -f experiments/locustfile.py --headless --host=http://localhost:5000
           --users 10 --spawn-rate 2 --run-time 60s
"""
import random
from locust import HttpUser, task, between


class WorkloadUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def cpu_fibonacci(self):
        self.client.post("/run", json={
            "workload_type": "cpu_fibonacci",
            "params": {"n": random.randint(28, 32)},
            "priority": 1
        }, name="/run [cpu_fibonacci]")

    @task(2)
    def cpu_matrix(self):
        self.client.post("/run", json={
            "workload_type": "cpu_matrix",
            "params": {"size": random.randint(200, 400)},
            "priority": 1
        }, name="/run [cpu_matrix]")

    @task(4)
    def io_sleep(self):
        self.client.post("/run", json={
            "workload_type": "io_sleep",
            "params": {"ms": random.randint(100, 500)},
            "priority": 3
        }, name="/run [io_sleep]")

    @task(2)
    def io_file(self):
        self.client.post("/run", json={
            "workload_type": "io_file",
            "params": {"size_kb": random.randint(100, 300), "iterations": 10},
            "priority": 3
        }, name="/run [io_file]")

    @task(2)
    def memory_numpy(self):
        self.client.post("/run", json={
            "workload_type": "memory_numpy",
            "params": {"mb": random.randint(50, 150)},
            "priority": 2
        }, name="/run [memory_numpy]")

    @task(1)
    def memory_list(self):
        self.client.post("/run", json={
            "workload_type": "memory_list",
            "params": {"size": random.randint(500000, 1500000)},
            "priority": 2
        }, name="/run [memory_list]")

    @task(2)
    def mixed_cpu_io(self):
        self.client.post("/run", json={
            "workload_type": "mixed_cpu_io",
            "params": {"cpu_param": random.randint(28, 30), "io_ms": 200},
            "priority": 2
        }, name="/run [mixed_cpu_io]")

    @task(2)
    def ml_predict(self):
        self.client.post("/run", json={
            "workload_type": "ml_predict",
            "params": {"n_samples": random.randint(1000, 5000)},
            "priority": 2
        }, name="/run [ml_predict]")
