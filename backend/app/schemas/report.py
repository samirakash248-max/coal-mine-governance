import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict
from app.models.report import ReportStatus, ReportType

class ReportResponse(BaseModel):
    id: uuid.UUID
    mine_id: uuid.UUID
    title: str
    type: ReportType
    status: ReportStatus
    data_snapshot: Dict[str, Any]
    generated_by_id: Optional[uuid.UUID]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ReportStatusUpdate(BaseModel):
    status: ReportStatus

class ReportGenerateRequest(BaseModel):
    title: str
    type: ReportType

# Analytics Schemas
class TrendDataPoint(BaseModel):
    date: str
    value: float
    secondary_value: Optional[float] = None

class RegionalCompareData(BaseModel):
    region_name: str
    avg_compliance: float
    total_incidents: int
    avg_risk: float
