from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./coalmine.db"
    
    # Redis
    REDIS_URL: str = "redis://127.0.0.1:6379/0"
    
    # Security
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    ALGORITHM: str = "HS256"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Providers
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
    return Settings()
