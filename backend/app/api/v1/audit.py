from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.database import get_db
from app.models.user import User
from app.models.workflow import AuditLog
from app.schemas.workflow import AuditLogResponse
from app.api.deps import get_current_user
import uuid

router = APIRouter()

@router.get("/", response_model=list[AuditLogResponse])
async def get_global_audit_timeline(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    entity_type: Optional[str] = None,
    action: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(AuditLog)
    
    if entity_type:
        stmt = stmt.where(AuditLog.entity_type == entity_type)
    if action:
        stmt = stmt.where(AuditLog.action == action)
        
    stmt = stmt.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    logs = result.scalars().all()
    for log in logs:
        setattr(log, 'timestamp', log.created_at)
        
    return logs

@router.get("/{entity_type}/{entity_id}", response_model=list[AuditLogResponse])
async def get_audit_timeline(
    entity_type: str,
    entity_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(AuditLog).where(
        AuditLog.entity_type == entity_type,
        AuditLog.entity_id == entity_id
    ).order_by(AuditLog.created_at.desc())
    
    result = await db.execute(stmt)
    logs = result.scalars().all()
    for log in logs:
        setattr(log, 'timestamp', log.created_at)
        
    return logs
