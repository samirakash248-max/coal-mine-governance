import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy import JSON as JSONB
from sqlalchemy.orm import Mapped, mapped_column
from .base import BaseModel

class Contractor(BaseModel):
    __tablename__ = "contractors"
    mine_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("mines.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    work_type: Mapped[str] = mapped_column(String(100), nullable=False)
    risk_indicator: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

class Worker(BaseModel):
    __tablename__ = "workers"
    mine_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("mines.id", ondelete="CASCADE"), nullable=False)
    contractor_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("contractors.id", ondelete="SET NULL"), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    training_metadata: Mapped[dict] = mapped_column(JSONB, default={}, nullable=False)

class AttendanceRecord(BaseModel):
    __tablename__ = "attendance_records"
    worker_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workers.id", ondelete="CASCADE"), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    location_data: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_anomaly: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
