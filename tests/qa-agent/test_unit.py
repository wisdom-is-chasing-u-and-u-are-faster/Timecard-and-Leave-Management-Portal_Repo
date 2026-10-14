"""
QA Persona v2 -- auto-generated tests
Service: cloned_repo
Suite:   unit
Source:  test_strategy/plans/cloned_repo__unit.json
Generated: 2024-07-12T12:05:43.138451Z
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from app.api.punches import sync_punches
from app.api.timecards import get_current_timecard
from app.api.supervisor import pending_timesheets, timesheet_action, leave_action
from app.api.leave import get_balances, request_time_off
from app.api.auth import login

from app.models.punch import PunchSyncRequest, PunchSyncItem
from app.models.timecard import TimecardResponse
from app.models.leave import SupervisorActionRequest, SupervisorActionResponse, LeaveBalanceResponse, LeaveRequestCreate, LeaveRequestItem
from app.models.user import LoginRequest, LoginResponse, UserProfile

def test_cloned_repo__unit__001_sync_punches():
    """Verifies sync_punches correctly processes punches and returns a sync count.

    test_id: cloned_repo__unit__001
    target: sync_punches
    requirement_id: REQ-F-002,REQ-F-001
    ac_ids: REQ-F-002-AC-1,REQ-F-001-AC-1
    """
    mock_db = MagicMock()
    punches_data = [
        PunchSyncItem(punch_type="CLOCK_IN", timestamp="2023-10-25 09:00:00"),
        PunchSyncItem(punch_type="CLOCK_OUT", timestamp="2023-10-25 17:00:00"),
    ]
    req = PunchSyncRequest(punches=punches_data)
    user_id = "usr_employee_01"

    with patch("app.api.punches.sync_batch_punches") as mock_sync_batch:
        mock_sync_batch.return_value = len(punches_data)
        
        result = sync_punches(req, user_id, mock_db)
        
        punches_dicts = [p.dict() for p in punches_data]
        mock_sync_batch.assert_called_once_with(mock_db, user_id, punches_dicts)
        assert result == {"synced_count": 2, "status": "synchronized"}

def test_cloned_repo__unit__002_get_current_timecard():
    """Verifies get_current_timecard fetches and processes timecard data correctly.

    test_id: cloned_repo__unit__002
    target: get_current_timecard
    requirement_id: REQ-F-010
    ac_ids: REQ-F-010-AC-1
    """
    mock_db = MagicMock()
    mock_cursor = MagicMock()
    mock_db.cursor.return_value = mock_cursor
    
    user_id = "usr_employee_01"
    
    tc_row = {
        "id": "tc_current_01", "employee_name": "Test User", "hourly_rate": 30.0,
        "pay_period_start": "2023-10-16", "pay_period_end": "2023-10-31", "status": "DRAFT"
    }
    entries_rows = [
        {
            "work_date": "2023-10-16", "punch_in_1": "09:00", "punch_out_1": "17:00",
            "punch_in_2": None, "punch_out_2": None, "hours": 8.0, "regular_hours": 8.0,
            "overtime_hours": 0.0, "double_time_hours": 0.0, "notes": None
        }
    ]
    mock_cursor.fetchone.return_value = tc_row
    mock_cursor.fetchall.return_value = entries_rows

    flsa_mock_data = {
        "total_hours": 8.0, "regular_hours": 8.0, "overtime_hours": 0.0,
        "double_time_hours": 0.0, "gross_pay_estimate": 240.0
    }

    with patch("app.api.timecards.calculate_pay_period_flsa", return_value=flsa_mock_data) as mock_flsa:
        result = get_current_timecard(user_id, mock_db)
        
        assert isinstance(result, TimecardResponse)
        assert result.timecard_id == "tc_current_01"
        assert result.total_hours == 8.0
        assert len(result.days) == 1
        assert result.days[0].date == "2023-10-16"
        mock_flsa.assert_called_once_with([8.0], 30.0)

def test_cloned_repo__unit__003_pending_timesheets():
    """Verifies pending_timesheets fetches pending timesheets correctly.

    test_id: cloned_repo__unit__003
    target: pending_timesheets
    requirement_id: REQ-F-011,REQ-N-006
    ac_ids: REQ-F-011-AC-1,REQ-N-006-AC-1
    """
    mock_db = MagicMock()
    mock_pending_data = [{"id": "ts_123", "employee_name": "Test User"}]
    
    with patch("app.api.supervisor.get_pending_timesheets", return_value=mock_pending_data) as mock_get_pending:
        result = pending_timesheets(mock_db)
        
        mock_get_pending.assert_called_once_with(mock_db)
        assert result == {"items": mock_pending_data}

@pytest.mark.parametrize("action, expected_status", [("APPROVE", "APPROVED"), ("DENY", "DENIED")])
def test_cloned_repo__unit__004_timesheet_action(action, expected_status):
    """Verifies timesheet_action processes approve/deny actions correctly.

    test_id: cloned_repo__unit__004
    target: timesheet_action
    requirement_id: REQ-F-012
    ac_ids: REQ-F-012-AC-1
    """
    mock_db = MagicMock()
    timesheet_id = "ts_123"
    supervisor_id = "sup_01"
    req = SupervisorActionRequest(action=action, comments="Test comment")
    
    mock_action_result = {
        "id": timesheet_id, "status": expected_status, "action_by": supervisor_id,
        "action_at": datetime.utcnow().isoformat(), "comments": req.comments
    }
    
    with patch("app.api.supervisor.act_on_timesheet", return_value=mock_action_result) as mock_act:
        result = timesheet_action(timesheet_id, req, supervisor_id, mock_db)
        
        mock_act.assert_called_once_with(
            conn=mock_db, timesheet_id=timesheet_id, action=action,
            supervisor_id=supervisor_id, comments=req.comments
        )
        assert isinstance(result, SupervisorActionResponse)
        assert result.status == expected_status
        assert result.id == timesheet_id

@pytest.mark.parametrize("action, expected_status", [("APPROVE", "APPROVED"), ("DENY", "DENIED")])
def test_cloned_repo__unit__005_leave_action(action, expected_status):
    """Verifies leave_action processes approve/deny actions correctly.

    test_id: cloned_repo__unit__005
    target: leave_action
    requirement_id: REQ-F-007
    ac_ids: REQ-F-007-AC-1
    """
    mock_db = MagicMock()
    request_id = "lr_123"
    supervisor_id = "sup_01"
    req = SupervisorActionRequest(action=action, comments="Test comment")
    
    mock_action_result = {
        "id": request_id, "status": expected_status, "action_by": supervisor_id,
        "action_at": datetime.utcnow().isoformat(), "comments": req.comments
    }
    
    with patch("app.api.supervisor.act_on_leave_request", return_value=mock_action_result) as mock_act:
        result = leave_action(request_id, req, supervisor_id, mock_db)
        
        mock_act.assert_called_once_with(
            conn=mock_db, request_id=request_id, action=action,
            supervisor_id=supervisor_id, comments=req.comments
        )
        assert isinstance(result, SupervisorActionResponse)
        assert result.status == expected_status
        assert result.id == request_id

def test_cloned_repo__unit__006_get_balances():
    """Verifies get_balances fetches user leave balances correctly.

    test_id: cloned_repo__unit__006
    target: get_balances
    requirement_id: REQ-F-004
    ac_ids: REQ-F-004-AC-1
    """
    mock_db = MagicMock()
    user_id = "usr_employee_01"
    mock_balance_data = {
        "user_id": user_id, "vacation_hours": 80.0, "sick_hours": 40.0,
        "unpaid_hours": 0.0, "accrual_rate_per_period": 3.75
    }
    
    with patch("app.api.leave.get_leave_balances", return_value=mock_balance_data) as mock_get_balances:
        result = get_balances(user_id, mock_db)
        
        mock_get_balances.assert_called_once_with(mock_db, user_id)
        assert isinstance(result, LeaveBalanceResponse)
        assert result.vacation_hours == 80.0
        assert result.user_id == user_id

def test_cloned_repo__unit__007_request_time_off():
    """Verifies request_time_off creates a new leave request correctly.

    test_id: cloned_repo__unit__007
    target: request_time_off
    requirement_id: REQ-F-005
    ac_ids: REQ-F-005-AC-1
    """
    mock_db = MagicMock()
    user_id = "usr_employee_01"
    req = LeaveRequestCreate(
        leave_type="Vacation", start_date="2023-12-25", end_date="2023-12-25",
        comments="Holiday"
    )
    
    mock_request_result = {
        "id": "lr_new", "user_id": user_id, "leave_type": "Vacation",
        "start_date": "2023-12-25", "end_date": "2023-12-25", "total_hours": 8.0,
        "comments": "Holiday", "status": "PENDING", "submitted_at": datetime.utcnow().isoformat()
    }
    
    with patch("app.api.leave.submit_leave_request", return_value=mock_request_result) as mock_submit:
        result = request_time_off(req, user_id, mock_db)
        
        mock_submit.assert_called_once_with(
            conn=mock_db, user_id=user_id, leave_type=req.leave_type,
            start_date=req.start_date, end_date=req.end_date, comments=req.comments
        )
        assert isinstance(result, LeaveRequestItem)
        assert result.id == "lr_new"
        assert result.status == "PENDING"

def test_cloned_repo__unit__008_login():
    """Verifies login function authenticates a user and returns a token.

    test_id: cloned_repo__unit__008
    target: login
    requirement_id: REQ-F-013
    ac_ids: REQ-F-013-AC-1
    """
    mock_db = MagicMock()
    req = LoginRequest(email="test@example.com", role="EMPLOYEE")
    
    mock_user = UserProfile(
        id="usr_test_01", name="Test User", email="test@example.com",
        role="EMPLOYEE", avatar_initials="TU", department="Testing", hourly_rate=50.0
    )
    
    with patch("app.api.auth.authenticate_user", return_value=mock_user) as mock_auth:
        result = login(req, mock_db)
        
        mock_auth.assert_called_once_with(mock_db, email=req.email, role=req.role)
        assert isinstance(result, LoginResponse)
        assert result.user == mock_user
        assert result.token == f"jwt_mock_token_{mock_user.id}_{mock_user.role}"
