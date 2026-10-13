import sqlite3
from fastapi import APIRouter, Depends, Query
from app.db.session import get_db
from app.models.leave import (
    LeaveBalanceResponse,
    LeaveRequestCreate,
    LeaveRequestItem,
    LeaveRequestListResponse,
)
from app.services.leave_service import (
    get_leave_balances,
    get_user_leave_requests,
    submit_leave_request,
)

router = APIRouter(prefix="/leave", tags=["Leave & Absence Management"])


@router.get("/balances", response_model=LeaveBalanceResponse)
def get_balances(
    user_id: str = Query("usr_employee_01"),
    db: sqlite3.Connection = Depends(get_db)
):
    """Get employee accrued leave balances for Vacation, Sick, and Unpaid Time Off."""
    data = get_leave_balances(db, user_id)
    return LeaveBalanceResponse(**data)


@router.post("/requests", response_model=LeaveRequestItem, status_code=201)
def request_time_off(
    req: LeaveRequestCreate,
    user_id: str = Query("usr_employee_01"),
    db: sqlite3.Connection = Depends(get_db)
):
    """Submit a new time-off request."""
    result = submit_leave_request(
        conn=db,
        user_id=user_id,
        leave_type=req.leave_type,
        start_date=req.start_date,
        end_date=req.end_date,
        comments=req.comments
    )
    return LeaveRequestItem(**result)


@router.get("/requests/my", response_model=LeaveRequestListResponse)
def get_my_requests(
    user_id: str = Query("usr_employee_01"),
    db: sqlite3.Connection = Depends(get_db)
):
    """Get employee's submitted leave request history."""
    items = get_user_leave_requests(db, user_id)
    return LeaveRequestListResponse(requests=[LeaveRequestItem(**i) for i in items])
