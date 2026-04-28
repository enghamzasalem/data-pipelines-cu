# 🌦️ Airflow + Ollama Weather Pipeline

An end-to-end data pipeline that transforms **raw weather API data into structured JSON** using **LLMs (Ollama)** and orchestrates it via **Apache Airflow**.

---

## 🚀 Features

* 🔄 Airflow DAG orchestration
* 🌐 Live API integration (Open-Meteo)
* 🤖 LLM-based structuring (Ollama)
* ✅ Strict schema validation
* 💾 Dual storage:

  * JSON file
  * SQLite database
* 🧪 Mock mode for testing

---

## 🧠 Pipeline Flow

```
Open-Meteo → Airflow → Ollama → Validation → Storage
```

---

## 📦 Tech Stack

* Apache Airflow 2.7+
* Ollama (qwen2.5-coder / tinyllama)
* Python (requests, sqlite3)
* Open-Meteo API

---

## ⚙️ Setup

### 1. Install Dependencies

```bash
pip install "apache-airflow>=2.7,<3" requests
```

---

### 2. Start Ollama

```bash
ollama serve
ollama pull qwen2.5-coder:7b
```

---

### 3. Configure Airflow

```bash
export AIRFLOW_HOME=~/airflow
airflow db init
airflow standalone
```

---

### 4. Add DAG

```bash
cp weather_ollama_dag.py $AIRFLOW_HOME/dags/
```

---

## ▶️ Run Pipeline

1. Open Airflow UI
2. Enable DAG: `weather_unstructured_to_structured`
3. Trigger run

---

## 📊 Output

### JSON File

```bash
~/airflow/lecture11/output.json
```

### SQLite DB

```bash
~/airflow/lecture11/weather.db
```

---

## 📄 Example Output

```json
{
  "temperature_c": 11.9,
  "windspeed_kmh": 13.1,
  "weather_code": 0,
  "conditions_short": "Clear"
}
```

---

## 🧪 Mock Mode

Run without Ollama:

```bash
export WEATHER_PIPELINES_MOCK_OLLAMA=1
```

---

## ⚠️ Common Issues

### DAG not updating

```bash
export AIRFLOW_HOME=~/airflow
airflow standalone
```

---

### File path errors

* Fixed using:

```python
os.makedirs(BASE_DIR, exist_ok=True)
```

---

## 🎯 Learning Highlights

* LLM integration in data pipelines
* Airflow DAG orchestration
* JSON schema enforcement
* Debugging distributed systems

---

## 👨‍💻 Author

**Subhankar Biswas**

---

## 📌 Assignment

Lecture 11 — Airflow + Ollama: Weather → Structured JSON
