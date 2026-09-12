from .base import StorageProvider, StoredFile
from datetime import datetime
import os
import asyncio

class LocalStorageProvider(StorageProvider):
    def __init__(self, base_path: str = "storage_local"):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)
        
    async def upload(
        self,
        file_bytes: bytes,
        path: str,
        original_filename: str,
        mime_type: str = "application/octet-stream"
    ) -> StoredFile:
        full_path = os.path.join(self.base_path, path)
        directory = os.path.dirname(full_path)
        
        def _write():
            os.makedirs(directory, exist_ok=True)
            with open(full_path, "wb") as f:
                f.write(file_bytes)
                
        await asyncio.to_thread(_write)
        
        return StoredFile(
            path=path,
            original_filename=original_filename,
            size_bytes=len(file_bytes),
            mime_type=mime_type,
            uploaded_at=datetime.now(),
            url=f"/storage/{path}"
        )
    
    async def download(self, path: str) -> bytes:
        full_path = os.path.join(self.base_path, path)
        def _read():
            if not os.path.exists(full_path):
                raise FileNotFoundError(f"File not found: {path}")
            with open(full_path, "rb") as f:
                return f.read()
        return await asyncio.to_thread(_read)
    
    async def delete(self, path: str) -> bool:
        full_path = os.path.join(self.base_path, path)
        def _delete():
            if os.path.exists(full_path):
                os.remove(full_path)
                return True
            return False
        return await asyncio.to_thread(_delete)
    
    async def get_url(self, path: str) -> str:
        return f"/storage/{path}"
    
    async def exists(self, path: str) -> bool:
        full_path = os.path.join(self.base_path, path)
        def _exists():
            return os.path.exists(full_path)
        return await asyncio.to_thread(_exists)
