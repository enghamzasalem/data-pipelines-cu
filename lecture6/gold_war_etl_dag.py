from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
import yfinance as yf
import feedparser
from textblob import TextBlob
import joblib
import os
from sklearn.ensemble import RandomForestClassifier


DATA_DIR = "data"
MODEL_DIR = "data/models"

os.makedirs(MODEL_DIR, exist_ok=True)





def fetch_gold_prices():
    df = yf.download("GC=F", start="2024-01-01")
    df = df.reset_index()

    df = df[['Date', 'Open', 'High', 'Low', 'Close']]
    df.columns = ['date', 'open', 'high', 'low', 'close']

    df.to_csv(f"{DATA_DIR}/gold_prices.csv", index=False)




def fetch_war_news():
    url = "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"
    feed = feedparser.parse(url)

    keywords = ["war", "attack", "military", "conflict", "invasion"]

    data = []

    for entry in feed.entries:
        text = (entry.title + entry.summary).lower()

        if any(word in text for word in keywords):
            data.append({
                "date": entry.published[:10],
                "title": entry.title,
                "summary": entry.summary
            })

    df = pd.DataFrame(data)
    df.to_csv(f"{DATA_DIR}/war_news.csv", index=False)



def process_data():
    gold = pd.read_csv(f"{DATA_DIR}/gold_prices.csv")
    news = pd.read_csv(f"{DATA_DIR}/war_news.csv")

    news["sentiment"] = news["summary"].apply(
        lambda x: TextBlob(str(x)).sentiment.polarity
    )

    news_grouped = news.groupby("date").agg({
        "sentiment": "mean",
        "title": "count"
    }).reset_index()

    news_grouped.columns = ["date", "sentiment_mean", "news_count"]

    df = pd.merge(gold, news_grouped, on="date", how="left")
    df.fillna(0, inplace=True)

    df["target"] = (df["close"].shift(-1) > df["close"]).astype(int)

    df.dropna(inplace=True)

    df.to_csv(f"{DATA_DIR}/training_data.csv", index=False)




def train_model():
    df = pd.read_csv(f"{DATA_DIR}/training_data.csv")

    X = df[["close", "sentiment_mean", "news_count"]]
    y = df["target"]

    model = RandomForestClassifier()
    model.fit(X, y)

    joblib.dump(model, f"{MODEL_DIR}/gold_model.pkl")



# DAG

with DAG(
    dag_id="gold_war_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule="@weekly",
    catchup=False
) as dag:

    t1 = PythonOperator(
        task_id="get_gold",
        python_callable=fetch_gold_prices
    )

    t2 = PythonOperator(
        task_id="get_news",
        python_callable=fetch_war_news
    )

    t3 = PythonOperator(
        task_id="process_data",
        python_callable=process_data
    )

    t4 = PythonOperator(
        task_id="train_model",
        python_callable=train_model
    )

    [t1, t2] >> t3 >> t4