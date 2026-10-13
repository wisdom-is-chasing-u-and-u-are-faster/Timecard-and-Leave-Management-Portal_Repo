

def test_full_stack_cross_tier_e2e_workflow(client):
    """
    [ARCH-2663-AC1..AC7] End-to-end integration test validating the complete user journey:
    1. Employee SSO login
    2. Clock in & Clock out
    3. View timecard & submit
    4. View leave balances & submit leave request
    5. Supervisor reviews pending dashboard
    6. Supervisor approves timesheet & leave request
    7. Cryptographic SOX audit ledger integrity check
    """
    # 1. Login
    login = client.post("/api/v1/auth/login", json={"email": "erin.employee@enterprise.com", "role": "EMPLOYEE"}).json()
    token = login["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Punches
    p1 = client.post("/api/v1/punches", headers=headers, json={"punch_type": "CLOCK_IN"}).json()
    assert p1["status"] == "recorded"

    status = client.get("/api/v1/punches/status", headers=headers).json()
    assert status["is_clocked_in"] is True

    p2 = client.post("/api/v1/punches", headers=headers, json={"punch_type": "CLOCK_OUT"}).json()
    assert p2["status"] == "recorded"

    # 3. Timecard
    tc = client.get("/api/v1/timecards/current", headers=headers).json()
    assert tc["total_hours"] >= 0

    sub = client.post("/api/v1/timecards/submit", headers=headers, json={"timecard_id": tc["timecard_id"]}).json()
    assert sub["status"] == "SUBMITTED"

    # 4. Leave
    lr = client.post("/api/v1/leave/requests", headers=headers, json={
        "leave_type": "Vacation",
        "start_date": "2023-11-20",
        "end_date": "2023-11-24"
    }).json()
    assert lr["status"] == "PENDING"

    # 5. Supervisor Login & Review
    sup_login = client.post("/api/v1/auth/login", json={"role": "SUPERVISOR"}).json()
    sup_headers = {"Authorization": f"Bearer {sup_login['token']}"}

    summary = client.get("/api/v1/supervisor/summary", headers=sup_headers).json()
    assert summary["pending_timesheets_count"] >= 1
    assert summary["pending_leave_requests_count"] >= 1

    # 6. Supervisor Approvals
    act_tc = client.post(
        f"/api/v1/supervisor/timesheets/{tc['timecard_id']}/action",
        headers=sup_headers,
        json={
            "action": "APPROVE"}).json()
    assert act_tc["status"] == "APPROVED"

    act_lr = client.post(
        f"/api/v1/supervisor/leave/{lr['id']}/action",
        headers=sup_headers,
        json={
            "action": "APPROVE"}).json()
    assert act_lr["status"] == "APPROVED"

    # 7. Audit Ledger verification
    ledger = client.get("/api/v1/audit/ledger").json()
    assert ledger["total_blocks"] >= 5
    assert ledger["ledger_valid"] is True


def test_static_routes_and_health(client):
    """Verifies /health and static frontend HTML routes return 200 OK."""
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json() == {"status": "ok"}

    index = client.get("/")
    assert index.status_code == 200

    dash = client.get("/pages/employee_dashboard.html")
    assert dash.status_code == 200

    timecard = client.get("/pages/my_timecard.html")
    assert timecard.status_code == 200

    leave = client.get("/pages/my_leave.html")
    assert leave.status_code == 200

    sup_dash = client.get("/pages/supervisor_dashboard.html")
    assert sup_dash.status_code == 200

    approvals = client.get("/pages/team_approvals.html")
    assert approvals.status_code == 200
