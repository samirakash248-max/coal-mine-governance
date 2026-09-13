import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.user import Role

class UserBase(BaseModel):
    email: str
    full_name: str
    role: Role
    is_active: bool = True
    organization_id: Optional[uuid.UUID] = None
    subsidiary_id: Optional[uuid.UUID] = None
    region_id: Optional[uuid.UUID] = None
    mine_id: Optional[uuid.UUID] = None
    department_id: Optional[uuid.UUID] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: uuid.UUID
    
    model_config = ConfigDict(from_attributes=True)

class UserUpdateMe(BaseModel):
    full_name: Optional[str] = None
