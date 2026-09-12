from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import uuid
from typing import Dict, Any

from app.models.hierarchy import Mine
from app.models.field import SafetyEvent, SafetyEventType, SafetyEventSeverity
from app.providers.weather.base import WeatherProvider

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
            return {"status": "error", "message": "Mine location unknown"}
            
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
        
        return {
            "advisory_risk_level": final_level,
            "weather": {
                "temperature": weather_data.temperature_celsius,
                "rainfall_mm": weather_data.rainfall_mm,
                "description": weather_data.description,
                "provider": "Mock" if weather_data.is_simulated else "Real"
            },
            "open_water_hazards": len(water_hazards),
            "disclaimer": "This is an application-generated advisory indicator, not an official statutory determination."
        }
