# 🚦 Traffic Analyzer

> Comprehensive traffic analysis powered by **Agentic AI** with [Groq](https://groq.com) ultra-fast LLM inference and [LangChain](https://langchain.com) agent orchestration.

---

## ✨ Features

| Feature | Description |
|---|---|
| **Agentic AI** | ReAct agent with Groq LLM and LangChain tool orchestration |
| **Real-time Analysis** | Traffic condition assessment with congestion scoring |
| **Route Optimisation** | Multi-route comparison with weather and congestion factors |
| **Congestion Prediction** | Time-of-day based forecasting for up to 24 hours ahead |
| **Traffic Alerts** | Threshold-based alert generation |
| **Weather Integration** | Weather impact assessment on traffic conditions |
| **REST API** | Async FastAPI endpoints with auto-generated Swagger docs |
| **CLI Interface** | Rich command-line interface via Click |
| **Historical Data** | SQLite persistence with SQLAlchemy ORM |
| **Docker Support** | Production-ready container configuration |

---

## 📁 Project Structure

```
traffic-analyzer/
├── README.md
├── requirements.txt
├── .env.example
├── setup.py
├── pyproject.toml
├── Dockerfile
├── config/
│   ├── __init__.py
│   └── settings.py          # Pydantic-settings configuration
├── src/
│   ├── __init__.py
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── groq_agent.py    # Groq + LangChain ReAct agent
│   │   └── tools.py         # LangChain tools for traffic/weather/route
│   ├── models/
│   │   ├── __init__.py
│   │   └── database.py      # SQLAlchemy ORM models
│   └── services/
│       ├── __init__.py
│       ├── traffic.py        # Traffic condition service
│       ├── weather.py        # Weather data service
│       └── route.py          # Route optimisation service
├── api/
│   ├── __init__.py
│   ├── main.py               # FastAPI application
│   └── routes.py             # API route handlers
├── cli/
│   ├── __init__.py
│   └── main.py               # Click CLI commands
├── tests/
│   ├── __init__.py
│   ├── test_agent.py
│   ├── test_api.py
│   └── test_tools.py
└── notebooks/
    └── demo.ipynb            # Interactive Jupyter demo
```

---

## 🚀 Quick Start

### 1. Clone and Install

```bash
git clone https://github.com/dhanush-m-s-0/traffic-analyzer.git
cd traffic-analyzer
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```dotenv
GROQ_API_KEY=your_groq_api_key_here   # Required for AI agent
WEATHER_API_KEY=your_key_here          # Optional – uses simulation if absent
```

Get a free Groq API key at [console.groq.com](https://console.groq.com).

### 3. Run the API Server

```bash
uvicorn api.main:app --reload
# API available at http://localhost:8000
# Swagger UI at  http://localhost:8000/docs
```

### 4. Use the CLI

```bash
# Analyse traffic
python -m cli.main analyze-traffic --location "New York"

# Optimise a route
python -m cli.main optimize-route --start "New York" --end "Philadelphia"

# Predict congestion
python -m cli.main predict-congestion --location "Manhattan" --hours 6

# Set an alert
python -m cli.main set-alert --location "Chicago" --threshold 75

# View history
python -m cli.main view-history --location "New York" --limit 10
```

---

## 🐳 Docker

```bash
docker build -t traffic-analyzer .
docker run -p 8000:8000 --env-file .env traffic-analyzer
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Service info |
| `GET` | `/health` | Health check |
| `POST` | `/api/v1/analyze` | Analyse traffic conditions |
| `POST` | `/api/v1/optimize-route` | Get optimised route recommendations |
| `GET` | `/api/v1/predictions` | Congestion predictions (N hours ahead) |
| `POST` | `/api/v1/alerts` | Create a traffic alert |
| `GET` | `/api/v1/history` | Retrieve historical traffic data |

### Example: Analyse Traffic

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"location": "New York", "include_weather": true}'
```

### Example: Optimise Route

```bash
curl -X POST http://localhost:8000/api/v1/optimize-route \
  -H "Content-Type: application/json" \
  -d '{"start": "New York", "end": "Philadelphia"}'
```

### Example: Get Predictions

```bash
curl "http://localhost:8000/api/v1/predictions?location=Boston&hours_ahead=3"
```

---

## 🤖 Using the Agentic AI

The agent uses a ReAct (Reasoning + Acting) pattern with Groq LLM:

```python
from src.agent.groq_agent import TrafficAnalyzerAgent

agent = TrafficAnalyzerAgent(api_key="your_groq_api_key")

# Natural language traffic analysis
result = agent.analyze(
    "What is the traffic like in New York right now? "
    "Should I drive to Philadelphia or take the train?"
)
print(result["output"])

# Convenience methods
result = agent.analyze_traffic("Chicago", coordinates="41.8781,-87.6298")
result = agent.optimize_route("New York", "Boston")
result = agent.predict_congestion("Manhattan", hours_ahead=4)
result = agent.generate_alerts("Los Angeles", threshold=80)
```

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

---

## ⚙️ Technology Stack

| Component | Technology |
|-----------|-----------|
| LLM | [Groq](https://groq.com) – ultra-fast LLama inference |
| Agent Framework | [LangChain](https://langchain.com) ReAct agent |
| API | [FastAPI](https://fastapi.tiangolo.com) with async support |
| CLI | [Click](https://click.palletsprojects.com) + [Rich](https://rich.readthedocs.io) |
| Database | SQLite with [SQLAlchemy](https://sqlalchemy.org) ORM |
| Config | [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) |
| Testing | [pytest](https://pytest.org) + pytest-asyncio |
| Deployment | [Docker](https://docker.com) |

---

## 📄 License

MIT License – see [LICENSE](LICENSE) for details.