import datetime as dt
from pathlib import Path

import pandas as pd

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

dag = DAG(
    '08_templated_path',
    schedule="@daily",
    start_date=dt.datetime(year=2019, month=1, day=1),
    end_date=dt.datetime(year=2019, month=1, day=5),
    catchup=True,
)

fetch_events = BashOperator(
    task_id='fetch_events',
    bash_command="""
        mkdir -p /home/mimou/airflow/data &&
        curl -o /home/mimou/airflow/data/events_{{ ds }}.json
        "http://127.0.0.1:5003/events?
        start_date={{ ds }}&end_date={{ (execution_date + macros.timedelta(days=1)).strftime('%Y-%m-%d') }}"
    """,
    dag=dag,
)

def _calculate_stats(**context):
    """Calculates event statistics."""
    input_path = context["templates_dict"]["input_path"]
    output_path = context["templates_dict"]["output_path"]

    events = pd.read_json(input_path)
    stats = events.groupby(["date", "user"]).size().reset_index()

    Path(output_path).parent.mkdir(exist_ok=True)
    stats.to_csv(output_path, index=False)


calculate_stats = PythonOperator(
    task_id="calculate_stats",
    python_callable=_calculate_stats,
    templates_dict={        
        "input_path": "/home/mimou/airflow/data/events_{{ ds }}.json",
        "output_path": "/home/mimou/airflow/data/stats_{{ ds }}.csv",
    },
    dag=dag,
)


fetch_events >> calculate_stats
