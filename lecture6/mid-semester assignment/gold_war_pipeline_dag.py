import sys
import os

# Absolute path to your project
PROJECT_ROOT = "/Users/subhankarbiswas/data-pipelines-cu/lecture6/gold_war_pipeline"

# Add project and src folder to Python path
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

from data_ingestion import fetch_gold_prices, fetch_war_news
from feature_engineering import create_features
from model_training import train_models
from model_selection import select_best_model


default_args = {
    "owner": "airflow"
}


def training_pipeline():

    df = create_features()

    results = train_models(df)

    select_best_model(results)


with DAG(
    dag_id="gold_war_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule="@weekly",
    catchup=False,
    default_args=default_args,
    tags=["ml", "gold", "news"],
) as dag:

    fetch_gold_prices_task = PythonOperator(
        task_id="fetch_gold_prices",
        python_callable=fetch_gold_prices,
    )

    fetch_war_news_task = PythonOperator(
        task_id="fetch_war_news",
        python_callable=fetch_war_news,
    )

    train_pipeline_task = PythonOperator(
        task_id="train_pipeline",
        python_callable=training_pipeline,
    )

    [fetch_gold_prices_task, fetch_war_news_task] >> train_pipeline_task