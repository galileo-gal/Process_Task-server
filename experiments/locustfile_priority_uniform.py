# experiments/locustfile_priority_uniform.py
"""Phase 5 — All jobs same priority (FIFO vs Priority should behave identically)."""
import random
from locust import HttpUser, task, between

class UniformPriorityUser(HttpUser):
    wait_time = between(1, 2)

    @task(2)
    def cpu_task(self):
        self.client.post("/run", json={
            "workload_type": "cpu_fibonacci",
            "params": {"n": random.randint(28, 32)},
            "priority": 2
        }, name="/run [uniform_cpu]")

    @task(2)
    def io_task(self):
        self.client.post("/run", json={
            "workload_type": "io_sleep",
            "params": {"ms": random.randint(100, 400)},
            "priority": 2
        }, name="/run [uniform_io]")

    @task(1)
    def memory_task(self):
        self.client.post("/run", json={
            "workload_type": "memory_numpy",
            "params": {"mb": random.randint(50, 150)},
            "priority": 2
        }, name="/run [uniform_memory]")
