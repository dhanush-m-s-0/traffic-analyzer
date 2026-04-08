"""Traffic analysis service providing real-time traffic data and condition assessment."""

import logging
import random
from datetime import datetime, UTC
from typing import Any, Optional

logger = logging.getLogger(__name__)


class TrafficService:
    """Service for retrieving and analyzing real-time traffic conditions."""

    # Congestion level thresholds (0-100 scale)
    CONGESTION_LOW = 30
    CONGESTION_MODERATE = 60
    CONGESTION_HIGH = 80

    def __init__(self, api_key: Optional[str] = None) -> None:
        """Initialize the traffic service.

        Args:
            api_key: Optional API key for a real traffic data provider.
                     If not provided, simulated data is used.
        """
        self.api_key = api_key
        self._use_simulation = api_key is None
        logger.info(
            "TrafficService initialised (simulation=%s)", self._use_simulation
        )

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def get_traffic_conditions(self, location: str, coordinates: Optional[str] = None) -> dict[str, Any]:
        """Retrieve current traffic conditions for a location.

        Args:
            location: Human-readable location name.
            coordinates: Optional "lat,lng" string for more precise lookup.

        Returns:
            Dictionary containing traffic condition data.
        """
        logger.info("Fetching traffic conditions for %s", location)

        if self._use_simulation:
            return self._simulate_traffic_conditions(location, coordinates)

        # Placeholder for real API integration
        return self._simulate_traffic_conditions(location, coordinates)

    def analyze_congestion(self, traffic_data: dict[str, Any]) -> dict[str, Any]:
        """Analyse congestion levels from raw traffic data.

        Args:
            traffic_data: Raw traffic condition data from ``get_traffic_conditions``.

        Returns:
            Congestion analysis with level, description, and recommendations.
        """
        congestion_score = traffic_data.get("congestion_score", 0)

        if congestion_score < self.CONGESTION_LOW:
            level = "low"
            description = "Traffic is flowing freely."
            recommendation = "No action needed. Roads are clear."
        elif congestion_score < self.CONGESTION_MODERATE:
            level = "moderate"
            description = "Some traffic slowdowns detected."
            recommendation = "Consider travelling during off-peak hours if possible."
        elif congestion_score < self.CONGESTION_HIGH:
            level = "high"
            description = "Significant congestion on major routes."
            recommendation = "Use alternative routes or delay travel by 30-60 minutes."
        else:
            level = "severe"
            description = "Severe congestion causing major delays."
            recommendation = "Avoid the area if possible. Expect delays of 60+ minutes."

        return {
            "congestion_score": congestion_score,
            "level": level,
            "description": description,
            "recommendation": recommendation,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    def predict_congestion(self, location: str, hours_ahead: int = 1) -> dict[str, Any]:
        """Predict congestion levels for the next N hours.

        Args:
            location: Location to predict congestion for.
            hours_ahead: Number of hours into the future to predict.

        Returns:
            Prediction data with expected congestion levels.
        """
        logger.info("Predicting congestion for %s (%d hours ahead)", location, hours_ahead)

        # Simulate prediction based on time-of-day patterns
        now = datetime.now(UTC)
        predictions = []
        for h in range(1, hours_ahead + 1):
            future_hour = (now.hour + h) % 24
            score = self._hour_to_congestion_score(future_hour)
            predictions.append(
                {
                    "hours_from_now": h,
                    "predicted_hour": future_hour,
                    "congestion_score": score,
                    "level": self._score_to_level(score),
                }
            )

        return {
            "location": location,
            "predictions": predictions,
            "generated_at": now.isoformat(),
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _simulate_traffic_conditions(
        self, location: str, coordinates: Optional[str]
    ) -> dict[str, Any]:
        """Generate realistic simulated traffic data."""
        hour = datetime.now(UTC).hour
        base_score = self._hour_to_congestion_score(hour)
        # Add some noise so each call differs slightly
        noise = random.randint(-5, 5)
        congestion_score = max(0, min(100, base_score + noise))

        avg_speed = max(5, 60 - int(congestion_score * 0.5))
        incident_count = random.randint(0, int(congestion_score / 25))

        return {
            "location": location,
            "coordinates": coordinates,
            "congestion_score": congestion_score,
            "average_speed_kmh": avg_speed,
            "incident_count": incident_count,
            "road_conditions": self._get_road_conditions(congestion_score),
            "timestamp": datetime.now(UTC).isoformat(),
            "data_source": "simulated",
        }

    @staticmethod
    def _hour_to_congestion_score(hour: int) -> int:
        """Map hour of day (0-23) to a realistic congestion score."""
        # Peak hours: 7-9 AM and 5-7 PM
        peak_morning = {7: 70, 8: 85, 9: 75}
        peak_evening = {17: 75, 18: 90, 19: 80}
        moderate_hours = {6: 40, 10: 45, 11: 50, 12: 55, 13: 50, 14: 45, 15: 50, 16: 65, 20: 55, 21: 40}

        if hour in peak_morning:
            return peak_morning[hour]
        if hour in peak_evening:
            return peak_evening[hour]
        if hour in moderate_hours:
            return moderate_hours[hour]
        if 0 <= hour <= 5:
            return random.randint(5, 20)
        return 30

    @staticmethod
    def _score_to_level(score: int) -> str:
        """Convert congestion score to human-readable level."""
        if score < 30:
            return "low"
        if score < 60:
            return "moderate"
        if score < 80:
            return "high"
        return "severe"

    @staticmethod
    def _get_road_conditions(congestion_score: int) -> str:
        """Derive road condition description from congestion score."""
        if congestion_score < 30:
            return "clear"
        if congestion_score < 60:
            return "slow"
        if congestion_score < 80:
            return "congested"
        return "gridlock"
