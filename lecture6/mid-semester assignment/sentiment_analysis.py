import os
import pandas as pd
from textblob import TextBlob

BASE_DIR = "/Users/subhankarbiswas/data-pipelines-cu/lecture6/gold_war_pipeline"
DATA_DIR = os.path.join(BASE_DIR, "data")

os.makedirs(DATA_DIR, exist_ok=True)

def compute_sentiment():

    news = pd.read_csv(f"{DATA_DIR}/war_news.csv")

    # replace missing summaries
    news["summary"] = news["summary"].fillna("")

    news["sentiment"] = news["summary"].apply(
        lambda x: TextBlob(str(x)).sentiment.polarity
    )

    sentiment_df = news.groupby("date").agg(
        sentiment_mean=("sentiment","mean"),
        sentiment_std=("sentiment","std"),
        news_count=("sentiment","count")
    ).reset_index()

    sentiment_df.fillna(0, inplace=True)

    return sentiment_df