Lecture 6: Mid-Semester Assignment  
Gold Price & War News ML Pipeline

📌 Overview
This project implements an end-to-end data pipeline using Apache Airflow to analyze the relationship between global conflict news and gold price movements.

The pipeline fetches gold price data and war-related news, performs sentiment analysis, and trains a machine learning model to predict whether gold prices will increase or decrease.

---

⚙️ Pipeline Architecture

The pipeline consists of the following steps:

1. Fetch Gold Prices
   - Source: yfinance (`GC=F`)
   - Time range: 2024 to present
   - Output: `gold_prices.csv`

2. Fetch War News
   - Source: New York Times RSS feeds
   - Filters articles related to war, conflict, military, etc.
   - Output: `war_news.csv`

3. Sentiment Analysis & Data Merge
   - Uses TextBlob to compute sentiment polarity
   - Aggregates sentiment per day
   - Merges with gold price data
   - Output: `training_data.csv`

4. Model Training
   - Model: Logistic Regression
   - Features:
     - sentiment_mean
     - news_count
   - Target:
     - 1 → price goes up
     - 0 → price goes down

---

🧠 Machine Learning Model

- Algorithm: Logistic Regression
- Input features:
  - Average daily sentiment
  - Number of news articles
- Output:
  - Binary classification (up/down movement)

---

📊 Model Performance

- Accuracy: **0.587**
- Dataset size: 554 samples
