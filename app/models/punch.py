from typing import List, Optional
from pydantic import BaseModel


class PunchCreate(BaseModel):
    punch_type: str  # CLOCK_IN, CLOCK_OUT, MEAL_IN, MEAL_OUT
    timestamp: Optional[str] = None
    client_vector: Optional[int] = 1
    offline_captured: Optional[bool] = False


class PunchSyncItem(BaseModel):
    punch_type: str
    timestamp: str
    client_vector: Optional[int] = 1


class PunchSyncRequest(BaseModel):
    punches: List[PunchSyncItem]


class PunchResponse(BaseModel):
    punch_id: str
    status: str
    punch_type: str
    timestamp: str
    audit_hash: str


class PunchStatusResponse(BaseModel):
    is_clocked_in: bool
    current_status: str
    last_punch_time: Optional[str] = None
    elapsed_today: str


class PunchTodayEntry(BaseModel):
    type: str
    time: str
    total: str


class PunchTodayResponse(BaseModel):
    date: str
    entries: List[PunchTodayEntry]
    total_hours: float
