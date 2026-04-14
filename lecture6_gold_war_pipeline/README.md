# Gold War Pipeline (Data Engineering Project)

## Overview

This project builds an end-to-end data pipeline that:

* Fetches gold prices data
* Collects war-related news
* Performs sentiment analysis
* Trains a machine learning model
* Orchestrates everything using Apache Airflow

## Technologies Used

* Python
* Pandas
* Scikit-learn
* TextBlob
* Apache Airflow

## Pipeline Steps

1. Fetch gold prices using yfinance
2. Fetch war news using RSS feed
3. Perform sentiment analysis
4. Merge datasets
5. Train ML model

## How to Run

1. Install dependencies:
   pip install -r requirements.txt

2. Run ETL:
   python gold_war_etl.py

3. Start Airflow:
   airflow standalone

## Airflow DAG

The DAG automates:

* Data collection
* Data processing
* Model training

## Output

* Processed datasets in /data
* Trained model in /models

