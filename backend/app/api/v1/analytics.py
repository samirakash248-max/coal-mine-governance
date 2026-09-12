from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.schemas.report import TrendDataPoint, RegionalCompareData

router = APIRouter()

@router.get("/trends/safety", response_model=List[TrendDataPoint])
async def get_safety_trends(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Mocking time-series data for the dashboard chart
    return [
        {"date": "2023-01", "value": 12, "secondary_value": 4},
        {"date": "2023-02", "value": 15, "secondary_value": 6},
        {"date": "2023-03", "value": 8, "secondary_value": 2},
        {"date": "2023-04", "value": 5, "secondary_value": 1}
    ]

@router.get("/compare/regions", response_model=List[RegionalCompareData])
async def compare_regions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Mocking aggregate comparison
    return [
        {"region_name": "Eastern Coalfields", "avg_compliance": 88.5, "total_incidents": 42, "avg_risk": 25.0},
        {"region_name": "Western Coalfields", "avg_compliance": 92.0, "total_incidents": 15, "avg_risk": 15.5},
        {"region_name": "Northern Coalfields", "avg_compliance": 75.5, "total_incidents": 89, "avg_risk": 60.0}
    ]
