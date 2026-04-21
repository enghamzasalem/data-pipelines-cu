"""
Lecture 4 - Exercise: StockSense Wikipedia Pageviews ETL

Pipeline:
get_data → extract_gz → fetch_pageviews → add_to_db
"""

from __future__ import annotations

from pathlib import Path
import pendulum

from airflow import DAG

try:
    from airflow.operators.bash import BashOperator
    from airflow.operators.python import PythonOperator
except ImportError:
    from airflow.providers.standard.operators.bash import BashOperator
    from airflow.providers.standard.operators.python import PythonOperator

PAGENAMES = {"Google", "Amazon", "Apple", "Microsoft", "Facebook"}

OUTPUT_DIR = "/home/mimou/airflow/data/stocksense/pageview_counts"
DB_PATH = "/home/mimou/airflow/data/stocksense/stocksense.db"


def _get_data(year, month, day, hour, output_path, **_):
    """Download Wikipedia pageviews for the given logical hour."""
    from urllib import request

    url = (
        "https://dumps.wikimedia.org/other/pageviews/"
        f"{year}/{year}-{int(month):02d}/"
        f"pageviews-{year}{int(month):02d}{int(day):02d}-{int(hour):02d}0000.gz"
    )

    print(f"Downloading {url}")
    request.urlretrieve(url, output_path)
    print(f"Saved to {output_path}")


def _fetch_pageviews(pagenames, logical_date, **context):
    """
    Parse pageviews file, extract counts for tracked companies, save to CSV.
    `logical_date` is injected by Airflow 3 in task context.
    """
    result = dict.fromkeys(pagenames, 0)

    with open("/tmp/wikipageviews", "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 4:
                continue

            domain, title, views = parts[0], parts[1], parts[2]

            if domain == "en" and title in pagenames:
                try:
                    result[title] = int(views)
                except ValueError:
                    pass

    output_path = context["templates_dict"]["output_path"]
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        f.write("pagename,pageviewcount,datetime\n")
        for name, count in result.items():
            f.write(f'"{name}",{count},{logical_date}\n')

    print(f"CSV written to {output_path}")
    print(f"Counts: {result}")
    return result


def _add_to_db(**context):
    """Load CSV data into SQLite database."""
    import csv
    import sqlite3

    output_path = context["templates_dict"]["output_path"]

    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS pageviews (
            pagename TEXT NOT NULL,
            pageviewcount INTEGER NOT NULL,
            datetime TEXT NOT NULL,
            PRIMARY KEY (pagename, datetime)
        )
        """
    )

    with open(output_path, newline="") as f:
        reader = csv.DictReader(f)
        rows = [
            (r["pagename"].strip('"'), int(r["pageviewcount"]), r["datetime"])
            for r in reader
        ]

    cur.executemany(
        """
        INSERT INTO pageviews (pagename, pageviewcount, datetime)
        VALUES (?, ?, ?)
        ON CONFLICT(pagename, datetime)
        DO UPDATE SET pageviewcount = excluded.pageviewcount
        """,
        rows,
    )

    conn.commit()
    conn.close()

    print(f"Inserted {len(rows)} rows into {DB_PATH}")


dag = DAG(
    dag_id="lecture4_stocksense_exercise",
    start_date=pendulum.datetime(2026, 2, 27, tz="UTC"),
    schedule="@hourly",
    catchup=False,
    max_active_runs=1,
    tags=["lecture4", "stocksense", "etl"],
)

get_data = PythonOperator(
    task_id="get_data",
    python_callable=_get_data,
    op_kwargs={
        "year": "{{ logical_date.year }}",
        "month": "{{ logical_date.month }}",
        "day": "{{ logical_date.day }}",
        "hour": "{{ logical_date.hour }}",
        "output_path": "/tmp/wikipageviews.gz",
    },
    dag=dag,
)

extract_gz = BashOperator(
    task_id="extract_gz",
    bash_command="gunzip -f /tmp/wikipageviews.gz",
    dag=dag,
)

fetch_pageviews = PythonOperator(
    task_id="fetch_pageviews",
    python_callable=_fetch_pageviews,
    op_kwargs={"pagenames": PAGENAMES, "logical_date": "{{ logical_date }}"},
    templates_dict={"output_path": f"{OUTPUT_DIR}/{{{{ ts_nodash }}}}.csv"},
    dag=dag,
)

add_to_db = PythonOperator(
    task_id="add_to_db",
    python_callable=_add_to_db,
    templates_dict={"output_path": f"{OUTPUT_DIR}/{{{{ ts_nodash }}}}.csv"},
    dag=dag,
)

get_data >> extract_gz >> fetch_pageviews >> add_to_db