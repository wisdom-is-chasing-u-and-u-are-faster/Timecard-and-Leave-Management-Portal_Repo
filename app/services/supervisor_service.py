import sqlite3
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import HTTPException
from app.services.audit_service import append_audit_event


def get_supervisor_summary(conn: sqlite3.Connection) -> Dict[str, Any]:
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM timecards WHERE status = 'SUBMITTED'")
    ts_count = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) as count FROM leave_requests WHERE status = 'PENDING'")
    leave_count = cursor.fetchone()["count"]

    return {
        "pending_timesheets_count": ts_count,
        "pending_leave_requests_count": leave_count
    }


def get_pending_timesheets(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT t.id, t.user_id, u.name as employee_name,
               (t.pay_period_start || ' - ' || t.pay_period_end) as pay_period,
               t.total_hours, t.overtime_hours, t.status
        FROM timecards t
        JOIN users u ON t.user_id = u.id
        WHERE t.status = 'SUBMITTED'
        ORDER BY t.submitted_at DESC
        """
    )
    rows = cursor.fetchall()
    return [
        {
            "id": r["id"],
            "user_id": r["user_id"],
            "employee_name": r["employee_name"],
            "pay_period": r["pay_period"],
            "total_hours": r["total_hours"],
            "overtime_hours": r["overtime_hours"],
            "status": r["status"]
        }
        for r in rows
    ]


def act_on_timesheet(
    conn: sqlite3.Connection,
    timesheet_id: Optional[str] = None,
    timecard_id: Optional[str] = None,
    action: str = "APPROVE",
    supervisor_id: str = "usr_supervisor_01",
    comments: Optional[str] = ""
) -> Dict[str, Any]:
    tid = timesheet_id or timecard_id or "all"
    cursor = conn.cursor()
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    new_status = "APPROVED" if action.upper() in ("APPROVE", "APPROVED") else "DENIED"

    if tid == "all":
        cursor.execute("SELECT id FROM timecards WHERE status = 'SUBMITTED'")
        ids = [r["id"] for r in cursor.fetchall()]
        for target_id in ids:
            cursor.execute(
                """
                UPDATE timecards
                SET status = ?, action_by = ?, action_at = ?, comments = ?
                WHERE id = ?
                """,
                (new_status, supervisor_id, now_str, comments or "", target_id)
            )
        conn.commit()
        append_audit_event(
            conn, f"BULK_TIMESHEETS_{new_status}", supervisor_id, "supervisor@enterprise.internal",
            {"count": len(ids), "status": new_status}
        )
        return {
            "id": "all",
            "status": new_status,
            "action_by": supervisor_id,
            "action_at": now_str,
            "comments": comments or ""
        }

    cursor.execute("SELECT * FROM timecards WHERE id = ?", (tid,))
    tc = cursor.fetchone()
    if not tc:
        raise HTTPException(status_code=404, detail="Timesheet not found")

    cursor.execute(
        """
        UPDATE timecards
        SET status = ?, action_by = ?, action_at = ?, comments = ?
        WHERE id = ?
        """,
        (new_status, supervisor_id, now_str, comments or "", tid)
    )
    conn.commit()

    append_audit_event(
        conn, f"TIMESHEET_{new_status}", supervisor_id, "supervisor@enterprise.internal",
        {"timesheet_id": tid, "status": new_status, "comments": comments or ""}
    )

    return {
        "id": tid,
        "status": new_status,
        "action_by": supervisor_id,
        "action_at": now_str,
        "comments": comments or ""
    }


def get_pending_leave_requests(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT l.id, l.user_id, u.name as employee_name, l.leave_type,
               (l.start_date || ' - ' || l.end_date) as dates,
               l.total_hours, l.status, l.comments
        FROM leave_requests l
        JOIN users u ON l.user_id = u.id
        WHERE l.status = 'PENDING'
        ORDER BY l.submitted_at DESC
        """
    )
    rows = cursor.fetchall()
    return [
        {
            "id": r["id"],
            "user_id": r["user_id"],
            "employee_name": r["employee_name"],
            "leave_type": r["leave_type"],
            "dates": r["dates"],
            "total_hours": r["total_hours"],
            "status": r["status"],
            "comments": r["comments"]
        }
        for r in rows
    ]


def act_on_leave_request(
    conn: sqlite3.Connection,
    request_id: Optional[str] = None,
    action: str = "APPROVE",
    supervisor_id: str = "usr_supervisor_01",
    comments: Optional[str] = ""
) -> Dict[str, Any]:
    rid = request_id or "all"
    cursor = conn.cursor()
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    new_status = "APPROVED" if action.upper() in ("APPROVE", "APPROVED") else "DENIED"

    if rid == "all":
        cursor.execute("SELECT id, user_id, total_hours, leave_type FROM leave_requests WHERE status = 'PENDING'")
        rows = cursor.fetchall()
        for r in rows:
            cursor.execute(
                """
                UPDATE leave_requests
                SET status = ?, action_by = ?, action_at = ?, action_notes = ?
                WHERE id = ?
                """,
                (new_status, supervisor_id, now_str, comments or "", r["id"])
            )
            if new_status == "APPROVED":
                if "Vacation" in r["leave_type"]:
                    cursor.execute("UPDATE leave_balances SET vacation_hours = MAX(0, vacation_hours - ?) WHERE user_id = ?", (r["total_hours"], r["user_id"]))
                elif "Sick" in r["leave_type"]:
                    cursor.execute("UPDATE leave_balances SET sick_hours = MAX(0, sick_hours - ?) WHERE user_id = ?", (r["total_hours"], r["user_id"]))
        conn.commit()
        append_audit_event(
            conn, f"BULK_LEAVE_REQUESTS_{new_status}", supervisor_id, "supervisor@enterprise.internal",
            {"count": len(rows), "status": new_status}
        )
        return {
            "id": "all",
            "status": new_status,
            "action_by": supervisor_id,
            "action_at": now_str,
            "comments": comments or ""
        }

    cursor.execute("SELECT * FROM leave_requests WHERE id = ?", (rid,))
    lr = cursor.fetchone()
    if not lr:
        raise HTTPException(status_code=404, detail="Leave request not found")

    cursor.execute(
        """
        UPDATE leave_requests
        SET status = ?, action_by = ?, action_at = ?, action_notes = ?
        WHERE id = ?
        """,
        (new_status, supervisor_id, now_str, comments or "", rid)
    )
    if new_status == "APPROVED":
        if "Vacation" in lr["leave_type"]:
            cursor.execute("UPDATE leave_balances SET vacation_hours = MAX(0, vacation_hours - ?) WHERE user_id = ?", (lr["total_hours"], lr["user_id"]))
        elif "Sick" in lr["leave_type"]:
            cursor.execute("UPDATE leave_balances SET sick_hours = MAX(0, sick_hours - ?) WHERE user_id = ?", (lr["total_hours"], lr["user_id"]))

    conn.commit()

    append_audit_event(
        conn, f"LEAVE_REQUEST_{new_status}", supervisor_id, "supervisor@enterprise.internal",
        {"request_id": rid, "status": new_status, "comments": comments or ""}
    )

    return {
        "id": rid,
        "status": new_status,
        "action_by": supervisor_id,
        "action_at": now_str,
        "comments": comments or ""
    }


class SupervisorService:
    get_summary = staticmethod(get_supervisor_summary)
    get_pending_timesheets = staticmethod(get_pending_timesheets)
    action_timesheet = staticmethod(act_on_timesheet)
    get_pending_leave_requests = staticmethod(get_pending_leave_requests)
    action_leave_request = staticmethod(act_on_leave_request)
