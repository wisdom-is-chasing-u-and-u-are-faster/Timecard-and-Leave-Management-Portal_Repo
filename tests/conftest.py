import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.init_db import init_database
from app.db.session import get_db_connection


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Initializes the test database before test session runs."""
    init_database()
    yield


@pytest.fixture
def client():
    """Provides FastAPI TestClient instance."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def db_conn():
    """Provides direct database connection fixture."""
    conn = get_db_connection()
    yield conn
    conn.close()
