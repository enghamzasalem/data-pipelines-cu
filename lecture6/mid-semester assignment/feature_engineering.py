import os
import pandas as pd
from sentiment_analysis import compute_sentiment

BASE_DIR = "/Users/subhankarbiswas/data-pipelines-cu/lecture6/gold_war_pipeline"
DATA_DIR = os.path.join(BASE_DIR, "data")

os.makedirs(DATA_DIR, exist_ok=True)

def create_features():

    gold = pd.read_csv(f"{DATA_DIR}/gold_prices.csv")

    sentiment = compute_sentiment()

    df = pd.merge(gold, sentiment, on="date", how="left")

    df.fillna(0, inplace=True)

    df["price_change"] = df["close"].pct_change()

    df["rolling_mean_3"] = df["close"].rolling(3).mean()

    df["rolling_mean_7"] = df["close"].rolling(7).mean()

    df["sentiment_lag1"] = df["sentiment_mean"].shift(1)

    df["sentiment_lag2"] = df["sentiment_mean"].shift(2)

    df["target"] = (df["close"].shift(-1) > df["close"]).astype(int)

    df.dropna(inplace=True)

    df.to_csv(f"{DATA_DIR}/training_data.csv", index=False)

    return df