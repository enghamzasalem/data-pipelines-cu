"""
Lecture 5 - Exercise: Supermarket Promotions ETL with FileSensor

Pipeline:
wait_for_supermarket_1 → process_supermarket → add_to_db
"""

import datetime as dt
from pathlib import Path

from airflow import DAG

try:
    from airflow.sensors.filesystem import FileSensor
except ImportError:
    from airflow.providers.filesystem.sensors.filesystem import FileSensor

from airflow.operators.python import PythonOperator

# Use writable path instead of /data
DATA_DIR = str(Path.home() / "airflow" / "data" / "supermarket1")


def _process_supermarket(**context):
    """
    Read raw data from supermarket, aggregate promotions, save to CSV.
    """
    import csv

    ds = context["ds"]

    output_path = Path(f"{DATA_DIR}/processed/promotions_{ds}.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)

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

    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)

        writer.writerow(["product_id", "promotion_count", "date"])

        for prod, count in promotions.items():
            writer.writerow([prod, count, ds])

    print(f"Saved to {output_path}: {len(promotions)} products")

    return str(output_path)


def _add_to_db(**context):
    """
    Placeholder task for loading results into database.
    """
    processed_file = context["ti"].xcom_pull(task_ids="process_supermarket")

    print(f"Would load {processed_file} into database...")


dag = DAG(
    dag_id="lecture5_supermarket_exercise",
    start_date=dt.datetime(2024, 1, 1),
    schedule="0 16 * * *",
    catchup=False,
    tags=["lecture5", "exercise", "supermarket", "filesensor"],
)

# Wait for supermarket data (_SUCCESS marker)
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
