from .base import StorageProvider, StoredFile
from .local import LocalStorageProvider

_PROVIDERS = {
    "local": LocalStorageProvider,
}

def get_storage_provider(provider_name: str = "local", **kwargs) -> StorageProvider:
    provider_class = _PROVIDERS.get(provider_name)
    if not provider_class:
        raise ValueError(f"Unknown Storage provider: {provider_name}. Available: {list(_PROVIDERS.keys())}")
    return provider_class(**kwargs)

__all__ = ["StorageProvider", "StoredFile", "get_storage_provider"]
