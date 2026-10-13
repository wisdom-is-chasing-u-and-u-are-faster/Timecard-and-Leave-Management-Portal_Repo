

def test_leave_balances_and_request_submission(client):
    """
    [ARCH-2663-AC4, ARCH-2663-AC5] Employees can view their leave balances and submit a leave request.
    """
    # 1. Fetch balances
    bal_resp = client.get("/api/v1/leave/balances")
    assert bal_resp.status_code == 200
    bal = bal_resp.json()
    assert bal["vacation_hours"] > 0
    assert bal["sick_hours"] > 0

    # 2. Submit leave request
    req_resp = client.post("/api/v1/leave/requests", json={
        "leave_type": "Vacation",
        "start_date": "2023-12-20",
        "end_date": "2023-12-24",
        "comments": "Winter holiday break"
    })
    assert req_resp.status_code == 201
    req_data = req_resp.json()
    assert req_data["status"] == "PENDING"
    assert req_data["leave_type"] == "Vacation"

    # 3. Verify in history
    my_resp = client.get("/api/v1/leave/requests/my")
    assert my_resp.status_code == 200
    my_requests = my_resp.json()["requests"]
    assert any(r["id"] == req_data["id"] for r in my_requests)
