import uuid
from typing import Optional
from enum import Enum
from sqlalchemy import String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy import JSON as JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel

class ReportType(str, Enum):
    COMPLIANCE = "COMPLIANCE"
    INCIDENT = "INCIDENT"
    ENVIRONMENTAL = "ENVIRONMENTAL"
    CONTRACTOR = "CONTRACTOR"
    GOVERNANCE = "GOVERNANCE"

class ReportStatus(str, Enum):
    DRAFT = "DRAFT"
    REVIEWED = "REVIEWED"
    APPROVED = "APPROVED"

class Report(BaseModel):
    __tablename__ = "reports"
    mine_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("mines.id", ondelete="CASCADE"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[ReportType] = mapped_column(SQLEnum(ReportType, native_enum=False, length=50), nullable=False)
    status: Mapped[ReportStatus] = mapped_column(SQLEnum(ReportStatus, native_enum=False, length=50), default=ReportStatus.DRAFT, nullable=False)
    data_snapshot: Mapped[dict] = mapped_column(JSONB, default={}, nullable=False)
    generated_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True)
