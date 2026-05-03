# experiments/locustfile_memory.py
"""Phase 3 — Memory-bound workloads only."""
import random
from locust import HttpUser, task, between

class MemoryUser(HttpUser):
    wait_time = between(1, 2)

    @task(2)
    def memory_numpy(self):
        self.client.post("/run", json={
            "workload_type": "memory_numpy",
            "params": {"mb": random.randint(50, 200)},
            "priority": 2
        }, name="/run [memory_numpy]")

    @task(2)
    def memory_list(self):
        self.client.post("/run", json={
            "workload_type": "memory_list",
            "params": {"size": random.randint(500000, 2000000)},
            "priority": 2
        }, name="/run [memory_list]")

    @task(1)
    def mixed_cpu_io(self):
        self.client.post("/run", json={
            "workload_type": "mixed_cpu_io",
            "params": {"cpu_param": random.randint(28, 31), "io_ms": 200},
            "priority": 2
        }, name="/run [mixed_cpu_io]")
