import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy import JSON as JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel

class Notification(BaseModel):
    __tablename__ = "notifications"
    
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    notification_type: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. ESCALATION, DEADLINE
    entity_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True) # e.g. CorrectiveAction
    entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
class EscalationRule(BaseModel):
    __tablename__ = "escalation_rules"
    
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    condition: Mapped[str] = mapped_column(String(255), nullable=False) # e.g. SEVERITY=CRITICAL
    delay_hours: Mapped[int] = mapped_column(nullable=False)
    escalate_to_role: Mapped[str] = mapped_column(String(100), nullable=False)

class AuditLog(BaseModel):
    __tablename__ = "audit_logs"
    
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    role: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False) # CREATE, UPDATE, ESCALATE, VERIFY
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    
    before_state: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    after_state: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    previous_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    hash_signature: Mapped[str] = mapped_column(String(64), nullable=False)
