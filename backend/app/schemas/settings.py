
from pydantic import BaseModel, ConfigDict
from typing import Optional
import uuid

class UserSettingsUpdate(BaseModel):
    theme: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None
    default_mine_id: Optional[str] = None

class UserSettingsResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    theme: str
    language: str
    timezone: str
    default_mine_id: Optional[str]
    model_config = ConfigDict(from_attributes=True)

class NotificationPreferenceUpdate(BaseModel):
    inspection_reminders: Optional[bool] = None
    safety_alerts: Optional[bool] = None
    critical_risk_alerts: Optional[bool] = None
    compliance_alerts: Optional[bool] = None
    overdue_action_reminders: Optional[bool] = None
    regulatory_updates: Optional[bool] = None
    email_notifications: Optional[bool] = None
    in_app_notifications: Optional[bool] = None

class NotificationPreferenceResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    inspection_reminders: bool
    safety_alerts: bool
    critical_risk_alerts: bool
    compliance_alerts: bool
    overdue_action_reminders: bool
    regulatory_updates: bool
    email_notifications: bool
    in_app_notifications: bool
    model_config = ConfigDict(from_attributes=True)

