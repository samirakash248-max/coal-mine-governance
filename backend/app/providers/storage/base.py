from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class StoredFile(BaseModel):
    path: str
    original_filename: str
    size_bytes: int
    mime_type: str
    uploaded_at: datetime
    url: str  # accessible URL/path

class StorageProvider(ABC):
    """Abstract interface for file storage.
    
    Local filesystem for development, S3-compatible for production.
    """
    
    @abstractmethod
    async def upload(
        self,
        file_bytes: bytes,
        path: str,
        original_filename: str,
        mime_type: str = "application/octet-stream"
    ) -> StoredFile:
        ...
    
    @abstractmethod
    async def download(self, path: str) -> bytes:
        ...
    
    @abstractmethod
    async def delete(self, path: str) -> bool:
        ...
    
    @abstractmethod
    async def get_url(self, path: str) -> str:
        ...
    
    @abstractmethod
    async def exists(self, path: str) -> bool:
        ...
