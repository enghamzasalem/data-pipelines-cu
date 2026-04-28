from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import requests
import json
import os
import time
from airflow import settings
from pydantic import BaseModel, ValidationError

# =========================
# CONFIG
# =========================

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:3b"

MAX_RETRIES = 3
REQUEST_TIMEOUT = 7200


OUTPUT_DIR = os.path.join(settings.AIRFLOW_HOME, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# =========================
# SCHEMA
# =========================


class WeatherSchema(BaseModel):
    latitude: float
    longitude: float
    temperature_c: float
    windspeed_kmh: float
    weather_code: int
    conditions_short: str


# =========================
# TASKS
# =========================


def fetch_weather():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {"latitude": 53.08, "longitude": 8.80, "current_weather": True}

    r = requests.get(url, params=params)
    r.raise_for_status()
    return r.json()


def build_prompt(raw_json):
    return f"""
You are a strict JSON generator.

Return ONLY valid JSON with this schema:

{{
  "latitude": number,
  "longitude": number,
  "temperature_c": number,
  "windspeed_kmh": number,
  "weather_code": number,
  "conditions_short": string
}}

RULES:
- output ONLY JSON
- NO markdown
- NO text
- NO explanation
- ALL fields required
- conditions_short must be short weather phrase

INPUT:
{json.dumps(raw_json)}
"""


def call_ollama(prompt):
    payload = {"model": MODEL_NAME, "prompt": prompt, "stream": False}

    r = requests.post(OLLAMA_URL, json=payload, timeout=REQUEST_TIMEOUT)

    r.raise_for_status()

    data = r.json()

    # 🔥 FIX: Ollama always returns "response" for /generate
    if "response" not in data:
        raise Exception(f"Invalid Ollama response: {data}")

    return data["response"]


def validate_and_parse(text):
    try:
        data = json.loads(text)
        return WeatherSchema(**data).model_dump()
    except (json.JSONDecodeError, ValidationError) as e:
        print("Validation error:", e)
        return None


def transform_weather():
    raw = fetch_weather()
    prompt = build_prompt(raw)

    for i in range(MAX_RETRIES):
        print(f"Attempt {i+1}")

        try:
            output = call_ollama(prompt)
            validated = validate_and_parse(output)

            if validated:
                return validated

        except Exception as e:
            print(f"Retry error: {e}")

        time.sleep(5)

    raise Exception("Failed to produce valid structured JSON")


def save_output(**context):
    data = context["ti"].xcom_pull(task_ids="transform_weather")

    file_path = os.path.join(
        OUTPUT_DIR, f"weather_{datetime.utcnow().isoformat()}.json"
    )

    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Saved to {file_path}")
    return file_path


# =========================
# DAG DEFINITION
# =========================

with DAG(
    dag_id="weather_unstructured_to_structured",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=["weather", "ollama"],
) as dag:
    task_transform = PythonOperator(
        task_id="transform_weather", python_callable=transform_weather
    )

    task_save = PythonOperator(
        task_id="save_output", python_callable=save_output, provide_context=True
    )

    task_transform >> task_save
