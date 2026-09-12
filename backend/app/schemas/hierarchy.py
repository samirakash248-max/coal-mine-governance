import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict

class HierarchyBase(BaseModel):
    name: str

class OrganizationResponse(HierarchyBase):
    id: uuid.UUID
    description: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class MineResponse(HierarchyBase):
    id: uuid.UUID
    region_id: uuid.UUID
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: str
    model_config = ConfigDict(from_attributes=True)
