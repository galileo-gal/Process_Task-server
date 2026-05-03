# experiments/locustfile_cpu.py
"""Phase 3 — CPU-bound workloads only."""
import random
from locust import HttpUser, task, between

class CPUUser(HttpUser):
    wait_time = between(1, 2)

    @task(3)
    def cpu_fibonacci(self):
        self.client.post("/run", json={
            "workload_type": "cpu_fibonacci",
            "params": {"n": random.randint(28, 33)},
            "priority": 1
        }, name="/run [cpu_fibonacci]")

    @task(2)
    def cpu_matrix(self):
        self.client.post("/run", json={
            "workload_type": "cpu_matrix",
            "params": {"size": random.randint(200, 500)},
            "priority": 1
        }, name="/run [cpu_matrix]")

    @task(1)
    def cpu_prime(self):
        self.client.post("/run", json={
            "workload_type": "cpu_prime",
            "params": {"limit": random.randint(10000, 60000)},
            "priority": 1
        }, name="/run [cpu_prime]")
