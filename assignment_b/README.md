# 🌦️ Lecture 11B — Hadoop + Spark ETL Assignment

## 🎯 Objective

Build a scalable ETL pipeline using Apache Spark to process weather data from the Open-Meteo API and store it in a structured format.

---

## 🧱 Architecture Overview

```
          ┌────────────────────┐
          │  Open-Meteo API    │
          └─────────┬──────────┘
                    │
                    ▼
          ┌────────────────────┐
          │ Fetch Script       │
          │ (fetch_weather.py) │
          └─────────┬──────────┘
                    │
                    ▼
          ┌────────────────────────────┐
          │ Raw JSON Storage           │
          │ assignment_b_submission/   │
          │ lecture11b-open-meteo-raw  │
          └─────────┬──────────────────┘
                    │
                    ▼
          ┌────────────────────────────┐
          │ Spark ETL (PySpark)        │
          │ weather_etl.py             │
          │ - Clean                    │
          │ - Flatten                 │
          │ - Transform               │
          └─────────┬──────────────────┘
                    │
         ┌──────────┴───────────┐
         ▼                      ▼
┌───────────────────┐   ┌────────────────────┐
│ Current Weather    │   │ Daily Weather      │
│ (Parquet Output)  │   │ (Parquet Output)   │
└───────────────────┘   └────────────────────┘
```

---

## ⚙️ Tech Stack

* Python 3
* Apache Spark (PySpark)
* Open-Meteo API
* Parquet (columnar storage format)

---

## 📂 Project Structure

```
lecture11/
└── assignment_b/
    ├── scripts/
    │   └── fetch_weather.py
    ├── spark/
    │   └── weather_etl.py
    ├── assignment_b_submission/
    │   ├── lecture11b-open-meteo-raw.json
    │   ├── curated_current_weather/
    │   ├── curated_daily_weather/
    │   └── screenshots...
    ├── requirements.txt
    └── README.md
```

---

## 🚀 How to Run

### 1️⃣ Install Dependencies

```bash
brew install openjdk@17
brew install apache-spark
```

---

### 2️⃣ Set Environment Variables

```bash
export JAVA_HOME=$(/usr/libexec/java_home -v 17)
export PATH="/opt/homebrew/opt/apache-spark/bin:$PATH"
```

---

### 3️⃣ Fetch Weather Data

```bash
python3 scripts/fetch_weather.py
```

---

### 4️⃣ Run Spark ETL

```bash
spark-submit spark/weather_etl.py
```

---

## 📊 Output

### ✅ Raw Data

* JSON file from Open-Meteo API

### ✅ Processed Data

* `curated_current_weather/`
* `curated_daily_weather/`

Stored in **Parquet format** for efficient analytics.

---

## 🧠 Key Concepts Demonstrated

* Distributed data processing with Spark
* Handling nested JSON data
* DataFrame transformations
* `explode()` and `arrays_zip()` usage
* Columnar storage with Parquet

---

## ⚠️ Note on Environment

Due to Apple Silicon (ARM) limitations:

* VirtualBox (x86) is not supported
* Spark was run in **local mode**, which is recommended for initial development

---

## 📸 Submission Includes

* ✅ Spark installation proof
* ✅ Data ingestion proof
* ✅ ETL execution logs
* ✅ Output datasets
* ✅ Data preview

---

## 🏁 Conclusion

This project demonstrates a complete ETL pipeline:

* Extracting real-time data
* Transforming using distributed computing
* Loading into optimized storage format

The solution reflects real-world data engineering practices using Spark.

---
