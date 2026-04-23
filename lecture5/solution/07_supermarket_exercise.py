"""
Lecture 5 - Exercise: Supermarket Promotions ETL with FileSensor

Pipeline:
wait_for_supermarket_1 -> process_supermarket -> add_to_db
"""


from datetime import datetime
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator

try:
    from airflow.sensors.filesystem import FileSensor
except ImportError:
    from airflow.providers.standard.sensors.filesystem import FileSensor


DATA_DIR = Path("/home/mimou/airflow/data/supermarket1")
OUTPUT_DIR = DATA_DIR / "processed"
DB_PATH = DATA_DIR / "supermarket.db"


def _process_supermarket(**context):
    import csv

    ds = context["ds"]
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f"promotions_{ds}.csv"

    data_files = list(DATA_DIR.glob("data-*.csv"))
    if not data_files:
        raise FileNotFoundError(f"No data-*.csv files found in {DATA_DIR}")

    promotions = {}
    for file in data_files:
        with open(file, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                product = row.get("product_id", row.get("product", "unknown"))
                promotions[product] = promotions.get(product, 0) + 1

    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["product_id", "promotion_count", "date"])
        for product, count in promotions.items():
            writer.writerow([product, count, ds])

    print(f"Saved processed file: {output_path}")
    return str(output_path)


def _add_to_db(**context):
    import csv
    import sqlite3

    ds = context["ds"]
    input_path = OUTPUT_DIR / f"promotions_{ds}.csv"

    if not input_path.exists():
        raise FileNotFoundError(f"Processed file not found: {input_path}")

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS promotions (
            product_id TEXT,
            promotion_count INTEGER,
            date TEXT
        )
    """)

    cursor.execute("DELETE FROM promotions WHERE date = ?", (ds,))

    with open(input_path, newline="") as f:
        reader = csv.DictReader(f)
        rows = [
            (row["product_id"], int(row["promotion_count"]), row["date"])
            for row in reader
        ]

    cursor.executemany("""
        INSERT INTO promotions (product_id, promotion_count, date)
        VALUES (?, ?, ?)
    """, rows)

    conn.commit()
    conn.close()

    print(f"Inserted {len(rows)} rows into database {DB_PATH}")


dag = DAG(
    dag_id="lecture5_supermarket_exercise",
    start_date=datetime(2024, 1, 1),
    schedule="0 16 * * *",
    catchup=False,
    tags=["lecture5", "exercise", "supermarket", "filesensor"],
)

wait_for_supermarket_1 = FileSensor(
    task_id="wait_for_supermarket_1",
    fs_conn_id="fs_default",
    filepath="_SUCCESS",
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