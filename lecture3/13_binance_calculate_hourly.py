"""
Binance Price Aggregator - Hourly Average (Airflow 3 Compatible)
=================================================================

Calculates hourly average Bitcoin price from minute-level data
produced by the binance_fetch_minute DAG.

Reads:
~/airflow/data/binance/raw/YYYY-MM-DD/daily_raw.csv

Writes:
~/airflow/data/binance/hourly/YYYY-MM-DD/hourly_avg.csv
"""

from datetime import datetime, timedelta
from pathlib import Path
import os

import pandas as pd
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator


def calculate_hourly_average(**context):
    """
    Calculates hourly average price from minute-level data.
    Aggregates the PREVIOUS hour using Airflow logical time.
    """

    # Use Airflow logical execution time
    logical_time = context["logical_date"]

    # We aggregate the previous completed hour
    target_time = logical_time - timedelta(hours=1)

    target_date = target_time.strftime("%Y-%m-%d")
    target_hour = target_time.strftime("%H")

    # Define raw data path
    airflow_home = Path(
        os.environ.get("AIRFLOW_HOME", "~/airflow")
    ).expanduser()

    raw_file = airflow_home / "data" / "binance" / "raw" / target_date / "daily_raw.csv"

    if not raw_file.exists():
        print(f"⚠ No raw data found at {raw_file}")
        return

    try:
        df = pd.read_csv(raw_file)

        df["fetch_time"] = pd.to_datetime(df["fetch_time"])
        df["hour"] = df["fetch_time"].dt.strftime("%H")

        # Filter for target hour
        hour_data = df[df["hour"] == target_hour].copy()

        if hour_data.empty:
            print(f"⚠ No data found for hour {target_hour}")
            return

        # Calculate statistics
        hourly_stats = {
            "date": target_date,
            "hour": target_hour,
            "avg_price": hour_data["price_float"].mean(),
            "min_price": hour_data["price_float"].min(),
            "max_price": hour_data["price_float"].max(),
            "first_price": hour_data["price_float"].iloc[0],
            "last_price": hour_data["price_float"].iloc[-1],
            "data_points": len(hour_data),
            "calculated_at": logical_time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        hourly_df = pd.DataFrame([hourly_stats])

        # Output directory
        output_dir = airflow_home / "data" / "binance" / "hourly" / target_date
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / "hourly_avg.csv"

        # Append while preventing duplicate hour
        if output_file.exists():
            existing_df = pd.read_csv(output_file)
            existing_df = existing_df[existing_df["hour"] != target_hour]
            hourly_df = pd.concat([existing_df, hourly_df], ignore_index=True)

        hourly_df.to_csv(output_file, index=False)

        print(f"✅ Hourly aggregation completed")
        print(f"Date: {target_date} Hour: {target_hour}")
        print(f"Average Price: ${hourly_stats['avg_price']:.2f}")
        print(f"Data Points: {hourly_stats['data_points']}")
        print(f"Saved to: {output_file}")

        return hourly_stats

    except Exception as e:
        print(f"❌ Error calculating hourly average: {e}")
        raise


# DAG Definition (Airflow 3)
dag = DAG(
    dag_id="binance_calculate_hourly",
    description="Calculates hourly average Bitcoin price from minute data",
    schedule=timedelta(hours=1),
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["binance", "crypto", "hourly", "aggregation"],
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
    },
)


calculate_hourly = PythonOperator(
    task_id="calculate_hourly_average",
    python_callable=calculate_hourly_average,
    dag=dag,
)

