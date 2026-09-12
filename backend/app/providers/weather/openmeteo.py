import httpx
from datetime import datetime, timezone
from .base import WeatherProvider, WeatherData, WeatherCondition, WeatherRiskAssessment, WeatherRiskLevel

class RealWeatherProvider(WeatherProvider):
    """Uses Open-Meteo for real weather data."""
    
    async def get_current(self, lat: float, lon: float) -> WeatherData:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&precipitation_unit=mm"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                current = data.get("current_weather", {})
                wmo_code = current.get("weathercode", 0)
                
                # Crude mapping
                cond = WeatherCondition.CLEAR
                if wmo_code >= 60 and wmo_code < 65: cond = WeatherCondition.RAIN
                if wmo_code >= 65: cond = WeatherCondition.HEAVY_RAIN
                
                return WeatherData(
                    temperature_celsius=current.get("temperature", 0.0),
                    humidity_percent=50.0, # open-meteo current doesn't return humidity without extra params
                    wind_speed_kmh=current.get("windspeed", 0.0),
                    condition=cond,
                    description=f"WMO Code {wmo_code}",
                    visibility_km=10.0,
                    rainfall_mm=10.0 if cond == WeatherCondition.HEAVY_RAIN else 0.0, # approximation
                    timestamp=datetime.now(timezone.utc),
                    is_simulated=False
                )
        # Fallback
        return WeatherData(
            temperature_celsius=0.0,
            humidity_percent=0.0,
            wind_speed_kmh=0.0,
            condition=WeatherCondition.CLEAR,
            description="API Error",
            visibility_km=0.0,
            rainfall_mm=0.0,
            timestamp=datetime.now(timezone.utc),
            is_simulated=False
        )

    async def get_forecast(self, lat: float, lon: float, days: int = 5) -> list[WeatherData]:
        return [] # Not heavily utilized in Phase 6 advisory yet
        
    async def assess_risk(self, weather_data: WeatherData) -> WeatherRiskAssessment:
        risk = WeatherRiskLevel.LOW
        if weather_data.condition == WeatherCondition.HEAVY_RAIN:
            risk = WeatherRiskLevel.HIGH
        
        return WeatherRiskAssessment(
            risk_level=risk,
            factors=[weather_data.description],
            recommendations=["Monitor open pits"],
            affects_operations=risk == WeatherRiskLevel.HIGH,
            is_simulated=weather_data.is_simulated
        )
