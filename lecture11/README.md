# Lecture 11 — Airflow + Ollama Weather Pipeline

## Overview

This project builds an Airflow DAG that:

* Fetches weather data from Open-Meteo API
* Sends raw JSON to Ollama (LLM)
* Converts it into structured JSON
* Validates and outputs clean data

## DAG Name

weather_unstructured_to_structured

## Steps

1. fetch_open_meteo_raw
2. ollama_to_structured
3. validate_and_emit

## Tools Used

* Apache Airflow
* Python
* Open-Meteo API
* Ollama (LLM)

## Output

Structured JSON containing:

* city_label
* observation_date
* temp_c_current
* temp_c_max
* temp_c_min
* conditions_short
* precipitation_mm

## How to Run

1. Start Airflow
2. Place DAG inside dags folder
3. Trigger DAG from UI

## Author

Renuka Joshi
