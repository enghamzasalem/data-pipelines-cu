import datetime as dt
from pathlib import Path

import pandas as pd
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

dag = DAG(
    '04_time_delta',
    schedule=dt.timedelta(days=3),  
    start_date=dt.datetime(year=2019, month=1, day=1),
    end_date=dt.datetime(year=2019, month=1, day=11),
    catchup=True,  
)


fetch_events = BashOperator(
    task_id="fetch_events",
    bash_command="""
      mkdir -p ~/airflow/data
      curl -o ~/airflow/data/events.json http://127.0.0.1:5003/events
    """,
    dag=dag,
)

def _calculate_stats(input_path, output_path, ds=None, **kwargs):
    """
    Calculates event statistics for the DAG run date only.
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    events = pd.read_json(input_path)

    if ds is not None:
        events = events[events["date"] == ds]

    stats = events.groupby(["date", "user"]).size().reset_index(name="count")
    stats.to_csv(output_path, index=False)

calculate_stats = PythonOperator(
    task_id="calculate_stats",
    python_callable=_calculate_stats,
    op_kwargs={
        "input_path": "/home/mimou/airflow/data/events.json",
        "output_path": "/home/mimou/airflow/data/stats4.csv",
    },
    dag=dag,
)


fetch_events >> calculate_stats
