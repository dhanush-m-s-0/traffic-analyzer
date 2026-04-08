"""Weather service for retrieving and processing weather data."""

import logging
import random
from datetime import datetime, UTC
from typing import Any, Optional

logger = logging.getLogger(__name__)


class WeatherService:
    """Service for fetching current weather data and assessing traffic impact."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_url: str = "https://api.openweathermap.org/data/2.5",
    ) -> None:
        """Initialise the weather service.

        Args:
            api_key: OpenWeatherMap API key. Falls back to simulation when absent.
            api_url: Base URL for the weather API.
        """
        self.api_key = api_key
        self.api_url = api_url
        self._use_simulation = api_key is None
        logger.info("WeatherService initialised (simulation=%s)", self._use_simulation)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def get_current_weather(self, location: str) -> dict[str, Any]:
        """Retrieve the current weather for a location.

        Args:
            location: City name or location string.

        Returns:
            Dictionary with weather data including temperature, conditions, and
            a traffic impact assessment.
        """
        logger.info("Fetching weather for %s", location)

        if self._use_simulation:
            return self._simulate_weather(location)

        # Placeholder for live OpenWeatherMap integration
        return self._simulate_weather(location)

    def assess_traffic_impact(self, weather_data: dict[str, Any]) -> dict[str, Any]:
        """Assess how current weather conditions affect traffic.

        Args:
            weather_data: Weather data from ``get_current_weather``.

        Returns:
            Impact assessment with severity and recommended adjustments.
        """
        condition = weather_data.get("condition", "clear").lower()
        visibility_km = weather_data.get("visibility_km", 10)
        wind_speed_kmh = weather_data.get("wind_speed_kmh", 0)
        precipitation_mm = weather_data.get("precipitation_mm", 0)

        severity = "none"
        factors: list[str] = []
        delay_multiplier = 1.0

        if precipitation_mm > 20:
            severity = "severe"
            factors.append("Heavy rain causing poor visibility and slippery roads")
            delay_multiplier *= 1.5
        elif precipitation_mm > 5:
            severity = max(severity, "moderate", key=self._severity_rank)
            factors.append("Moderate rain reducing road traction")
            delay_multiplier *= 1.2

        if "snow" in condition or "blizzard" in condition:
            severity = "severe"
            factors.append("Snow/ice significantly reducing safe speeds")
            delay_multiplier *= 2.0
        elif "fog" in condition or visibility_km < 1:
            severity = "severe"
            factors.append("Dense fog severely limiting visibility")
            delay_multiplier *= 1.8

        if wind_speed_kmh > 80:
            severity = max(severity, "high", key=self._severity_rank)
            factors.append("High winds affecting vehicle control")
            delay_multiplier *= 1.3

        if not factors:
            factors.append("Weather conditions are favourable for driving")

        return {
            "severity": severity,
            "delay_multiplier": round(delay_multiplier, 2),
            "factors": factors,
            "recommendation": self._impact_recommendation(severity),
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _simulate_weather(location: str) -> dict[str, Any]:
        """Generate realistic simulated weather data."""
        conditions = ["clear", "partly cloudy", "overcast", "light rain", "heavy rain", "fog", "snow"]
        weights = [35, 25, 15, 15, 5, 3, 2]
        condition = random.choices(conditions, weights=weights, k=1)[0]

        temperature = random.uniform(5, 35)
        humidity = random.randint(30, 95)
        wind_speed = random.uniform(0, 60)
        visibility = 10.0 if condition == "clear" else random.uniform(1, 9)
        precipitation = 0.0 if condition in ("clear", "partly cloudy", "overcast") else random.uniform(1, 30)

        return {
            "location": location,
            "condition": condition,
            "temperature_c": round(temperature, 1),
            "humidity_pct": humidity,
            "wind_speed_kmh": round(wind_speed, 1),
            "visibility_km": round(visibility, 1),
            "precipitation_mm": round(precipitation, 1),
            "timestamp": datetime.now(UTC).isoformat(),
            "data_source": "simulated",
        }

    @staticmethod
    def _severity_rank(severity: str) -> int:
        """Numeric rank for severity comparison."""
        return {"none": 0, "low": 1, "moderate": 2, "high": 3, "severe": 4}.get(severity, 0)

    @staticmethod
    def _impact_recommendation(severity: str) -> str:
        """Human-readable recommendation based on impact severity."""
        recommendations = {
            "none": "Weather has no significant impact on traffic.",
            "low": "Minor weather impact. Allow extra time.",
            "moderate": "Reduced road speeds recommended. Drive carefully.",
            "high": "Significant weather impact. Consider delaying travel.",
            "severe": "Dangerous driving conditions. Avoid travel if possible.",
        }
        return recommendations.get(severity, "Check local weather advisories.")
