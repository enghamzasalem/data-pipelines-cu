import yfinance as yf
import pandas as pd
import feedparser
from textblob import TextBlob
from sklearn.ensemble import RandomForestClassifier
import pickle


def fetch_gold_prices():
    df = yf.download("GC=F", start="2024-01-01")
    df.reset_index(inplace=True)
    df = df[["Date", "Open", "High", "Low", "Close"]]
    df.columns = ["date", "open", "high", "low", "close"]

    df.to_csv("data/gold_prices.csv", index=False)
    print("Gold prices saved!")




def fetch_war_news():
    url = "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"
    feed = feedparser.parse(url)

    data = []
    keywords = ["war", "conflict", "attack", "military", "invasion"]

    for entry in feed.entries:
        title = entry.title.lower()
        summary = entry.summary.lower()

        if any(k in title or k in summary for k in keywords):
            data.append({
                "date": entry.published[:10],
                "title": entry.title,
                "summary": entry.summary
            })

    df = pd.DataFrame(data)
    df.to_csv("data/war_news.csv", index=False)

    print("War news saved!")



def compute_sentiment_and_merge():
    gold = pd.read_csv("data/gold_prices.csv")
    news = pd.read_csv("data/war_news.csv")

    # Convert sentiment
    news["sentiment"] = news["summary"].apply(lambda x: TextBlob(x).sentiment.polarity)

    # Group by date
    news_grouped = news.groupby("date").agg({
        "sentiment": "mean",
        "title": "count"
    }).reset_index()

    news_grouped.columns = ["date", "sentiment_mean", "news_count"]

    # Merge with gold data
    merged = pd.merge(gold, news_grouped, on="date", how="left")
    merged.fillna(0, inplace=True)

    # Create target (next day price up/down)
    merged["target"] = (merged["close"].shift(-1) > merged["close"]).astype(int)

    # Save
    merged.to_csv("data/training_data.csv", index=False)

    print("Training data created!")

def train_model():
    df = pd.read_csv("data/training_data.csv")

    # Remove missing values
    df.dropna(inplace=True)

    # Features & target
    X = df[["sentiment_mean", "news_count"]]
    y = df["target"]

    # Train model
    model = RandomForestClassifier()
    model.fit(X, y)

    # Save model
    with open("models/gold_model.pkl", "wb") as f:
        pickle.dump({"model": model, "features": X.columns.tolist()}, f)

    print("Model trained and saved!")


if __name__ == "__main__":
    fetch_gold_prices()
    fetch_war_news()
    compute_sentiment_and_merge()
    train_model()
