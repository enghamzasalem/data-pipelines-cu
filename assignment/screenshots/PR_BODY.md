## 📌 Lecture 11: Airflow + Ollama Weather Pipeline

### 👤 Author

Subhankar Biswas

---

## 🚀 Overview

This project implements an **end-to-end Airflow pipeline** that:

1. Fetches live weather data from the Open-Meteo API
2. Uses Ollama (LLM) to convert raw/unstructured JSON → structured schema
3. Validates the output strictly
4. Stores results in:

   * JSON file (history)
   * SQLite database

---

## ⚙️ Pipeline Architecture

```
Open-Meteo API → Airflow DAG → Ollama → Validation → Storage
```

### DAG Tasks:

* `fetch` → Retrieves raw weather JSON
* `ollama_to_structured` → Converts to structured format via LLM
* `validate_and_emit` → Validates + saves output

---

## 🧠 Key Features

### ✅ LLM-Powered Structuring

* Uses Ollama `/api/chat`
* Enforces strict JSON output with `"format": "json"`

---

### ✅ Strict Schema Validation

Required fields:

```json
{
  "temperature_c": float,
  "windspeed_kmh": float,
  "weather_code": int,
  "conditions_short": string
}
```

* Pipeline fails if any field is missing
* Type validation enforced

---

### ✅ Robust Storage

* JSON file (append history)
* SQLite database with schema:

  * temperature
  * windspeed
  * weather code
  * condition
  * timestamp

---

### ✅ Fault Tolerance

* Retries on API + Ollama failures
* Mock mode support:

```bash
export WEATHER_PIPELINES_MOCK_OLLAMA=1
```

---

## 🛠️ Setup Instructions

### 1. Start Ollama

```bash
ollama serve
ollama pull qwen2.5-coder:7b
```

---

### 2. Setup Airflow

```bash
export AIRFLOW_HOME=~/airflow

python3 -m venv .venv-airflow
source .venv-airflow/bin/activate

pip install "apache-airflow>=2.7,<3" requests

airflow db init
airflow standalone
```

---

### 3. Copy DAG

```bash
cp weather_ollama_dag.py $AIRFLOW_HOME/dags/
```

---

### 4. Run DAG

* Open Airflow UI
* Enable DAG
* Trigger run

---

## 📸 Results

### ✅ Successful DAG Run

* All tasks: **GREEN**

### ✅ Example Output

```json
{
  "temperature_c": 11.9,
  "windspeed_kmh": 13.1,
  "weather_code": 0,
  "conditions_short": "Clear",
  "recorded_at": "2026-04-21T12:55:13"
}
```

---

## 🧪 Issues Faced & Fixes

### ❌ DAG not updating

* Cause: `AIRFLOW_HOME` not set
* Fix: explicitly set `export AIRFLOW_HOME=~/airflow`

---

### ❌ FileNotFoundError

* Cause: non-existent output directory
* Fix: used `os.makedirs()` for safe directory creation

---

### ❌ Deprecated Airflow decorators

* Fix: migrated to `airflow.sdk`

---

## 🎯 Learning Outcomes

* Built real-world Airflow DAG
* Integrated LLM (Ollama) into pipelines
* Enforced schema validation
* Debugged Airflow environment issues
* Implemented persistent storage

---

## ✅ Submission Checklist

* [x] DAG runs successfully
* [x] Structured JSON output generated
* [x] Validation enforced
* [x] JSON + SQLite storage working
* [x] Screenshots included

---

## 📌 PR Title

```
Lecture 11: Airflow + Ollama weather pipeline - Subhankar Biswas
```
