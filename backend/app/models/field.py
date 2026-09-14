from geoalchemy2 import Geometry
import uuid
import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, Text, Enum as SQLEnum, Float, Boolean
from sqlalchemy import JSON as JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel

class InspectionStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    VERIFIED = "VERIFIED"
    CLOSED = "CLOSED"

class SafetyEventType(str, enum.Enum):
    INCIDENT = "INCIDENT"
    NEAR_MISS = "NEAR_MISS"
    HAZARD_OBSERVATION = "HAZARD_OBSERVATION"
    UNSAFE_CONDITION = "UNSAFE_CONDITION"

class SafetyEventCategory(str, enum.Enum):
    SAFETY = "SAFETY"
    ENVIRONMENT = "ENVIRONMENT"
    OPERATIONS = "OPERATIONS"
    SECURITY = "SECURITY"
    OTHER = "OTHER"

class SafetyEventSeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class ActionStatus(str, enum.Enum):
    OPEN = "OPEN"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    EVIDENCE_SUBMITTED = "EVIDENCE_SUBMITTED"
    UNDER_VERIFICATION = "UNDER_VERIFICATION"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

class Inspection(BaseModel):
    __tablename__ = "inspections"
    
    mine_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("mines.id", ondelete="CASCADE"), nullable=False, index=True)
    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    inspector_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    
    type: Mapped[str] = mapped_column(String(100), nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    checklist_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    location_geom = mapped_column(Geometry('POINT', srid=4326), nullable=True)
    status: Mapped[InspectionStatus] = mapped_column(SQLEnum(InspectionStatus), nullable=False, default=InspectionStatus.DRAFT, index=True)
    
    idempotency_key: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)

class SafetyEvent(BaseModel):
    __tablename__ = "safety_events"
    
    mine_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("mines.id", ondelete="CASCADE"), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Human-approved or final fields
    type: Mapped[Optional[SafetyEventType]] = mapped_column(SQLEnum(SafetyEventType), nullable=True, index=True)
    category: Mapped[Optional[SafetyEventCategory]] = mapped_column(SQLEnum(SafetyEventCategory), nullable=True)
    severity: Mapped[Optional[SafetyEventSeverity]] = mapped_column(SQLEnum(SafetyEventSeverity), nullable=True, index=True)
    
    # AI predicted fields
    ai_event_type: Mapped[Optional[SafetyEventType]] = mapped_column(SQLEnum(SafetyEventType), nullable=True)
    ai_category: Mapped[Optional[SafetyEventCategory]] = mapped_column(SQLEnum(SafetyEventCategory), nullable=True)
    ai_severity: Mapped[Optional[SafetyEventSeverity]] = mapped_column(SQLEnum(SafetyEventSeverity), nullable=True)
    ai_prediction_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Review tracking
    human_reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    human_reviewer_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_ai_overridden: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Risk Engine outputs
    risk_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    risk_level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True) # LOW, MEDIUM, HIGH, CRITICAL
    risk_factors: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    location_details: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    location_geom = mapped_column(Geometry('POINT', srid=4326), nullable=True)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    is_anonymous: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    reporter_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    inspection_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("inspections.id", ondelete="SET NULL"), nullable=True)
    
    idempotency_key: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)

class CorrectiveAction(BaseModel):
    __tablename__ = "corrective_actions"
    
    mine_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("mines.id", ondelete="CASCADE"), nullable=False)
    source_inspection_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("inspections.id", ondelete="SET NULL"), nullable=True)
    source_event_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("safety_events.id", ondelete="SET NULL"), nullable=True)
    
    description: Mapped[str] = mapped_column(Text, nullable=False)
    assigned_to_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[ActionStatus] = mapped_column(SQLEnum(ActionStatus), nullable=False, default=ActionStatus.OPEN)


