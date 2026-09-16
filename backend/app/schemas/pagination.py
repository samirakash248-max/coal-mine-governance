from typing import Generic, TypeVar, Sequence
from pydantic import BaseModel, Field

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    items: Sequence[T]
    total: int
    skip: int = 0
    limit: int = 100

class PaginationParams(BaseModel):
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=100, ge=1, le=1000)
