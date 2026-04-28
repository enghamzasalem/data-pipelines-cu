import json
import os
import sqlite3
from datetime import datetime, timedelta

import requests
from airflow.sdk import dag, task
from airflow.exceptions import AirflowFailException


# -----------------------------
# Config
# -----------------------------
OLLAMA_BASE_URL = "http://127.0.0.1:11434"
OLLAMA_MODEL = "qwen2.5-coder:7b"

MOCK_OLLAMA = os.environ.get("WEATHER_PIPELINES_MOCK_OLLAMA", "0") == "1"

REQUIRED_FIELDS = [
    "temperature_c",
    "windspeed_kmh",
    "weather_code",
    "conditions_short",
]

# ✅ FIX: safer portable path
BASE_DIR = os.path.expanduser("~/airflow/lecture11")
os.makedirs(BASE_DIR, exist_ok=True)

OUTPUT_JSON = os.path.join(BASE_DIR, "output.json")
OUTPUT_DB = os.path.join(BASE_DIR, "weather.db")


# -----------------------------
# DAG
# -----------------------------
@dag(
    dag_id="weather_unstructured_to_structured",
    schedule="@hourly",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["weather", "ollama", "lecture11"],
)
def weather_unstructured_to_structured():

    # -----------------------------
    # Task 1: Fetch
    # -----------------------------
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

        print(f"Fetched {len(response.text)} bytes")
        return response.text


    # -----------------------------
    # Task 2: Ollama
    # -----------------------------
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

        prompt = f"""
You are a strict JSON generator.

Return ONLY this JSON structure:
{{
  "temperature_c": float,
  "windspeed_kmh": float,
  "weather_code": int,
  "conditions_short": string
}}

Rules:
- Output ONLY JSON
- No extra keys
- No explanation

Input:
{raw_payload}
"""

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

        try:
            content = response.json()["message"]["content"]
            structured = json.loads(content)
        except Exception as e:
            raise AirflowFailException(f"Ollama parsing failed: {e}")

        print("Ollama output:")
        print(json.dumps(structured, indent=2))

        return structured


    # -----------------------------
    # Task 3: Validate + Save
    # -----------------------------
    @task
    def validate_and_emit(structured: dict) -> dict:

        # ✅ STRICT validation
        missing = [f for f in REQUIRED_FIELDS if f not in structured]
        if missing:
            raise AirflowFailException(f"Missing fields: {missing}")

        if not isinstance(structured["temperature_c"], (int, float)):
            raise AirflowFailException("temperature_c must be numeric")

        if not isinstance(structured["windspeed_kmh"], (int, float)):
            raise AirflowFailException("windspeed_kmh must be numeric")

        if not isinstance(structured["weather_code"], int):
            raise AirflowFailException("weather_code must be integer")

        if not isinstance(structured["conditions_short"], str):
            raise AirflowFailException("conditions_short must be string")

        print("✅ Validation passed!")
        print(json.dumps(structured, indent=2))

        # Add timestamp
        structured["recorded_at"] = datetime.utcnow().isoformat()

        # -----------------------------
        # Save to JSON (safe)
        # -----------------------------
        history = []
        if os.path.exists(OUTPUT_JSON):
            try:
                with open(OUTPUT_JSON, "r") as f:
                    history = json.load(f)
            except Exception:
                history = []

        history.append(structured)

        with open(OUTPUT_JSON, "w") as f:
            json.dump(history, f, indent=2)

        print(f"✅ Saved JSON → {OUTPUT_JSON}")

        # -----------------------------
        # Save to SQLite
        # -----------------------------
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
            INSERT INTO weather 
            (temperature_c, windspeed_kmh, weather_code, conditions_short, recorded_at)
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

        print(f"✅ Saved SQLite → {OUTPUT_DB}")

        return structured


    # -----------------------------
    # Pipeline
    # -----------------------------
    raw = fetch()
    structured = ollama_to_structured(raw)
    validate_and_emit(structured)


# Instantiate DAG
weather_unstructured_to_structured()