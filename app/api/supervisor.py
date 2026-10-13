import sqlite3
from fastapi import APIRouter, Depends, Query
from app.db.session import get_db
from app.models.leave import SupervisorActionRequest, SupervisorActionResponse
from app.services.supervisor_service import (
    act_on_leave_request,
    act_on_timesheet,
    get_pending_leave_requests,
    get_pending_timesheets,
    get_supervisor_summary,
)

router = APIRouter(prefix="/supervisor", tags=["Supervisor Hub & Team Approvals"])


@router.get("/summary")
def get_summary(db: sqlite3.Connection = Depends(get_db)):
    """Get metrics for supervisor dashboard (pending timesheets, pending leave requests)."""
    return get_supervisor_summary(db)


@router.get("/timesheets/pending")
def pending_timesheets(db: sqlite3.Connection = Depends(get_db)):
    """Get list of pending timesheet submissions awaiting supervisor sign-off."""
    return {"items": get_pending_timesheets(db)}


@router.post("/timesheets/{id}/action", response_model=SupervisorActionResponse)
def timesheet_action(
    id: str,
    req: SupervisorActionRequest,
    supervisor_id: str = Query("usr_supervisor_01"),
    db: sqlite3.Connection = Depends(get_db)
):
    """Approve or Deny a timesheet submission."""
    result = act_on_timesheet(
        conn=db,
        timesheet_id=id,
        action=req.action,
        supervisor_id=supervisor_id,
        comments=req.comments
    )
    return SupervisorActionResponse(**result)


@router.post("/timesheets/bulk-approve")
def bulk_approve_timesheets(
    supervisor_id: str = Query("usr_supervisor_01"),
    db: sqlite3.Connection = Depends(get_db)
):
    """Bulk approve all pending timesheet submissions."""
    pending = get_pending_timesheets(db)
    approved_ids = []
    for item in pending:
        act_on_timesheet(db, item["id"], "APPROVE", supervisor_id, "Bulk approved by supervisor")
        approved_ids.append(item["id"])
    return {"status": "SUCCESS", "approved_count": len(approved_ids), "timecard_ids": approved_ids}


@router.get("/leave/pending")
def pending_leave(db: sqlite3.Connection = Depends(get_db)):
    """Get list of pending leave requests awaiting supervisor sign-off."""
    return {"items": get_pending_leave_requests(db)}


@router.post("/leave/{id}/action", response_model=SupervisorActionResponse)
def leave_action(
    id: str,
    req: SupervisorActionRequest,
    supervisor_id: str = Query("usr_supervisor_01"),
    db: sqlite3.Connection = Depends(get_db)
):
    """Approve or Deny a leave request."""
    result = act_on_leave_request(
        conn=db,
        request_id=id,
        action=req.action,
        supervisor_id=supervisor_id,
        comments=req.comments
    )
    return SupervisorActionResponse(**result)


@router.post("/leave/bulk-approve")
def bulk_approve_leave(
    supervisor_id: str = Query("usr_supervisor_01"),
    db: sqlite3.Connection = Depends(get_db)
):
    """Bulk approve all pending leave requests."""
    pending = get_pending_leave_requests(db)
    approved_ids = []
    for item in pending:
        act_on_leave_request(db, item["id"], "APPROVE", supervisor_id, "Bulk approved by supervisor")
        approved_ids.append(item["id"])
    return {"status": "SUCCESS", "approved_count": len(approved_ids), "request_ids": approved_ids}
