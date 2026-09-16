import uuid
from typing import Optional
from pydantic import BaseModel, Field
from fastapi import Query

class PaginationParams(BaseModel):
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=100, ge=1, le=1000)

def get_pagination(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
) -> PaginationParams:
    return PaginationParams(skip=skip, limit=limit)

"""FastAPI dependency injection functions.

These provide database sessions and provider instances to route handlers.
"""
from app.database import get_db  # noqa: F401 â€” re-exported for convenience
from app.config import get_settings  # noqa: F401

from app.providers.ai import get_ai_provider as _get_ai_provider, AIProvider
from app.providers.weather import get_weather_provider as _get_weather_provider, WeatherProvider
from app.providers.ocr import get_ocr_provider as _get_ocr_provider, OCRProvider
from app.providers.storage import get_storage_provider as _get_storage_provider, StorageProvider

__all__ = [
    "get_db", "get_settings",
    "get_ai_provider_dep", "get_weather_provider_dep",
    "get_ocr_provider_dep", "get_storage_provider_dep",
]


def get_ai_provider_dep() -> AIProvider:
    """FastAPI dependency â€” returns the configured AI provider instance."""
    settings = get_settings()
    return _get_ai_provider(settings.AI_PROVIDER)


def get_weather_provider_dep() -> WeatherProvider:
    """FastAPI dependency â€” returns the configured Weather provider instance."""
    settings = get_settings()
    return _get_weather_provider(settings.WEATHER_PROVIDER)


def get_ocr_provider_dep() -> OCRProvider:
    """FastAPI dependency â€” returns the configured OCR provider instance."""
    settings = get_settings()
    return _get_ocr_provider(settings.OCR_PROVIDER)


def get_storage_provider_dep() -> StorageProvider:
    """FastAPI dependency â€” returns the configured Storage provider instance."""
    settings = get_settings()
    return _get_storage_provider(settings.STORAGE_PROVIDER)

from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError, ExpiredSignatureError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.security import decode_access_token
from app.models.user import User, Role
from app.config import Settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise credentials_exception
        
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user

def require_role(roles: list[Role]):
    async def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return role_checker

from app.core.permissions import Permission, get_role_permissions

def require_authenticated_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user

def require_permission(permission: Permission):
    async def permission_checker(current_user: User = Depends(get_current_user)):
        user_permissions = get_role_permissions(current_user.role)
        if permission not in user_permissions and current_user.role not in (Role.SYSTEM_ADMIN, Role.ADMIN):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission: {permission.value}"
            )
        return current_user
    return permission_checker



