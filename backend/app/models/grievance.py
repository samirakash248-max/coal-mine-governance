import uuid
from typing import Optional
from enum import Enum
from sqlalchemy import String, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy import JSON as JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel

class GrievanceStatus(str, Enum):
    PENDING = "PENDING"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

class Grievance(BaseModel):
    __tablename__ = "grievances"
    mine_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("mines.id", ondelete="CASCADE"), nullable=False)
    submitter_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[GrievanceStatus] = mapped_column(SQLEnum(GrievanceStatus), default=GrievanceStatus.PENDING, nullable=False)
    assigned_department_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    
    ai_suggestions: Mapped[dict] = mapped_column(JSONB, default={}, nullable=False)
