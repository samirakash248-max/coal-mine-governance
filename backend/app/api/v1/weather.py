from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
import uuid

from app.database import get_db
from app.models.user import User
from app.api.deps import get_current_user, get_weather_provider_dep
from app.providers.weather.base import WeatherProvider
from app.services.weather_risk import WeatherRiskService

router = APIRouter()

@router.get("/risk/{mine_id}", response_model=Dict[str, Any])
async def get_weather_risk(
    mine_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    weather_provider: WeatherProvider = Depends(get_weather_provider_dep)
):
    service = WeatherRiskService(db, weather_provider)
    result = await service.calculate_mine_risk(mine_id)
    return result
