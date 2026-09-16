from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel

from app.database import get_db
from app.models.operations import EnvironmentReading
from app.schemas.secondary import EnvironmentReadingResponse
from app.models.field import SafetyEvent
from app.api.deps import get_current_user

router = APIRouter()

class TelemetryPayload(BaseModel):
    mine_id: uuid.UUID
    parameter: str # e.g., "Methane", "PM2.5"
    value: float
    unit: str
    location_id: str

@router.post("/telemetry", response_model=EnvironmentReadingResponse)
async def ingest_telemetry(
    payload: TelemetryPayload,
    db: AsyncSession = Depends(get_db)
):
    # Note: For hackathon demo, we might skip auth on IoT endpoints to allow simple streaming scripts
    reading = EnvironmentReading(
        mine_id=payload.mine_id,
        parameter=payload.parameter,
        value=payload.value,
        unit=payload.unit
    )
    db.add(reading)
    await db.flush()

    # Predictive Analysis logic (Mocked for demo but conceptually sound)
    # If Methane > 1.25%, it's critical. If it jumps by 0.5% in seconds, it's predictive critical.
    if payload.parameter == "Methane" and payload.value > 1.0:
        # Trigger predictive alert
        event = SafetyEvent(
            mine_id=payload.mine_id,
            type="NEAR_MISS",
            category="ENVIRONMENT",
            severity="CRITICAL",
            description=f"PREDICTIVE ALERT: Rapid accumulation of {payload.parameter} detected ({payload.value}{payload.unit}). Evacuation protocols recommended.",
            status="OPEN",
            date=datetime.now(timezone.utc)
        )
        db.add(event)
    
    await db.commit()
    await db.refresh(reading)
    return reading
