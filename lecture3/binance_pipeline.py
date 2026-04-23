"""
Binance Price Pipeline
======================

Single DAG containing:
1. Minute price fetch
2. Hourly aggregation
3. Daily aggregation

Schedule: Runs every minute
"""

from datetime import datetime, timedelta
from pathlib import Path
import requests
import pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator


BASE_PATH = Path.home() / "airflow" / "data" / "binance"


# -----------------------------
# Task 1: Fetch Minute Price
# -----------------------------
def fetch_price():
    api_url = "https://api.binance.com/api/v3/avgPrice?symbol=BTCUSDT"

    response = requests.get(api_url, timeout=10)
    response.raise_for_status()
    data = response.json()

    now = datetime.now()
    data["timestamp"] = now.isoformat()
    data["fetch_time"] = now.strftime("%Y-%m-%d %H:%M:%S")
    data["price_float"] = float(data["price"])

    df = pd.DataFrame([data])

    date_str = now.strftime("%Y-%m-%d")
    hour_str = now.strftime("%H")
    minute_str = now.strftime("%M")

    output_dir = BASE_PATH / "raw" / date_str
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save minute file
    minute_file = output_dir / f"price_{hour_str}_{minute_str}.csv"
    df.to_csv(minute_file, index=False)

    # Append to daily raw file
    daily_file = output_dir / "daily_raw.csv"
    if daily_file.exists():
        existing_df = pd.read_csv(daily_file)
        df = pd.concat([existing_df, df], ignore_index=True)

    df.to_csv(daily_file, index=False)

    print(f"Minute data saved at {data['fetch_time']}")


# -----------------------------
# Task 2: Hourly Aggregation
# -----------------------------
def calculate_hourly():
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    current_hour = now.strftime("%H")

    raw_file = BASE_PATH / "raw" / current_date / "daily_raw.csv"

    if not raw_file.exists():
        print("No raw data yet.")
        return

    df = pd.read_csv(raw_file)
    df["fetch_time"] = pd.to_datetime(df["fetch_time"])
    df["hour"] = df["fetch_time"].dt.strftime("%H")

    hour_df = df[df["hour"] == current_hour]

    if hour_df.empty:
        return

    stats = {
        "date": current_date,
        "hour": current_hour,
        "avg_price": hour_df["price_float"].mean(),
        "min_price": hour_df["price_float"].min(),
        "max_price": hour_df["price_float"].max(),
        "first_price": hour_df["price_float"].iloc[0],
        "last_price": hour_df["price_float"].iloc[-1],
        "data_points": len(hour_df),
        "calculated_at": now.strftime("%Y-%m-%d %H:%M:%S"),
    }

    hourly_df = pd.DataFrame([stats])

    output_dir = BASE_PATH / "hourly" / current_date
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "hourly_avg.csv"

    if output_file.exists():
        existing_df = pd.read_csv(output_file)
        existing_df = existing_df[existing_df["hour"] != current_hour]
        hourly_df = pd.concat([existing_df, hourly_df], ignore_index=True)

    hourly_df.to_csv(output_file, index=False)

    print(f"Hourly aggregation saved for hour {current_hour}")


# -----------------------------
# Task 3: Daily Aggregation
# -----------------------------
def calculate_daily():
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")

    hourly_file = BASE_PATH / "hourly" / current_date / "hourly_avg.csv"

    if not hourly_file.exists():
        print("No hourly data yet.")
        return

    df = pd.read_csv(hourly_file)

    if df.empty:
        return

    opening_price = df["first_price"].iloc[0]
    closing_price = df["last_price"].iloc[-1]

    stats = {
        "date": current_date,
        "avg_price": df["avg_price"].mean(),
        "min_price": df["min_price"].min(),
        "max_price": df["max_price"].max(),
        "opening_price": opening_price,
        "closing_price": closing_price,
        "price_change": closing_price - opening_price,
        "price_change_pct": ((closing_price - opening_price) / opening_price) * 100,
        "total_data_points": df["data_points"].sum(),
        "hours_with_data": len(df),
        "calculated_at": now.strftime("%Y-%m-%d %H:%M:%S"),
    }

    daily_df = pd.DataFrame([stats])

    output_dir = BASE_PATH / "daily"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "daily_avg.csv"

    if output_file.exists():
        existing_df = pd.read_csv(output_file)
        existing_df = existing_df[existing_df["date"] != current_date]
        daily_df = pd.concat([existing_df, daily_df], ignore_index=True)

    daily_df.to_csv(output_file, index=False)

    print("Daily aggregation saved.")


# -----------------------------
# DAG Definition
# -----------------------------
dag = DAG(
    dag_id="binance_pipeline",
    schedule=timedelta(minutes=1),  # runs every minute
    start_date=datetime(2024, 1, 1),
    catchup=False,
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=2),
    },
)


fetch_task = PythonOperator(
    task_id="fetch_minute",
    python_callable=fetch_price,
    dag=dag,
)

hourly_task = PythonOperator(
    task_id="aggregate_hourly",
    python_callable=calculate_hourly,
    dag=dag,
)

daily_task = PythonOperator(
    task_id="aggregate_daily",
    python_callable=calculate_daily,
    dag=dag,
)

# Task Order
fetch_task >> hourly_task >> daily_task