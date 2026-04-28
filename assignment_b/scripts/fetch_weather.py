from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen


# ✅ Correct path for your project structure
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PATH = BASE_DIR / "assignment_b_submission/lecture11b-open-meteo-raw.json"

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def fetch_weather() -> dict:
    params = {
        "latitude": 48.8566,   # Paris
        "longitude": 2.3522,
        "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "Europe/Paris",
    }

    url = f"{OPEN_METEO_URL}?{urlencode(params)}"

    try:
        with urlopen(url, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        raise RuntimeError(f"❌ Failed to fetch weather data: {e}") from e


def main() -> None:
    payload = fetch_weather()

    # ✅ Ensure directory exists
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # ✅ Save JSON
    OUTPUT_PATH.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8"
    )

    print(f"✅ Wrote raw Open-Meteo JSON to {OUTPUT_PATH}")
    print(f"🌍 Location: Paris (48.8566, 2.3522)")
    print(f"🕒 Current observation time: {payload.get('current', {}).get('time')}")


if __name__ == "__main__":
    main()