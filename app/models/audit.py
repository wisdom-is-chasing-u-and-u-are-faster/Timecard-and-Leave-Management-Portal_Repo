from typing import List, Optional
from pydantic import BaseModel


class AuditBlock(BaseModel):
    id: str
    event_type: str
    actor_id: str
    actor_email: str
    payload: str
    previous_hash: str
    block_hash: str
    timestamp: str


class AuditBlockItem(BaseModel):
    event_id: str
    event_type: str
    actor: str
    timestamp: str
    hash: str


class AuditLedgerResponse(BaseModel):
    total_blocks: int
    ledger_valid: bool
    recent_events: List[AuditBlock]


class ConnectorItem(BaseModel):
    system: str
    status: str
    last_sync_time: Optional[str] = None
    pending_outbox_count: Optional[int] = 0


class IntegrationStatusResponse(BaseModel):
    connectors: List[ConnectorItem]
