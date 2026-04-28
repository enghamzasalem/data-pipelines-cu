# Weather Transformer DAG (Airflow + Ollama)

## Overview
This Airflow DAG fetches real-time weather data, transforms it using an LLM (Ollama), validates the output with Pydantic, and saves the structured JSON file.

## Workflow
1. Fetch weather data from Open-Meteo API
2. Send data to Ollama model
3. Transform into strict JSON schema
4. Validate output using Pydantic
5. Retry if output is invalid
6. Save final JSON file locally

## Tech Stack
- Apache Airflow
- Python
- Requests
- Pydantic
- Ollama

## DAG Structure
- transform_weather → calls API + LLM + validation
- save_output → stores final JSON file

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

Start Airflow:
airflow scheduler
airflow webserver
airflow dag-processor

Start Ollama:
ollama serve

Trigger DAG:
airflow dags trigger weather_unstructured_to_structured

## Output
- Structured JSON saved in:
  ~/airflow/outputs/

## Notes
- Uses retry mechanism (max 3 attempts)
- Requires Ollama running locally
- Uses /api/generate endpoint