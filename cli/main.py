"""CLI interface for Traffic Analyzer using Click."""

import json
import sys

import click
import requests

from config.settings import settings

API_BASE = settings.api_base_url


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _post(endpoint: str, payload: dict) -> dict:
    """POST to the API and return the JSON response."""
    try:
        resp = requests.post(f"{API_BASE}/api{endpoint}", json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        click.secho(
            f"Cannot connect to the API server at {API_BASE}. "
            "Please start the server first: python -m api.main",
            fg="red",
        )
        sys.exit(1)
    except requests.exceptions.HTTPError as exc:
        click.secho(f"API error: {exc}", fg="red")
        sys.exit(1)


def _get(endpoint: str, params: dict | None = None) -> dict:
    """GET from the API and return the JSON response."""
    try:
        resp = requests.get(f"{API_BASE}/api{endpoint}", params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        click.secho(
            f"Cannot connect to the API server at {API_BASE}. "
            "Please start the server first: python -m api.main",
            fg="red",
        )
        sys.exit(1)
    except requests.exceptions.HTTPError as exc:
        click.secho(f"API error: {exc}", fg="red")
        sys.exit(1)


# ---------------------------------------------------------------------------
# CLI group
# ---------------------------------------------------------------------------


@click.group()
@click.version_option(settings.APP_VERSION)
def cli() -> None:
    """Traffic Analyzer – Agentic AI traffic intelligence powered by Groq."""


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


@cli.command("analyze")
@click.option("--location", "-l", required=True, help="Location to analyze.")
@click.option(
    "--time",
    "-t",
    default=None,
    help="Time of day (morning/afternoon/evening/night).",
)
@click.option("--weather/--no-weather", default=False, help="Include weather impact.")
@click.option("--query", "-q", default=None, help="Natural language query for the AI.")
@click.option("--json-output", is_flag=True, help="Output raw JSON.")
def analyze_traffic(
    location: str,
    time: str | None,
    weather: bool,
    query: str | None,
    json_output: bool,
) -> None:
    """Analyze traffic conditions for a location."""
    click.echo(f"🔍 Analyzing traffic for: {location} …")
    payload = {
        "location": location,
        "time_of_day": time,
        "include_weather": weather,
        "query": query,
    }
    result = _post("/analyze", payload)
    if json_output:
        click.echo(json.dumps(result, indent=2))
        return

    click.secho(f"\n📍 Location: {result.get('location')}", fg="cyan")
    click.secho(
        f"🚦 Congestion: {result.get('congestion_level', 'N/A').upper()}",
        fg="yellow" if result.get("congestion_level") != "low" else "green",
    )
    click.secho(
        f"⏱  Estimated delay: {result.get('estimated_delay', 0)} minutes", fg="white"
    )
    click.secho("\n📊 Analysis:", fg="bright_white")
    click.echo(result.get("analysis", ""))
    click.secho("\n💡 Recommendations:", fg="bright_white")
    for rec in result.get("recommendations", []):
        click.echo(f"  • {rec}")


@cli.command("optimize-route")
@click.option("--origin", "-o", required=True, help="Starting point.")
@click.option("--destination", "-d", required=True, help="End point.")
@click.option("--avoid-congestion/--no-avoid-congestion", default=True)
@click.option("--time", "-t", default=None, help="Preferred departure time.")
@click.option("--json-output", is_flag=True, help="Output raw JSON.")
def optimize_route(
    origin: str,
    destination: str,
    avoid_congestion: bool,
    time: str | None,
    json_output: bool,
) -> None:
    """Find the best route from origin to destination."""
    click.echo(f"🗺  Optimizing route: {origin} → {destination} …")
    payload = {
        "origin": origin,
        "destination": destination,
        "avoid_congestion": avoid_congestion,
        "time_of_day": time,
    }
    result = _post("/optimize-route", payload)
    if json_output:
        click.echo(json.dumps(result, indent=2))
        return

    click.secho("\n🛣  Route Analysis:", fg="bright_white")
    click.echo(result.get("analysis", ""))
    click.secho("\n💡 Recommendations:", fg="bright_white")
    for rec in result.get("recommendations", []):
        click.echo(f"  • {rec}")


@cli.command("congestion")
@click.argument("location")
@click.option("--json-output", is_flag=True)
def check_congestion(location: str, json_output: bool) -> None:
    """Check current congestion level at a location."""
    click.echo(f"🚗 Checking congestion at: {location} …")
    import urllib.parse
    encoded = urllib.parse.quote(location)
    result = _get(f"/congestion/{encoded}")
    if json_output:
        click.echo(json.dumps(result, indent=2))
        return

    click.secho(
        f"\n🚦 Congestion at {location}: {result.get('congestion_level', 'N/A').upper()}",
        fg="yellow",
    )
    click.echo(result.get("analysis", ""))


@cli.command("weather")
@click.argument("location")
@click.option("--json-output", is_flag=True)
def weather_impact(location: str, json_output: bool) -> None:
    """Get weather impact on traffic for a location."""
    click.echo(f"🌦  Weather impact for: {location} …")
    import urllib.parse
    encoded = urllib.parse.quote(location)
    result = _get(f"/weather/{encoded}")
    if json_output:
        click.echo(json.dumps(result, indent=2))
        return

    click.secho("\n🌤  Weather & Traffic Impact:", fg="bright_white")
    click.echo(result.get("analysis", ""))


@cli.command("alerts")
@click.option("--json-output", is_flag=True)
def list_alerts(json_output: bool) -> None:
    """List active traffic alerts."""
    result = _get("/alerts")
    if json_output:
        click.echo(json.dumps(result, indent=2))
        return

    alerts = result.get("alerts", [])
    if not alerts:
        click.secho("✅ No active alerts.", fg="green")
    else:
        for alert in alerts:
            click.secho(
                f"⚠  [{alert.get('severity', '').upper()}] "
                f"{alert.get('location')}: {alert.get('description')}",
                fg="yellow",
            )


@cli.command("serve")
@click.option("--host", default=settings.API_HOST, help="Host to bind.")
@click.option("--port", default=settings.API_PORT, type=int, help="Port to listen on.")
@click.option("--reload", is_flag=True, help="Enable auto-reload (development only).")
def serve(host: str, port: int, reload: bool) -> None:
    """Start the Traffic Analyzer API server."""
    import uvicorn

    click.secho(
        f"🚀 Starting Traffic Analyzer API on http://{host}:{port}", fg="green"
    )
    click.echo("   Press Ctrl+C to stop.\n")
    uvicorn.run("api.main:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    cli()
