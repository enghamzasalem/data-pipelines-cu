import json
import os
import sqlite3
from datetime import datetime, timedelta

import requests
from airflow.decorators import dag, task

OLLAMA_BASE_URL = "http://127.0.0.1:11434"
OLLAMA_MODEL    = "qwen2.5-coder:7b"
MOCK_OLLAMA     = os.environ.get("WEATHER_PIPELINES_MOCK_OLLAMA", "0") == "1"
REQUIRED_FIELDS = ["temperature_c", "windspeed_kmh", "weather_code", "conditions_short"]
OUTPUT_JSON     = "/home/mimou/airflow/lecture11/output.json"
OUTPUT_DB       = "/home/mimou/airflow/lecture11/weather.db"

@dag(
    dag_id="weather_unstructured_to_structured",
    schedule="@hourly",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["weather", "ollama", "lecture11"],
)
def weather_unstructured_to_structured():

    @task(retries=3, retry_delay=timedelta(seconds=15))
    def fetch() -> str:
        url = (
            "https://api.open-meteo.com/v1/forecast"
            "?latitude=53.07&longitude=8.80"
            "&current_weather=true"
            "&hourly=temperature_2m,windspeed_10m,weathercode"
            "&forecast_days=1"
        )
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        print(f"Fetched {len(response.text)} bytes from Open-Meteo")
        return response.text

    @task(retries=2, retry_delay=timedelta(seconds=30))
    def ollama_to_structured(raw_payload: str) -> dict:
        if MOCK_OLLAMA:
            print("MOCK MODE — skipping Ollama")
            return {
                "temperature_c": 12.3,
                "windspeed_kmh": 18.5,
                "weather_code": 61,
                "conditions_short": "Light rain",
            }

        prompt = (
            "You are a data transformer. You receive a raw weather API JSON string.\n"
            "Return ONLY a raw JSON object with exactly these keys, nothing else:\n"
            "{\n"
            '  "temperature_c": <number, 1 decimal>,\n'
            '  "windspeed_kmh": <number, 1 decimal>,\n'
            '  "weather_code": <integer>,\n'
            '  "conditions_short": "<short human-readable string from WMO code>"\n'
            "}\n"
            "No markdown, no explanation, just JSON.\n\n"
            f"Raw weather payload:\n{raw_payload}"
        )

        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "format": "json",
                "stream": False,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=120,
        )
        response.raise_for_status()
        content = response.json()["message"]["content"]
        structured = json.loads(content)
        print(f"Ollama output:\n{json.dumps(structured, indent=2)}")
        return structured

    @task
    def validate_and_emit(structured: dict) -> dict:
        # Validate required fields
        missing = [f for f in REQUIRED_FIELDS if f not in structured]
        if missing:
            raise ValueError(f"Pipeline failed — missing fields: {missing}")
        if not isinstance(structured["temperature_c"], (int, float)):
            raise TypeError("temperature_c must be a number")
        if not isinstance(structured["windspeed_kmh"], (int, float)):
            raise TypeError("windspeed_kmh must be a number")
        if not isinstance(structured["weather_code"], int):
            raise TypeError("weather_code must be an integer")
        if not isinstance(structured["conditions_short"], str):
            raise TypeError("conditions_short must be a string")

        print("✅ Validation passed!")
        print(json.dumps(structured, indent=2))

        # Add timestamp
        structured["recorded_at"] = datetime.utcnow().isoformat()

        # --- Save to JSON file ---
        history = []
        if os.path.exists(OUTPUT_JSON):
            with open(OUTPUT_JSON, "r") as f:
                history = json.load(f)
        history.append(structured)
        with open(OUTPUT_JSON, "w") as f:
            json.dump(history, f, indent=2)
        print(f"✅ Saved to JSON: {OUTPUT_JSON}")

        # --- Save to SQLite ---
        conn = sqlite3.connect(OUTPUT_DB)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weather (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                temperature_c REAL,
                windspeed_kmh REAL,
                weather_code INTEGER,
                conditions_short TEXT,
                recorded_at TEXT
            )
        """)
        cursor.execute("""
            INSERT INTO weather (temperature_c, windspeed_kmh, weather_code, conditions_short, recorded_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            structured["temperature_c"],
            structured["windspeed_kmh"],
            structured["weather_code"],
            structured["conditions_short"],
            structured["recorded_at"],
        ))
        conn.commit()
        conn.close()
        print(f"✅ Saved to SQLite: {OUTPUT_DB}")

        return structured

    raw        = fetch()
    structured = ollama_to_structured(raw)
    validate_and_emit(structured)

weather_unstructured_to_structured()