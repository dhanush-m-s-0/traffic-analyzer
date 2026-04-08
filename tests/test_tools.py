"""Unit tests for agent tools."""

import json
from unittest.mock import MagicMock, patch

import pytest

from src.agent.tools import (
    GenerateAlertTool,
    GetTrafficConditionsTool,
    GetWeatherConditionsTool,
    OptimizeRouteTool,
    PredictCongestionTool,
    get_all_tools,
)


class TestGetTrafficConditionsTool:
    """Tests for GetTrafficConditionsTool."""

    def test_run_returns_json(self):
        tool = GetTrafficConditionsTool()
        result = tool._run(location="New York")
        data = json.loads(result)
        assert "congestion_score" in data
        assert "location" in data
        assert data["location"] == "New York"

    def test_run_with_coordinates(self):
        tool = GetTrafficConditionsTool()
        result = tool._run(location="Los Angeles", coordinates="34.0522,-118.2437")
        data = json.loads(result)
        assert data["coordinates"] == "34.0522,-118.2437"

    def test_run_includes_analysis(self):
        tool = GetTrafficConditionsTool()
        result = tool._run(location="Chicago")
        data = json.loads(result)
        assert "analysis" in data
        assert "level" in data["analysis"]
        assert data["analysis"]["level"] in ("low", "moderate", "high", "severe")


class TestPredictCongestionTool:
    """Tests for PredictCongestionTool."""

    def test_predict_returns_predictions_list(self):
        tool = PredictCongestionTool()
        result = tool._run(location="Boston", hours_ahead=2)
        data = json.loads(result)
        assert "predictions" in data
        assert len(data["predictions"]) == 2

    def test_predict_default_hours(self):
        tool = PredictCongestionTool()
        result = tool._run(location="Seattle")
        data = json.loads(result)
        assert len(data["predictions"]) == 1

    def test_prediction_has_required_fields(self):
        tool = PredictCongestionTool()
        result = tool._run(location="Denver", hours_ahead=3)
        data = json.loads(result)
        for pred in data["predictions"]:
            assert "hours_from_now" in pred
            assert "congestion_score" in pred
            assert "level" in pred


class TestGetWeatherConditionsTool:
    """Tests for GetWeatherConditionsTool."""

    def test_run_returns_weather_data(self):
        tool = GetWeatherConditionsTool()
        result = tool._run(location="Miami")
        data = json.loads(result)
        assert "condition" in data
        assert "temperature_c" in data
        assert "traffic_impact" in data

    def test_weather_impact_has_severity(self):
        tool = GetWeatherConditionsTool()
        result = tool._run(location="Phoenix")
        data = json.loads(result)
        impact = data["traffic_impact"]
        assert "severity" in impact
        assert "delay_multiplier" in impact


class TestOptimizeRouteTool:
    """Tests for OptimizeRouteTool."""

    def test_run_returns_routes(self):
        tool = OptimizeRouteTool()
        result = tool._run(start="New York", end="Philadelphia")
        data = json.loads(result)
        assert "routes" in data
        assert "recommended" in data

    def test_recommended_route_has_distance_and_duration(self):
        tool = OptimizeRouteTool()
        result = tool._run(start="Chicago", end="Detroit")
        data = json.loads(result)
        rec = data["recommended"]
        assert "distance_km" in rec
        assert "estimated_duration_min" in rec

    def test_congestion_affects_duration(self):
        tool = OptimizeRouteTool()
        result_low = json.loads(tool._run(start="Atlanta", end="Nashville", congestion_score=10))
        result_high = json.loads(tool._run(start="Atlanta", end="Nashville", congestion_score=90))
        # High congestion should increase travel time
        assert (
            result_high["recommended"]["estimated_duration_min"]
            > result_low["recommended"]["estimated_duration_min"]
        )


class TestGenerateAlertTool:
    """Tests for GenerateAlertTool."""

    def test_alert_triggered_when_above_threshold(self):
        tool = GenerateAlertTool()
        result = tool._run(location="Houston", congestion_score=85, threshold=70)
        data = json.loads(result)
        assert data["alert_triggered"] is True

    def test_alert_not_triggered_when_below_threshold(self):
        tool = GenerateAlertTool()
        result = tool._run(location="Houston", congestion_score=50, threshold=70)
        data = json.loads(result)
        assert data["alert_triggered"] is False

    def test_critical_severity_for_high_congestion(self):
        tool = GenerateAlertTool()
        result = tool._run(location="Dallas", congestion_score=95, threshold=70)
        data = json.loads(result)
        assert data["severity"] == "critical"

    def test_no_alert_severity_when_below_threshold(self):
        tool = GenerateAlertTool()
        result = tool._run(location="Dallas", congestion_score=20, threshold=70)
        data = json.loads(result)
        assert data["severity"] == "none"


class TestGetAllTools:
    """Tests for the get_all_tools helper."""

    def test_returns_five_tools(self):
        tools = get_all_tools()
        assert len(tools) == 5

    def test_all_tools_have_name_and_description(self):
        for tool in get_all_tools():
            assert tool.name
            assert tool.description
