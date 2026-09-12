from .base import WeatherProvider, WeatherData, WeatherCondition, WeatherRiskAssessment, WeatherRiskLevel
from datetime import datetime
import random

class MockWeatherProvider(WeatherProvider):
    async def get_current(self, lat: float, lon: float) -> WeatherData:
        now = datetime.now()
        temp = random.uniform(25.0, 42.0)
        humidity = random.uniform(40.0, 85.0)
        condition = random.choice(list(WeatherCondition))
        rain = 0.0
        if condition in [WeatherCondition.RAIN, WeatherCondition.HEAVY_RAIN, WeatherCondition.THUNDERSTORM]:
            rain = random.uniform(5.0, 50.0)
        
        return WeatherData(
            temperature_celsius=round(temp, 1),
            humidity_percent=round(humidity, 1),
            wind_speed_kmh=round(random.uniform(5.0, 25.0), 1),
            condition=condition,
            description=f"Current condition is {condition.value}",
            visibility_km=round(random.uniform(2.0, 10.0), 1),
            rainfall_mm=round(rain, 1),
            timestamp=now,
            is_simulated=True
        )

    async def get_forecast(self, lat: float, lon: float, days: int = 5) -> list[WeatherData]:
        forecast = []
        now = datetime.now()
        is_monsoon = 6 <= now.month <= 9
        for i in range(days):
            temp = random.uniform(25.0, 42.0)
            condition = random.choice(list(WeatherCondition))
            if is_monsoon and random.random() > 0.5:
                condition = WeatherCondition.RAIN
            rain = 0.0
            if condition in [WeatherCondition.RAIN, WeatherCondition.HEAVY_RAIN, WeatherCondition.THUNDERSTORM]:
                rain = random.uniform(5.0, 50.0)
                
            forecast.append(WeatherData(
                temperature_celsius=round(temp, 1),
                humidity_percent=round(random.uniform(40.0, 85.0), 1),
                wind_speed_kmh=round(random.uniform(5.0, 25.0), 1),
                condition=condition,
                description=f"Forecasted {condition.value}",
                visibility_km=round(random.uniform(2.0, 10.0), 1),
                rainfall_mm=round(rain, 1),
                timestamp=now,
                is_simulated=True
            ))
        return forecast

    async def assess_risk(self, weather_data: WeatherData) -> WeatherRiskAssessment:
        if weather_data.condition in [WeatherCondition.HEAVY_RAIN, WeatherCondition.THUNDERSTORM] or weather_data.rainfall_mm > 30:
            return WeatherRiskAssessment(
                risk_level=WeatherRiskLevel.HIGH,
                factors=["Heavy rainfall may affect slope stability", "Risk of pit flooding"],
                recommendations=["Monitor pit drainage", "Evacuate lower benches if water level rises"],
                affects_operations=True,
                is_simulated=True
            )
        elif weather_data.temperature_celsius > 40 or weather_data.condition == WeatherCondition.EXTREME_HEAT:
            return WeatherRiskAssessment(
                risk_level=WeatherRiskLevel.MODERATE,
                factors=["Extreme heat poses risk to worker health"],
                recommendations=["Ensure hydration stations are stocked", "Provide shaded rest areas"],
                affects_operations=False,
                is_simulated=True
            )
        else:
            return WeatherRiskAssessment(
                risk_level=WeatherRiskLevel.LOW,
                factors=["Normal weather conditions"],
                recommendations=["Proceed with standard operations"],
                affects_operations=False,
                is_simulated=True
            )
