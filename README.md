# Traffic Analyzer

## Overview
The Traffic Analyzer is a comprehensive application designed to analyze traffic patterns, weather integration, route optimization, and more through a user-friendly API and CLI.

## Features
- Traffic analysis algorithms
- Weather data integration
- Route optimization logic
- FastAPI RESTful API
- Command line interface with Click

## Installation
To install the required dependencies, run:
```
pip install -r requirements.txt
```

## Usage
### Running the API
To start the FastAPI application:
```
uvicorn api.main:app --reload
```

### CLI Commands
To use the CLI commands:
```
python cli/main.py <command>
```

## Configuration
Environment variables should be set according to the .env.example file.