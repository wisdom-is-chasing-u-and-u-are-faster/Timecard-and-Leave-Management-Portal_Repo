from typing import List, Optional
from pydantic import BaseModel


class LeaveBalanceResponse(BaseModel):
    user_id: str
    vacation_hours: float
    sick_hours: float
    unpaid_hours: float
    accrual_rate_per_period: float


class LeaveRequestCreate(BaseModel):
    leave_type: str
    start_date: str
    end_date: str
    comments: Optional[str] = None


class LeaveRequestItem(BaseModel):
    id: str
    user_id: str
    employee_name: Optional[str] = None
    leave_type: str
    start_date: str
    end_date: str
    total_hours: float
    comments: Optional[str] = None
    status: str
    submitted_at: str
    action_by: Optional[str] = None
    action_at: Optional[str] = None


class LeaveRequestListResponse(BaseModel):
    requests: List[LeaveRequestItem]


class SupervisorActionRequest(BaseModel):
    action: str  # APPROVE, DENY
    comments: Optional[str] = None


class SupervisorActionResponse(BaseModel):
    id: str
    status: str
    action_by: str
    action_at: str
    comments: Optional[str] = None
