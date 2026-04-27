## 📌 Lecture 11 – Airflow Weather Pipeline

### 🔹 What I did

* Set up Airflow and registered the provided DAG
* Ran the pipeline (`weather_unstructured_to_structured`)
* Verified execution through Airflow UI (Graph & Logs)
* Extracted structured JSON output from `validate_and_emit`

---

### 🔹 Issue encountered

While using `tinyllama`, the pipeline failed during validation:

```
ValueError: Structured output missing keys: ['conditions_short']
```

The LLM output did not consistently follow the required JSON schema.

---

### 🔹 Solution

To ensure stable execution, I enabled mock mode:

```bash
export WEATHER_PIPELINES_MOCK_OLLAMA=1
```

This bypasses the LLM and returns a valid structured JSON.

---

### 🔹 Result

The pipeline executed successfully and returned the following structured output:

```json
{
  "city_label": "Paris (mock)",
  "observation_date": "2024-01-15",
  "temp_c_current": 12.0,
  "temp_c_max": 14.0,
  "temp_c_min": 8.0,
  "conditions_short": "Mock: enable Ollama for real output.",
  "precipitation_mm": 0.1
}
```

---

### 🔹 Notes

* The DAG was successfully triggered and all tasks completed
* Mock mode was used due to instability in LLM-generated outputs

---

