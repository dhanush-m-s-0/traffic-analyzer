"""Command-line interface for the traffic analyzer using Click."""

import json
import logging
import sys

import click
from rich.console import Console
from rich.table import Table

from config.settings import settings
from src.services.route import RouteService
from src.services.traffic import TrafficService
from src.services.weather import WeatherService

console = Console()
logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))


@click.group()
@click.version_option(version="0.1.0")
def cli() -> None:
    """Traffic Analyzer – AI-powered traffic analysis and route optimisation."""


# ---------------------------------------------------------------------------
# analyze-traffic
# ---------------------------------------------------------------------------


@cli.command("analyze-traffic")
@click.option("--location", "-l", required=True, help="Location to analyse (e.g. 'New York')")
@click.option("--coordinates", "-c", default=None, help="Optional 'lat,lng' coordinates")
@click.option("--weather/--no-weather", default=True, help="Include weather impact")
@click.option("--json-output", is_flag=True, help="Output raw JSON")
def analyze_traffic(location: str, coordinates: str, weather: bool, json_output: bool) -> None:
    """Analyse current traffic conditions for a location."""
    traffic_svc = TrafficService()
    weather_svc = WeatherService()

    with console.status(f"[bold green]Fetching traffic data for {location}…"):
        traffic_data = traffic_svc.get_traffic_conditions(location, coordinates)
        analysis = traffic_svc.analyze_congestion(traffic_data)
        weather_data = weather_svc.get_current_weather(location) if weather else None
        impact = weather_svc.assess_traffic_impact(weather_data) if weather_data else None

    result = {
        "location": location,
        "traffic": traffic_data,
        "analysis": analysis,
        "weather": weather_data,
        "weather_impact": impact,
    }

    if json_output:
        click.echo(json.dumps(result, indent=2))
        return

    # Pretty output
    console.print(f"\n[bold cyan]📍 Traffic Analysis: {location}[/bold cyan]")

    table = Table(title="Traffic Conditions", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="dim")
    table.add_column("Value")

    table.add_row("Congestion Score", str(traffic_data.get("congestion_score")))
    table.add_row("Congestion Level", analysis.get("level", "").upper())
    table.add_row("Average Speed", f"{traffic_data.get('average_speed_kmh')} km/h")
    table.add_row("Incidents", str(traffic_data.get("incident_count", 0)))
    table.add_row("Road Conditions", traffic_data.get("road_conditions", "N/A").title())

    if weather_data:
        table.add_row("", "")
        table.add_row("Weather", weather_data.get("condition", "N/A").title())
        table.add_row("Temperature", f"{weather_data.get('temperature_c')} °C")
        table.add_row("Weather Impact", impact.get("severity", "none").upper() if impact else "N/A")

    console.print(table)
    console.print(f"\n[bold yellow]Recommendation:[/bold yellow] {analysis.get('recommendation', '')}")


# ---------------------------------------------------------------------------
# optimize-route
# ---------------------------------------------------------------------------


@cli.command("optimize-route")
@click.option("--start", "-s", required=True, help="Starting location")
@click.option("--end", "-e", required=True, help="Destination location")
@click.option("--avoid-tolls", is_flag=True, default=False, help="Avoid toll roads")
@click.option("--json-output", is_flag=True, help="Output raw JSON")
def optimize_route(start: str, end: str, avoid_tolls: bool, json_output: bool) -> None:
    """Find the optimal route between two locations."""
    traffic_svc = TrafficService()
    weather_svc = WeatherService()
    route_svc = RouteService()

    with console.status("[bold green]Calculating routes…"):
        traffic_data = traffic_svc.get_traffic_conditions(start)
        congestion = traffic_data.get("congestion_score", 0)
        weather_data = weather_svc.get_current_weather(start)
        impact = weather_svc.assess_traffic_impact(weather_data)
        result = route_svc.get_alternative_routes(
            start, end, congestion, impact.get("delay_multiplier", 1.0)
        )

    if json_output:
        click.echo(json.dumps(result, indent=2))
        return

    console.print(f"\n[bold cyan]🗺️  Route: {start} → {end}[/bold cyan]")

    for i, route in enumerate(result["routes"]):
        label = "✅ RECOMMENDED" if i == 0 else f"Option {i + 1}"
        style = "bold green" if i == 0 else "white"
        route_type = route.get("route_type", "direct")
        console.print(
            f"\n[{style}]{label} – {route_type}[/{style}]  "
            f"Distance: {route['distance_km']} km  |  "
            f"ETA: {route['estimated_duration_min']} min"
        )

    console.print(
        f"\n[bold yellow]Current congestion:[/bold yellow] {congestion}/100  |  "
        f"Weather delay: ×{impact.get('delay_multiplier', 1.0)}"
    )


# ---------------------------------------------------------------------------
# predict-congestion
# ---------------------------------------------------------------------------


@cli.command("predict-congestion")
@click.option("--location", "-l", required=True, help="Location to predict")
@click.option("--hours", "-h", default=3, show_default=True, help="Hours ahead to predict (1-24)")
@click.option("--json-output", is_flag=True, help="Output raw JSON")
def predict_congestion(location: str, hours: int, json_output: bool) -> None:
    """Predict future congestion levels at a location."""
    if not 1 <= hours <= 24:
        console.print("[bold red]Error:[/bold red] --hours must be between 1 and 24.")
        sys.exit(1)

    traffic_svc = TrafficService()

    with console.status(f"[bold green]Predicting congestion for {location}…"):
        result = traffic_svc.predict_congestion(location, hours)

    if json_output:
        click.echo(json.dumps(result, indent=2))
        return

    console.print(f"\n[bold cyan]🔮 Congestion Prediction: {location}[/bold cyan]")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Hours from Now")
    table.add_column("Predicted Hour (UTC)")
    table.add_column("Score")
    table.add_column("Level")

    for pred in result["predictions"]:
        level = pred["level"]
        color = {"low": "green", "moderate": "yellow", "high": "red", "severe": "bold red"}.get(
            level, "white"
        )
        table.add_row(
            str(pred["hours_from_now"]),
            f"{pred['predicted_hour']:02d}:00",
            str(pred["congestion_score"]),
            f"[{color}]{level.upper()}[/{color}]",
        )

    console.print(table)


# ---------------------------------------------------------------------------
# set-alert
# ---------------------------------------------------------------------------


@cli.command("set-alert")
@click.option("--location", "-l", required=True, help="Location to monitor")
@click.option(
    "--threshold",
    "-t",
    default=70,
    show_default=True,
    help="Congestion score threshold (0-100)",
)
@click.option("--json-output", is_flag=True, help="Output raw JSON")
def set_alert(location: str, threshold: int, json_output: bool) -> None:
    """Set a traffic alert for a location and check if it is currently triggered."""
    traffic_svc = TrafficService()

    with console.status(f"[bold green]Checking conditions for alert at {location}…"):
        traffic_data = traffic_svc.get_traffic_conditions(location)
        current_score = traffic_data.get("congestion_score", 0)
        triggered = current_score >= threshold

    result = {
        "location": location,
        "threshold": threshold,
        "current_score": current_score,
        "alert_triggered": triggered,
        "message": (
            f"⚠️  ALERT TRIGGERED: Congestion {current_score}/100 ≥ threshold {threshold}"
            if triggered
            else f"✅ No alert: Congestion {current_score}/100 < threshold {threshold}"
        ),
    }

    if json_output:
        click.echo(json.dumps(result, indent=2))
        return

    color = "bold red" if triggered else "bold green"
    console.print(f"\n[{color}]{result['message']}[/{color}]")


# ---------------------------------------------------------------------------
# view-history
# ---------------------------------------------------------------------------


@cli.command("view-history")
@click.option("--location", "-l", default=None, help="Filter by location")
@click.option("--limit", default=10, show_default=True, help="Number of records to display")
@click.option("--json-output", is_flag=True, help="Output raw JSON")
def view_history(location: str, limit: int, json_output: bool) -> None:
    """View historical traffic data from the database."""
    from src.models.database import TrafficRecord, init_db

    session_factory = init_db(settings.database_url)
    db = session_factory()

    try:
        query = db.query(TrafficRecord).order_by(TrafficRecord.recorded_at.desc())
        if location:
            query = query.filter(TrafficRecord.location.ilike(f"%{location}%"))
        records = query.limit(limit).all()
    finally:
        db.close()

    if not records:
        console.print("[yellow]No historical records found.[/yellow]")
        return

    if json_output:
        click.echo(
            json.dumps(
                [
                    {
                        "id": r.id,
                        "location": r.location,
                        "congestion_score": r.congestion_score,
                        "congestion_level": r.congestion_level,
                        "recorded_at": r.recorded_at.isoformat() if r.recorded_at else None,
                    }
                    for r in records
                ],
                indent=2,
            )
        )
        return

    console.print(f"\n[bold cyan]📊 Traffic History[/bold cyan] (last {len(records)} records)")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID")
    table.add_column("Location")
    table.add_column("Congestion")
    table.add_column("Level")
    table.add_column("Speed (km/h)")
    table.add_column("Recorded At")

    for r in records:
        level = r.congestion_level or "unknown"
        color = {"low": "green", "moderate": "yellow", "high": "red", "severe": "bold red"}.get(
            level, "white"
        )
        table.add_row(
            str(r.id),
            r.location,
            str(r.congestion_score),
            f"[{color}]{level.upper()}[/{color}]",
            str(r.average_speed_kmh or "N/A"),
            r.recorded_at.strftime("%Y-%m-%d %H:%M") if r.recorded_at else "N/A",
        )

    console.print(table)


if __name__ == "__main__":
    cli()
