import hashlib
import json
import uuid
from typing import Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.workflow import AuditLog
from app.models.user import User

async def log_audit_event(
    db: AsyncSession,
    user: Optional[User],
    action: str,
    entity_type: str,
    entity_id: uuid.UUID,
    before_state: Optional[dict] = None,
    after_state: Optional[dict] = None
) -> AuditLog:
    """
    Creates an immutable, cryptographically chained audit log.
    """
    
    # 1. Fetch the previous hash for this entity type to maintain a chain
    stmt = select(AuditLog.hash_signature).where(
        AuditLog.entity_type == entity_type
    ).order_by(AuditLog.created_at.desc()).limit(1)
    
    result = await db.execute(stmt)
    previous_hash = result.scalar_one_or_none() or "0000000000000000000000000000000000000000000000000000000000000000"
    
    user_id_str = str(user.id) if user else "SYSTEM"
    role_str = user.role if user else "SYSTEM"
    
    # 2. Construct canonical payload
    payload = {
        "previous_hash": previous_hash,
        "user_id": user_id_str,
        "action": action,
        "entity_type": entity_type,
        "entity_id": str(entity_id),
        "before_state": before_state,
        "after_state": after_state
    }
    
    canonical_string = json.dumps(payload, sort_keys=True, default=str)
    
    # 3. Compute SHA256
    signature = hashlib.sha256(canonical_string.encode('utf-8')).hexdigest()
    
    # 4. Save
    log = AuditLog(
        user_id=user.id if user else None,
        role=role_str,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        before_state=before_state,
        after_state=after_state,
        previous_hash=previous_hash,
        hash_signature=signature
    )
    
    db.add(log)
    await db.flush() # Flush to get it into the transaction
    
    return log
