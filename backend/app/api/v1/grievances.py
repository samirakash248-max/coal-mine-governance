from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.database import get_db
from app.models.user import User
from app.api.deps import get_current_user, get_ai_provider_dep, require_permission
from app.core.permissions import Permission
from app.providers.ai.base import AIProvider
from app.models.grievance import Grievance, GrievanceStatus
from app.schemas.secondary import GrievanceResponse, GrievanceCreate, ApplyAISuggestion
from app.services.grievance_ai import GrievanceAIProcessor

router = APIRouter()

@router.get("/", response_model=list[GrievanceResponse])
async def list_grievances(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.GRIEVANCE_READ))
):
    stmt = select(Grievance).where(Grievance.mine_id == current_user.mine_id).order_by(Grievance.created_at.desc())
    return (await db.execute(stmt)).scalars().all()

@router.post("/", response_model=GrievanceResponse)
async def create_grievance(
    req: GrievanceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.GRIEVANCE_CREATE)),
    ai_provider: AIProvider = Depends(get_ai_provider_dep)
):
    doc = Grievance(
        mine_id=current_user.mine_id,
        submitter_id=current_user.id,
        title=req.title,
        description=req.description,
        status=GrievanceStatus.PENDING
    )
    db.add(doc)
    await db.flush()
    
    # Trigger AI triage (await for prototype ease)
    processor = GrievanceAIProcessor(db, ai_provider)
    await processor.process_new_grievance(doc.id)
    
    await db.refresh(doc)
    return doc

@router.put("/{grievance_id}/apply-ai", response_model=GrievanceResponse)
async def apply_ai_suggestion(
    grievance_id: uuid.UUID,
    req: ApplyAISuggestion,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.GRIEVANCE_UPDATE))
):
    stmt = select(Grievance).where(Grievance.id == grievance_id, Grievance.mine_id == current_user.mine_id)
    doc = (await db.execute(stmt)).scalar_one_or_none()
    
    if not doc:
        raise HTTPException(404, "Not found")
        
    doc.category = req.category
    doc.status = GrievanceStatus.INVESTIGATING
    await db.commit()
    await db.refresh(doc)
    return doc

