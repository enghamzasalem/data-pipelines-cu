# Weather Transformer (Python + Ollama)

## Overview
This script fetches real-time weather data from Open-Meteo API and uses Ollama (LLM) to convert it into a structured JSON format validated with Pydantic.

## What it does
- Fetch weather data from API
- Send raw JSON to Ollama model
- Transform it into strict schema
- Validate output with Pydantic
- Retry if output is invalid
- Save final result as JSON file

## Tech Stack
- Python
- Requests
- Pydantic
- Ollama

## Schema Output
{
  "latitude": float,
  "longitude": float,
  "temperature_c": float,
  "windspeed_kmh": float,
  "weather_code": int,
  "conditions_short": string
}

## Run Instructions

Install dependencies:
pip install requests pydantic

Start Ollama:
ollama serve

Run script:
python unstructered_to_structered_JSON.py

## Output
Generates:
weather_structured.json

## Notes
- Uses retry mechanism (max 3 attempts)
- Ensures valid JSON output using Pydantic validation