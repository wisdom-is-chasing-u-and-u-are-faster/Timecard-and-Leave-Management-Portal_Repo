import sqlite3
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from app.db.session import get_db
from app.models.timecard import (
    DaySummary,
    PunchItem,
    TimecardResponse,
    TimecardSubmitRequest,
    TimecardSubmitResponse,
)
from app.services.audit_service import append_audit_event
from app.services.flsa_engine import calculate_pay_period_flsa

router = APIRouter(prefix="/timecards", tags=["Timecards & FLSA Computation"])


@router.get("/current", response_model=TimecardResponse)
def get_current_timecard(
    user_id: str = Query("usr_employee_01"),
    db: sqlite3.Connection = Depends(get_db)
):
    """Get active pay period timecard with daily entries and FLSA overtime."""
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT t.*, u.name as employee_name, u.hourly_rate
        FROM timecards t
        JOIN users u ON t.user_id = u.id
        WHERE t.user_id = ?
        ORDER BY t.pay_period_start DESC LIMIT 1
        """,
        (user_id,)
    )
    tc_row = cursor.fetchone()

    if not tc_row:
        # Default active pay period
        tc_id = "tc_current_01"
        emp_name = "Erin Employee"
        hourly_rate = 28.50
        pay_period = "Oct 16 - Oct 31, 2023"
        status = "DRAFT"
    else:
        tc_id = tc_row["id"]
        emp_name = tc_row["employee_name"]
        hourly_rate = tc_row["hourly_rate"]
        pay_period = f"{tc_row['pay_period_start']} - {tc_row['pay_period_end']}"
        status = tc_row["status"]

    # Retrieve daily entries
    cursor.execute("SELECT * FROM timecard_entries WHERE timecard_id = ?", (tc_id,))
    entries = cursor.fetchall()

    days: list[DaySummary] = []
    daily_hours: list[float] = []

    if entries:
        for e in entries:
            punches = []
            if e["punch_in_1"]:
                punches.append(PunchItem(type="Clock In", time=e["punch_in_1"]))
            if e["punch_out_1"]:
                punches.append(PunchItem(type="Clock Out", time=e["punch_out_1"]))
            if e["punch_in_2"]:
                punches.append(PunchItem(type="Clock In", time=e["punch_in_2"]))
            if e["punch_out_2"]:
                punches.append(PunchItem(type="Clock Out", time=e["punch_out_2"]))

            days.append(DaySummary(
                date=e["work_date"],
                punches=punches,
                hours=e["hours"],
                regular_hours=e["regular_hours"],
                overtime_hours=e["overtime_hours"],
                double_time_hours=e["double_time_hours"],
                notes=e["notes"]
            ))
            daily_hours.append(e["hours"])
    else:
        # Standard default workweek matching UI preview
        default_days = [
            ("Mon, Oct 16", ["08:57 AM", "01:00 PM", "01:30 PM", "05:32 PM"], 8.08, None),
            ("Tue, Oct 17", ["09:01 AM", "01:05 PM", "01:33 PM", "05:29 PM"], 7.97, None),
            ("Wed, Oct 18", ["08:55 AM", "12:30 PM", "01:00 PM", "05:30 PM"], 8.08, None),
            ("Thu, Oct 19", ["09:05 AM", "01:00 PM", "01:30 PM", "05:35 PM"], 8.00, None),
            ("Fri, Oct 20", [], 8.00, "APPROVED LEAVE - 8h")
        ]
        for d_date, p_list, h_val, note in default_days:
            p_items = [PunchItem(type="Clock In" if i % 2 == 0 else "Clock Out", time=t) for i, t in enumerate(p_list)]
            days.append(DaySummary(
                date=d_date,
                punches=p_items,
                hours=h_val,
                regular_hours=min(h_val, 8.0),
                overtime_hours=max(0.0, round(h_val - 8.0, 2)),
                double_time_hours=0.0,
                notes=note
            ))
            daily_hours.append(h_val)

    flsa_totals = calculate_pay_period_flsa(daily_hours, hourly_rate)

    return TimecardResponse(
        timecard_id=tc_id,
        user_id=user_id,
        employee_name=emp_name,
        pay_period=pay_period,
        status=status,
        days=days,
        total_hours=flsa_totals["total_hours"],
        regular_hours=flsa_totals["regular_hours"],
        overtime_hours=flsa_totals["overtime_hours"],
        double_time_hours=flsa_totals["double_time_hours"],
        gross_pay_estimate=flsa_totals["gross_pay_estimate"]
    )


@router.post("/submit", response_model=TimecardSubmitResponse)
def submit_timecard(
    req: TimecardSubmitRequest,
    user_id: str = Query("usr_employee_01"),
    db: sqlite3.Connection = Depends(get_db)
):
    """Submit timecard for supervisor review and sign-off."""
    cursor = db.cursor()
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        """
        UPDATE timecards
        SET status = 'SUBMITTED', submitted_at = ?
        WHERE id = ?
        """,
        (timestamp, req.timecard_id)
    )

    cursor.execute("SELECT email FROM users WHERE id = ?", (user_id,))
    u_row = cursor.fetchone()
    email = u_row["email"] if u_row else "employee@enterprise.com"

    append_audit_event(db, "TIMECARD_SUBMITTED", user_id, email, {"timecard_id": req.timecard_id})
    db.commit()

    return TimecardSubmitResponse(
        timecard_id=req.timecard_id,
        status="SUBMITTED",
        submitted_at=timestamp
    )
