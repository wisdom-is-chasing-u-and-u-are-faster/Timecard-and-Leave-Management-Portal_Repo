"""
QA Persona v2 -- auto-generated tests
Service: cloned_repo
Suite:   performance
Source:  test_strategy/plans/cloned_repo__performance.json
Generated: 2024-05-24T15:04:47.585149Z
"""
import os
import time
from datetime import datetime, timezone
from locust import HttpUser, events, task, between

SERVICE_URL = os.environ.get("SERVICE_URL", "").strip()
P95_MS_THRESHOLD = float(os.environ.get("PERF_P95_MS_THRESHOLD", "500"))
FAIL_RATIO_THRESHOLD = float(os.environ.get("PERF_FAIL_RATIO_THRESHOLD", "0.01"))

class TargetUser(HttpUser):
    """
    Simulates a user interacting with the timecard portal API.
    The host is configured via the SERVICE_URL environment variable.
    """
    host = SERVICE_URL
    wait_time = between(0.5, 1.5)

    @task(3)
    def get_health(self):
        """Task to hit the health check endpoint as a baseline.

        test_id: n/a (baseline task)
        """
        self.client.get("/health", name="/health")

    @task(1)
    def post_sync(self):
        """Task to simulate batch synchronization of offline punches.

        test_id: cloned_repo__performance__001
        target: POST /sync
        ac_ids: REQ-N-002-AC-1
        """
        now = datetime.now(timezone.utc)
        payload = {
            "punches": [
                {
                    "punch_type": "CLOCK_IN",
                    "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                    "client_vector": int(time.time())
                }
            ]
        }
        # The router is at /api/v1/punches and the endpoint is /sync
        self.client.post("/api/v1/punches/sync", json=payload, name="/api/v1/punches/sync")

@events.test_stop.add_listener
def enforce_thresholds(environment, **kwargs):
    """
    Checks if performance thresholds were met and sets the process exit code to 1 on failure,
    allowing CI/CD pipelines to detect the performance regression.
    """
    if not environment.stats.total.num_requests:
        print("No requests were made, skipping threshold checks.")
        return

    stats = environment.stats.total
    fail_ratio = stats.fail_ratio
    p95_ms = stats.get_response_time_percentile(0.95)

    print(f"\n--- Performance Thresholds ---")
    print(f"Total requests: {stats.num_requests}")
    print(f"Failure ratio: {fail_ratio:.4f} (Threshold: {FAIL_RATIO_THRESHOLD})")
    if p95_ms is not None:
        print(f"P95 response time: {p95_ms:.2f}ms (Threshold: {P95_MS_THRESHOLD}ms)")
    else:
        print("P95 response time: N/A (not enough data points)")
    print("----------------------------\n")

    if fail_ratio > FAIL_RATIO_THRESHOLD:
        print(f"*** Test failed: Failure ratio {fail_ratio:.4f} exceeded threshold {FAIL_RATIO_THRESHOLD}")
        environment.process_exit_code = 1

    if p95_ms and p95_ms >= P95_MS_THRESHOLD:
        print(f"*** Test failed: P95 response time {p95_ms:.2f}ms exceeded threshold {P95_MS_THRESHOLD}ms")
        environment.process_exit_code = 1

    if environment.process_exit_code == 0:
        print("+++ Test passed: All performance thresholds met.")
