"""Route optimisation service providing intelligent routing recommendations."""

import logging
import math
import random
from datetime import datetime, UTC
from typing import Any

logger = logging.getLogger(__name__)

# Average driving speed used for travel-time estimates (km/h)
_BASE_SPEED_KMH = 50.0


class RouteService:
    """Service for calculating and optimising routes between locations."""

    def __init__(self) -> None:
        """Initialise the route service."""
        logger.info("RouteService initialised")

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def calculate_route(
        self,
        start: str,
        end: str,
        congestion_score: int = 0,
        weather_delay_multiplier: float = 1.0,
    ) -> dict[str, Any]:
        """Calculate the optimal route between two locations.

        Args:
            start: Starting location name.
            end: Destination location name.
            congestion_score: Current traffic congestion (0-100).
            weather_delay_multiplier: Factor by which weather increases travel time.

        Returns:
            Dictionary with route details including distance, duration, and steps.
        """
        logger.info("Calculating route: %s -> %s", start, end)

        distance_km = self._estimate_distance(start, end)
        base_duration_min = (distance_km / _BASE_SPEED_KMH) * 60

        # Apply congestion and weather penalties
        congestion_factor = 1 + (congestion_score / 100)
        adjusted_duration = base_duration_min * congestion_factor * weather_delay_multiplier

        return {
            "start": start,
            "end": end,
            "distance_km": round(distance_km, 2),
            "estimated_duration_min": round(adjusted_duration, 1),
            "congestion_factor": round(congestion_factor, 2),
            "weather_delay_multiplier": round(weather_delay_multiplier, 2),
            "steps": self._generate_route_steps(start, end, int(distance_km)),
            "calculated_at": datetime.now(UTC).isoformat(),
        }

    def get_alternative_routes(
        self,
        start: str,
        end: str,
        congestion_score: int = 0,
        weather_delay_multiplier: float = 1.0,
        num_alternatives: int = 3,
    ) -> dict[str, Any]:
        """Generate multiple alternative routes ranked by total travel time.

        Args:
            start: Starting location name.
            end: Destination location name.
            congestion_score: Current congestion level (0-100).
            weather_delay_multiplier: Weather-based delay factor.
            num_alternatives: Number of alternative routes to generate.

        Returns:
            Dictionary with ranked list of alternative routes.
        """
        logger.info("Getting %d alternative routes: %s -> %s", num_alternatives, start, end)

        base_route = self.calculate_route(start, end, congestion_score, weather_delay_multiplier)
        alternatives = [base_route]

        route_types = ["via highway", "via local roads", "via scenic route", "via toll road"]
        for i in range(num_alternatives):
            variant_label = route_types[i % len(route_types)]
            # Alternate routes vary by ±15% distance and have different congestion exposure
            distance_factor = random.uniform(0.85, 1.15)
            alt_congestion = max(0, min(100, congestion_score + random.randint(-20, 20)))
            alt_route = self.calculate_route(
                start,
                end,
                alt_congestion,
                weather_delay_multiplier,
            )
            alt_route["distance_km"] = round(alt_route["distance_km"] * distance_factor, 2)
            alt_route["estimated_duration_min"] = round(
                alt_route["estimated_duration_min"] * distance_factor, 1
            )
            alt_route["route_type"] = variant_label
            alternatives.append(alt_route)

        # Rank by estimated travel time
        alternatives.sort(key=lambda r: r["estimated_duration_min"])
        for idx, route in enumerate(alternatives):
            route["rank"] = idx + 1

        return {
            "start": start,
            "end": end,
            "routes": alternatives,
            "recommended": alternatives[0],
            "generated_at": datetime.now(UTC).isoformat(),
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _estimate_distance(start: str, end: str) -> float:
        """Estimate distance between two locations.

        Uses a hash-based deterministic pseudo-distance so repeated calls
        return consistent results without a real geocoding API.
        """
        # Deterministic seed from location names
        seed = hash(f"{start.lower()}-{end.lower()}") % 10000
        rng = random.Random(seed)
        return rng.uniform(5.0, 200.0)

    @staticmethod
    def _generate_route_steps(start: str, end: str, distance_km: int) -> list[dict[str, Any]]:
        """Generate plausible turn-by-turn steps for a route."""
        directions = ["north", "south", "east", "west", "northeast", "northwest", "southeast", "southwest"]
        road_types = ["Main St", "Highway", "Ave", "Blvd", "Rd", "Expressway"]

        num_steps = max(3, min(8, distance_km // 20 + 2))
        rng = random.Random(hash(f"{start}-{end}"))

        steps = [{"step": 1, "instruction": f"Depart from {start}", "distance_km": 0.0}]
        remaining = distance_km
        for step_num in range(2, num_steps):
            seg_dist = round(rng.uniform(1, remaining / (num_steps - step_num + 1)), 1)
            remaining -= seg_dist
            direction = rng.choice(directions)
            road = rng.choice(road_types)
            steps.append(
                {
                    "step": step_num,
                    "instruction": f"Head {direction} on {road}",
                    "distance_km": seg_dist,
                }
            )
        steps.append(
            {
                "step": num_steps,
                "instruction": f"Arrive at {end}",
                "distance_km": round(max(0, remaining), 1),
            }
        )
        return steps
