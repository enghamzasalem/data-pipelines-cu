# Mid-Semester Assignment - Gold Price & War News ML Pipeline

This project implements an ETL + ML pipeline using Apache Airflow to predict whether the next-day gold price will go up or down based on war-related news sentiment.

## Data Sources
- **Gold prices:** Yahoo Finance (`GC=F`)
- **War news:** New York Times RSS feeds
- **Historical backfill:** Official New York Times historical data was used to cover the 2024-to-today requirement, while NYT RSS is used for the recurring pipeline updates

## Pipeline Tasks
1. Fetch gold prices from 2024-01-01 to today
2. Fetch war-related NYT news
3. Compute sentiment from article text
4. Aggregate daily sentiment features
5. Merge sentiment features with gold prices
6. Create target variable (`1 = next-day price up`, `0 = down`)
7. Train a classification model
8. Save the trained model

## Airflow DAG
- **DAG file:** `gold_war_etl_dag.py`
- **DAG id:** `gold_war_pipeline`
- **Schedule:** `@weekly`

## Model
- **Model type:** Logistic Regression
- **Saved model file:** `gold_model.pkl`

## Submitted Files
- `gold_war_etl_dag.py`
- `test_model.py`
- `gold_model.pkl`
- `gold_prices_sample.csv`
- `war_news_sample.csv`
- `training_data_sample.csv`
- `MID_SEMESTER_ASSIGNMENT_README.md`
- `requirements.txt`

## Additional Source Files
- `src/fetch_gold_prices.py`
- `src/fetch_nyt_news.py`
- `src/fetch_nyt_backfill.py`
- `src/sentiment_and_merge.py`
- `src/train_model.py`

## How to Run
Install dependencies:

```bash
pip install -r requirements.txt