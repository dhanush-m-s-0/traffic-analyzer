"""Groq-powered LangChain agent for intelligent traffic analysis."""

import logging
from typing import Any, Optional

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from config.settings import settings
from src.agent.tools import get_all_tools

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are an intelligent traffic analysis assistant powered by real-time data tools.
Your goal is to help users understand traffic conditions, plan optimal routes, predict congestion, and receive timely alerts.

Guidelines:
1. Always check traffic conditions before giving route advice.
2. Consider weather impact when assessing travel times.
3. Provide specific, actionable recommendations.
4. Include congestion scores and estimated delays in your answers.
5. Proactively mention alternative routes when congestion is high.

Use the available tools to gather real-time data before providing your analysis."""


class TrafficAnalyzerAgent:
    """Agentic AI system for comprehensive traffic analysis using Groq LLM.

    Attributes:
        llm: The Groq language model instance.
        tools: List of LangChain tools available to the agent.
        agent: The compiled agent graph that orchestrates tool calls.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_iterations: Optional[int] = None,
        verbose: Optional[bool] = None,
    ) -> None:
        """Initialise the traffic analyzer agent.

        Args:
            api_key: Groq API key. Defaults to ``settings.groq_api_key``.
            model: Groq model name. Defaults to ``settings.groq_model``.
            temperature: Sampling temperature. Defaults to ``settings.agent_temperature``.
            max_iterations: Maximum agent iterations. Defaults to ``settings.agent_max_iterations``.
            verbose: Enable verbose output. Defaults to ``settings.agent_verbose``.
        """
        _api_key = api_key or settings.groq_api_key
        _model = model or settings.groq_model
        _temperature = temperature if temperature is not None else settings.agent_temperature
        _verbose = verbose if verbose is not None else settings.agent_verbose

        if not _api_key:
            raise ValueError(
                "Groq API key is required. Set GROQ_API_KEY in .env or pass api_key parameter."
            )

        logger.info("Initialising TrafficAnalyzerAgent (model=%s)", _model)

        self.llm = ChatGroq(
            api_key=_api_key,
            model=_model,
            temperature=_temperature,
        )

        self.tools = get_all_tools()
        self._conversation_history: list = []

        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=_SYSTEM_PROMPT,
            debug=_verbose,
        )

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def analyze(self, query: str) -> dict[str, Any]:
        """Run the agent on a natural-language traffic query.

        Args:
            query: User question or instruction.

        Returns:
            Dictionary with the agent ``output`` and the original ``query``.
        """
        logger.info("Agent query: %s", query)
        try:
            self._conversation_history.append(HumanMessage(content=query))
            result = self.agent.invoke({"messages": self._conversation_history})
            messages = result.get("messages", [])
            output = messages[-1].content if messages else "No response generated."
            # Keep assistant message in history for context
            if messages:
                self._conversation_history.append(messages[-1])
            return {"query": query, "output": output}
        except Exception as exc:
            logger.exception("Agent error processing query: %s", query)
            return {"query": query, "output": f"Error: {exc}", "error": True}

    def analyze_traffic(self, location: str, coordinates: Optional[str] = None) -> dict[str, Any]:
        """Analyse traffic conditions for a specific location.

        Args:
            location: Location name.
            coordinates: Optional "lat,lng" string.

        Returns:
            Agent analysis result.
        """
        coord_hint = f" (coordinates: {coordinates})" if coordinates else ""
        query = (
            f"Analyze current traffic conditions for {location}{coord_hint}. "
            "Include congestion levels, average speeds, any incidents, and recommendations."
        )
        return self.analyze(query)

    def optimize_route(
        self, start: str, end: str, avoid_tolls: bool = False
    ) -> dict[str, Any]:
        """Find the optimal route between two locations.

        Args:
            start: Origin location.
            end: Destination location.
            avoid_tolls: Whether to prefer non-toll routes.

        Returns:
            Agent route optimisation result.
        """
        toll_hint = " Avoid toll roads." if avoid_tolls else ""
        query = (
            f"Find the optimal route from {start} to {end}.{toll_hint} "
            "Check current traffic conditions and weather, then recommend the best route "
            "with estimated travel time and any alternatives."
        )
        return self.analyze(query)

    def predict_congestion(self, location: str, hours_ahead: int = 2) -> dict[str, Any]:
        """Predict future congestion at a location.

        Args:
            location: Location to predict congestion for.
            hours_ahead: How many hours ahead to predict.

        Returns:
            Agent congestion prediction result.
        """
        query = (
            f"Predict traffic congestion at {location} for the next {hours_ahead} hours. "
            "Identify peak congestion times and suggest the best times to travel."
        )
        return self.analyze(query)

    def generate_alerts(self, location: str, threshold: int = 70) -> dict[str, Any]:
        """Check if current conditions warrant a traffic alert.

        Args:
            location: Location to check.
            threshold: Congestion score threshold (0-100) to trigger an alert.

        Returns:
            Agent alert generation result.
        """
        query = (
            f"Check traffic conditions at {location} and generate an alert "
            f"if the congestion score exceeds {threshold}. "
            "Include weather conditions and provide actionable advice."
        )
        return self.analyze(query)

    def clear_memory(self) -> None:
        """Clear the agent's conversation history."""
        self._conversation_history.clear()
        logger.info("Agent memory cleared")

