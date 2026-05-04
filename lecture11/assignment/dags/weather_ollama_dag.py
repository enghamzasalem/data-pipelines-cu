"""
Lecture 11 — Airflow + Ollama: Open-Meteo weather JSON → structured JSON via LLM.

Open-Meteo: https://open-meteo.com/  (no API key required)
Ollama API:  POST /api/chat with format="json"

Pipeline:
    fetch_open_meteo_raw  →  ollama_to_structured  →  validate_and_emit

Mock mode (no Ollama / no network):
    export WEATHER_PIPELINES_MOCK_OLLAMA=1
    The ollama_to_structured task returns canned JSON without any HTTP call.

Airflow Variables (Admin → Variables in the UI):
    ollama_base_url  – default: http://127.0.0.1:11434
    ollama_model     – default: tinyllama
"""

from __future__ import annotations

import json
import logging
import os
from datetime import timedelta

import pendulum
from airflow.decorators import dag, task
from airflow.models import Variable

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Schema we want the LLM to produce
# ---------------------------------------------------------------------------
REQUIRED_KEYS = {
    "city_label",
    "observation_date",
    "temp_c_current",
    "temp_c_max",
    "temp_c_min",
    "conditions_short",
    "precipitation_mm",
}

default_args = {
    "owner": "lecture11",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}


@dag(
    dag_id="weather_unstructured_to_structured",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule=None,          # manual trigger only
    catchup=False,
    tags=["lecture11", "ollama", "weather", "open-meteo"],
    default_args=default_args,
    doc_md=__doc__,
)
def weather_ollama_pipeline():

    # ------------------------------------------------------------------
    # Task 1 – Fetch raw JSON from Open-Meteo
    # ------------------------------------------------------------------
    @task
    def fetch_open_meteo_raw() -> str:
        """
        Download the current forecast for Paris (48.8566 N, 2.3522 E)
        and return the raw JSON string.

        Change latitude/longitude here to fetch weather for any city.
        Example – Bremen, Germany: latitude=53.0793, longitude=8.8017

        When WEATHER_PIPELINES_MOCK_OLLAMA=1 the HTTP call is skipped and a
        realistic sample payload is returned instead (useful in sandboxed CI).
        """
        import requests

        # --- Mock path ---------------------------------------------------
        if os.environ.get("WEATHER_PIPELINES_MOCK_OLLAMA") == "1":
            log.warning("WEATHER_PIPELINES_MOCK_OLLAMA=1 – returning mock Open-Meteo payload.")
            return json.dumps({
                "latitude": 48.8566, "longitude": 2.3522,
                "timezone": "Europe/Paris", "elevation": 35.0,
                "current_units": {"temperature_2m": "°C", "relative_humidity_2m": "%",
                                  "weather_code": "wmo code", "wind_speed_10m": "km/h"},
                "current": {"time": "2024-01-15T12:00", "temperature_2m": 12.3,
                            "relative_humidity_2m": 78, "weather_code": 3, "wind_speed_10m": 14.2},
                "daily_units": {"temperature_2m_max": "°C", "temperature_2m_min": "°C",
                                "precipitation_sum": "mm"},
                "daily": {"time": ["2024-01-15"], "temperature_2m_max": [14.1],
                          "temperature_2m_min": [7.8], "precipitation_sum": [0.1]},
            })

        # --- Real path ---------------------------------------------------
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": 48.8566,
            "longitude": 2.3522,
            "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
            "timezone": "Europe/Paris",
            "forecast_days": 1,   # we only need today
        }
        log.info("Fetching Open-Meteo forecast for lat=%s lon=%s", params["latitude"], params["longitude"])
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        log.info("Open-Meteo responded with %d bytes", len(resp.text))
        return resp.text

    # ------------------------------------------------------------------
    # Task 2 – Ask Ollama to produce structured JSON
    # ------------------------------------------------------------------
    @task
    def ollama_to_structured(raw_json_text: str) -> str:
        """
        Send the raw weather JSON to Ollama and request a single JSON object
        matching our fixed schema.

        Set WEATHER_PIPELINES_MOCK_OLLAMA=1 to skip the real HTTP call.
        """
        # ---- Mock path (CI / no GPU / no network) ----------------------
        if os.environ.get("WEATHER_PIPELINES_MOCK_OLLAMA") == "1":
            log.warning("WEATHER_PIPELINES_MOCK_OLLAMA=1 – returning canned response.")
            mock = {
                "city_label": "Paris, France (mock)",
                "observation_date": "2024-01-15",
                "temp_c_current": 12.0,
                "temp_c_max": 14.0,
                "temp_c_min": 8.0,
                "conditions_short": "Mild and partly cloudy. Mock mode — enable Ollama for real output.",
                "precipitation_mm": 0.1,
            }
            return json.dumps(mock)

        # ---- Real path: call Ollama ------------------------------------
        import requests

        base = Variable.get("ollama_base_url", default_var="http://127.0.0.1:11434").rstrip("/")
        model = Variable.get("ollama_model", default_var="tinyllama")
        log.info("Calling Ollama model=%s at %s", model, base)

        prompt = (
            "Convert the following weather API JSON into ONE JSON object "
            "with EXACTLY these keys:\n"
            '  "city_label"        – string, human-readable place name for the coordinates\n'
            '  "observation_date"  – string, ISO date (YYYY-MM-DD) for the first daily forecast day\n'
            '  "temp_c_current"    – number or null, current temperature in Celsius\n'
            '  "temp_c_max"        – number or null, daily maximum in Celsius\n'
            '  "temp_c_min"        – number or null, daily minimum in Celsius\n'
            '  "conditions_short"  – string ≤160 chars, plain-English weather summary\n'
            '  "precipitation_mm"  – number or null, precipitation sum in mm for that day\n\n'
            "Rules:\n"
            "- Temperatures are always Celsius.\n"
            "- Use JSON null (not the string 'null') if a value is absent.\n"
            "- Output ONLY valid JSON — no markdown, no code fences, no extra keys.\n\n"
            f"RAW INPUT:\n{raw_json_text}"
        )

        body = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "format": "json",           # structured-output mode in Ollama ≥0.1.9
            "options": {"temperature": 0},  # deterministic output
        }

        resp = requests.post(f"{base}/api/chat", json=body, timeout=180)
        resp.raise_for_status()
        payload = resp.json()

        content = payload.get("message", {}).get("content")
        if not content:
            raise RuntimeError(f"Unexpected Ollama response shape: {payload!r}")

        # Ollama may return content as a dict already (some versions)
        if isinstance(content, dict):
            log.info("Ollama returned content as dict – serialising.")
            return json.dumps(content)

        # Validate it parses before passing downstream
        try:
            json.loads(content)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Ollama output is not valid JSON: {content!r}") from exc

        log.info("Ollama raw output: %s", content)
        return content

    # ------------------------------------------------------------------
    # Task 3 – Validate schema and surface the result via XCom
    # ------------------------------------------------------------------
    @task
    def validate_and_emit(structured_json: str) -> dict:
        """
        Parse the JSON string, assert all required keys are present, log the
        final object, and return it so it appears in XCom for inspection.
        """
        obj = json.loads(structured_json)

        missing = REQUIRED_KEYS - obj.keys()
        if missing:
            raise ValueError(
                f"Structured output is missing required keys: {sorted(missing)}\n"
                f"Got keys: {sorted(obj.keys())}"
            )

        # Extra keys are fine – log a warning but don't fail
        extra = set(obj.keys()) - REQUIRED_KEYS
        if extra:
            log.warning("Structured output contains unexpected extra keys: %s", sorted(extra))

        log.info("✅ Structured weather JSON:\n%s", json.dumps(obj, indent=2, ensure_ascii=False))
        return obj

    # ------------------------------------------------------------------
    # Wire up the pipeline
    # ------------------------------------------------------------------
    raw = fetch_open_meteo_raw()
    structured = ollama_to_structured(raw)
    validate_and_emit(structured)


dag = weather_ollama_pipeline()