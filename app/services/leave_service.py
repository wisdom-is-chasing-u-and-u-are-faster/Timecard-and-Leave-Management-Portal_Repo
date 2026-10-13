import sqlite3
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from app.services.audit_service import append_audit_event


def get_leave_balances(conn: sqlite3.Connection, user_id: str) -> Dict[str, Any]:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM leave_balances WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if not row:
        bal_id = f"bal_{uuid.uuid4().hex[:8]}"
        cursor.execute(
            """
            INSERT INTO leave_balances (id, user_id, vacation_hours, sick_hours, unpaid_hours, accrual_rate_per_period)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (bal_id, user_id, 80.0, 40.0, 0.0, 3.75)
        )
        conn.commit()
        cursor.execute("SELECT * FROM leave_balances WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()

    return {
        "user_id": user_id,
        "vacation_hours": row["vacation_hours"],
        "sick_hours": row["sick_hours"],
        "unpaid_hours": row["unpaid_hours"],
        "accrual_rate_per_period": row["accrual_rate_per_period"]
    }


def submit_leave_request(
    conn: sqlite3.Connection,
    user_id: str,
    leave_type: str,
    start_date: str,
    end_date: str,
    comments: Optional[str] = ""
) -> Dict[str, Any]:
    cursor = conn.cursor()
    total_hours = 8.0
    req_id = f"lr_{uuid.uuid4().hex[:10]}"
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    # Fetch user email for audit
    cursor.execute("SELECT email FROM users WHERE id = ?", (user_id,))
    user_row = cursor.fetchone()
    user_email = user_row["email"] if user_row else "user@enterprise.internal"

    audit_payload = {
        "request_id": req_id,
        "leave_type": leave_type,
        "start_date": start_date,
        "end_date": end_date,
        "hours": total_hours
    }
    append_audit_event(conn, "LEAVE_REQUEST_SUBMITTED", user_id, user_email, audit_payload)

    cursor.execute(
        """
        INSERT INTO leave_requests
        (id, user_id, leave_type, start_date, end_date, total_hours, comments, status, submitted_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'PENDING', ?)
        """,
        (req_id, user_id, leave_type, start_date, end_date, total_hours, comments or "", now_str)
    )
    conn.commit()

    return {
        "id": req_id,
        "user_id": user_id,
        "leave_type": leave_type,
        "start_date": start_date,
        "end_date": end_date,
        "total_hours": total_hours,
        "comments": comments or "",
        "status": "PENDING",
        "submitted_at": now_str
    }


def get_user_leave_requests(conn: sqlite3.Connection, user_id: str) -> List[Dict[str, Any]]:
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM leave_requests WHERE user_id = ? ORDER BY submitted_at DESC",
        (user_id,)
    )
    rows = cursor.fetchall()
    return [
        {
            "id": r["id"],
            "user_id": r["user_id"],
            "leave_type": r["leave_type"],
            "start_date": r["start_date"],
            "end_date": r["end_date"],
            "total_hours": r["total_hours"],
            "comments": r["comments"],
            "status": r["status"],
            "submitted_at": r["submitted_at"],
            "action_by": r["action_by"],
            "action_at": r["action_at"]
        }
        for r in rows
    ]


class LeaveService:
    get_balances = staticmethod(get_leave_balances)
    create_request = staticmethod(submit_leave_request)
    get_my_requests = staticmethod(get_user_leave_requests)
