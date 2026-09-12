
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.user import User
from app.models.field import Inspection, SafetyEvent, CorrectiveAction
from app.schemas.inspection import InspectionCreate, InspectionResponse
from app.schemas.field import SafetyEventResponse, CorrectiveActionResponse
from app.api.deps import get_current_user
import uuid

router = APIRouter()

@router.get('/stats')
async def get_stats(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    from sqlalchemy import case
    stmt = select(
        func.count(Inspection.id).label('total'),
        func.sum(case((Inspection.status.in_(['CLOSED', 'VERIFIED']), 1), else_=0)).label('completed'),
        func.sum(case((Inspection.status.in_(['SUBMITTED', 'UNDER_REVIEW']), 1), else_=0)).label('pending'),
        func.sum(case((Inspection.status == 'DRAFT', 1), else_=0)).label('scheduled')
    )
    if current_user.mine_id:
        stmt = stmt.where(Inspection.mine_id == current_user.mine_id)
        
    result = (await db.execute(stmt)).first()
    
    total = result.total or 0
    completed = result.completed or 0
    pending = result.pending or 0
    scheduled = result.scheduled or 0
    
    compliance = 0
    if total > 0:
        compliance = int((completed / total) * 100)
        
    return {
        'total': total,
        'completed': completed,
        'pending': pending,
        'scheduled': scheduled,
        'compliance_percentage': compliance
    }

@router.get('/', response_model=list[InspectionResponse])
async def list_inspections(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = select(Inspection).order_by(Inspection.date.desc()).offset(skip).limit(limit)
    if current_user.mine_id:
        stmt = stmt.where(Inspection.mine_id == current_user.mine_id)
    return (await db.execute(stmt)).scalars().all()

@router.post('/', response_model=InspectionResponse)
async def create_inspection(inspection_in: InspectionCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    data = inspection_in.model_dump()
    inspection = Inspection(**data, inspector_id=current_user.id)
    db.add(inspection)
    await db.commit()
    await db.refresh(inspection)
    return inspection

@router.get('/{id}', response_model=InspectionResponse)
async def get_inspection(id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    inspection = (await db.execute(select(Inspection).where(Inspection.id == id))).scalar_one_or_none()
    if not inspection:
        raise HTTPException(status_code=404, detail='Inspection not found')
    return inspection

@router.get('/{id}/findings', response_model=list[SafetyEventResponse])
async def get_findings(id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = select(SafetyEvent).where(SafetyEvent.inspection_id == id)
    return (await db.execute(stmt)).scalars().all()

@router.get('/{id}/actions', response_model=list[CorrectiveActionResponse])
async def get_actions(id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = select(CorrectiveAction).where(CorrectiveAction.source_inspection_id == id)
    return (await db.execute(stmt)).scalars().all()

