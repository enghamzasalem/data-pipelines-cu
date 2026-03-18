from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from pathlib import Path
import os
import pickle

import feedparser
import pandas as pd
import yfinance as yf
from textblob import TextBlob
from sklearn.linear_model import LogisticRegression


# Change this path if needed
DATA_DIR = Path(os.path.expanduser("~/airflow_data/gold_war_pipeline"))
MODELS_DIR = DATA_DIR / "models"

KEYWORDS = [
    "war",
    "conflict",
    "attack",
    "military",
    "invasion",
    "missile",
    "bomb",
    "troops",
    "battle",
    "strike",
]


def ensure_dirs():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)


def fetch_gold_prices():
    ensure_dirs()

    df = yf.download("GC=F", start="2024-01-01", progress=False)

    if df.empty:
        raise ValueError("No gold price data downloaded")

    df = df.reset_index()

    # Flatten columns if yfinance returns multi-index columns
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

    df.columns = [str(c).lower() for c in df.columns]

    rename_map = {
        "date": "date",
        "open": "open",
        "high": "high",
        "low": "low",
        "close": "close",
    }

    missing = [c for c in ["date", "open", "high", "low", "close"] if c not in df.columns]
    if missing:
        raise ValueError(f"Missing expected gold columns: {missing}")

    gold_df = df[["date", "open", "high", "low", "close"]].copy()
    gold_df["date"] = pd.to_datetime(gold_df["date"]).dt.strftime("%Y-%m-%d")

    gold_df.to_csv(DATA_DIR / "gold_prices.csv", index=False)
    print(f"Saved {DATA_DIR / 'gold_prices.csv'}")


def fetch_war_news():
    ensure_dirs()

    feeds = [
        "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    ]

    rows = []

    for feed_url in feeds:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries:
            title = entry.get("title", "")
            summary = entry.get("summary", "")
            published = entry.get("published", "") or entry.get("pubDate", "")

            text = f"{title} {summary}".lower()

            if not any(keyword in text for keyword in KEYWORDS):
                continue

            try:
                date = pd.to_datetime(published).strftime("%Y-%m-%d")
            except Exception:
                continue

            rows.append(
                {
                    "date": date,
                    "title": title,
                    "summary": summary,
                }
            )

    news_df = pd.DataFrame(rows)

    if news_df.empty:
        # create empty file with correct columns
        news_df = pd.DataFrame(columns=["date", "title", "summary"])

    news_df = news_df.drop_duplicates()
    news_df.to_csv(DATA_DIR / "war_news.csv", index=False)
    print(f"Saved {DATA_DIR / 'war_news.csv'}")


def compute_sentiment_and_merge():
    ensure_dirs()

    gold_path = DATA_DIR / "gold_prices.csv"
    news_path = DATA_DIR / "war_news.csv"

    if not gold_path.exists():
        raise FileNotFoundError(f"Missing file: {gold_path}")

    if not news_path.exists():
        raise FileNotFoundError(f"Missing file: {news_path}")

    gold_df = pd.read_csv(gold_path)
    news_df = pd.read_csv(news_path)

    gold_df["date"] = pd.to_datetime(gold_df["date"])
    gold_df = gold_df.sort_values("date").copy()

    if news_df.empty:
        sentiment_daily = pd.DataFrame(
            {
                "date": gold_df["date"],
                "sentiment_mean": 0.0,
                "news_count": 0,
            }
        )
    else:
        news_df["date"] = pd.to_datetime(news_df["date"])
        news_df["text"] = news_df["title"].fillna("") + " " + news_df["summary"].fillna("")
        news_df["sentiment"] = news_df["text"].apply(lambda x: TextBlob(str(x)).sentiment.polarity)

        sentiment_daily = (
            news_df.groupby("date")
            .agg(
                sentiment_mean=("sentiment", "mean"),
                news_count=("sentiment", "count"),
            )
            .reset_index()
        )

    merged = gold_df.merge(sentiment_daily, on="date", how="left")
    merged["sentiment_mean"] = merged["sentiment_mean"].fillna(0.0)
    merged["news_count"] = merged["news_count"].fillna(0).astype(int)

    merged["next_close"] = merged["close"].shift(-1)
    merged["target"] = (merged["next_close"] > merged["close"]).astype(int)

    training_df = merged[["date", "close", "sentiment_mean", "news_count", "target"]].copy()
    training_df = training_df.iloc[:-1]  # drop last row because next_close is missing
    training_df["date"] = pd.to_datetime(training_df["date"]).dt.strftime("%Y-%m-%d")

    training_df.to_csv(DATA_DIR / "training_data.csv", index=False)
    print(f"Saved {DATA_DIR / 'training_data.csv'}")


def train_model():
    ensure_dirs()

    training_path = DATA_DIR / "training_data.csv"
    if not training_path.exists():
        raise FileNotFoundError(f"Missing file: {training_path}")

    df = pd.read_csv(training_path)

    feature_cols = ["sentiment_mean", "news_count"]
    X = df[feature_cols].fillna(0)
    y = df["target"]

    model = LogisticRegression()
    model.fit(X, y)

    with open(MODELS_DIR / "gold_model.pkl", "wb") as f:
        pickle.dump({"model": model, "features": feature_cols}, f)

    print(f"Saved {MODELS_DIR / 'gold_model.pkl'}")


default_args = {
    "owner": "adithya",
    "start_date": datetime(2024, 1, 1),
}


with DAG(
    dag_id="gold_war_ml_pipeline",
    default_args=default_args,
    schedule="@weekly",
    catchup=False,
    description="Gold price + war news sentiment ML pipeline",
) as dag:

    task_fetch_gold = PythonOperator(
        task_id="fetch_gold_prices",
        python_callable=fetch_gold_prices,
    )

    task_fetch_news = PythonOperator(
        task_id="fetch_war_news",
        python_callable=fetch_war_news,
    )

    task_merge = PythonOperator(
        task_id="compute_sentiment_and_merge",
        python_callable=compute_sentiment_and_merge,
    )

    task_train = PythonOperator(
        task_id="train_model",
        python_callable=train_model,
    )

    [task_fetch_gold, task_fetch_news] >> task_merge >> task_train