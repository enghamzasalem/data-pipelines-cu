"""
Binance Backfill ETL - Last 30 Days (Airflow 3 Compatible)
===========================================================

Backfills last 30 days of BTC minute data using Binance historical klines API.

Populates:
~/airflow/data/binance/raw/YYYY-MM-DD/daily_raw.csv
~/airflow/data/binance/hourly/YYYY-MM-DD/hourly_avg.csv
~/airflow/data/binance/daily/daily_avg.csv

Manual trigger only.
"""

from datetime import datetime, timedelta
from pathlib import Path
import os

import pandas as pd
import requests
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator


BINANCE_KLINES_URL = "https://api.binance.com/api/v3/klines"
SYMBOL = "BTCUSDT"
INTERVAL = "1m"
LIMIT = 1000


# -------------------------
# Helper: Fetch klines
# -------------------------
def fetch_klines(start_time_ms: int, end_time_ms: int) -> list:
    all_klines = []
    current_start = start_time_ms

    while current_start < end_time_ms:
        params = {
            "symbol": SYMBOL,
            "interval": INTERVAL,
            "startTime": current_start,
            "endTime": end_time_ms,
            "limit": LIMIT,
        }

        response = requests.get(BINANCE_KLINES_URL, params=params, timeout=30)
        response.raise_for_status()
        klines = response.json()

        if not klines:
            break

        all_klines.extend(klines)
        current_start = klines[-1][0] + 1

        if len(klines) < LIMIT:
            break

    return all_klines


# -------------------------
# Helper: Convert to raw format
# -------------------------
def klines_to_raw_df(klines: list) -> pd.DataFrame:
    records = []

    for k in klines:
        open_time_ms = k[0]
        close_time_ms = k[6]
        price = float(k[4])  # close price
        dt = datetime.utcfromtimestamp(open_time_ms / 1000)

        records.append({
            "mins": 1,
            "price": str(price),
            "closeTime": close_time_ms,
            "timestamp": dt.isoformat(),
            "fetch_time": dt.strftime("%Y-%m-%d %H:%M:%S"),
            "price_float": price,
        })

    return pd.DataFrame(records)


# -------------------------
# Main Backfill ETL
# -------------------------
def backfill_last_month(**context):

    utc_now = datetime.utcnow()
    end_date = utc_now.date()
    start_date = end_date - timedelta(days=30)

    print(f"Backfilling from {start_date} to {end_date}")

    start_time_ms = int(datetime.combine(start_date, datetime.min.time()).timestamp() * 1000)
    end_time_ms = int(utc_now.timestamp() * 1000)

    klines = fetch_klines(start_time_ms, end_time_ms)

    if not klines:
        print("No klines data received.")
        return

    raw_df = klines_to_raw_df(klines)
    raw_df["fetch_time"] = pd.to_datetime(raw_df["fetch_time"])
    raw_df["date"] = raw_df["fetch_time"].dt.strftime("%Y-%m-%d")
    raw_df["hour"] = raw_df["fetch_time"].dt.strftime("%H")

    print(f"Fetched {len(raw_df)} minute records")

    # Base paths
    airflow_home = Path(
        os.environ.get("AIRFLOW_HOME", "~/airflow")
    ).expanduser()

    base_raw = airflow_home / "data" / "binance" / "raw"
    base_hourly = airflow_home / "data" / "binance" / "hourly"
    base_daily = airflow_home / "data" / "binance" / "daily"

    base_daily.mkdir(parents=True, exist_ok=True)

    daily_records = []

    for date_str, day_df in raw_df.groupby("date"):

        # ---------------- RAW ----------------
        raw_dir = base_raw / date_str
        raw_dir.mkdir(parents=True, exist_ok=True)

        raw_file = raw_dir / "daily_raw.csv"

        day_raw = day_df.drop(columns=["date", "hour"])

        if raw_file.exists():
            existing = pd.read_csv(raw_file)
            existing["fetch_time"] = pd.to_datetime(existing["fetch_time"])
            combined = pd.concat([existing, day_raw], ignore_index=True)
            combined = combined.drop_duplicates(subset=["closeTime"])
            combined = combined.sort_values("fetch_time")
        else:
            combined = day_raw

        combined.to_csv(raw_file, index=False)

        # ---------------- HOURLY ----------------
        hourly_records = []

        for hour_str, hour_df in day_df.groupby("hour"):
            hourly_records.append({
                "date": date_str,
                "hour": hour_str,
                "avg_price": hour_df["price_float"].mean(),
                "min_price": hour_df["price_float"].min(),
                "max_price": hour_df["price_float"].max(),
                "first_price": hour_df["price_float"].iloc[0],
                "last_price": hour_df["price_float"].iloc[-1],
                "data_points": len(hour_df),
                "calculated_at": utc_now.strftime("%Y-%m-%d %H:%M:%S"),
            })

        hourly_df = pd.DataFrame(hourly_records)
        hourly_dir = base_hourly / date_str
        hourly_dir.mkdir(parents=True, exist_ok=True)
        hourly_df.to_csv(hourly_dir / "hourly_avg.csv", index=False)

        # ---------------- DAILY ----------------
        opening = hourly_df["first_price"].iloc[0]
        closing = hourly_df["last_price"].iloc[-1]

        price_change = closing - opening
        price_change_pct = (price_change / opening) * 100 if opening > 0 else 0

        daily_records.append({
            "date": date_str,
            "avg_price": hourly_df["avg_price"].mean(),
            "min_price": hourly_df["min_price"].min(),
            "max_price": hourly_df["max_price"].max(),
            "opening_price": opening,
            "closing_price": closing,
            "price_change": price_change,
            "price_change_pct": price_change_pct,
            "total_data_points": hourly_df["data_points"].sum(),
            "hours_with_data": len(hourly_df),
            "calculated_at": utc_now.strftime("%Y-%m-%d %H:%M:%S"),
        })

    # Merge daily
    if daily_records:
        new_daily = pd.DataFrame(daily_records)
        daily_file = base_daily / "daily_avg.csv"

        if daily_file.exists():
            existing_daily = pd.read_csv(daily_file)
            existing_daily = existing_daily[~existing_daily["date"].isin(new_daily["date"])]
            combined_daily = pd.concat([existing_daily, new_daily], ignore_index=True)
        else:
            combined_daily = new_daily

        combined_daily = combined_daily.sort_values("date")
        combined_daily.to_csv(daily_file, index=False)

        print(f"Backfill complete: {len(new_daily)} days written.")

    print("Backfill finished successfully.")


# -------------------------
# DAG Definition
# -------------------------
dag = DAG(
    dag_id="binance_backfill_last_month",
    description="Backfills last 30 days of BTC data from Binance",
    schedule=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["binance", "crypto", "backfill", "etl"],
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
    },
)

backfill_task = PythonOperator(
    task_id="backfill_last_month",
    python_callable=backfill_last_month,
    dag=dag,
)
