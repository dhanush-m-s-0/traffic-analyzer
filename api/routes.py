"""Pydantic request/response models and FastAPI route handlers for the traffic analyzer API."""

import logging
from datetime import datetime, UTC
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from config.settings import settings
from src.models.database import (
    AlertRecord,
    AnalysisRecord,
    RouteRecord,
    TrafficRecord,
    get_db,
    init_db,
)
from src.services.route import RouteService
from src.services.traffic import TrafficService
from src.services.weather import WeatherService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["traffic"])

# Session factory initialised once at module import
_session_factory = init_db(settings.database_url)

# Service singletons
_traffic_svc = TrafficService(api_key=settings.traffic_api_key)
_weather_svc = WeatherService(
    api_key=settings.weather_api_key, api_url=settings.weather_api_url
)
_route_svc = RouteService()


def _get_db():
    yield from get_db(_session_factory)


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


class AnalyzeRequest(BaseModel):
    """Request body for POST /analyze."""

    location: str = Field(..., description="Location to analyze", min_length=1)
    coordinates: Optional[str] = Field(None, description="Optional 'lat,lng' string")
    include_weather: bool = Field(True, description="Include weather impact in analysis")


class AnalyzeResponse(BaseModel):
    """Response body for POST /analyze."""

    location: str
    traffic: dict[str, Any]
    congestion_analysis: dict[str, Any]
    weather: Optional[dict[str, Any]] = None
    weather_impact: Optional[dict[str, Any]] = None
    timestamp: str


class OptimizeRouteRequest(BaseModel):
    """Request body for POST /optimize-route."""

    start: str = Field(..., description="Start location", min_length=1)
    end: str = Field(..., description="End / destination location", min_length=1)
    avoid_tolls: bool = Field(False, description="Prefer routes without tolls")


class OptimizeRouteResponse(BaseModel):
    """Response body for POST /optimize-route."""

    start: str
    end: str
    routes: list[dict[str, Any]]
    recommended: dict[str, Any]
    generated_at: str


class AlertRequest(BaseModel):
    """Request body for POST /alerts."""

    location: str = Field(..., description="Location to monitor", min_length=1)
    threshold: int = Field(70, description="Congestion threshold (0-100)", ge=0, le=100)
    alert_type: str = Field("congestion", description="Type of alert")


class AlertResponse(BaseModel):
    """Response body for POST /alerts."""

    location: str
    threshold: int
    alert_type: str
    current_congestion: int
    alert_triggered: bool
    message: str
    created_at: str


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.post("/analyze", response_model=AnalyzeResponse, summary="Analyze traffic conditions")
def analyze_traffic(
    request: AnalyzeRequest,
    db: Session = Depends(_get_db),
) -> AnalyzeResponse:
    """Analyse real-time traffic conditions for a given location.

    Returns congestion score, average speed, incident count, and optional weather impact.
    """
    traffic_data = _traffic_svc.get_traffic_conditions(request.location, request.coordinates)
    congestion_analysis = _traffic_svc.analyze_congestion(traffic_data)

    weather_data = None
    weather_impact = None
    if request.include_weather:
        weather_data = _weather_svc.get_current_weather(request.location)
        weather_impact = _weather_svc.assess_traffic_impact(weather_data)

    # Persist to database
    try:
        record = TrafficRecord(
            location=request.location,
            coordinates=request.coordinates,
            congestion_score=traffic_data["congestion_score"],
            congestion_level=congestion_analysis["level"],
            average_speed_kmh=traffic_data.get("average_speed_kmh"),
            incident_count=traffic_data.get("incident_count", 0),
            road_conditions=traffic_data.get("road_conditions"),
        )
        db.add(record)
        db.commit()
    except Exception:
        logger.exception("Failed to persist traffic record")
        db.rollback()

    return AnalyzeResponse(
        location=request.location,
        traffic=traffic_data,
        congestion_analysis=congestion_analysis,
        weather=weather_data,
        weather_impact=weather_impact,
        timestamp=datetime.now(UTC).isoformat(),
    )


@router.post(
    "/optimize-route",
    response_model=OptimizeRouteResponse,
    summary="Get optimized route recommendations",
)
def optimize_route(
    request: OptimizeRouteRequest,
    db: Session = Depends(_get_db),
) -> OptimizeRouteResponse:
    """Calculate and return optimised route options between two locations."""
    # Get traffic conditions for congestion-aware routing
    traffic_data = _traffic_svc.get_traffic_conditions(request.start)
    congestion_score = traffic_data.get("congestion_score", 0)

    # Get weather for delay calculation
    weather_data = _weather_svc.get_current_weather(request.start)
    weather_impact = _weather_svc.assess_traffic_impact(weather_data)
    delay_multiplier = weather_impact.get("delay_multiplier", 1.0)

    result = _route_svc.get_alternative_routes(
        request.start,
        request.end,
        congestion_score,
        delay_multiplier,
    )

    # Persist best route
    try:
        rec = result["recommended"]
        route_record = RouteRecord(
            start_location=request.start,
            end_location=request.end,
            distance_km=rec["distance_km"],
            estimated_duration_min=rec["estimated_duration_min"],
            congestion_factor=rec.get("congestion_factor", 1.0),
            weather_delay_multiplier=rec.get("weather_delay_multiplier", 1.0),
        )
        db.add(route_record)
        db.commit()
    except Exception:
        logger.exception("Failed to persist route record")
        db.rollback()

    return OptimizeRouteResponse(
        start=request.start,
        end=request.end,
        routes=result["routes"],
        recommended=result["recommended"],
        generated_at=result["generated_at"],
    )


@router.get("/predictions", summary="Get congestion predictions")
def get_predictions(
    location: str = Query(..., description="Location to predict congestion for"),
    hours_ahead: int = Query(default=3, ge=1, le=24, description="Hours to predict ahead"),
) -> dict[str, Any]:
    """Return congestion predictions for the next N hours."""
    return _traffic_svc.predict_congestion(location, hours_ahead)


@router.post("/alerts", response_model=AlertResponse, summary="Create a traffic alert")
def create_alert(
    request: AlertRequest,
    db: Session = Depends(_get_db),
) -> AlertResponse:
    """Create a traffic alert and check whether it is currently triggered."""
    traffic_data = _traffic_svc.get_traffic_conditions(request.location)
    current_score = traffic_data.get("congestion_score", 0)
    triggered = current_score >= request.threshold

    message = (
        f"ALERT: Congestion at {request.location} is {current_score}/100, "
        f"exceeding threshold of {request.threshold}."
        if triggered
        else f"No alert: Congestion at {request.location} is {current_score}/100 "
        f"(threshold: {request.threshold})."
    )

    # Persist
    try:
        record = AlertRecord(
            location=request.location,
            alert_type=request.alert_type,
            threshold=request.threshold,
            message=message,
            triggered=1 if triggered else 0,
            triggered_at=datetime.now(UTC) if triggered else None,
        )
        db.add(record)
        db.commit()
    except Exception:
        logger.exception("Failed to persist alert record")
        db.rollback()

    return AlertResponse(
        location=request.location,
        threshold=request.threshold,
        alert_type=request.alert_type,
        current_congestion=current_score,
        alert_triggered=triggered,
        message=message,
        created_at=datetime.now(UTC).isoformat(),
    )


@router.get("/history", summary="Retrieve historical traffic data")
def get_history(
    location: Optional[str] = Query(None, description="Filter by location"),
    limit: int = Query(default=50, ge=1, le=500, description="Number of records to return"),
    db: Session = Depends(_get_db),
) -> dict[str, Any]:
    """Return historical traffic records from the database."""
    query = db.query(TrafficRecord).order_by(TrafficRecord.recorded_at.desc())
    if location:
        query = query.filter(TrafficRecord.location.ilike(f"%{location}%"))
    records = query.limit(limit).all()

    return {
        "records": [
            {
                "id": r.id,
                "location": r.location,
                "congestion_score": r.congestion_score,
                "congestion_level": r.congestion_level,
                "average_speed_kmh": r.average_speed_kmh,
                "incident_count": r.incident_count,
                "road_conditions": r.road_conditions,
                "recorded_at": r.recorded_at.isoformat() if r.recorded_at else None,
            }
            for r in records
        ],
        "total": len(records),
        "location_filter": location,
    }
