from typing import Optional
from pydantic import BaseModel


class UserProfile(BaseModel):
    id: str
    name: str
    email: str
    role: str
    avatar_initials: str
    department: Optional[str] = "Engineering"
    hourly_rate: float = 25.00


class LoginRequest(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = "EMPLOYEE"


class LoginResponse(BaseModel):
    token: str
    user: UserProfile
