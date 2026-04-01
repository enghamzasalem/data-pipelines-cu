import airflow.utils.dates
from airflow import DAG
import pendulum
import os
from pathlib import Path

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

AIRFLOW_HOME = os.environ.get("AIRFLOW_HOME", str(Path.home() / "airflow"))
DATA_DIR = f"{AIRFLOW_HOME}/data/supermarket1"


def _process_supermarket(**context):
    import csv
    from pathlib import Path

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
            writer.writerow([prod, count, context["ds"]])

    print(f"Saved to {output_path}: {len(promotions)} products")
    return str(output_path)


def _add_to_db(**context):
    ds = context["ds"]
    file_path = f"{DATA_DIR}/processed/promotions_{ds}.csv"

    import sqlite3

    conn = sqlite3.connect("supermarket.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS promotions (
        product_id TEXT,
        promotion_count INTEGER,
        date TEXT
    )
    """)

    import csv

    with open(file_path, newline="") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            cursor.execute(
                    "INSERT INTO promotions VALUES (?, ?, ?)",
                    (row["product_id"], row["promotion_count"], row["date"])
            )

    conn.commit()
    conn.close()
            


dag = DAG(
    dag_id="lecture5_supermarket_exercise",
    start_date=pendulum.datetime(2026, 3, 5, tz="UTC"),
    schedule="0 16 * * *",
    catchup=False,
    tags=["lecture5", "exercise", "supermarket", "filesensor"],
)


wait_for_supermarket_1 = FileSensor(
    task_id="wait_for_supermarket_1",
    filepath=f"{DATA_DIR}/_SUCCESS",
    fs_conn_id="fs_default",
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
