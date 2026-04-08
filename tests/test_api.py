"""Unit tests for the FastAPI routes."""

import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


class TestRootEndpoints:
    """Tests for root and health check endpoints."""

    def test_root_returns_service_info(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Traffic Analyzer API"
        assert data["status"] == "running"

    def test_health_returns_healthy(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestAnalyzeEndpoint:
    """Tests for POST /api/v1/analyze."""

    def test_analyze_returns_traffic_data(self):
        response = client.post(
            "/api/v1/analyze",
            json={"location": "New York", "include_weather": True},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["location"] == "New York"
        assert "traffic" in data
        assert "congestion_analysis" in data

    def test_analyze_without_weather(self):
        response = client.post(
            "/api/v1/analyze",
            json={"location": "Los Angeles", "include_weather": False},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["weather"] is None

    def test_analyze_with_weather_includes_impact(self):
        response = client.post(
            "/api/v1/analyze",
            json={"location": "Chicago", "include_weather": True},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["weather"] is not None
        assert data["weather_impact"] is not None

    def test_analyze_missing_location_returns_422(self):
        response = client.post("/api/v1/analyze", json={})
        assert response.status_code == 422

    def test_analyze_with_coordinates(self):
        response = client.post(
            "/api/v1/analyze",
            json={
                "location": "San Francisco",
                "coordinates": "37.7749,-122.4194",
                "include_weather": False,
            },
        )
        assert response.status_code == 200


class TestOptimizeRouteEndpoint:
    """Tests for POST /api/v1/optimize-route."""

    def test_optimize_route_returns_routes(self):
        response = client.post(
            "/api/v1/optimize-route",
            json={"start": "New York", "end": "Philadelphia"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "routes" in data
        assert "recommended" in data
        assert data["start"] == "New York"
        assert data["end"] == "Philadelphia"

    def test_optimize_route_recommended_has_required_fields(self):
        response = client.post(
            "/api/v1/optimize-route",
            json={"start": "Chicago", "end": "Detroit"},
        )
        assert response.status_code == 200
        rec = response.json()["recommended"]
        assert "distance_km" in rec
        assert "estimated_duration_min" in rec

    def test_optimize_route_missing_fields_returns_422(self):
        response = client.post("/api/v1/optimize-route", json={"start": "Chicago"})
        assert response.status_code == 422


class TestPredictionsEndpoint:
    """Tests for GET /api/v1/predictions."""

    def test_predictions_returns_data(self):
        response = client.get("/api/v1/predictions?location=Boston&hours_ahead=3")
        assert response.status_code == 200
        data = response.json()
        assert data["location"] == "Boston"
        assert len(data["predictions"]) == 3

    def test_predictions_missing_location_returns_422(self):
        response = client.get("/api/v1/predictions")
        assert response.status_code == 422

    def test_predictions_invalid_hours_returns_422(self):
        response = client.get("/api/v1/predictions?location=Boston&hours_ahead=99")
        assert response.status_code == 422


class TestAlertsEndpoint:
    """Tests for POST /api/v1/alerts."""

    def test_create_alert_returns_alert_data(self):
        response = client.post(
            "/api/v1/alerts",
            json={"location": "Miami", "threshold": 70, "alert_type": "congestion"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["location"] == "Miami"
        assert "alert_triggered" in data
        assert "current_congestion" in data

    def test_alert_uses_default_threshold(self):
        response = client.post(
            "/api/v1/alerts",
            json={"location": "Seattle"},
        )
        assert response.status_code == 200
        assert response.json()["threshold"] == 70

    def test_alert_missing_location_returns_422(self):
        response = client.post("/api/v1/alerts", json={})
        assert response.status_code == 422


class TestHistoryEndpoint:
    """Tests for GET /api/v1/history."""

    def test_history_returns_records_list(self):
        response = client.get("/api/v1/history")
        assert response.status_code == 200
        data = response.json()
        assert "records" in data
        assert "total" in data

    def test_history_with_location_filter(self):
        # First create a record
        client.post("/api/v1/analyze", json={"location": "Denver", "include_weather": False})
        response = client.get("/api/v1/history?location=Denver")
        assert response.status_code == 200
        data = response.json()
        assert data["location_filter"] == "Denver"

    def test_history_limit_parameter(self):
        response = client.get("/api/v1/history?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] <= 5
