from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User, Role
from app.models.field import SafetyEvent, CorrectiveAction, SafetyEventType, SafetyEventCategory, SafetyEventSeverity
from app.schemas.field import SafetyEventCreate, SafetyEventResponse, CorrectiveActionResponse
from app.api.deps import get_current_user, require_permission
from app.core.permissions import Permission
from app.core.security import generate_cryptographic_signature
from app.services.workflow_service import WorkflowService
from app.services.risk_engine import RiskEngine

router = APIRouter()

class ReviewRequest(BaseModel):
    type: SafetyEventType
    category: SafetyEventCategory
    severity: SafetyEventSeverity

@router.get("/events/stats")
async def get_event_stats(db: AsyncSession = Depends(get_db), current_user: User = Depends(require_permission(Permission.SAFETY_READ))):
    from sqlalchemy import case, func
    stmt = select(
        func.count(SafetyEvent.id).label('total'),
        func.sum(case((SafetyEvent.type == 'NEAR_MISS', 1), else_=0)).label('near_misses'),
        func.sum(case((SafetyEvent.type == 'INCIDENT', 1), else_=0)).label('incidents'),
        func.sum(case((SafetyEvent.severity == 'CRITICAL', 1), else_=0)).label('critical')
    )
    if current_user.mine_id:
        stmt = stmt.where(SafetyEvent.mine_id == current_user.mine_id)
        
    result = (await db.execute(stmt)).first()
    
    return {
        "total_events": result.total or 0,
        "near_misses": result.near_misses or 0,
        "incidents": result.incidents or 0,
        "critical_hazards": result.critical or 0
    }

@router.post("/events", response_model=SafetyEventResponse)
async def create_safety_event(
    event_in: SafetyEventCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.SAFETY_CREATE))
):
    # Idempotency check for PWA Offline Sync
    if event_in.idempotency_key:
        stmt = select(SafetyEvent).where(SafetyEvent.idempotency_key == event_in.idempotency_key)
        existing = (await db.execute(stmt)).scalar_one_or_none()
        if existing:
            return existing
            
    # Assuming the frontend/AI provider passed AI predictions inside the event_in payload
    # For prototype, we will just map them
    event_data = event_in.model_dump()
    
    if current_user.mine_id and event_data.get("mine_id") != current_user.mine_id:
        raise HTTPException(status_code=403, detail="Cannot create event for another mine")
    event = SafetyEvent(
        **event_data,
        date=datetime.now(timezone.utc),
        reporter_id=current_user.id
    )
    event.cryptographic_signature = generate_cryptographic_signature(event_data)
    
    # Check if AI fields were provided
    # If the provider wants to separate AI vs Final immediately:
    if "ai_event_type" in event_data:
        event.ai_prediction_timestamp = datetime.now(timezone.utc)
        
    db.add(event)
    await db.commit()
    await db.refresh(event)
    
    # Calculate Risk Score
    risk_engine = RiskEngine(db)
    event = await risk_engine.evaluate_event_risk(event)
    
    return event

@router.post("/events/{event_id}/review", response_model=SafetyEventResponse)
async def review_event(
    event_id: uuid.UUID,
    req: ReviewRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.SAFETY_UPDATE))
):
    event = (await db.execute(select(SafetyEvent).where(SafetyEvent.id == event_id))).scalar_one_or_none()
    if not event or (current_user.mine_id and event.mine_id != current_user.mine_id):
        raise HTTPException(status_code=404, detail="Event not found")
    workflow_svc = WorkflowService(db, current_user)
    try:
        event = await workflow_svc.review_ai_prediction(
            event_id=event_id,
            event_type=req.type,
            category=req.category,
            severity=req.severity
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    # Recalculate Risk based on human review
    risk_engine = RiskEngine(db)
    event = await risk_engine.evaluate_event_risk(event)
    
    return event

@router.get("/events", response_model=list[SafetyEventResponse])
async def get_events(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.SAFETY_READ))
):
    stmt = select(SafetyEvent)
    
    # Scope check
    if current_user.mine_id:
        stmt = stmt.where(SafetyEvent.mine_id == current_user.mine_id)
        
    stmt = stmt.offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    events = result.scalars().all()
    
    # ANONYMIZATION LOGIC
    # Only SYSTEM_ADMIN and REGULATORY_AUDITOR can see reporter_id for anonymous events.
    can_deanonymize = current_user.role in [Role.SYSTEM_ADMIN, Role.REGULATORY_AUDITOR]
    
    for e in events:
        if e.is_anonymous and not can_deanonymize:
            # Nullify the reporter ID before serialization
            e.reporter_id = None
            
    return events

@router.get("/events/{id}", response_model=SafetyEventResponse)
async def get_event(id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_permission(Permission.SAFETY_READ))):
    stmt = select(SafetyEvent).where(SafetyEvent.id == id)
    event = (await db.execute(stmt)).scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if current_user.mine_id and event.mine_id != current_user.mine_id:
        raise HTTPException(status_code=403, detail="Access denied")
    return event

@router.get("/actions", response_model=list[CorrectiveActionResponse])
async def get_actions(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.SAFETY_READ))
):
    stmt = select(CorrectiveAction).order_by(CorrectiveAction.due_date.asc()).offset(skip).limit(limit)
    
    if current_user.mine_id:
        stmt = stmt.where(CorrectiveAction.mine_id == current_user.mine_id)
        
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/events/spatial/{mine_id}", response_model=list[SafetyEventResponse])
async def get_spatial_events(
    mine_id: uuid.UUID,
    radius_km: float = 50.0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.SAFETY_READ))
):
    from sqlalchemy import func
    from app.models.hierarchy import Mine
    
    target_mine = (await db.execute(select(Mine).where(Mine.id == mine_id))).scalar_one_or_none()
    if not target_mine or not target_mine.location_geom:
        return []
        
    stmt = select(SafetyEvent).where(SafetyEvent.location_geom.is_not(None))
    
    if current_user.mine_id:
        if current_user.mine_id != mine_id:
            return []
        stmt = stmt.where(SafetyEvent.mine_id == current_user.mine_id)
        
    # Spatial filter for events within radius of the target mine
    radius_deg = radius_km / 111.0
    stmt = stmt.where(
        func.ST_DWithin(SafetyEvent.location_geom, target_mine.location_geom, radius_deg)
    ).limit(50)
    
    result = await db.execute(stmt)
    return result.scalars().all()

