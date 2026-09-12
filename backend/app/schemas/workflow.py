import uuid
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, ConfigDict

class NotificationResponse(BaseModel):
    id: uuid.UUID
    title: str
    message: str
    notification_type: str
    entity_type: Optional[str] = None
    entity_id: Optional[uuid.UUID] = None
    is_read: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class AuditLogResponse(BaseModel):
    id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    role: Optional[str] = None
    action: str
    entity_type: str
    entity_id: uuid.UUID
    before_state: Optional[Any] = None
    after_state: Optional[Any] = None
    timestamp: datetime = None # maps to created_at
    hash_signature: str
    
    model_config = ConfigDict(from_attributes=True)
