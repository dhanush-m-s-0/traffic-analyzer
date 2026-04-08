"""Unit tests for the TrafficAnalyzerAgent."""

import pytest
from unittest.mock import MagicMock, patch


class TestTrafficAnalyzerAgentInit:
    """Tests for agent initialisation."""

    def test_raises_without_api_key(self):
        """Agent should raise ValueError when no Groq API key is available."""
        from src.agent.groq_agent import TrafficAnalyzerAgent

        with patch("src.agent.groq_agent.settings") as mock_settings:
            mock_settings.groq_api_key = ""
            mock_settings.groq_model = "llama3-8b-8192"
            mock_settings.agent_temperature = 0.1
            mock_settings.agent_max_iterations = 10
            mock_settings.agent_verbose = False

            with pytest.raises(ValueError, match="Groq API key is required"):
                TrafficAnalyzerAgent()

    def test_initialises_with_api_key(self):
        """Agent initialises successfully when a Groq API key is provided."""
        from src.agent.groq_agent import TrafficAnalyzerAgent

        with (
            patch("src.agent.groq_agent.ChatGroq") as mock_groq,
            patch("src.agent.groq_agent.create_agent") as mock_create_agent,
        ):
            mock_groq.return_value = MagicMock()
            mock_create_agent.return_value = MagicMock()

            agent = TrafficAnalyzerAgent(api_key="gsk_test_key")
            assert agent is not None

    def test_analyze_returns_dict_with_output(self):
        """Agent.analyze should return a dict with 'query' and 'output' keys."""
        from src.agent.groq_agent import TrafficAnalyzerAgent
        from langchain_core.messages import AIMessage

        mock_compiled_agent = MagicMock()
        mock_compiled_agent.invoke.return_value = {
            "messages": [AIMessage(content="Test traffic analysis result")]
        }

        with (
            patch("src.agent.groq_agent.ChatGroq") as mock_groq,
            patch("src.agent.groq_agent.create_agent") as mock_create_agent,
        ):
            mock_groq.return_value = MagicMock()
            mock_create_agent.return_value = mock_compiled_agent

            agent = TrafficAnalyzerAgent(api_key="gsk_test_key")
            result = agent.analyze("What is the traffic like in NYC?")

        assert result["query"] == "What is the traffic like in NYC?"
        assert result["output"] == "Test traffic analysis result"

    def test_analyze_handles_exception_gracefully(self):
        """Agent.analyze should catch exceptions and return an error dict."""
        from src.agent.groq_agent import TrafficAnalyzerAgent

        mock_compiled_agent = MagicMock()
        mock_compiled_agent.invoke.side_effect = RuntimeError("LLM unavailable")

        with (
            patch("src.agent.groq_agent.ChatGroq") as mock_groq,
            patch("src.agent.groq_agent.create_agent") as mock_create_agent,
        ):
            mock_groq.return_value = MagicMock()
            mock_create_agent.return_value = mock_compiled_agent

            agent = TrafficAnalyzerAgent(api_key="gsk_test_key")
            result = agent.analyze("Analyze traffic")

        assert result.get("error") is True
        assert "LLM unavailable" in result["output"]

    def test_clear_memory_clears_conversation_history(self):
        """clear_memory should empty the conversation history list."""
        from src.agent.groq_agent import TrafficAnalyzerAgent
        from langchain_core.messages import HumanMessage

        with (
            patch("src.agent.groq_agent.ChatGroq") as mock_groq,
            patch("src.agent.groq_agent.create_agent") as mock_create_agent,
        ):
            mock_groq.return_value = MagicMock()
            mock_create_agent.return_value = MagicMock()

            agent = TrafficAnalyzerAgent(api_key="gsk_test_key")
            agent._conversation_history.append(HumanMessage(content="test"))
            assert len(agent._conversation_history) == 1

            agent.clear_memory()
            assert len(agent._conversation_history) == 0

