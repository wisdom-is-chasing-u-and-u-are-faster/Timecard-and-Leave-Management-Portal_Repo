import sys
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent.parent
if str(base_dir) not in sys.path:
    sys.path.insert(0, str(base_dir))

from app.db.session import get_db_connection  # noqa: E402


def init_database() -> None:
    """Initializes SQLite schema and populates baseline seeds."""
    conn = get_db_connection()
    cursor = conn.cursor()

    schema_path = base_dir / "db" / "schema.sql"
    seed_path = base_dir / "db" / "seed.sql"

    if schema_path.exists():
        with open(schema_path, "r", encoding="utf-8") as f:
            cursor.executescript(f.read())

    if seed_path.exists():
        cursor.execute("DELETE FROM audit_ledger")
        with open(seed_path, "r", encoding="utf-8") as f:
            cursor.executescript(f.read())

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_database()
    print("Database initialized successfully.")
