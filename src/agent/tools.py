"""LangChain-compatible tools for the traffic analysis agent."""

import json
import logging
from typing import Optional, Type

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from src.services.route import RouteService
from src.services.traffic import TrafficService
from src.services.weather import WeatherService

logger = logging.getLogger(__name__)

# Module-level service singletons (shared across tool instances)
_traffic_svc: Optional[TrafficService] = None
_weather_svc: Optional[WeatherService] = None
_route_svc: Optional[RouteService] = None


def _get_traffic_service(api_key: Optional[str] = None) -> TrafficService:
    global _traffic_svc
    if _traffic_svc is None:
        _traffic_svc = TrafficService(api_key=api_key)
    return _traffic_svc


def _get_weather_service(api_key: Optional[str] = None) -> WeatherService:
    global _weather_svc
    if _weather_svc is None:
        _weather_svc = WeatherService(api_key=api_key)
    return _weather_svc


def _get_route_service() -> RouteService:
    global _route_svc
    if _route_svc is None:
        _route_svc = RouteService()
    return _route_svc


# ---------------------------------------------------------------------------
# Input schemas (Pydantic v2 style)
# ---------------------------------------------------------------------------


class TrafficConditionsInput(BaseModel):
    """Input schema for the get_traffic_conditions tool."""

    location: str = Field(description="City or area name, e.g. 'New York'")
    coordinates: Optional[str] = Field(
        default=None, description="Optional 'lat,lng' string for precision"
    )


class CongestionPredictionInput(BaseModel):
    """Input schema for the predict_congestion tool."""

    location: str = Field(description="Location to predict congestion for")
    hours_ahead: int = Field(default=1, description="Hours into the future (1-24)", ge=1, le=24)


class WeatherConditionsInput(BaseModel):
    """Input schema for the get_weather tool."""

    location: str = Field(description="Location to fetch weather for")


class RouteOptimizationInput(BaseModel):
    """Input schema for the optimize_route tool."""

    start: str = Field(description="Starting location")
    end: str = Field(description="Destination location")
    congestion_score: int = Field(default=0, description="Current congestion score (0-100)", ge=0, le=100)


class AlertInput(BaseModel):
    """Input schema for the generate_alert tool."""

    location: str = Field(description="Location of the alert")
    congestion_score: int = Field(description="Congestion score to evaluate (0-100)", ge=0, le=100)
    threshold: int = Field(default=70, description="Alert threshold (0-100)", ge=0, le=100)


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------


class GetTrafficConditionsTool(BaseTool):
    """Tool that fetches current traffic conditions for a given location."""

    name: str = "get_traffic_conditions"
    description: str = (
        "Retrieve real-time traffic conditions for a location. "
        "Returns congestion score, average speed, and incident count."
    )
    args_schema: Type[BaseModel] = TrafficConditionsInput

    def _run(self, location: str, coordinates: Optional[str] = None) -> str:
        try:
            svc = _get_traffic_service()
            data = svc.get_traffic_conditions(location, coordinates)
            analysis = svc.analyze_congestion(data)
            return json.dumps({**data, "analysis": analysis}, indent=2)
        except Exception as exc:
            logger.exception("Error in get_traffic_conditions tool")
            return json.dumps({"error": str(exc)})

    async def _arun(self, location: str, coordinates: Optional[str] = None) -> str:
        return self._run(location, coordinates)


class PredictCongestionTool(BaseTool):
    """Tool that predicts future congestion levels."""

    name: str = "predict_congestion"
    description: str = (
        "Predict traffic congestion levels for the next N hours at a location. "
        "Useful for planning future journeys."
    )
    args_schema: Type[BaseModel] = CongestionPredictionInput

    def _run(self, location: str, hours_ahead: int = 1) -> str:
        try:
            svc = _get_traffic_service()
            result = svc.predict_congestion(location, hours_ahead)
            return json.dumps(result, indent=2)
        except Exception as exc:
            logger.exception("Error in predict_congestion tool")
            return json.dumps({"error": str(exc)})

    async def _arun(self, location: str, hours_ahead: int = 1) -> str:
        return self._run(location, hours_ahead)


class GetWeatherConditionsTool(BaseTool):
    """Tool that fetches current weather and its traffic impact."""

    name: str = "get_weather_conditions"
    description: str = (
        "Get current weather conditions and assess how they impact traffic. "
        "Returns temperature, precipitation, visibility, and a traffic impact score."
    )
    args_schema: Type[BaseModel] = WeatherConditionsInput

    def _run(self, location: str) -> str:
        try:
            svc = _get_weather_service()
            weather = svc.get_current_weather(location)
            impact = svc.assess_traffic_impact(weather)
            return json.dumps({**weather, "traffic_impact": impact}, indent=2)
        except Exception as exc:
            logger.exception("Error in get_weather_conditions tool")
            return json.dumps({"error": str(exc)})

    async def _arun(self, location: str) -> str:
        return self._run(location)


class OptimizeRouteTool(BaseTool):
    """Tool that calculates and optimises routes between two points."""

    name: str = "optimize_route"
    description: str = (
        "Calculate and optimise the route between a start and end location. "
        "Returns distance, estimated travel time, and turn-by-turn directions."
    )
    args_schema: Type[BaseModel] = RouteOptimizationInput

    def _run(self, start: str, end: str, congestion_score: int = 0) -> str:
        try:
            svc = _get_route_service()
            result = svc.get_alternative_routes(start, end, congestion_score)
            return json.dumps(result, indent=2)
        except Exception as exc:
            logger.exception("Error in optimize_route tool")
            return json.dumps({"error": str(exc)})

    async def _arun(self, start: str, end: str, congestion_score: int = 0) -> str:
        return self._run(start, end, congestion_score)


class GenerateAlertTool(BaseTool):
    """Tool that generates traffic alerts based on congestion thresholds."""

    name: str = "generate_traffic_alert"
    description: str = (
        "Generate a traffic alert if congestion exceeds a defined threshold. "
        "Returns alert details and recommended actions."
    )
    args_schema: Type[BaseModel] = AlertInput

    def _run(self, location: str, congestion_score: int, threshold: int = 70) -> str:
        try:
            triggered = congestion_score >= threshold
            severity = "none"
            if congestion_score >= 90:
                severity = "critical"
            elif congestion_score >= 80:
                severity = "high"
            elif congestion_score >= threshold:
                severity = "moderate"

            return json.dumps(
                {
                    "location": location,
                    "congestion_score": congestion_score,
                    "threshold": threshold,
                    "alert_triggered": triggered,
                    "severity": severity,
                    "message": (
                        f"ALERT: Congestion level {congestion_score}/100 at {location} "
                        f"has exceeded threshold {threshold}."
                        if triggered
                        else f"No alert: Congestion {congestion_score}/100 is below threshold {threshold}."
                    ),
                    "recommended_action": (
                        "Avoid the area or use alternative routes."
                        if triggered
                        else "No action required."
                    ),
                },
                indent=2,
            )
        except Exception as exc:
            logger.exception("Error in generate_traffic_alert tool")
            return json.dumps({"error": str(exc)})

    async def _arun(self, location: str, congestion_score: int, threshold: int = 70) -> str:
        return self._run(location, congestion_score, threshold)


def get_all_tools() -> list[BaseTool]:
    """Return the full list of tools available to the traffic agent.

    Returns:
        List of instantiated LangChain ``BaseTool`` objects.
    """
    return [
        GetTrafficConditionsTool(),
        PredictCongestionTool(),
        GetWeatherConditionsTool(),
        OptimizeRouteTool(),
        GenerateAlertTool(),
    ]
