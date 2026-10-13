

def test_clock_in_and_clock_out_punch_capture(client):
    """
    [ARCH-2663-AC2] Employees can clock in and out, and the punches appear on their timecard.
    """
    # 1. Clock In
    resp_in = client.post("/api/v1/punches", json={
        "punch_type": "CLOCK_IN",
        "client_vector": 101,
        "offline_captured": False
    })
    assert resp_in.status_code == 201
    in_data = resp_in.json()
    assert in_data["status"] == "recorded"
    assert in_data["punch_type"] == "CLOCK_IN"
    assert "audit_hash" in in_data

    # Check status is clocked in
    resp_status = client.get("/api/v1/punches/status")
    assert resp_status.status_code == 200
    assert resp_status.json()["is_clocked_in"] is True

    # 2. Clock Out
    resp_out = client.post("/api/v1/punches", json={
        "punch_type": "CLOCK_OUT",
        "client_vector": 102,
        "offline_captured": False
    })
    assert resp_out.status_code == 201
    out_data = resp_out.json()
    assert out_data["punch_type"] == "CLOCK_OUT"


def test_offline_punch_batch_synchronization(client):
    """
    [ARCH-2663-AC3] The application indicates when it is in offline mode
    and successfully syncs when connectivity returns.
    """
    offline_batch = [
        {"punch_type": "CLOCK_IN", "timestamp": "2023-10-18 08:30:00", "client_vector": 1},
        {"punch_type": "CLOCK_OUT", "timestamp": "2023-10-18 12:30:00", "client_vector": 2},
        {"punch_type": "CLOCK_IN", "timestamp": "2023-10-18 13:00:00", "client_vector": 3},
        {"punch_type": "CLOCK_OUT", "timestamp": "2023-10-18 17:00:00", "client_vector": 4}
    ]

    resp = client.post("/api/v1/punches/sync", json={"punches": offline_batch})
    assert resp.status_code == 200
    data = resp.json()
    assert data["synced_count"] == 4
    assert data["status"] == "synchronized"
