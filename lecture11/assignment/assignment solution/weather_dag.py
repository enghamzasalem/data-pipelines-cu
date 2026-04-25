from airflow import DAG
from airflow.decorators import task
from datetime import datetime, timedelta
import requests
import json
import time
from pydantic import BaseModel, ValidationError



DAG_ID = "weather_pipeline"

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "tinyllama"   # safe local model
MAX_RETRIES = 3


default_args = {
    "owner": "mariem",
    "retries": 1,
    "retry_delay": timedelta(seconds=30),
}



class WeatherSchema(BaseModel):
    lat: float
    lon: float
    temp_celsius: float
    wind_kmh: float
    weather_code: int
    summary: str
    is_windy: bool



with DAG(
    dag_id=DAG_ID,
    default_args=default_args,
    start_date=datetime(2026, 4, 20),
    schedule=None,
    catchup=False,
    tags=["weather", "ai"],
    is_paused_upon_creation=False,
) as dag:


    @task
    def fetch_weather():
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": 53.08,
            "longitude": 8.80,
            "current_weather": True
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()


  
    def build_prompt(raw_json):
        return f"""
You are responsible for extracting useful weather information and returning a structured result.

Produce a JSON object with the following fields:

{{
  "lat": float,
  "lon": float,
  "temp_celsius": float,
  "wind_kmh": float,
  "weather_code": int,
  "summary": string,
  "is_windy": boolean
}}

Guidelines:
- Return ONLY a JSON object (no extra text)
- All fields must be included
- Use numeric types for numbers
- "summary" should be a short natural description of the weather
- "is_windy" should be true if wind speed > 10 km/h, otherwise false
- Round temperature to 1 decimal place

Input:
{json.dumps(raw_json)}
"""


    def call_ollama(prompt):
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            },
            timeout=60,
        )

        response.raise_for_status()
        return response.json()["response"]



    def validate_output(output_text):
        try:
            data = json.loads(output_text)
            validated = WeatherSchema(**data)
            return validated.dict()
        except (json.JSONDecodeError, ValidationError) as e:
            print("Validation error:", e)
            return None


 
    @task
    def transform_weather(raw_json):
        prompt = build_prompt(raw_json)

        for attempt in range(1, MAX_RETRIES + 1):
            print(f"Attempt {attempt}...")

            output = call_ollama(prompt)
            validated = validate_output(output)

            if validated:
                return validated

            print("Retrying...\n")
            time.sleep(2)

        raise ValueError("Failed to get valid JSON from model")


  
    @task
    def save_result(data):
        file_path = "/tmp/weather_structured.json"

        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)

        print("Saved result to:", file_path)
        print(data)


   
    raw = fetch_weather()
    structured = transform_weather(raw)
    save_result(structured)