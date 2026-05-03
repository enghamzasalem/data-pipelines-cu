# Gold Price & War News ML Pipeline

## Project Overview
An automated ETL + ML pipeline that collects gold prices (2024–present) and war-related news, performs sentiment analysis, and trains a prediction model. The entire pipeline is orchestrated using Apache Airflow and runs on a weekly schedule.

## Methodology

### 1. Data Sources

| Source | Description |
|--------|-------------|
| **Gold Prices** | Yahoo Finance (`GC=F`) – daily open, high, low, close, volume from 2024-01-01 |
| **War News** | RSS feeds (NYT, BBC) filtered by war-related keywords |

### 2. Pipeline Architecture
[fetch gold prices] and [fetch war news] --> compute sentiment and merge --> train model

### 3. Data Processing

#### Gold Prices
- Data is fetched incrementally using Yahoo Finance (`GC=F`)
- If previous data exists, only new dates are downloaded
- Stored in `gold_prices.csv` with columns:
  - date, open, high, low, close, volume

#### War News
- News collected from RSS feeds (NYT, BBC)
- Articles filtered using war-related keywords (e.g., war, conflict, attack)
- Duplicate articles removed based on date and title
- Stored in `war_news.csv`

#### Sentiment Analysis
- TextBlob polarity score (-1 to 1) applied to title + summary
- Daily aggregation:
  - `sentiment_mean`: average sentiment per day
  - `news_count`: number of articles per day

#### Feature Engineering
- Target:
  - `1` if next day's closing price > current day's close, else `0`
- Features:
  - `price_change`
  - `ma7`, `ma14`
  - `high_low_diff`
  - `open_close_diff`
  - `volume`
  - `sentiment_mean`
  - `news_count`
- Missing sentiment/news values are filled with 0
- Rolling features introduce NaNs, which are removed before training

### 4. Model

**Random Forest Classifier**

Chosen because:
- Dataset size is relatively small (~500 rows)
- Handles non-linear relationships between price and sentiment features
- Robust to noise and outliers
- Works well without extensive hyperparameter tuning

#### Training Strategy
- Data sorted by date
- Time-based split:
  - 80% training
  - 20% testing
- No shuffling (to preserve temporal order)

#### Model Management
- Versioned model saved with timestamp:
  - `gold_model_YYYYMMDD.pkl`
- Best model saved as:
  - `gold_model.pkl`
- Model updated only if new accuracy ≥ previous accuracy

### 5. Scheduling

| Setting | Value |
|---------|-------|
| **Frequency** | `@weekly` (Sundays at 01:00) |
| **Catchup** | `False`|
| **Automation** | Fully automated|

### 6. Results

| Run Date | Version | Accuracy |
|----------|--------|----------|
| March 15, 2026 | v1 | 0.5321 |
| March 17, 2026 | v1 | 0.5872 |
| March 23, 2026 | v1 | 0.5091 |
| March 23, 2026 | v2 | 0.5545 |

**Key observation**:
- Performance degraded in v1 as new data was added, indicating a potential issue in the training setup.
- After fixing data leakage (v2), initial accuracy improved.
- However, further validation over multiple future runs is required to confirm long-term stability.

**Final submission uses the improved v2 pipeline (data leakage fixed).**

### 7. Troubleshooting

#### Issue: Accuracy dropped after adding new weekly data

Initially, the model showed unstable performance when new data was appended weekly.  
Based on the analysis, the issue was likely caused by **data leakage**.

#### Previous approach (v1)
- The dataset was randomly split into training and test sets using `train_test_split`.
- This ignored the temporal order of the data.
- As a result, future data points could be included in the training set while earlier data appeared in the test set.

#### Problem
- The use of random train-test split caused data leakage in time-series data
- Future information was unintentionally used during training
- This led to overly optimistic and unstable performance

#### Solution
- Data sorted by date
- Time-based split applied instead of random split
- Target shifted to predict next day's price (`t+1`)
- Ensured that only past information is used for prediction

#### Result
- Initial accuracy increased
- However, long-term performance has not yet been fully validated

**Note**:
- Using the full training dataset, the model achieved an accuracy of 0.5545.
- However, when evaluated using the required 20-row sample dataset (as specified in the submission guidelines), the accuracy was 1.0000.

