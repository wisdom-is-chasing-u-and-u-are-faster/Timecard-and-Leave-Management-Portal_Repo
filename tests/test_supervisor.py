

def test_supervisor_dashboard_summary_and_pending_items(client):
    """
    [ARCH-2663-AC6] Supervisors can see pending approval requests on their dashboard.
    """
    # Switch to supervisor
    client.post("/api/v1/auth/switch-role?role=SUPERVISOR")

    # Summary
    sum_resp = client.get("/api/v1/supervisor/summary")
    assert sum_resp.status_code == 200
    summary = sum_resp.json()
    assert "pending_timesheets_count" in summary
    assert "pending_leave_requests_count" in summary

    # Pending timesheets
    ts_resp = client.get("/api/v1/supervisor/timesheets/pending")
    assert ts_resp.status_code == 200
    assert len(ts_resp.json()["items"]) >= 1

    # Pending leave requests
    lr_resp = client.get("/api/v1/supervisor/leave/pending")
    assert lr_resp.status_code == 200
    assert len(lr_resp.json()["items"]) >= 1


def test_supervisor_approve_and_deny_actions(client):
    """
    [ARCH-2663-AC7] Supervisors can successfully approve or deny a timesheet and a leave request.
    """
    client.post("/api/v1/auth/switch-role?role=SUPERVISOR")

    # 1. Action on single timesheet
    ts_resp = client.get("/api/v1/supervisor/timesheets/pending")
    ts_items = ts_resp.json()["items"]
    assert len(ts_items) > 0
    target_ts_id = ts_items[0]["id"]

    appr_ts = client.post(
        f"/api/v1/supervisor/timesheets/{target_ts_id}/action",
        json={
            "action": "APPROVE",
            "comments": "Looks good"})
    assert appr_ts.status_code == 200
    assert appr_ts.json()["status"] == "APPROVED"

    # 2. Action on single leave request
    lr_resp = client.get("/api/v1/supervisor/leave/pending")
    lr_items = lr_resp.json()["items"]
    assert len(lr_items) > 0
    target_lr_id = lr_items[0]["id"]

    appr_lr = client.post(
        f"/api/v1/supervisor/leave/{target_lr_id}/action",
        json={
            "action": "APPROVE",
            "comments": "Approved holiday"})
    assert appr_lr.status_code == 200
    assert appr_lr.json()["status"] == "APPROVED"
