import sqlite3
from fastapi import APIRouter, Depends
from app.db.session import get_db
from app.models.audit import AuditBlock, AuditLedgerResponse, IntegrationStatusResponse
from app.services.audit_service import verify_audit_chain

router = APIRouter(tags=["Audit & Integrations"])


@router.get("/audit/ledger", response_model=AuditLedgerResponse)
def get_audit_ledger(db: sqlite3.Connection = Depends(get_db)):
    """Retrieve append-only cryptographic SOX 404 audit ledger."""
    cursor = db.cursor()
    cursor.execute("SELECT * FROM audit_ledger ORDER BY timestamp DESC, rowid DESC LIMIT 20")
    rows = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) AS total FROM audit_ledger")
    total_blocks = cursor.fetchone()["total"]

    is_valid = verify_audit_chain(db)
    blocks = [
        AuditBlock(
            id=r["id"],
            event_type=r["event_type"],
            actor_id=r["actor_id"],
            actor_email=r["actor_email"],
            payload=r["payload"],
            previous_hash=r["previous_hash"],
            block_hash=r["block_hash"],
            timestamp=r["timestamp"]
        )
        for r in rows
    ]

    return AuditLedgerResponse(
        total_blocks=total_blocks,
        ledger_valid=is_valid,
        recent_events=blocks
    )


@router.get("/integrations/status", response_model=IntegrationStatusResponse)
def get_integration_status():
    """Retrieve HCM and payroll connector status (Workday, SAP, ADP, RabbitMQ Outbox)."""
    return IntegrationStatusResponse(
        connectors=[
            {
                "system": "Workday HCM",
                "status": "HEALTHY",
                "last_sync_time": "2023-10-20 04:00:00 UTC",
                "pending_outbox_count": 0
            },
            {
                "system": "SAP SuccessFactors",
                "status": "HEALTHY",
                "last_sync_time": "2023-10-20 04:15:00 UTC",
                "pending_outbox_count": 0
            },
            {
                "system": "ADP Payroll Engine",
                "status": "HEALTHY",
                "last_sync_time": "2023-10-20 04:30:00 UTC",
                "pending_outbox_count": 0
            },
            {
                "system": "RabbitMQ Outbox Dispatcher",
                "status": "ONLINE",
                "last_sync_time": "2023-10-20 05:00:00 UTC",
                "pending_outbox_count": 0
            }
        ]
    )
