"""FastAPI dependency injection functions.

These provide database sessions and provider instances to route handlers.
"""
from app.database import get_db  # noqa: F401 — re-exported for convenience
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
    """FastAPI dependency — returns the configured AI provider instance."""
    settings = get_settings()
    return _get_ai_provider(settings.AI_PROVIDER)


def get_weather_provider_dep() -> WeatherProvider:
    """FastAPI dependency — returns the configured Weather provider instance."""
    settings = get_settings()
    return _get_weather_provider(settings.WEATHER_PROVIDER)


def get_ocr_provider_dep() -> OCRProvider:
    """FastAPI dependency — returns the configured OCR provider instance."""
    settings = get_settings()
    return _get_ocr_provider(settings.OCR_PROVIDER)


def get_storage_provider_dep() -> StorageProvider:
    """FastAPI dependency — returns the configured Storage provider instance."""
    settings = get_settings()
    return _get_storage_provider(settings.STORAGE_PROVIDER)

from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
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
