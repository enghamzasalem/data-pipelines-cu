"""
Lecture 11 — Airflow + Ollama: Open-Meteo weather JSON → structured JSON via LLM.

Open-Meteo: https://open-meteo.com/ (no API key)
Ollama API: POST /api/chat with format json when supported by your Ollama version.
"""

from __future__ import annotations

import json
import os
from datetime import timedelta

import pendulum
from airflow.decorators import dag, task
from airflow.models import Variable


default_args = {
    "owner": "lecture11",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}


@dag(
    dag_id="weather_unstructured_to_structured",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule=None,
    catchup=False,
    tags=["lecture11", "ollama", "weather", "open-meteo"],
    default_args=default_args,
    doc_md=__doc__,
)
def weather_ollama_pipeline():
    @task
    def fetch_open_meteo_raw() -> str:
        """Download raw forecast JSON (string) — semi-structured source for the LLM."""
        import requests

        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": 48.8566,
            "longitude": 2.3522,
            "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
            "timezone": "Europe/Paris",
        }
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        return resp.text

    @task
    def ollama_to_structured(raw_json_text: str) -> str:
        """
        Ask Ollama to emit ONE JSON object with a fixed schema.
        Set WEATHER_PIPELINES_MOCK_OLLAMA=1 to skip the HTTP call (tests / no GPU).
        """
        raw_weather = json.loads(raw_json_text)

        def build_contract(model_obj=None) -> dict:
            model_obj = model_obj or {}
            current = raw_weather.get("current", {})
            daily = raw_weather.get("daily", {})
            daily_dates = daily.get("time") or []
            max_values = daily.get("temperature_2m_max") or []
            min_values = daily.get("temperature_2m_min") or []
            precipitation_values = daily.get("precipitation_sum") or []

            conditions = model_obj.get("conditions_short") or model_obj.get("condition_short")
            if not conditions:
                weather_code = current.get("weather_code")
                wind_speed = current.get("wind_speed_10m")
                humidity = current.get("relative_humidity_2m")
                conditions = (
                    f"Weather code {weather_code}, wind {wind_speed} km/h, "
                    f"humidity {humidity}%."
                )

            return {
                "city_label": "Paris",
                "observation_date": daily_dates[0]
                if daily_dates
                else model_obj.get("observation_date", pendulum.now("UTC").to_date_string()),
                "temp_c_current": current.get("temperature_2m"),
                "temp_c_max": max_values[0] if max_values else None,
                "temp_c_min": min_values[0] if min_values else None,
                "conditions_short": str(conditions)[:160],
                "precipitation_mm": precipitation_values[0] if precipitation_values else None,
            }

        if os.environ.get("WEATHER_PIPELINES_MOCK_OLLAMA") == "1":
            return json.dumps(
                build_contract(
                    {
                        "city_label": "Paris (mock)",
                        "conditions_short": "Mock: enable Ollama for real output.",
                    }
                )
            )

        import requests

        base = Variable.get("ollama_base_url", default_var="http://127.0.0.1:11434").rstrip("/")
        model = Variable.get("ollama_model", default_var="tinyllama")

        prompt = f"""Convert the following weather API JSON into ONE JSON object with exactly these keys:
"city_label" (string, human-readable place name for the coordinates),
"observation_date" (string, ISO date for the first daily forecast day if present, else today UTC),
"temp_c_current" (number or null),
"temp_c_max" (number or null),
"temp_c_min" (number or null),
"conditions_short" (string, max 160 characters, plain English summary),
"precipitation_mm" (number or null, daily sum for that first day if present).

Rules:
- Temperatures are Celsius.
- Use null if a value is missing.
- Output must be valid JSON only, no markdown.

RAW INPUT:
{raw_json_text}
"""

        body = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "format": "json",
        }
        resp = requests.post(f"{base}/api/chat", json=body, timeout=180)
        resp.raise_for_status()
        payload = resp.json()
        content = payload.get("message", {}).get("content")
        if not content:
            raise RuntimeError(f"Unexpected Ollama response: {payload!r}")
        if isinstance(content, dict):
            model_obj = content
        else:
            model_obj = json.loads(content)
        return json.dumps(build_contract(model_obj), sort_keys=True)

    @task
    def validate_and_emit(structured_json: str) -> dict:
        """Parse and ensure required keys exist (structured contract)."""
        obj = json.loads(structured_json)
        required = {
            "city_label",
            "observation_date",
            "temp_c_current",
            "temp_c_max",
            "temp_c_min",
            "conditions_short",
            "precipitation_mm",
        }
        missing = required - obj.keys()
        if missing:
            raise ValueError(f"Structured output missing keys: {sorted(missing)}")
        return obj

    raw = fetch_open_meteo_raw()
    structured = ollama_to_structured(raw)
    validate_and_emit(structured)


dag = weather_ollama_pipeline()
