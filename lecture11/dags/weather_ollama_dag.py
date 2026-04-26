"""
Lecture 11 — Airflow + Ollama: Open-Meteo weather JSON → structured JSON via LLM.
"""

from __future__ import annotations

import json
import re
from datetime import timedelta

import pendulum
import requests
from airflow.decorators import dag, task


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
    tags=["lecture11", "ollama", "weather"],
    default_args=default_args,
)
def weather_ollama_pipeline():

    @task
    def fetch_open_meteo_raw() -> str:
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
        base = "http://127.0.0.1:11434"
        model = "llama3"

        prompt = f"""
Return ONLY valid JSON.

{{
  "city_label": null,
  "observation_date": "",
  "temp_c_current": 0,
  "temp_c_max": 0,
  "temp_c_min": 0,
  "conditions_short": null,
  "precipitation_mm": 0
}}

Input:
{raw_json_text}
"""

        body = {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }

        resp = requests.post(f"{base}/api/generate", json=body, timeout=180)
        resp.raise_for_status()

        payload = resp.json()
        content = payload.get("response")

        if not content:
            raise RuntimeError(f"Unexpected Ollama response: {payload}")

        match = re.search(r"\{[\s\S]*\}", content)

        if not match:
            raise ValueError(f"No JSON found in Ollama output: {content}")

        cleaned = match.group(0).strip()
        json.loads(cleaned)

        return cleaned

    @task
    def validate_and_emit(structured_json: str) -> dict:
        obj = json.loads(structured_json)

        required = [
            "city_label",
            "observation_date",
            "temp_c_current",
            "temp_c_max",
            "temp_c_min",
            "conditions_short",
            "precipitation_mm",
        ]

        for key in required:
            obj.setdefault(key, None)

        return obj

    raw = fetch_open_meteo_raw()
    structured = ollama_to_structured(raw)
    validate_and_emit(structured)


dag = weather_ollama_pipeline()
