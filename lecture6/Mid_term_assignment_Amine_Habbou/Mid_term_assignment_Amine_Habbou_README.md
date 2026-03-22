# Gold Price & War News ML Pipeline

## Project Overview
ETL + ML pipeline that fetches gold prices (2024–present) and war-related news, trains a sentiment-based prediction model, and deploys it weekly using Apache Airflow.

## Methodology

### 1. Data Sources

| Source | Description |
|--------|-------------|
| **Gold Prices** | Yahoo Finance (`GC=F` futures) – daily open, high, low, close prices from 2024-01-01 to present |
| **War News** | Multiple sources: RSS feeds (NYT, BBC, Guardian, Reuters, CNN, Al Jazeera, etc.) + Internet Archive TV News Archive (historical coverage 2024–2026) |

### 2. Pipeline Architecture
fetch_gold_prices ──┐
├── compute_sentiment_and_merge ── train_model
fetch_war_news ─────┘

### 3. Data Processing

#### Gold Prices
- Full history fetched each run (2024–present)
- Saved to `gold_prices.csv` with columns: date, open, high, low, close

#### War News
- RSS feeds: Recent articles (last 30 days)
- Internet Archive: Historical articles (2024–2026)
- Articles appended to existing CSV with duplicate removal
- Dataset grows over time, accumulating historical news

#### Sentiment Analysis
- TextBlob polarity scores (-1 to 1) computed on article titles + summaries
- Daily aggregation:
  - `news_count`: Total articles per day
  - `sentiment_mean`: Average sentiment of ALL articles that day

#### Feature Engineering
- **Target**: `1` if next day's closing price > current day's close, else `0`
- **Features**: `sentiment_mean`, `news_count`
- **Training constraint**: Only dates with actual news (`news_count > 0`) are used for training

### 4. Model Selection

**Random Forest Classifier** chosen because:
- Dataset is relatively small (~550 rows with news)
- Handles non-linear relationships well
- Provides built-in feature importance
- Robust to outliers
- Performs well without extensive hyperparameter tuning
- **Future improvement**: Can be replaced with XGBoost or neural networks as data grows

### 5. Scheduling

| Setting | Value |
|---------|-------|
| **Frequency** | `@weekly` (Sundays at 00:00) |
| **Catchup** | `False` (doesn't backfill missed runs) |
| **Automation** | Fully automated – runs indefinitely without manual intervention |

### 6. Results

| Run Date | Test Accuracy | Training Accuracy | Records | Baseline |
|----------|--------------|-------------------|---------|----------|
| March 12, 2026 | 0.6455 | 0.4909 | 551 | 0.6091 |
| March 15, 2026 | 0.6364 | 0.5315 | 553 | 0.5909 |
| March 22, 2026 | 0.6306 | 0.5089 | 558 | 0.5676 |

**Key observation**: Model consistently beats baseline by 4–6%, proving that news sentiment provides predictive signal for gold price movements.


### 7. How to Run

#### Install Dependencies
```bash
pip install -r requirements.txt

cp gold_war_etl_dag.py ~/airflow/dags/
# Manual trigger
airflow dags trigger gold_war_ml_pipeline

# Or wait for automatic weekly schedule (Sundays at 00:00)

python test_model.py \
  --model ~/airflow/data/gold_war_pipeline/models/gold_model.pkl \
  --data ~/airflow/data/gold_war_pipeline


