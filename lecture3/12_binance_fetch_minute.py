"""
Binance Price Fetcher - Minute Level (Airflow 3 Compatible)
===========================================================

Fetches Bitcoin (BTCUSDT) average price from Binance API every minute
and stores raw minute-level data partitioned by date.

Storage location:
~/airflow/data/binance/raw/YYYY-MM-DD/

Airflow 3 compatible:
- Uses `schedule`
- Uses `logical_date`
"""

from datetime import datetime, timedelta
from pathlib import Path
import os

import requests
import pandas as pd

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator


def fetch_binance_price(**context):
    """
    Fetch Bitcoin average price from Binance API
    and store minute-level raw data.
    """

    api_url = "https://api.binance.com/api/v3/avgPrice?symbol=BTCUSDT"

    try:
        # Use Airflow logical execution time (IMPORTANT)
        logical_time = context["logical_date"]

        # Fetch API data
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Enrich with metadata
        data["timestamp"] = logical_time.isoformat()
        data["fetch_time"] = logical_time.strftime("%Y-%m-%d %H:%M:%S")
        data["price_float"] = float(data["price"])

        # Convert to DataFrame
        df = pd.DataFrame([data])

        # Date partitions using logical time
        date_str = logical_time.strftime("%Y-%m-%d")
        hour_str = logical_time.strftime("%H")
        minute_str = logical_time.strftime("%M")

        # Use AIRFLOW_HOME safely
        airflow_home = Path(
            os.environ.get("AIRFLOW_HOME", "~/airflow")
        ).expanduser()

        output_dir = airflow_home / "data" / "binance" / "raw" / date_str
        output_dir.mkdir(parents=True, exist_ok=True)

        # Minute-level file
        minute_file = output_dir / f"price_{hour_str}_{minute_str}.csv"
        df.to_csv(minute_file, index=False)

        # Append to daily file
        daily_file = output_dir / "daily_raw.csv"

        if daily_file.exists():
            existing_df = pd.read_csv(daily_file)
            df = pd.concat([existing_df, df], ignore_index=True)

        df.to_csv(daily_file, index=False)

        print(f"✅ Price fetched: {data['price']}")
        print(f"📁 Saved to: {minute_file}")

        return data

    except requests.exceptions.RequestException as e:
        print(f"❌ API request failed: {e}")
        raise

    except Exception as e:
        print(f"❌ Processing error: {e}")
        raise


# DAG Definition (Airflow 3)
dag = DAG(
    dag_id="binance_fetch_minute",
    description="Fetch Bitcoin price from Binance every minute",
    schedule=timedelta(minutes=1),
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["binance", "crypto", "minute"],
    default_args={
        "retries": 3,
        "retry_delay": timedelta(minutes=1),
    },
)


# Task
fetch_price = PythonOperator(
    task_id="fetch_binance_price",
    python_callable=fetch_binance_price,
    dag=dag,
)

