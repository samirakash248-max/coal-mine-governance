from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class WeatherRiskLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    SEVERE = "severe"

class WeatherCondition(str, Enum):
    CLEAR = "clear"
    CLOUDY = "cloudy"
    RAIN = "rain"
    HEAVY_RAIN = "heavy_rain"
    THUNDERSTORM = "thunderstorm"
    FOG = "fog"
    DUST_STORM = "dust_storm"
    EXTREME_HEAT = "extreme_heat"

class WeatherData(BaseModel):
    temperature_celsius: float
    humidity_percent: float
    wind_speed_kmh: float
    condition: WeatherCondition
    description: str
    visibility_km: float
    rainfall_mm: float = 0.0
    timestamp: datetime
    is_simulated: bool = False

class WeatherRiskAssessment(BaseModel):
    risk_level: WeatherRiskLevel
    factors: list[str]  # e.g., ["Heavy rainfall may affect slope stability"]
    recommendations: list[str]  # e.g., ["Monitor pit drainage"]
    affects_operations: bool
    is_simulated: bool = False

class WeatherProvider(ABC):
    """Abstract interface for weather data providers.
    
    Weather data influences risk analysis but does NOT automatically
    declare legal violations or compliance failures.
    """
    
    @abstractmethod
    async def get_current(self, lat: float, lon: float) -> WeatherData:
        ...
    
    @abstractmethod
    async def get_forecast(
        self, lat: float, lon: float, days: int = 5
    ) -> list[WeatherData]:
        ...
    
    @abstractmethod
    async def assess_risk(self, weather_data: WeatherData) -> WeatherRiskAssessment:
        """Assess mining-specific weather risk.
        
        This assessment is advisory only. It should influence
        governance risk scoring but never auto-declare violations.
        """
        ...
