"""
Lecture 4 - Exercise: StockSense Wikipedia Pageviews ETL (Airflow 3.x)

Complete ETL pipeline:
get_data → extract_gz → fetch_pageviews → add_to_db

Uses templating and logical_date.
"""

from datetime import datetime
from pathlib import Path

from airflow import DAG

try:
    from airflow.operators.bash import BashOperator
    from airflow.operators.python import PythonOperator
except ImportError:
    from airflow.providers.standard.operators.bash import BashOperator
    from airflow.providers.standard.operators.python import PythonOperator


PAGENAMES = {"Google", "Amazon", "Apple", "Microsoft", "Facebook"}
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "data" / "stocksense" / "pageview_counts"


# -----------------------------------------------------
# TASK 1: Download Wikipedia pageviews (templated)
# -----------------------------------------------------
from urllib import request, error
from pathlib import Path

def _get_data(year, month, day, hour, output_path, **_):
    url = (
        f"https://dumps.wikimedia.org/other/pageviews/"
        f"{year}/{year}-{int(month):02d}/"
        f"pageviews-{year}{int(month):02d}{int(day):02d}-{int(hour):02d}0000.gz"
    )

    # Remove old file if exists
    path = Path(output_path)
    if path.exists():
        path.unlink()

    try:
        request.urlretrieve(url, output_path)
        print("Download successful.")
    except error.HTTPError as e:
        if e.code == 404:
            print("File not available yet.")
            return
        raise


# -----------------------------------------------------
# TASK 2: Parse pageviews + Save CSV
# -----------------------------------------------------
def _fetch_pageviews(pagenames, **context):

    logical_date = context["logical_date"]
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

    with open(output_path, "w") as f:
        f.write("pagename,pageviewcount,datetime\n")
        for pagename, count in result.items():
            f.write(f'"{pagename}",{count},{logical_date}\n')

    print(f"Saved pageview counts to {output_path}")
    print(f"Counts: {result}")

    return result


# -----------------------------------------------------
# TASK 3: Simulated DB Load
# -----------------------------------------------------
def _add_to_db(**context):
    """
    Simulated DB load.
    In production, this would insert into Postgres.
    """

    output_path = context["templates_dict"]["output_path"]

    print(f"Loading data from {output_path} into database...")

    try:
        with open(output_path, "r") as f:
            rows = f.readlines()

        print("Inserted rows:")
        for row in rows[1:]:
            print(f"  {row.strip()}")

    except FileNotFoundError:
        print("CSV not found. Ensure previous task succeeded.")
        raise

    print("Database load complete.")


# -----------------------------------------------------
# DAG Definition
# -----------------------------------------------------
dag = DAG(
    dag_id="lecture4_stocksense_exercise",
    start_date=datetime(2024, 1, 1),
    schedule="@hourly",
    catchup=False,
    max_active_runs=1,
    tags=["lecture4", "exercise", "stocksense", "etl"],
)


# Download task (templated using logical_date)
get_data = PythonOperator(
    task_id="get_data",
    python_callable=_get_data,
    op_kwargs={
    "year": "2024",
    "month": "03",
    "day": "01",
    "hour": "00",
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
