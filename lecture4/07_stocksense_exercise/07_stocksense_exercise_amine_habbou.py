"""
Lecture 4 - Exercise: StockSense Wikipedia Pageviews ETL

Based on listing_4_20 from "Data Pipelines with Apache Airflow" (Chapter 4).

EXERCISE: Complete ETL pipeline that fetches Wikipedia pageviews for tracked
companies and saves to CSV. Uses Jinja templating for dynamic date handling.

Pipeline: get_data → extract_gz → fetch_pageviews → add_to_db

Data source: https://dumps.wikimedia.org/other/pageviews/
Format: domain_code page_title view_count response_size (space-separated)

Run for at least one successful execution, then include the output CSV in your PR.
"""

from pathlib import Path
import csv
import sqlite3
from datetime import datetime, timedelta

import airflow.utils.dates
from airflow import DAG
from airflow.exceptions import AirflowFailException

try:
    from airflow.operators.bash import BashOperator
    from airflow.operators.python import PythonOperator
except ImportError:
    from airflow.providers.standard.operators.bash import BashOperator
    from airflow.providers.standard.operators.python import PythonOperator

PAGENAMES = {"Google", "Amazon", "Apple", "Microsoft", "Facebook"}

OUTPUT_DIR = "/home/amine_apache/airflow/outputs/07_stocksense_exercise"
DB_PATH = "/home/amine_apache/airflow/outputs/07_stocksense_exercise/pageviews.db"


def _get_data(year, month, day, hour, output_path, **context):
    """Download Wikipedia pageviews for the given hour (templated op_kwargs)."""
    from urllib import request
    from urllib.error import HTTPError

    # Try the requested hour
    url = (
        f"https://dumps.wikimedia.org/other/pageviews/"
        f"{year}/{year}-{int(month):02d}/"
        f"pageviews-{year}{int(month):02d}{int(day):02d}-{int(hour):02d}0000.gz"
    )
    print(f"Downloading {url}")

    try:
        request.urlretrieve(url, output_path)
        print(f"Successfully downloaded to {output_path}")

        # Push the REAL data hour to XCom
        data_hour = f"{year}-{month}-{day} {hour}:00:00"
        context["ti"].xcom_push(key="data_hour", value=data_hour)

        return output_path

    except HTTPError as e:
        if e.code == 404:
            # Try 3 hours earlier as fallback
            fallback_time = datetime(
                int(year), int(month), int(day), int(hour), 0
            ) - timedelta(hours=3)
            fallback_year = fallback_time.strftime("%Y")
            fallback_month = fallback_time.strftime("%m")
            fallback_day = fallback_time.strftime("%d")
            fallback_hour = fallback_time.strftime("%H")

            fallback_url = (
                f"https://dumps.wikimedia.org/other/pageviews/"
                f"{fallback_year}/{fallback_year}-{int(fallback_month):02d}/"
                f"pageviews-{fallback_year}{int(fallback_month):02d}{int(fallback_day):02d}-{int(fallback_hour):02d}0000.gz"
            )
            print(f"Trying fallback: {fallback_url}")

            try:
                request.urlretrieve(fallback_url, output_path)
                print(f"Successfully downloaded fallback data")

                # Push the FALLBACK data hour to XCom
                data_hour = f"{fallback_year}-{fallback_month}-{fallback_day} {fallback_hour}:00:00"
                context["ti"].xcom_push(key="data_hour", value=data_hour)

                return output_path

            except HTTPError as e2:
                if e2.code == 404:
                    raise AirflowFailException(
                        f"File not found at {url} or {fallback_url}. Wikipedia data takes 2-3 hours to appear."
                    )
                else:
                    raise
        else:
            raise


def _fetch_pageviews(pagenames, execution_date, **context):
    """
    Parse pageviews file, extract counts for tracked companies, save to CSV.
    execution_date is injected by Airflow from task context.
    output_path comes from templates_dict (date-partitioned path).
    """
    result = dict.fromkeys(pagenames, 0)

    input_file = "/tmp/wikipageviews"
    if not Path(input_file).exists():
        raise FileNotFoundError(f"{input_file} not found")

    with open(input_file, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 4:
                domain_code, page_title, view_count = parts[0], parts[1], parts[2]
                if domain_code == "en" and page_title in pagenames:
                    result[page_title] = int(view_count)

    # Get the REAL data hour from XCom
    ti = context["ti"]
    data_hour = ti.xcom_pull(task_ids="get_data", key="data_hour")

    if not data_hour:
        # Fallback to execution_date if XCom fails
        data_hour = execution_date
        print(f"Warning: Using execution_date as fallback: {data_hour}")

    output_path = context["templates_dict"]["output_path"]
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    file_exists = Path(output_path).exists()
    with open(output_path, "a") as f:
        if not file_exists:
            f.write("pagename,pageviewcount,datetime\n")
        for pagename, count in result.items():
            f.write(f'"{pagename}",{count},{data_hour}\n')  # Using REAL data hour!

    print(f"Saved pageview counts to {output_path} for data hour: {data_hour}")
    return result


def _add_to_db(**context):
    """Add pageview counts to SQLite database."""
    output_path = context["templates_dict"]["output_path"]

    if not Path(output_path).exists():
        raise FileNotFoundError(f"CSV file not found at {output_path}")

    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS pageview_counts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pagename TEXT NOT NULL,
            pageviewcount INTEGER NOT NULL,
            datetime TEXT NOT NULL
        )
    """
    )
    conn.commit()

    cursor.execute("SELECT datetime, pagename FROM pageview_counts")
    existing = set((row[0], row[1]) for row in cursor.fetchall())

    rows_inserted = 0
    with open(output_path, "r") as csvfile:
        csv_reader = csv.reader(csvfile)
        next(csv_reader)

        for row in csv_reader:
            if len(row) >= 3:
                pagename = row[0].strip('"')
                pageviewcount = int(row[1])
                datetime_val = row[2]

                if (datetime_val, pagename) not in existing:
                    cursor.execute(
                        """
                        INSERT INTO pageview_counts (pagename, pageviewcount, datetime)
                        VALUES (?, ?, ?)
                    """,
                        (pagename, pageviewcount, datetime_val),
                    )
                    rows_inserted += 1

    conn.commit()
    conn.close()
    print(f"Inserted {rows_inserted} rows into database")


dag = DAG(
    dag_id="lecture4_stocksense_exercise",
    start_date=datetime(2026, 2, 24),
    schedule="@hourly",
    catchup=True,
    max_active_runs=1,
    tags=["lecture4", "exercise", "stocksense", "etl"],
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
    },
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
