import uuid
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.models.compliance import ComplianceStatus

class ComplianceRequirementBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: str
    frequency: Optional[str] = None
    source_reference: Optional[str] = None
    applicable_mine_id: Optional[uuid.UUID] = None

class ComplianceRequirementResponse(ComplianceRequirementBase):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)

class ComplianceRecordBase(BaseModel):
    requirement_id: uuid.UUID
    due_date: date
    status: ComplianceStatus
    responsible_department_id: Optional[uuid.UUID] = None
    responsible_officer_id: Optional[uuid.UUID] = None
    submission_date: Optional[datetime] = None
    verification_date: Optional[datetime] = None

class ComplianceRecordResponse(ComplianceRecordBase):
    id: uuid.UUID
    requirement: Optional[ComplianceRequirementResponse] = None
    model_config = ConfigDict(from_attributes=True)
