from datetime import datetime

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator

PROJECT_DIR = "/home/dshan/midterm_gold_pipeline"
PYTHON_BIN = "/home/dshan/midterm_gold_pipeline/.venv/bin/python"

with DAG(
    dag_id="gold_war_pipeline",
    description="Fetch gold prices, fetch NYT war news, compute sentiment, and train model",
    start_date=datetime(2026, 3, 23),
    schedule="@weekly",
    catchup=False,
    tags=["midterm", "gold", "nyt", "ml"],
) as dag:

    fetch_gold_prices = BashOperator(
        task_id="fetch_gold_prices",
        bash_command=f"cd {PROJECT_DIR} && {PYTHON_BIN} src/fetch_gold_prices.py",
    )

    fetch_nyt_news = BashOperator(
        task_id="fetch_nyt_news",
        bash_command=f"cd {PROJECT_DIR} && {PYTHON_BIN} src/fetch_nyt_news.py",
    )

    sentiment_and_merge = BashOperator(
        task_id="sentiment_and_merge",
        bash_command=f"cd {PROJECT_DIR} && {PYTHON_BIN} src/sentiment_and_merge.py",
    )

    train_model = BashOperator(
        task_id="train_model",
        bash_command=f"cd {PROJECT_DIR} && {PYTHON_BIN} src/train_model.py",
    )

    fetch_gold_prices >> fetch_nyt_news >> sentiment_and_merge >> train_model