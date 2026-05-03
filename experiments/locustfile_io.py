# experiments/locustfile_io.py
"""Phase 3 — IO-bound workloads only."""
import random
from locust import HttpUser, task, between

class IOUser(HttpUser):
    wait_time = between(0.5, 1.5)

    @task(3)
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
            "params": {"size_kb": random.randint(100, 400), "iterations": 15},
            "priority": 3
        }, name="/run [io_file]")
