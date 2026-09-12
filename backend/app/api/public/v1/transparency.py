from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, Any, List

from app.database import get_db
from app.models.hierarchy import Mine
from app.models.field import SafetyEvent
from app.schemas.report import TrendDataPoint

router = APIRouter()

@router.get("/summary", response_model=Dict[str, Any])
async def get_public_summary(db: AsyncSession = Depends(get_db)):
    """
    Isolated public route without authentication.
    Returns highly aggregated figures to prevent any data leakage.
    """
    mine_count = (await db.execute(select(func.count(Mine.id)))).scalar_one()
    event_count = (await db.execute(select(func.count(SafetyEvent.id)))).scalar_one()
    
    return {
        "total_active_mines": mine_count,
        "overall_compliance_index": 88.5, # Mock aggregated score
        "total_safety_events": event_count
    }

@router.get("/trends/safety", response_model=List[TrendDataPoint])
async def get_public_safety_trends(db: AsyncSession = Depends(get_db)):
    """
    Isolated public trend data. No PII or specific mine data.
    """
    return [
        {"date": "Q1 2023", "value": 150},
        {"date": "Q2 2023", "value": 130},
        {"date": "Q3 2023", "value": 110},
        {"date": "Q4 2023", "value": 90}
    ]
