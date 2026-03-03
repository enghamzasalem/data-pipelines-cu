from datetime import datetime, timedelta
from pathlib import Path

import requests

import pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator

BASE_DIR = Path.home() / "data" / "binance"


def _fetch_binance_price(**context):

    api_url = "https://api.binance.com/api/v3/avgPrice?symbol=BTCUSDT"

    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        data = response.json()

        data["timestamp"] = datetime.now().isoformat()
        data["fetch_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        data["price_float"] = float(data["price"])

        df = pd.DataFrame([data])

        date_str = datetime.now().strftime("%Y-%m-%d")
        hour_str = datetime.now().strftime("%H")
        minute_str = datetime.now().strftime("%M")

        output_dir = BASE_DIR / "raw" / date_str
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / f"price_{hour_str}_{minute_str}.csv"
        df.to_csv(output_file, index=False)

        daily_file = output_dir / "daily_raw.csv"
        if daily_file.exists():
            existing_df = pd.read_csv(daily_file)
            df = pd.concat([existing_df, df], ignore_index=True)

        df.to_csv(daily_file, index=False)

        print(f"Successfully fetched price: {data['price']} at {data['fetch_time']}")
        print(f"Saved to: {output_file}")

        return data

    except requests.exceptions.RequestException as e:
        print(f"Error fetching from Binance API: {e}")
        raise
    except Exception as e:
        print(f"Error processing data: {e}")
        raise


dag = DAG(
    dag_id="binance_fetch_minute",
    description="Fetches Bitcoin price from Binance every minute",
    schedule=timedelta(minutes=1),
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["binance", "crypto", "price", "minute"],
    default_args={
        "retries": 3,
        "retry_delay": timedelta(minutes=1),
    },
)

fetch_price = PythonOperator(
    task_id="fetch_binance_price",
    python_callable=_fetch_binance_price,
    dag=dag,
)