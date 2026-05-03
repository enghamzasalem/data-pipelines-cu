from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

from datetime import datetime, timedelta
from pathlib import Path

import feedparser
import joblib
import pandas as pd
import yfinance as yf

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from textblob import TextBlob


# -----------------------------------------------------------------------------
# Paths
# -----------------------------------------------------------------------------
DATA_DIR = Path.home() / "airflow" / "data" / "gold_war_pipeline_v3"
MODEL_DIR = DATA_DIR / "models"
SNAPSHOT_DIR = DATA_DIR / "snapshots"

DATA_DIR.mkdir(parents=True, exist_ok=True)
MODEL_DIR.mkdir(parents=True, exist_ok=True)
SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)

GOLD_FILE = DATA_DIR / "gold_prices.csv"
NEWS_FILE = DATA_DIR / "war_news.csv"
TRAIN_FILE = DATA_DIR / "training_data.csv"
LATEST_MODEL_FILE = MODEL_DIR / "gold_model.pkl"

FEATURES = [
    "price_change",
    "ma7",
    "ma14",
    "high_low_diff",
    "open_close_diff",
    "volume",
    "sentiment_mean",
    "news_count",
]

FEEDS = [
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
]

KEYWORDS = ["war", "conflict", "attack", "military", "invasion", "battle", "troops"]


# -----------------------------------------------------------------------------
# Task 1: Fetch gold prices
# -----------------------------------------------------------------------------
def fetch_gold_prices():
    if GOLD_FILE.exists():
        existing = pd.read_csv(GOLD_FILE, parse_dates=["date"])
        last_date = existing["date"].max().normalize()
        next_date = last_date + pd.Timedelta(days=1)

        today = pd.Timestamp.today().normalize()

        if next_date > today:
            print("No new gold price data available (already up to date)")
            return

        print(f"Existing data found. Fetching from {next_date.date()} to {today.date()}")
        new_data = yf.download(
            "GC=F",
            start=next_date.strftime("%Y-%m-%d"),
            end=(today + pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
            progress=False,
        )
    else:
        print("First run. Fetching all data from 2024-01-01")
        new_data = yf.download("GC=F", start="2024-01-01", progress=False)

    if new_data.empty:
        print("No new gold data available")
        return

    new_data = new_data[["Open", "High", "Low", "Close", "Volume"]].reset_index()
    new_data.columns = ["date", "open", "high", "low", "close", "volume"]
    new_data["date"] = pd.to_datetime(new_data["date"]).dt.strftime("%Y-%m-%d")

    if GOLD_FILE.exists():
        existing = pd.read_csv(GOLD_FILE)
        combined = pd.concat([existing, new_data], ignore_index=True)
        combined = combined.drop_duplicates(subset="date").sort_values("date")
        combined.to_csv(GOLD_FILE, index=False)
    else:
        new_data.to_csv(GOLD_FILE, index=False)

    print(f"Saved gold data to: {GOLD_FILE}")


# -----------------------------------------------------------------------------
# Task 2: Fetch war news from NYT RSS
# -----------------------------------------------------------------------------
def fetch_war_news():
    articles = []

    for url in FEEDS:
        feed = feedparser.parse(url)
        print(f"{url} -> {len(feed.entries)} articles received")

        for entry in feed.entries:
            title = entry.get("title", "")
            summary = entry.get("summary", "")
            text = f"{title} {summary}".lower()

            if any(keyword in text for keyword in KEYWORDS):
                try:
                    published = entry.get("published_parsed")
                    date = datetime(*published[:3]).strftime("%Y-%m-%d")
                except Exception:
                    date = datetime.today().strftime("%Y-%m-%d")

                articles.append(
                    {
                        "date": date,
                        "title": title,
                        "summary": summary,
                    }
                )

    if not articles:
        print("No war-related articles found")
        return

    new_df = pd.DataFrame(articles)

    if NEWS_FILE.exists():
        existing = pd.read_csv(NEWS_FILE)
        combined = pd.concat([existing, new_df], ignore_index=True)
        combined = combined.drop_duplicates(subset=["date", "title"])
        combined.to_csv(NEWS_FILE, index=False)
    else:
        new_df.to_csv(NEWS_FILE, index=False)

    print(f"Saved war news to: {NEWS_FILE}")


# -----------------------------------------------------------------------------
# Task 3: Sentiment + merge + feature engineering
# -----------------------------------------------------------------------------
def compute_sentiment_and_merge():
    if not GOLD_FILE.exists():
        raise FileNotFoundError(f"Missing file: {GOLD_FILE}")
    if not NEWS_FILE.exists():
        raise FileNotFoundError(f"Missing file: {NEWS_FILE}")

    gold = pd.read_csv(GOLD_FILE, parse_dates=["date"])
    news = pd.read_csv(NEWS_FILE, parse_dates=["date"])

    def get_sentiment(text):
        return TextBlob(str(text)).sentiment.polarity

    news["text"] = news["title"].fillna("") + " " + news["summary"].fillna("")
    news["sentiment"] = news["text"].apply(get_sentiment)

    news_agg = (
        news.groupby("date")
        .agg(
            sentiment_mean=("sentiment", "mean"),
            news_count=("title", "count"),
        )
        .reset_index()
    )

    merged = pd.merge(gold, news_agg, on="date", how="left")
    merged["sentiment_mean"] = merged["sentiment_mean"].fillna(0)
    merged["news_count"] = merged["news_count"].fillna(0)

    merged = merged.sort_values("date").reset_index(drop=True)

    merged["price_change"] = merged["close"].pct_change()
    merged["ma7"] = merged["close"].rolling(7).mean()
    merged["ma14"] = merged["close"].rolling(14).mean()
    merged["high_low_diff"] = merged["high"] - merged["low"]
    merged["open_close_diff"] = merged["close"] - merged["open"]

    merged["target"] = (merged["close"].shift(-1) > merged["close"]).astype(float)
    merged = merged.dropna().copy()
    merged["target"] = merged["target"].astype(int)

    output = merged[
        [
            "date",
            "price_change",
            "ma7",
            "ma14",
            "high_low_diff",
            "open_close_diff",
            "volume",
            "sentiment_mean",
            "news_count",
            "target",
        ]
    ]

    output.to_csv(TRAIN_FILE, index=False)

    date_str = datetime.today().strftime("%Y%m%d")
    snapshot_path = SNAPSHOT_DIR / f"training_data_{date_str}.csv"
    output.to_csv(snapshot_path, index=False)

    print(f"Saved training data to: {TRAIN_FILE}")
    print(f"Snapshot saved to: {snapshot_path}")
    print(f"Total rows: {len(output)}")


# -----------------------------------------------------------------------------
# Task 4: Train model
# -----------------------------------------------------------------------------
def train_model():
    if not TRAIN_FILE.exists():
        raise FileNotFoundError(f"Missing file: {TRAIN_FILE}")

    df = pd.read_csv(TRAIN_FILE, parse_dates=["date"])
    df = df.sort_values("date").reset_index(drop=True)

    X = df[FEATURES]
    y = df["target"]

    split_idx = int(len(df) * 0.8)
    if split_idx == 0 or split_idx == len(df):
        raise ValueError("Not enough data to perform train/test split.")

    X_train = X.iloc[:split_idx]
    X_test = X.iloc[split_idx:]
    y_train = y.iloc[:split_idx]
    y_test = y.iloc[split_idx:]

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    new_acc = accuracy_score(y_test, preds)
    print(f"New model accuracy: {new_acc:.4f}")

    date_str = datetime.today().strftime("%Y%m%d")
    versioned_model_path = MODEL_DIR / f"gold_model_{date_str}.pkl"
    joblib.dump(model, versioned_model_path)
    print(f"Versioned model saved to: {versioned_model_path}")

    if LATEST_MODEL_FILE.exists():
        old_model = joblib.load(LATEST_MODEL_FILE)
        old_preds = old_model.predict(X_test)
        old_acc = accuracy_score(y_test, old_preds)
        print(f"Old model accuracy: {old_acc:.4f}")

        if new_acc >= old_acc:
            joblib.dump(model, LATEST_MODEL_FILE)
            print("Updated latest gold_model.pkl")
        else:
            print("Kept existing gold_model.pkl")
    else:
        joblib.dump(model, LATEST_MODEL_FILE)
        print(f"First run. Saved latest model to: {LATEST_MODEL_FILE}")


# -----------------------------------------------------------------------------
# Airflow DAG
# -----------------------------------------------------------------------------
default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="gold_war_pipeline_v3",
    default_args=default_args,
    start_date=datetime(2026, 3, 15),
    schedule="@weekly",
    catchup=False,
    tags=["gold", "mid"],
) as dag:

    t1 = PythonOperator(
        task_id="fetch_gold_prices",
        python_callable=fetch_gold_prices,
    )

    t2 = PythonOperator(
        task_id="fetch_war_news",
        python_callable=fetch_war_news,
    )

    t3 = PythonOperator(
        task_id="compute_sentiment_and_merge",
        python_callable=compute_sentiment_and_merge,
    )

    t4 = PythonOperator(
        task_id="train_model",
        python_callable=train_model,
    )

    [t1, t2] >> t3 >> t4