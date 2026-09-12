from .base import AIProvider, AIMessage, AIResponse, AIRole
from .mock import MockAIProvider
from .local import LocalModelProvider

_PROVIDERS = {
    "mock": MockAIProvider,
    "local": LocalModelProvider,
}

def get_ai_provider(provider_name: str = "mock") -> AIProvider:
    provider_class = _PROVIDERS.get(provider_name.lower())
    if not provider_class:
        raise ValueError(f"Unknown AI provider: {provider_name}. Available: {list(_PROVIDERS.keys())}")
    return provider_class()

__all__ = ["AIProvider", "AIMessage", "AIResponse", "AIRole", "get_ai_provider"]
