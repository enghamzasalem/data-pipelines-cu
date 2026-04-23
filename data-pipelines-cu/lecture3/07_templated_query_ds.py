import datetime as dt
from datetime import timedelta
from pathlib import Path
import pandas as pd

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator


dag = DAG(
    '07_templated_query_ds',
    schedule=timedelta(days=3),   
    start_date=dt.datetime(2019, 1, 1),
    end_date=dt.datetime(2019, 1, 5),
    catchup=True,
)


fetch_events = BashOperator(
    task_id="fetch_events",
    bash_command="""
        mkdir -p /home/mimou/airflow/data &&
        curl -o /home/mimou/airflow/data/events_{{ ds }}.json
        "http://127.0.0.1:5003/events?start_date={{ ds }}&end_date={{ next_ds }}"
    """,
    dag=dag,
)


def _calculate_stats(input_path, output_path):
    """Calculates event statistics."""

    events = pd.read_json(input_path)

    stats = (
        events.groupby(["date", "user"])
        .size()
        .reset_index(name="count")
    )

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    stats.to_csv(output_path, index=False)


calculate_stats = PythonOperator(
    task_id="calculate_stats",
    python_callable=_calculate_stats,
    op_kwargs={
        "input_path": "/home/mimou/airflow/data/events_{{ ds }}.json",
        "output_path": "/home/mimou/airflow/data/stats_{{ ds }}.csv",
    },
)


fetch_events >> calculate_stats
