from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator

BASE_DIR = Path.home() / "data" / "binance"


def _calculate_daily_average(**context):
    """
    Calculates daily average price from hourly data.
    Reads the hourly CSV file and aggregates by day.
    """
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")

    hourly_file = BASE_DIR / "hourly" / current_date / "hourly_avg.csv"

    if not hourly_file.exists():
        print(f"No hourly data file found at {hourly_file}")
        print("Waiting for hourly data to be collected...")
        return

    try:
        df = pd.read_csv(hourly_file)

        if df.empty:
            print(f"No hourly data found for {current_date}")
            return

        daily_stats = {
            "date": current_date,
            "avg_price": df["avg_price"].mean(),
            "min_price": df["min_price"].min(),
            "max_price": df["max_price"].max(),
            "opening_price": df["first_price"].iloc[0] if "first_price" in df.columns else df["avg_price"].iloc[0],
            "closing_price": df["last_price"].iloc[-1] if "last_price" in df.columns else df["avg_price"].iloc[-1],
            "price_change": 0,
            "price_change_pct": 0,
            "total_data_points": df["data_points"].sum(),
            "hours_with_data": len(df),
            "calculated_at": now.strftime("%Y-%m-%d %H:%M:%S"),
        }

        if daily_stats["opening_price"] > 0:
            daily_stats["price_change"] = daily_stats["closing_price"] - daily_stats["opening_price"]
            daily_stats["price_change_pct"] = (daily_stats["price_change"] / daily_stats["opening_price"]) * 100

        daily_df = pd.DataFrame([daily_stats])

        output_dir = BASE_DIR / "daily"
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / "daily_avg.csv"

        if output_file.exists():
            existing_df = pd.read_csv(output_file)
            existing_df = existing_df[existing_df["date"] != current_date]
            daily_df = pd.concat([existing_df, daily_df], ignore_index=True)
        else:
            daily_df.to_csv(output_file, index=False)
            print(f"Created new daily average file: {output_file}")
            return daily_stats

        daily_df = daily_df.sort_values("date")
        daily_df.to_csv(output_file, index=False)

        print(f"Daily average calculated for {current_date}:")
        print(f"  Average Price: ${daily_stats['avg_price']:.2f}")
        print(f"  Min Price: ${daily_stats['min_price']:.2f}")
        print(f"  Max Price: ${daily_stats['max_price']:.2f}")
        print(f"  Opening Price: ${daily_stats['opening_price']:.2f}")
        print(f"  Closing Price: ${daily_stats['closing_price']:.2f}")
        print(f"  Price Change: ${daily_stats['price_change']:.2f} ({daily_stats['price_change_pct']:.2f}%)")
        print(f"  Hours with Data: {daily_stats['hours_with_data']}")
        print(f"  Total Data Points: {daily_stats['total_data_points']}")
        print(f"  Saved to: {output_file}")

        return daily_stats

    except Exception as e:
        print(f"Error calculating daily average: {e}")
        raise


dag = DAG(
    dag_id="binance_calculate_daily",
    description="Calculates daily average Bitcoin price from hourly data",
    schedule=timedelta(days=1),
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["binance", "crypto", "price", "daily", "aggregation"],
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=10),
    },
)

calculate_daily = PythonOperator(
    task_id="calculate_daily_average",
    python_callable=_calculate_daily_average,
    dag=dag,
)