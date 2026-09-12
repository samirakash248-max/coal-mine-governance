
import uuid
from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .base import BaseModel

class UserSettings(BaseModel):
    __tablename__ = 'user_settings'
    
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    theme: Mapped[str] = mapped_column(String(50), default='system')
    language: Mapped[str] = mapped_column(String(50), default='en')
    timezone: Mapped[str] = mapped_column(String(50), default='UTC')
    default_mine_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

class NotificationPreference(BaseModel):
    __tablename__ = 'notification_preferences'
    
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    inspection_reminders: Mapped[bool] = mapped_column(Boolean, default=True)
    safety_alerts: Mapped[bool] = mapped_column(Boolean, default=True)
    critical_risk_alerts: Mapped[bool] = mapped_column(Boolean, default=True)
    compliance_alerts: Mapped[bool] = mapped_column(Boolean, default=True)
    overdue_action_reminders: Mapped[bool] = mapped_column(Boolean, default=True)
    regulatory_updates: Mapped[bool] = mapped_column(Boolean, default=True)
    email_notifications: Mapped[bool] = mapped_column(Boolean, default=True)
    in_app_notifications: Mapped[bool] = mapped_column(Boolean, default=True)

