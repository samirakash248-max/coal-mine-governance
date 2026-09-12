import uuid
from datetime import datetime, date
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, ConfigDict
from app.models.grievance import GrievanceStatus

# Contractors & Workforce
class ContractorResponse(BaseModel):
    id: uuid.UUID
    mine_id: uuid.UUID
    name: str
    work_type: str
    risk_indicator: int
    active: bool
    model_config = ConfigDict(from_attributes=True)

class WorkerResponse(BaseModel):
    id: uuid.UUID
    mine_id: uuid.UUID
    contractor_id: Optional[uuid.UUID]
    name: str
    training_metadata: Dict[str, Any]
    model_config = ConfigDict(from_attributes=True)

# Operations
class EnvironmentReadingResponse(BaseModel):
    id: uuid.UUID
    parameter: str
    value: float
    unit: str
    is_simulated: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ProductionRecordResponse(BaseModel):
    id: uuid.UUID
    date: date
    target: float
    actual: float
    deviation: float
    model_config = ConfigDict(from_attributes=True)

# Grievances
class GrievanceCreate(BaseModel):
    title: str
    description: str

class GrievanceResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    category: Optional[str]
    status: GrievanceStatus
    ai_suggestions: Dict[str, Any]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
    
class ApplyAISuggestion(BaseModel):
    category: str
