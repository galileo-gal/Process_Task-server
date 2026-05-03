# experiments/locustfile_priority_bimodal.py
"""Phase 5 — Bimodal: half priority=1 (high CPU), half priority=3 (low IO).
Maximises starvation potential under Priority scheduler."""
import random
from locust import HttpUser, task, between

class BimodalPriorityUser(HttpUser):
    wait_time = between(1, 2)

    @task(3)
    def high_priority_cpu(self):
        self.client.post("/run", json={
            "workload_type": "cpu_fibonacci",
            "params": {"n": random.randint(28, 33)},
            "priority": 1
        }, name="/run [high_cpu]")

    @task(3)
    def low_priority_io(self):
        self.client.post("/run", json={
            "workload_type": "io_sleep",
            "params": {"ms": random.randint(200, 600)},
            "priority": 3
        }, name="/run [low_io]")
