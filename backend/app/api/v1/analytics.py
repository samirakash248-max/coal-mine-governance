from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta, timezone
from typing import List

from app.database import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.schemas.report import TrendDataPoint, RegionalCompareData
from app.models.field import SafetyEvent, SafetyEventType
from app.schemas.field import SafetyEventResponse
from app.models.hierarchy import Mine, Region

router = APIRouter()

@router.get("/trends/safety", response_model=List[TrendDataPoint])
async def get_safety_trends(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get events from last 6 months
    six_months_ago = datetime.now(timezone.utc) - timedelta(days=180)
    
    stmt = select(SafetyEvent).where(SafetyEvent.created_at >= six_months_ago)
    if current_user.mine_id:
        stmt = stmt.where(SafetyEvent.mine_id == current_user.mine_id)
        
    events = (await db.execute(stmt)).scalars().all()
    
    # Group by month (YYYY-MM) in Python for simplicity
    trends = {}
    for ev in events:
        month = ev.created_at.strftime("%Y-%m")
        if month not in trends:
            trends[month] = {"incidents": 0, "near_misses": 0}
            
        if ev.type == SafetyEventType.INCIDENT:
            trends[month]["incidents"] += 1
        elif ev.type == SafetyEventType.NEAR_MISS:
            trends[month]["near_misses"] += 1
            
    # Format for response
    result = []
    # Ensure last 6 months exist even if empty
    for i in range(5, -1, -1):
        d = datetime.now(timezone.utc) - timedelta(days=i*30)
        m = d.strftime("%Y-%m")
        if m not in trends:
            trends[m] = {"incidents": 0, "near_misses": 0}
            
    for month in sorted(trends.keys()):
        result.append(TrendDataPoint(
            date=month,
            value=trends[month]["incidents"],
            secondary_value=trends[month]["near_misses"]
        ))
        
    return result

@router.get("/compare/regions", response_model=List[RegionalCompareData])
async def compare_regions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.mine_id:
        # If user is restricted to a mine, we show mine vs others in same region, or just their mine
        mine = (await db.execute(select(Mine).where(Mine.id == current_user.mine_id))).scalar_one()
        events = (await db.execute(select(SafetyEvent).where(SafetyEvent.mine_id == current_user.mine_id))).scalars().all()
        
        incidents = sum(1 for e in events if e.type == SafetyEventType.INCIDENT)
        avg_r = sum(e.risk_score or 0 for e in events) / max(len(events), 1)
        
        return [RegionalCompareData(
            region_name=mine.name, # Use mine name since they are restricted
            avg_compliance=100.0, # Placeholder until compliance is fully aggregated
            total_incidents=incidents,
            avg_risk=avg_r
        )]
    else:
        # User is region/corporate -> group by Region
        regions = (await db.execute(select(Region))).scalars().all()
        result = []
        for r in regions:
            # Get mines in region
            mines = (await db.execute(select(Mine).where(Mine.region_id == r.id))).scalars().all()
            mine_ids = [m.id for m in mines]
            
            if not mine_ids:
                continue
                
            events = (await db.execute(select(SafetyEvent).where(SafetyEvent.mine_id.in_(mine_ids)))).scalars().all()
            
            incidents = sum(1 for e in events if e.type == SafetyEventType.INCIDENT)
            avg_r = sum(e.risk_score or 0 for e in events) / max(len(events), 1)
            
            result.append(RegionalCompareData(
                region_name=r.name,
                avg_compliance=90.0, # Placeholder
                total_incidents=incidents,
                avg_risk=avg_r
            ))
            
        return result

@router.get("/risk/cases", response_model=List[SafetyEventResponse])
async def get_high_risk_cases(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(SafetyEvent).where(SafetyEvent.risk_level.in_(["HIGH", "CRITICAL"]))
    if current_user.mine_id:
        stmt = stmt.where(SafetyEvent.mine_id == current_user.mine_id)
        
    stmt = stmt.order_by(SafetyEvent.risk_score.desc().nullslast()).limit(50)
    
    events = (await db.execute(stmt)).scalars().all()
    return events

