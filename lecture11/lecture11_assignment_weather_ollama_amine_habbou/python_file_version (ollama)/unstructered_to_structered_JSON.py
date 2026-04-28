import requests
import json
import time
from pydantic import BaseModel, ValidationError

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gpt-oss:120b-cloud"
MAX_RETRIES = 3


class WeatherSchema(BaseModel):
    latitude: float
    longitude: float
    temperature_c: float
    windspeed_kmh: float
    weather_code: int
    conditions_short: str


def fetch_weather():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {"latitude": 53.08, "longitude": 8.80, "current_weather": True}

    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def build_prompt(raw_json):
    return f"""
You are a strict JSON transformation engine.

Convert the input weather JSON into EXACTLY this schema:

{{
  "latitude": float,
  "longitude": float,
  "temperature_c": float,
  "windspeed_kmh": float,
  "weather_code": int,
  "conditions_short": string
}}

Rules:
- Output ONLY valid JSON
- NO explanations, NO markdown
- All fields are REQUIRED
- Keep numbers as numbers (no strings)
- "conditions_short" = short human-readable phrase (e.g. "clear sky", "light rain")
- Use weather_code meaning when possible (WMO standard)

Input:
{json.dumps(raw_json)}
"""


def call_ollama(prompt):
    response = requests.post(
        OLLAMA_URL,
        json={"model": MODEL_NAME, "prompt": prompt, "stream": False},
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


def transform_with_retry(raw_json):
    prompt = build_prompt(raw_json)

    for attempt in range(1, MAX_RETRIES + 1):
        print(f"Attempt {attempt}...")

        output = call_ollama(prompt)
        validated = validate_output(output)

        if validated:
            return validated

        print("Retrying...\n")
        time.sleep(2)

    raise Exception("Failed after multiple attempts (invalid JSON)")


def main():
    print("Fetching weather data...")
    raw_data = fetch_weather()

    print("Transforming with Ollama...")
    structured = transform_with_retry(raw_data)

    print("Final structured JSON:")
    print(json.dumps(structured, indent=2))

    with open("weather_structured.json", "w") as f:
        json.dump(structured, f, indent=2)

    print("Saved to weather_structured.json")


if __name__ == "__main__":
    main()
