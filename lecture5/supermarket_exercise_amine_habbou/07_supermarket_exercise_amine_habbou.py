"""
Lecture 5 - Exercise: Supermarket Promotions ETL with FileSensor

Based on Chapter 6 "Triggering Workflows" – supermarket data ingestion pattern.

EXERCISE: Complete pipeline that waits for supermarket data (FileSensor),
processes it, and loads to a database. The add_to_db task is left empty.

Pipeline: wait_for_supermarket_1 → process_supermarket → add_to_db
"""

import airflow.utils.dates
from airflow import DAG

try:
    from airflow.sensors.filesystem import FileSensor
except ImportError:
    from airflow.providers.filesystem.sensors.filesystem import FileSensor

try:
    from airflow.operators.bash import BashOperator
    from airflow.operators.python import PythonOperator
except ImportError:
    from airflow.operators.bash import BashOperator
    from airflow.operators.python import PythonOperator

import os
import sqlite3
import csv
from pathlib import Path

DATA_DIR = "/home/amine_apache/airflow/data/supermarket1"
OUTPUT_DIR = "/home/amine_apache/airflow/outputs/07_supermarket_exercise"

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)


def _process_supermarket(**context):
    """
    Read raw data from supermarket, aggregate promotions, save to CSV.
    execution_date (ds) comes from Airflow context.
    """
    import csv
    from pathlib import Path

    ds = context["ds"]

    # Original location
    original_path = Path(f"{DATA_DIR}/processed/promotions_{ds}.csv")
    original_path.parent.mkdir(parents=True, exist_ok=True)

    # Output location
    output_dir = Path("/home/amine_apache/airflow/outputs/07_supermarket_exercise")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"promotions_{ds}.csv"

    # Read all data-*.csv files and aggregate
    raw_dir = Path(DATA_DIR)
    data_files = list(raw_dir.glob("data-*.csv"))
    if not data_files:
        raise FileNotFoundError(f"No data-*.csv files in {raw_dir}")

    promotions = {}
    for f in data_files:
        with open(f, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                prod = row.get("product_id", row.get("product", "unknown"))
                promotions[prod] = promotions.get(prod, 0) + 1

    # Save to original location
    with open(original_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["product_id", "promotion_count", "date"])
        for prod, count in promotions.items():
            writer.writerow([prod, count, ds])

    # Save to output directory
    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["product_id", "promotion_count", "date"])
        for prod, count in promotions.items():
            writer.writerow([prod, count, ds])

    return str(original_path)


def _add_to_db(**context):
    """Add promotions to SQLite database in the output directory."""
    ds = context["ds"]

    # Path to the CSV file
    csv_path = Path(f"{DATA_DIR}/processed/promotions_{ds}.csv")

    # Path to the SQLite database
    db_path = os.path.join(OUTPUT_DIR, "supermarket_promotions.db")

    # Check if CSV exists
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS promotions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT NOT NULL,
            promotion_count INTEGER NOT NULL,
            date TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # Read CSV and insert data
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        inserted_count = 0

        for row in reader:
            cursor.execute(
                """
                INSERT INTO promotions (product_id, promotion_count, date)
                VALUES (?, ?, ?)
            """,
                (row["product_id"], int(row["promotion_count"]), row["date"]),
            )
            inserted_count += 1

    # Commit and close
    conn.commit()
    conn.close()


dag = DAG(
    dag_id="lecture5_supermarket_exercise",
    start_date=airflow.utils.dates.days_ago(3),
    schedule="0 16 * * *",
    catchup=False,
    tags=["lecture5", "exercise", "supermarket", "filesensor"],
)

# Wait for supermarket data (FileSensor checks for _SUCCESS marker)
wait_for_supermarket_1 = FileSensor(
    task_id="wait_for_supermarket_1",
    filepath=f"{DATA_DIR}/_SUCCESS",
    poke_interval=60,
    timeout=60 * 60 * 24,
    mode="reschedule",
    dag=dag,
)

process_supermarket = PythonOperator(
    task_id="process_supermarket",
    python_callable=_process_supermarket,
    dag=dag,
)

add_to_db = PythonOperator(
    task_id="add_to_db",
    python_callable=_add_to_db,
    dag=dag,
)

wait_for_supermarket_1 >> process_supermarket >> add_to_db
