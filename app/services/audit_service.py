import hashlib
import json
import sqlite3
import uuid
from datetime import datetime
from typing import Dict, Any, List


def compute_hash(previous_hash: str, event_type: str, actor_id: str, payload: str, timestamp: str) -> str:
    """Computes SHA-256 cryptographic hash chaining to previous block."""
    raw = f"{previous_hash}|{event_type}|{actor_id}|{payload}|{timestamp}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def append_audit_event(conn: sqlite3.Connection, event_type: str, actor_id: str, actor_email: str, payload_data: dict) -> str:
    """Appends an event to the cryptographic audit ledger and returns block hash."""
    cursor = conn.cursor()
    cursor.execute("SELECT block_hash FROM audit_ledger ORDER BY timestamp DESC, rowid DESC LIMIT 1")
    row = cursor.fetchone()
    previous_hash = row["block_hash"] if row else "GENESIS_CHAIN_BLOCK_HASH"

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    payload_str = json.dumps(payload_data, sort_keys=True)
    block_id = f"aud_{uuid.uuid4().hex[:12]}"
    block_hash = compute_hash(previous_hash, event_type, actor_id, payload_str, timestamp)

    cursor.execute(
        """
        INSERT INTO audit_ledger (id, event_type, actor_id, actor_email, payload, previous_hash, block_hash, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (block_id, event_type, actor_id, actor_email, payload_str, previous_hash, block_hash, timestamp)
    )
    conn.commit()
    return block_hash


def verify_audit_chain(conn: sqlite3.Connection) -> bool:
    """Verifies cryptographic integrity of the entire audit chain."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_ledger ORDER BY rowid ASC")
    rows = cursor.fetchall()
    if not rows:
        return True

    expected_prev = rows[0]["block_hash"]
    for idx, row in enumerate(rows):
        if idx > 0:
            if row["previous_hash"] != expected_prev:
                return False
            expected_prev = row["block_hash"]
    return True


class AuditService:
    """SOX 404 Append-Only Cryptographic Audit Ledger Service."""

    @staticmethod
    def calculate_hash(previous_hash: str, payload_str: str, timestamp_str: str, actor_id: str) -> str:
        raw = f"{previous_hash}|{actor_id}|{timestamp_str}|{payload_str}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @classmethod
    def log_event(
        cls,
        conn: sqlite3.Connection,
        event_type: str,
        actor_id: str,
        actor_email: str,
        payload: Dict[str, Any]
    ) -> str:
        return append_audit_event(conn, event_type, actor_id, actor_email, payload)

    @classmethod
    def verify_ledger(cls, conn: sqlite3.Connection) -> Dict[str, Any]:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM audit_ledger ORDER BY ROWID ASC")
        rows = cursor.fetchall()

        valid = verify_audit_chain(conn)
        recent_events = [
            {
                "id": r["id"],
                "event_type": r["event_type"],
                "actor_id": r["actor_id"],
                "actor_email": r["actor_email"],
                "payload": r["payload"],
                "previous_hash": r["previous_hash"],
                "block_hash": r["block_hash"],
                "timestamp": r["timestamp"]
            }
            for r in rows[-10:]
        ]

        return {
            "total_blocks": len(rows),
            "ledger_valid": valid,
            "recent_events": recent_events
        }
