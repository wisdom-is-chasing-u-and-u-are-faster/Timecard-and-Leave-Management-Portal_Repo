import sqlite3
from fastapi import APIRouter, Depends
from app.db.session import get_db
from app.models.user import LoginRequest, LoginResponse, UserProfile
from app.services.auth_service import authenticate_user, get_user_by_id

router = APIRouter(prefix="/auth", tags=["Authentication & SSO"])


@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest, db: sqlite3.Connection = Depends(get_db)):
    """Authenticate user via SSO / Persona credentials."""
    user = authenticate_user(db, email=req.email, role=req.role)
    token = f"jwt_mock_token_{user.id}_{user.role}"
    return LoginResponse(token=token, user=user)


@router.get("/me", response_model=UserProfile)
def get_current_user(user_id: str = "usr_employee_01", db: sqlite3.Connection = Depends(get_db)):
    """Get profile for active user session."""
    user = get_user_by_id(db, user_id)
    if not user:
        user = authenticate_user(db, role="EMPLOYEE")
    return user


@router.post("/switch-role", response_model=LoginResponse)
def switch_role(role: str, db: sqlite3.Connection = Depends(get_db)):
    """Fast SSO role switcher for testing and demonstration."""
    user = authenticate_user(db, role=role)
    token = f"jwt_mock_token_{user.id}_{user.role}"
    return LoginResponse(token=token, user=user)
