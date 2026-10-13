import sqlite3
from typing import Optional
from app.models.user import UserProfile


def get_user_by_id(conn: sqlite3.Connection, user_id: str) -> Optional[UserProfile]:
    """Retrieves user profile by ID."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    if not row:
        return None
    return UserProfile(
        id=row["id"],
        name=row["name"],
        email=row["email"],
        role=row["role"],
        avatar_initials=row["avatar_initials"],
        department=row["department"],
        hourly_rate=row["hourly_rate"]
    )


def get_user_by_email(conn: sqlite3.Connection, email: str) -> Optional[UserProfile]:
    """Retrieves user profile by Email."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    if not row:
        return None
    return UserProfile(
        id=row["id"],
        name=row["name"],
        email=row["email"],
        role=row["role"],
        avatar_initials=row["avatar_initials"],
        department=row["department"],
        hourly_rate=row["hourly_rate"]
    )


def authenticate_user(conn: sqlite3.Connection,
                      email: Optional[str] = None, role: Optional[str] = "EMPLOYEE") -> UserProfile:
    """Authenticates or resolves active user based on email or default role persona."""
    if email:
        user = get_user_by_email(conn, email)
        if user:
            return user

    target_role = role.upper() if role else "EMPLOYEE"
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE role = ? LIMIT 1", (target_role,))
    row = cursor.fetchone()
    if row:
        return UserProfile(
            id=row["id"],
            name=row["name"],
            email=row["email"],
            role=row["role"],
            avatar_initials=row["avatar_initials"],
            department=row["department"],
            hourly_rate=row["hourly_rate"]
        )

    # Fallback to first available employee
    return UserProfile(
        id="usr_employee_01",
        name="Erin Employee",
        email="erin.employee@enterprise.com",
        role="EMPLOYEE",
        avatar_initials="EE",
        department="Engineering",
        hourly_rate=28.50
    )
