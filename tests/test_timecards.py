from app.services.flsa_engine import FLSAEngine


def test_flsa_engine_daily_and_weekly_overtime_math():
    """
    [ARCH-2663-AC4] Validates FLSA daily (>8h), double-time (>12h), and weekly (>40h) computations.
    """
    # 1. Standard 8h day
    res_8h = FLSAEngine.calculate_daily_distribution(8.0)
    assert res_8h["regular"] == 8.0
    assert res_8h["overtime"] == 0.0
    assert res_8h["double_time"] == 0.0

    # 2. 10h day (2h daily overtime)
    res_10h = FLSAEngine.calculate_daily_distribution(10.0)
    assert res_10h["regular"] == 8.0
    assert res_10h["overtime"] == 2.0
    assert res_10h["double_time"] == 0.0

    # 3. 14h day (8h reg + 4h OT + 2h double time)
    res_14h = FLSAEngine.calculate_daily_distribution(14.0)
    assert res_14h["regular"] == 8.0
    assert res_14h["overtime"] == 4.0
    assert res_14h["double_time"] == 2.0

    # 4. Weekly aggregate calculation
    week_hours = [8.08, 7.97, 8.08, 8.00, 8.00]
    summary = FLSAEngine.calculate_pay_period_summary(week_hours, hourly_rate=25.0)
    assert summary["total_hours"] == 40.13
    assert summary["regular_hours"] == 40.0
    assert summary["overtime_hours"] == 0.13
    assert summary["gross_pay_estimate"] > 1000.0


def test_current_timecard_and_submission(client):
    """
    [ARCH-2663-AC4] Employees can view their timecard and submit for approval.
    """
    resp = client.get("/api/v1/timecards/current")
    assert resp.status_code == 200
    tc = resp.json()
    assert tc["total_hours"] >= 40.0
    assert len(tc["days"]) >= 5

    # Submit timecard
    submit_resp = client.post("/api/v1/timecards/submit", json={"timecard_id": tc["timecard_id"]})
    assert submit_resp.status_code == 200
    assert submit_resp.json()["status"] == "SUBMITTED"
