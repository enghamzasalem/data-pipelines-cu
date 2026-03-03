from pathlib import Path
import os
import csv
import sqlite3

import airflow.utils.dates
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

PAGENAMES = {"Google", "Amazon", "Apple", "Microsoft", "Facebook"}

BASE_DIR = os.path.expanduser("~/data/stocksense")
OUTPUT_DIR = os.path.join(BASE_DIR, "pageview_counts")
DB_PATH = os.path.join(BASE_DIR, "db", "stocksense.db")


def _get_data(year, month, day, hour, output_path, **_):
    from urllib import request

    url = (
        f"https://dumps.wikimedia.org/other/pageviews/"
        f"{year}/{year}-{int(month):02d}/"
        f"pageviews-{year}{int(month):02d}{int(day):02d}-{int(hour):02d}0000.gz"
    )
    print(f"Downloading {url}")
    request.urlretrieve(url, output_path)


def _fetch_pageviews(pagenames, execution_date, **context):
    result = dict.fromkeys(pagenames, 0)

    with open("/tmp/wikipageviews", "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 4:
                domain_code, page_title, view_count = parts[0], parts[1], parts[2]
                if domain_code == "en" and page_title in pagenames:
                    result[page_title] = int(view_count)

    output_path = context["templates_dict"]["output_path"]
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="") as f:
        f.write("pagename,pageviewcount,datetime\n")
        for pagename, count in result.items():
            f.write(f'"{pagename}",{count},{execution_date}\n')

    print(f"Saved pageview counts to {output_path}")
    print(f"Counts: {result}")
    return result


def _add_to_db(**context):
    output_path = context["templates_dict"]["output_path"]
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS pageviews (
            ds TEXT NOT NULL,
            pagename TEXT NOT NULL,
            pageviewcount INTEGER NOT NULL,
            datetime TEXT NOT NULL
        )
        """
    )

    rows = []
    with open(output_path, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            dt = row["datetime"]
            ds = dt[:10]
            rows.append((ds, row["pagename"], int(row["pageviewcount"]), dt))

    cur.executemany(
        "INSERT INTO pageviews (ds, pagename, pageviewcount, datetime) VALUES (?, ?, ?, ?)",
        rows,
    )

    conn.commit()
    conn.close()

    print(f"Inserted {len(rows)} rows into {DB_PATH}")


dag = DAG(
    dag_id="lecture4_stocksense_exercise",
    start_date=airflow.utils.dates.days_ago(1),
    schedule="@hourly",
    catchup=False,
    max_active_runs=1,
    tags=["lecture4", "exercise", "stocksense", "etl"],
)

get_data = PythonOperator(
    task_id="get_data",
    python_callable=_get_data,
    op_kwargs={
        "year": "{{ execution_date.year }}",
        "month": "{{ execution_date.month }}",
        "day": "{{ execution_date.day }}",
        "hour": "{{ execution_date.hour }}",
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
    op_kwargs={"pagenames": PAGENAMES},
    templates_dict={"output_path": f"{OUTPUT_DIR}/{{{{ ds }}}}.csv"},
    dag=dag,
)

add_to_db = PythonOperator(
    task_id="add_to_db",
    python_callable=_add_to_db,
    templates_dict={"output_path": f"{OUTPUT_DIR}/{{{{ ds }}}}.csv"},
    dag=dag,
)

get_data >> extract_gz >> fetch_pageviews >> add_to_db