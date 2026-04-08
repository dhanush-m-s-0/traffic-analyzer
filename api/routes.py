"""API route definitions for Traffic Analyzer."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


class TrafficAnalysisRequest(BaseModel):
    """Request payload for traffic analysis."""

    location: str = Field(..., description="Location or address to analyze")
    time_of_day: Optional[str] = Field(None, description="Time of day (morning/afternoon/evening/night)")
    include_weather: bool = Field(False, description="Include weather impact analysis")
    query: Optional[str] = Field(None, description="Natural language query for AI agent")


class RouteOptimizationRequest(BaseModel):
    """Request payload for route optimization."""

    origin: str = Field(..., description="Starting point")
    destination: str = Field(..., description="End point")
    avoid_congestion: bool = Field(True, description="Avoid congested areas")
    time_of_day: Optional[str] = Field(None, description="Preferred departure time")


class AlertRequest(BaseModel):
    """Request payload for creating a traffic alert."""

    location: str = Field(..., description="Location for the alert")
    alert_type: str = Field(..., description="Type: congestion/accident/roadwork/weather")
    severity: str = Field("medium", description="Severity: low/medium/high/critical")
    description: Optional[str] = Field(None, description="Alert description")


class AnalysisResponse(BaseModel):
    """Unified analysis response."""

    status: str
    location: Optional[str] = None
    analysis: Optional[str] = None
    congestion_level: Optional[str] = None
    estimated_delay: Optional[int] = None
    recommendations: List[str] = []
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    raw: Optional[Dict[str, Any]] = None


# ---------------------------------------------------------------------------
# Helper – AI agent (lazy-loaded so the server starts even without a key)
# ---------------------------------------------------------------------------


def _run_agent(prompt: str) -> str:
    """Run the LangChain / Groq agent for the given prompt."""
    try:
        from config.settings import settings
        from groq import Groq

        client = Groq(api_key=settings.GROQ_API_KEY)
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert traffic analyst AI assistant. "
                        "Provide concise, actionable insights about traffic conditions, "
                        "congestion, route optimization, and weather impacts. "
                        "Format responses with clear sections and bullet points."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=1024,
            temperature=0.3,
        )
        return response.choices[0].message.content or "No response generated."
    except Exception as exc:
        logger.warning("AI agent call failed: %s", exc)
        return f"AI analysis unavailable: {exc}"


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.get("/health")
def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@router.post("/analyze", response_model=AnalysisResponse)
def analyze_traffic(req: TrafficAnalysisRequest) -> AnalysisResponse:
    """Analyze traffic conditions for a given location using AI."""
    logger.info("Traffic analysis requested for location: %s", req.location)

    prompt_parts = [f"Analyze current traffic conditions for: {req.location}"]
    if req.time_of_day:
        prompt_parts.append(f"Time of day: {req.time_of_day}")
    if req.include_weather:
        prompt_parts.append("Include weather impact on traffic.")
    if req.query:
        prompt_parts.append(f"Additional query: {req.query}")
    prompt_parts.append(
        "Provide: congestion level (low/moderate/high/severe), "
        "estimated delay in minutes, top 3 recommendations."
    )

    analysis_text = _run_agent("\n".join(prompt_parts))

    # Parse congestion level heuristically from the AI response
    congestion = "unknown"
    delay = 0
    lower = analysis_text.lower()
    for level in ("severe", "high", "moderate", "low"):
        if level in lower:
            congestion = level
            delay = {"severe": 45, "high": 25, "moderate": 10, "low": 2}[level]
            break

    return AnalysisResponse(
        status="success",
        location=req.location,
        analysis=analysis_text,
        congestion_level=congestion,
        estimated_delay=delay,
        recommendations=[
            "Check real-time traffic maps before departing.",
            "Consider alternate routes during peak hours.",
            "Allow extra travel time if congestion is high.",
        ],
    )


@router.post("/optimize-route", response_model=AnalysisResponse)
def optimize_route(req: RouteOptimizationRequest) -> AnalysisResponse:
    """Suggest optimized routes between origin and destination."""
    logger.info("Route optimization: %s -> %s", req.origin, req.destination)

    prompt = (
        f"Suggest the best route from '{req.origin}' to '{req.destination}'.\n"
        f"Avoid congestion: {req.avoid_congestion}.\n"
        f"Time of day: {req.time_of_day or 'not specified'}.\n"
        "Provide: recommended route, estimated travel time, alternative routes, "
        "and key waypoints to avoid."
    )
    analysis_text = _run_agent(prompt)

    return AnalysisResponse(
        status="success",
        analysis=analysis_text,
        recommendations=[
            f"Primary: {req.origin} → {req.destination}",
            "Check live traffic before departure.",
            "Use GPS navigation for real-time updates.",
        ],
    )


@router.get("/congestion/{location}")
def get_congestion(location: str) -> AnalysisResponse:
    """Get current congestion level for a location."""
    logger.info("Congestion query for: %s", location)

    prompt = (
        f"What is the current congestion level at '{location}'? "
        "Rate it as low / moderate / high / severe and explain briefly."
    )
    analysis_text = _run_agent(prompt)

    lower = analysis_text.lower()
    congestion = "unknown"
    for level in ("severe", "high", "moderate", "low"):
        if level in lower:
            congestion = level
            break

    return AnalysisResponse(
        status="success",
        location=location,
        analysis=analysis_text,
        congestion_level=congestion,
    )


@router.post("/alerts")
def create_alert(req: AlertRequest) -> Dict[str, Any]:
    """Create a new traffic alert."""
    logger.info("Alert created: %s at %s", req.alert_type, req.location)
    alert_id = f"alert_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    return {
        "status": "created",
        "alert_id": alert_id,
        "location": req.location,
        "alert_type": req.alert_type,
        "severity": req.severity,
        "description": req.description,
        "created_at": datetime.utcnow().isoformat(),
    }


@router.get("/alerts")
def list_alerts() -> Dict[str, Any]:
    """List active traffic alerts (placeholder – extend with DB)."""
    return {
        "status": "ok",
        "alerts": [],
        "message": "No active alerts. Connect a database to persist alerts.",
    }


@router.get("/history")
def get_history(limit: int = 20) -> Dict[str, Any]:
    """Retrieve recent analysis history (placeholder – extend with DB)."""
    return {
        "status": "ok",
        "history": [],
        "message": "History tracking requires database configuration.",
        "limit": limit,
    }


@router.get("/weather/{location}")
def get_weather_impact(location: str) -> AnalysisResponse:
    """Get weather impact on traffic for a location."""
    logger.info("Weather impact query for: %s", location)

    prompt = (
        f"Describe the current weather conditions at '{location}' and "
        "how they are impacting traffic. Include visibility, road conditions, "
        "and recommended precautions."
    )
    analysis_text = _run_agent(prompt)

    return AnalysisResponse(
        status="success",
        location=location,
        analysis=analysis_text,
    )
