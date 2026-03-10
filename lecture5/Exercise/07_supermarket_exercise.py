import airflow.utils.dates
from airflow import DAG
from airflow.sensors.filesystem import FileSensor
from airflow.operators.python import PythonOperator

DATA_DIR = "/Users/harikrishna/data/supermarket1"


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
    import csv
    import sqlite3
    from pathlib import Path

    ds = context["ds"]
    csv_path = Path(f"{DATA_DIR}/processed/promotions_{ds}.csv")
    db_path = Path(f"{DATA_DIR}/processed/promotions.db")

    if not csv_path.exists():
        raise FileNotFoundError(f"Processed CSV not found: {csv_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS promotions (
            product_id TEXT,
            promotion_count INTEGER,
            date TEXT
        )
    """)

    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        rows_inserted = 0
        for row in reader:
            cursor.execute("""
                INSERT INTO promotions (product_id, promotion_count, date)
                VALUES (?, ?, ?)
            """, (
                row["product_id"],
                int(row["promotion_count"]),
                row["date"]
            ))
            rows_inserted += 1

    conn.commit()
    conn.close()

    print(f"Inserted {rows_inserted} rows into database: {db_path}")


dag = DAG(
    dag_id="lecture5_supermarket_exercise",
    start_date=airflow.utils.dates.days_ago(3),
    schedule="0 16 * * *",
    catchup=False,
    tags=["lecture5", "exercise", "supermarket", "filesensor"],
)

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