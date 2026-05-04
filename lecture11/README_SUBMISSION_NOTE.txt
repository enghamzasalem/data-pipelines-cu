Lecture 11 submission - Airflow + Ollama weather pipeline

Student: WEZDAR AHMED
Email: awezdar@constructor.university

What changed:
- completed the Lecture 11 Open-Meteo -> Ollama -> validated JSON DAG
- kept the DAG ID as weather_unstructured_to_structured
- configured the DAG to call local Ollama at http://127.0.0.1:11434
- used the tinyllama model pulled locally
- added schema normalization so the small model still produces the exact required fields
- added proof files for the successful Airflow DAG test and structured JSON output

Run proof:
- DAG: weather_unstructured_to_structured
- Run ID: manual__2026-05-04T15:50:00+00:00
- State: success
- Tasks:
  - fetch_open_meteo_raw: success
  - ollama_to_structured: success
  - validate_and_emit: success

Structured output:
{
  "city_label": "Paris",
  "conditions_short": "Weather code 61, wind 3.8 km/h, humidity 73%.",
  "observation_date": "2026-05-04",
  "precipitation_mm": 4.9,
  "temp_c_current": 17.0,
  "temp_c_max": 17.8,
  "temp_c_min": 14.5
}

Notes:
- Ollama was run locally with tinyllama:latest.
- The first live API attempt briefly returned a 502 from Open-Meteo, then the retry/test run succeeded.
- No mock mode was used for the final proof run.
