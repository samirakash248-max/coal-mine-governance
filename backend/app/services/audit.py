import hashlib
import json
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.workflow import AuditLog
from fastapi import Request

async def get_last_audit_hash(db: AsyncSession) -> str:
    # Get the most recent audit log to continue the chain
    stmt = select(AuditLog).order_by(AuditLog.created_at.desc()).limit(1)
    result = await db.execute(stmt)
    last_log = result.scalar_one_or_none()
    return last_log.hash_signature if last_log else ("0" * 64)

async def log_audit_event(
    db: AsyncSession,
    user_id: Optional[uuid.UUID],
    role: Optional[str],
    action: str,
    entity_type: str,
    entity_id: Optional[uuid.UUID],
    request: Optional[Request] = None,
    before_state: Optional[dict] = None,
    after_state: Optional[dict] = None
):
    prev_hash = await get_last_audit_hash(db)
    
    payload = f"{prev_hash}|{action}|{entity_type}|{entity_id}|{json.dumps(after_state, default=str) if after_state else ''}"
    current_hash = hashlib.sha256(payload.encode()).hexdigest()
    
    ip_address = "0.0.0.0"
    if request and request.client:
        ip_address = request.client.host
        
    audit_log = AuditLog(
        user_id=user_id,
        role=role or "system",
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        before_state=before_state,
        after_state=after_state,
        previous_hash=prev_hash,
        hash_signature=current_hash
    )
    db.add(audit_log)
    await db.commit()
    return audit_log



