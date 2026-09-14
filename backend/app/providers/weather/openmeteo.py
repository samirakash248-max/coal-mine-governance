import httpx
from datetime import datetime, timezone
from .base import WeatherProvider, WeatherData, WeatherCondition, WeatherRiskAssessment, WeatherRiskLevel

class RealWeatherProvider(WeatherProvider):
    """Uses Open-Meteo for real weather data."""
    
    def _map_wmo_code(self, wmo_code: int) -> tuple[WeatherCondition, str]:
        # WMO Weather interpretation codes
        if wmo_code == 0: return WeatherCondition.CLEAR, "Clear sky"
        if wmo_code in [1, 2, 3]: return WeatherCondition.CLOUDY, "Partly cloudy to overcast"
        if wmo_code in [45, 48]: return WeatherCondition.FOG, "Fog"
        if wmo_code in [51, 53, 55, 56, 57]: return WeatherCondition.RAIN, "Drizzle"
        if wmo_code in [61, 63, 66]: return WeatherCondition.RAIN, "Rain"
        if wmo_code in [65, 67]: return WeatherCondition.HEAVY_RAIN, "Heavy Rain"
        if wmo_code in [71, 73, 75, 77]: return WeatherCondition.CLEAR, "Snow fall" # Not standard for India but handled
        if wmo_code in [80, 81, 82]: return WeatherCondition.HEAVY_RAIN, "Rain showers"
        if wmo_code >= 95: return WeatherCondition.THUNDERSTORM, "Thunderstorm"
        return WeatherCondition.CLEAR, f"WMO Code {wmo_code}"

    async def get_current(self, lat: float, lon: float) -> WeatherData:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m&timezone=auto"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, timeout=10.0)
                if response.status_code == 200:
                    data = response.json()
                    current = data.get("current", {})
                    
                    wmo_code = current.get("weather_code", 0)
                    cond, desc = self._map_wmo_code(wmo_code)
                    
                    temp = current.get("temperature_2m", 0.0)
                    humidity = current.get("relative_humidity_2m", 0.0)
                    wind = current.get("wind_speed_10m", 0.0)
                    precip = current.get("precipitation", 0.0)
                    
                    if temp > 45:
                        cond = WeatherCondition.EXTREME_HEAT
                        desc = "Extreme Heat"
                    
                    return WeatherData(
                        temperature_celsius=float(temp),
                        humidity_percent=float(humidity),
                        wind_speed_kmh=float(wind),
                        condition=cond,
                        description=desc,
                        visibility_km=10.0 if cond != WeatherCondition.FOG else 1.0,
                        rainfall_mm=float(precip),
                        timestamp=datetime.now(timezone.utc),
                        is_simulated=False
                    )
            except Exception as e:
                pass # Fallback below
                
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
        factors = []
        recs = []
        
        if weather_data.condition == WeatherCondition.API_ERROR or weather_data.description == "API Error":
            return WeatherRiskAssessment(
                risk_level=WeatherRiskLevel.LOW,
                factors=["Weather API Unavailable"],
                recommendations=["Rely on local sensors"],
                affects_operations=False,
                is_simulated=False
            )
            
        if weather_data.condition in [WeatherCondition.HEAVY_RAIN, WeatherCondition.THUNDERSTORM] or weather_data.rainfall_mm > 15:
            risk = WeatherRiskLevel.HIGH
            factors.append("Heavy rainfall detected in the area")
            recs.append("Monitor pit drainage and slope stability visually")
            
        if weather_data.wind_speed_kmh > 40:
            if risk == WeatherRiskLevel.LOW: risk = WeatherRiskLevel.MODERATE
            factors.append("High winds detected")
            recs.append("Secure loose equipment and monitor dust suppression")
            
        if weather_data.temperature_celsius > 42 or weather_data.condition == WeatherCondition.EXTREME_HEAT:
            risk = WeatherRiskLevel.HIGH
            factors.append("Extreme heat poses immediate risk to worker health")
            recs.append("Ensure hydration stations are stocked and provide shaded rest areas")
            
        if weather_data.condition == WeatherCondition.FOG:
            if risk == WeatherRiskLevel.LOW: risk = WeatherRiskLevel.MODERATE
            factors.append("Low visibility due to fog")
            recs.append("Exercise extreme caution during heavy machinery operation")

        if risk == WeatherRiskLevel.LOW:
            factors.append("Normal weather conditions")
            recs.append("Proceed with standard operations")
            
        return WeatherRiskAssessment(
            risk_level=risk,
            factors=factors,
            recommendations=recs,
            affects_operations=(risk == WeatherRiskLevel.HIGH or risk == WeatherRiskLevel.SEVERE),
            is_simulated=weather_data.is_simulated
        )
