"""Provider abstractions for external services.

All external integrations (AI, Weather, OCR, Storage) are accessed through
provider interfaces. This allows swapping implementations without changing
business logic.
"""
from .ai import get_ai_provider, AIProvider
from .weather import get_weather_provider, WeatherProvider  
from .ocr import get_ocr_provider, OCRProvider
from .storage import get_storage_provider, StorageProvider

__all__ = [
    "get_ai_provider", "AIProvider",
    "get_weather_provider", "WeatherProvider",
    "get_ocr_provider", "OCRProvider", 
    "get_storage_provider", "StorageProvider",
]
