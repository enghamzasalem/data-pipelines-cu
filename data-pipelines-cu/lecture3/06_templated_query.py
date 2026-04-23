import datetime as dt
from pathlib import Path
import pandas as pd

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator


dag = DAG(
    '06_templated_query',
    schedule="@daily",
    start_date=dt.datetime(2019, 1, 1),
    end_date=dt.datetime(2019, 1, 5),
    catchup=True,
)

fetch_events = BashOperator(
    task_id="fetch_events",
    bash_command="""
        mkdir -p /home/mimou/airflow/data &&
        curl -o /home/mimou/airflow/data/events_{{ data_interval_start.strftime('%Y-%m-%d') }}.json \
        "http://127.0.0.1:5003/events?
        start_date={{ data_interval_start.strftime('%Y-%m-%d') }}&
        end_date={{ data_interval_end.strftime('%Y-%m-%d') }}"
    """,
    dag=dag,
)

def _calculate_stats(input_path, output_path):
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    events = pd.read_json(input_path)

    stats = (
        events.groupby(["date", "user"])
        .size()
        .reset_index(name="count")
    )

    stats.to_csv(output_path, index=False)


calculate_stats = PythonOperator(
    task_id="calculate_stats",
    python_callable=_calculate_stats,
    op_kwargs={
        "input_path": "/home/mimou/airflow/data/events_{{ data_interval_start.strftime('%Y-%m-%d') }}.json",
        "output_path": "/home/mimou/airflow/data/stats_{{ data_interval_start.strftime('%Y-%m-%d') }}.csv",
    },
    dag=dag,
)

fetch_events >> calculate_stats
