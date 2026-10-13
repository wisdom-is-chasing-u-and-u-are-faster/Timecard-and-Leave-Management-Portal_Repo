from typing import List, Optional
from pydantic import BaseModel


class PunchItem(BaseModel):
    type: str
    time: str


class DaySummary(BaseModel):
    date: str
    punches: List[PunchItem]
    hours: float
    regular_hours: float
    overtime_hours: float
    double_time_hours: float
    notes: Optional[str] = None


class TimecardResponse(BaseModel):
    timecard_id: str
    user_id: str
    employee_name: str
    pay_period: str
    status: str
    days: List[DaySummary]
    total_hours: float
    regular_hours: float
    overtime_hours: float
    double_time_hours: float
    gross_pay_estimate: float


class TimecardSubmitRequest(BaseModel):
    timecard_id: str
    comments: Optional[str] = None


class TimecardSubmitResponse(BaseModel):
    timecard_id: str
    status: str
    submitted_at: str
