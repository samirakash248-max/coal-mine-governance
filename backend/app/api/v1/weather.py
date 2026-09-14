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

@router.get("/summary", response_model=Dict[str, Any])
async def get_weather_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    weather_provider: WeatherProvider = Depends(get_weather_provider_dep)
):
    from sqlalchemy import select
    from app.models.hierarchy import Mine
    
    service = WeatherRiskService(db, weather_provider)
    
    stmt = select(Mine)
    if current_user.mine_id:
        stmt = stmt.where(Mine.id == current_user.mine_id)
        
    mines = (await db.execute(stmt)).scalars().all()
    
    # We only analyze up to 3 mines for the summary to avoid rate limits
    highest_risk = "LOW"
    major_factors = []
    affected_mines = []
    last_observation = None
    
    risk_weights = {"LOW": 1, "ELEVATED": 2, "SEVERE": 3}
    
    for m in mines[:3]:
        risk = await service.calculate_mine_risk(m.id)
        if risk.get("status") == "error": continue
        
        lvl = risk.get("advisory_risk_level", "LOW")
        if risk_weights.get(lvl, 1) > risk_weights.get(highest_risk, 1):
            highest_risk = lvl
            
        if lvl in ["ELEVATED", "SEVERE"]:
            affected_mines.append(m.name)
            
        factors = risk.get("assessment", {}).get("factors", [])
        for f in factors:
            if f not in major_factors and "Normal" not in f:
                major_factors.append(f)
                
        last_observation = risk.get("weather", {}).get("timestamp")
        
    return {
        "highest_risk": highest_risk,
        "affected_mines": affected_mines,
        "major_factors": major_factors[:3],
        "last_observation": last_observation
    }

@router.post("/risk/{mine_id}/acknowledge")
async def acknowledge_weather_risk(
    mine_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    weather_provider: WeatherProvider = Depends(get_weather_provider_dep)
):
    from app.models.workflow import AuditLog
    import hashlib
    import json
    
    # Calculate current risk to record it
    service = WeatherRiskService(db, weather_provider)
    risk = await service.calculate_mine_risk(mine_id)
    
    log = AuditLog(
        user_id=current_user.id,
        role=current_user.role,
        action="ACKNOWLEDGE",
        entity_type="WeatherRisk",
        entity_id=mine_id,
        before_state={"status": "UNACKNOWLEDGED"},
        after_state={"status": "ACKNOWLEDGED", "risk": risk.get("advisory_risk_level")}
    )
    
    # Generate signature
    sig_payload = f"{log.action}:{log.entity_id}:{current_user.id}:{json.dumps(log.after_state)}"
    log.hash_signature = hashlib.sha256(sig_payload.encode()).hexdigest()
    
    db.add(log)
    await db.commit()
    return {"status": "success"}
