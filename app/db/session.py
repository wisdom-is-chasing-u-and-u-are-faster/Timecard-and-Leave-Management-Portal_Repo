import os
import sqlite3
from pathlib import Path
from typing import Generator

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./timecard_portal.db")


def get_db_path() -> str:
    """Extract SQLite database file path from DATABASE_URL."""
    if DATABASE_URL.startswith("sqlite:///"):
        raw_path = DATABASE_URL.replace("sqlite:///", "")
        return str(Path(raw_path).resolve())
    return "timecard_portal.db"


def get_db_connection() -> sqlite3.Connection:
    """Creates and returns an active sqlite3 connection with dict-like row factory."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def get_db() -> Generator[sqlite3.Connection, None, None]:
    """FastAPI dependency yielding database connection."""
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()
