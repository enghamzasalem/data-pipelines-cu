# Gold Price & War News ML Pipeline

## Overview

This project builds an ETL + ML pipeline that predicts whether the gold price will go up or down based on war-related news sentiment.

The pipeline runs weekly using Apache Airflow.

## Data Sources

Gold prices:
- API: yfinance
- Symbol: GC=F
- Date range: 2024–today

War news:
- Source: NYT RSS feeds
- Feeds used:
  - https://rss.nytimes.com/services/xml/rss/nyt/World.xml
  - https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml

## Pipeline Tasks

1. Fetch gold prices
2. Fetch war-related news
3. Perform sentiment analysis on news
4. Merge with gold price data
5. Train ML model
6. Save best model

## Features

- sentiment_mean
- sentiment_std
- news_count
- price_change
- rolling_mean_3
- rolling_mean_7
- sentiment_lag1
- sentiment_lag2

## Target

1 = next-day gold price increases  
0 = next-day gold price decreases

## Model

Models tested:

- Logistic Regression
- Random Forest
- Gradient Boosting

Best model selected automatically.

Sample model accuracy:

0.58