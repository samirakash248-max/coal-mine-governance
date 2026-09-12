from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.models.workflow import AuditLog
from app.schemas.workflow import AuditLogResponse
from app.api.deps import get_current_user
import uuid

router = APIRouter()

@router.get("/{entity_type}/{entity_id}", response_model=list[AuditLogResponse])
async def get_audit_timeline(
    entity_type: str,
    entity_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # In a real app, verify the user has access to this entity_id based on scope.
    stmt = select(AuditLog).where(
        AuditLog.entity_type == entity_type,
        AuditLog.entity_id == entity_id
    ).order_by(AuditLog.created_at.desc())
    
    result = await db.execute(stmt)
    
    # Map created_at to timestamp for the response schema
    logs = result.scalars().all()
    for log in logs:
        setattr(log, 'timestamp', log.created_at)
        
    return logs
