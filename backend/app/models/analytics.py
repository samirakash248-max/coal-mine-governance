import uuid
from typing import Optional
from datetime import datetime
from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy import JSON as JSONB
from sqlalchemy.orm import Mapped, mapped_column
from .base import BaseModel

class RiskHistory(BaseModel):
    __tablename__ = "risk_history"
    
    mine_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("mines.id", ondelete="CASCADE"), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False) # 0 to 100
    factors: Mapped[dict] = mapped_column(JSONB, nullable=False) # Explainable factors
    evaluated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

class AnomalyEvent(BaseModel):
    __tablename__ = "anomaly_events"
    
    mine_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("mines.id", ondelete="CASCADE"), nullable=False)
    what_was_abnormal: Mapped[str] = mapped_column(String(255), nullable=False)
    baseline_reference: Mapped[str] = mapped_column(String(255), nullable=False)
    observed_value: Mapped[str] = mapped_column(String(255), nullable=False)
    anomaly_signal: Mapped[str] = mapped_column(String(255), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

class RecurringIssue(BaseModel):
    __tablename__ = "recurring_issues"
    
    mine_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("mines.id", ondelete="CASCADE"), nullable=False)
    recurrence_count: Mapped[int] = mapped_column(Integer, nullable=False)
    time_window_days: Mapped[int] = mapped_column(Integer, nullable=False)
    location_details: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    issue_category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    related_record_ids: Mapped[list[str]] = mapped_column(JSONB, nullable=False) # List of string UUIDs
    recurrence_signal: Mapped[str] = mapped_column(String(255), nullable=False)
