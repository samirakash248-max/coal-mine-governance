
from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from app.models.field import InspectionStatus

class InspectionCreate(BaseModel):
    mine_id: uuid.UUID
    department_id: Optional[uuid.UUID] = None
    type: str
    date: datetime
    checklist_data: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    idempotency_key: Optional[str] = None

class InspectionResponse(BaseModel):
    id: uuid.UUID
    mine_id: uuid.UUID
    department_id: Optional[uuid.UUID]
    inspector_id: uuid.UUID
    type: str
    date: datetime
    checklist_data: Optional[Dict[str, Any]]
    notes: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    status: InspectionStatus
    idempotency_key: Optional[str]
    model_config = ConfigDict(from_attributes=True)

