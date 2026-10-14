"""
QA Persona v2 -- auto-generated tests
Service: cloned_repo
Suite:   performance
Source:  test_strategy/plans/cloned_repo__performance.json
Generated: 2024-07-12T17:01:21.051394Z
"""

import os
import time
from datetime import datetime, timezone
from locust import HttpUser, events, task, between

# --- Test Configuration ---
# These values are configurable via environment variables.
SERVICE_URL = os.environ.get("SERVICE_URL", "").strip()
P95_MS_THRESHOLD = float(os.environ.get("PERF_P95_MS_THRESHOLD", "500"))
FAIL_RATIO_THRESHOLD = float(os.environ.get("PERF_FAIL_RATIO_THRESHOLD", "0.01"))


class TargetUser(HttpUser):
    """Simulates a typical user interacting with the Timecard Portal API."""
    # The host to test against is read from the SERVICE_URL environment variable.
    host = SERVICE_URL
    # Users will wait between 0.5 and 1.5 seconds between tasks.
    wait_time = between(0.5, 1.5)

    @task(3)
    def sync_punches(self):
        """Simulates a client syncing a batch of offline punches.

        test_id: cloned_repo__performance__001
        target: POST /sync
        requirement_id: REQ-N-002
        ac_ids: REQ-N-002-AC-1
        """
        # The API prefix is /api/v1 as seen in app/main.py
        endpoint = "/api/v1/punches/sync"
        payload = {
            "punches": [
                {
                    "punch_type": "CLOCK_IN",
                    "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                    "client_vector": int(time.time())
                }
            ]
        }
        self.client.post(endpoint, json=payload, params={"user_id": "usr_employee_01"})

    @task(1)
    def get_health(self):
        """Hits the basic health check endpoint."""
        self.client.get("/health")

    @task(2)
    def get_current_timecard(self):
        """Fetches the current timecard for a user."""
        self.client.get("/api/v1/timecards/current", params={"user_id": "usr_employee_01"})


@events.test_stop.add_listener
def enforce_thresholds(environment, **kwargs):
    """Checks performance statistics against defined thresholds after the test run.

    This function is triggered when the Locust test is stopped. It checks the
    aggregate statistics (P95 response time and failure ratio) and sets the
    process exit code to 1 if thresholds are exceeded, causing the CI/CD
    pipeline to fail.
    """
    stats = environment.stats.total
    fail_ratio = stats.fail_ratio
    p95_ms = stats.get_response_time_percentile(0.95)

    print(f"\n--- Performance Thresholds ---")
    print(f"P95 Response Time: {p95_ms:.2f}ms (Threshold: {P95_MS_THRESHOLD}ms)")
    print(f"Failure Ratio: {fail_ratio:.2%} (Threshold: {FAIL_RATIO_THRESHOLD:.2%})")

    if fail_ratio > FAIL_RATIO_THRESHOLD:
        print("\n*** TEST FAILED: Failure ratio exceeded threshold. ***")
        environment.process_exit_code = 1

    if p95_ms and p95_ms >= P95_MS_THRESHOLD:
        print("\n*** TEST FAILED: P95 response time exceeded threshold. ***")
        environment.process_exit_code = 1

    if environment.process_exit_code == 0:
        print("\n--- TEST PASSED: All performance thresholds met. ---")
