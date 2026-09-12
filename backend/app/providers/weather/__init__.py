from .base import WeatherProvider, WeatherData, WeatherCondition, WeatherRiskAssessment, WeatherRiskLevel
from .mock import MockWeatherProvider
from .openmeteo import RealWeatherProvider

_PROVIDERS = {
    "mock": MockWeatherProvider,
    "real": RealWeatherProvider
}

def get_weather_provider(provider_name: str = "mock") -> WeatherProvider:
    provider_class = _PROVIDERS.get(provider_name)
    if not provider_class:
        raise ValueError(f"Unknown Weather provider: {provider_name}. Available: {list(_PROVIDERS.keys())}")
    return provider_class()

__all__ = ["WeatherProvider", "WeatherData", "WeatherCondition", "WeatherRiskAssessment", "WeatherRiskLevel", "get_weather_provider"]
