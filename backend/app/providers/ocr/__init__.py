from .base import OCRProvider, OCRResult
from .mock import MockOCRProvider

_PROVIDERS = {
    "mock": MockOCRProvider,
}

def get_ocr_provider(provider_name: str = "mock") -> OCRProvider:
    provider_class = _PROVIDERS.get(provider_name)
    if not provider_class:
        raise ValueError(f"Unknown OCR provider: {provider_name}. Available: {list(_PROVIDERS.keys())}")
    return provider_class()

__all__ = ["OCRProvider", "OCRResult", "get_ocr_provider"]
