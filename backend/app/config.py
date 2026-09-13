from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
import warnings
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: Optional[str] = None
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None
    POSTGRES_HOST: Optional[str] = None
    POSTGRES_PORT: Optional[str] = None
    
    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    
    # Security
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    ALGORITHM: str = "HS256"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    FRONTEND_URL: str = "http://localhost:5173"
    
    # OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    AI_PROVIDER: str = "local"
    AI_BASE_URL: str = "http://127.0.0.1:8001/v1"
    AI_MODEL: str = "coal-gov-qwen3-4b"
    AI_TIMEOUT: float = 30.0
    WEATHER_PROVIDER: str = "mock"
    OCR_PROVIDER: str = "mock"
    STORAGE_PROVIDER: str = "local"
    
    # Storage
    STORAGE_LOCAL_PATH: str = "./storage"
    
    # App
    DEBUG: bool = False
    APP_VERSION: str = "0.1.0"
    APP_TITLE: str = "CoalMine Governance Platform"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore")

def get_settings() -> Settings:
    settings = Settings()
    
    # If DATABASE_URL is provided (e.g. Render production)
    if settings.DATABASE_URL:
        # Fix Render postgres URL if needed
        if settings.DATABASE_URL.startswith("postgres://"):
            settings.DATABASE_URL = settings.DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
        elif settings.DATABASE_URL.startswith("postgresql://"):
            settings.DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    # Else if local Docker POSTGRES_ vars are provided
    elif settings.POSTGRES_USER and settings.POSTGRES_PASSWORD and settings.POSTGRES_DB:
        host = settings.POSTGRES_HOST or "postgres"
        port = settings.POSTGRES_PORT or "5432"
        settings.DATABASE_URL = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{host}:{port}/{settings.POSTGRES_DB}"
        
    # Ultimate fallback to SQLite for local direct python running (without docker)
    if not settings.DATABASE_URL:
        warnings.warn("No PostgreSQL configuration found. Falling back to local SQLite.")
        settings.DATABASE_URL = "sqlite+aiosqlite:///./coalmine.db"
        
    return settings
