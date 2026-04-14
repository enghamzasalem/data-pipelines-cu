import sys
sys.path.append("/mnt/c/Users/joshi/Downloads/gold_war_pipeline")

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

# Import your functions
from lecture6_gold_war_pipeline.gold_war_etl import (
    fetch_gold_prices,
    fetch_war_news,
    compute_sentiment_and_merge,
    train_model
)

# Default args
default_args = {
    "start_date": datetime(2024, 1, 1),
}

# Create DAG
dag = DAG(
    "gold_war_pipeline",
    default_args=default_args,
    schedule="@weekly",
    catchup=False
)

# Tasks
t1 = PythonOperator(
    task_id="fetch_gold_prices",
    python_callable=fetch_gold_prices,
    dag=dag
)

t2 = PythonOperator(
    task_id="fetch_war_news",
    python_callable=fetch_war_news,
    dag=dag
)

t3 = PythonOperator(
    task_id="compute_sentiment",
    python_callable=compute_sentiment_and_merge,
    dag=dag
)

t4 = PythonOperator(
    task_id="train_model",
    python_callable=train_model,
    dag=dag
)

# Task flow
[t1, t2] >> t3 >> t4
