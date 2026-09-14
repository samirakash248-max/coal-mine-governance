from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import uuid
import time
from typing import Dict, Any

from app.models.hierarchy import Mine
from app.models.field import SafetyEvent, SafetyEventType, SafetyEventSeverity
from app.providers.weather.base import WeatherProvider

# Simple in-memory cache to prevent spamming the weather provider
# Maps mine_id -> (timestamp, data)
_WEATHER_CACHE: Dict[str, tuple[float, Dict[str, Any]]] = {}
CACHE_TTL_SECONDS = 15 * 60 # 15 minutes

class WeatherRiskService:
    def __init__(self, db: AsyncSession, provider: WeatherProvider):
        self.db = db
        self.provider = provider
        
    async def calculate_mine_risk(self, mine_id: uuid.UUID) -> Dict[str, Any]:
        """
        Calculates an application-level advisory risk indicator combining weather
        forecast data with unresolved safety events matching drainage/water hazards.
        """
        mine = (await self.db.execute(select(Mine).where(Mine.id == mine_id))).scalar_one_or_none()
        if not mine or not mine.latitude or not mine.longitude:
            return {"status": "error", "message": "Location unavailable"}
            
        mine_id_str = str(mine_id)
        now = time.time()
        
        # Check cache
        if mine_id_str in _WEATHER_CACHE:
            cached_time, cached_data = _WEATHER_CACHE[mine_id_str]
            if now - cached_time < CACHE_TTL_SECONDS:
                cached_data["cached"] = True
                return cached_data

        # Get real or mock weather
        weather_data = await self.provider.get_current(mine.latitude, mine.longitude)
        base_assessment = await self.provider.assess_risk(weather_data)
        
        # Overlay application data (Hazards relating to water/drainage)
        stmt = select(SafetyEvent).where(
            and_(
                SafetyEvent.mine_id == mine_id,
                SafetyEvent.type.in_([SafetyEventType.HAZARD_OBSERVATION, SafetyEventType.UNSAFE_CONDITION])
            )
        )
        events = (await self.db.execute(stmt)).scalars().all()
        
        water_hazards = [e for e in events if "water" in e.description.lower() or "drain" in e.description.lower()]
        
        # Risk elevation logic
        app_risk_level = base_assessment.risk_level.value
        risk_score = 0
        if app_risk_level == "low": risk_score = 1
        elif app_risk_level == "moderate": risk_score = 2
        elif app_risk_level == "high": risk_score = 3
        elif app_risk_level == "severe": risk_score = 4
        
        if len(water_hazards) > 0 and risk_score > 1:
            risk_score += 1 # Elevate due to existing drainage hazards
            
        final_level = "LOW"
        if risk_score == 2: final_level = "ELEVATED"
        if risk_score >= 3: final_level = "SEVERE"
        
        result = {
            "status": "success",
            "advisory_risk_level": final_level,
            "weather": {
                "temperature": weather_data.temperature_celsius,
                "humidity": weather_data.humidity_percent,
                "wind_speed": weather_data.wind_speed_kmh,
                "rainfall_mm": weather_data.rainfall_mm,
                "condition": weather_data.condition,
                "description": weather_data.description,
                "timestamp": weather_data.timestamp.isoformat(),
                "provider": "Mock" if weather_data.is_simulated else "Real"
            },
            "assessment": {
                "risk_level": base_assessment.risk_level,
                "factors": base_assessment.factors,
                "recommendations": base_assessment.recommendations
            },
            "open_water_hazards": len(water_hazards),
            "disclaimer": "AI/Environmental Recommendation. This is an application-generated advisory indicator, not an official statutory determination.",
            "cached": False
        }
        
        # Save to cache if it wasn't an API error
        if weather_data.description != "API Error":
            _WEATHER_CACHE[mine_id_str] = (now, result)
            
        return result
