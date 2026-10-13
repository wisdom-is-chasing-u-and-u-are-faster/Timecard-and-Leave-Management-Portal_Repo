import sqlite3
from fastapi import APIRouter, Depends, Query
from app.db.session import get_db
from app.models.punch import (
    PunchCreate,
    PunchResponse,
    PunchStatusResponse,
    PunchSyncRequest,
    PunchTodayResponse,
)
from app.services.punch_service import (
    get_current_punch_status,
    get_today_timecard,
    record_punch,
    sync_batch_punches,
)

router = APIRouter(prefix="/punches", tags=["Time Punch & Sync"])


@router.post("", response_model=PunchResponse, status_code=201)
def create_punch(
    req: PunchCreate,
    user_id: str = Query("usr_employee_01"),
    db: sqlite3.Connection = Depends(get_db)
):
    """Record a time punch (CLOCK_IN, CLOCK_OUT, MEAL_IN, MEAL_OUT)."""
    result = record_punch(
        conn=db,
        user_id=user_id,
        punch_type=req.punch_type,
        timestamp_str=req.timestamp,
        client_vector=req.client_vector or 1,
        offline_captured=bool(req.offline_captured)
    )
    return PunchResponse(**result)


@router.post("/sync")
def sync_punches(
    req: PunchSyncRequest,
    user_id: str = Query("usr_employee_01"),
    db: sqlite3.Connection = Depends(get_db)
):
    """Batch synchronize offline punches captured client-side."""
    punches_dicts = [p.dict() if hasattr(p, "dict") else dict(p) for p in req.punches]
    count = sync_batch_punches(db, user_id, punches_dicts)
    return {
        "synced_count": count,
        "status": "synchronized"
    }


@router.get("/status", response_model=PunchStatusResponse)
def punch_status(
    user_id: str = Query("usr_employee_01"),
    db: sqlite3.Connection = Depends(get_db)
):
    """Get employee current punch status (Clocked In vs Clocked Out)."""
    status = get_current_punch_status(db, user_id)
    return PunchStatusResponse(**status)


@router.get("/today", response_model=PunchTodayResponse)
def today_punches(
    user_id: str = Query("usr_employee_01"),
    db: sqlite3.Connection = Depends(get_db)
):
    """Get punches and summary for today's timecard view."""
    data = get_today_timecard(db, user_id)
    return PunchTodayResponse(**data)
