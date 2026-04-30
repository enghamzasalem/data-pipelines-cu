from pathlib import Path
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


def classify_sentiment(score: float) -> str:
    if score >= 0.05:
        return "positive"
    elif score <= -0.05:
        return "negative"
    return "neutral"


def sentiment_and_merge():
    project_root = Path(__file__).resolve().parent.parent

    gold_file = project_root / "data" / "raw" / "gold_prices.csv"
    rss_news_file = project_root / "data" / "raw" / "nyt_news.csv"
    backfill_news_file = project_root / "data" / "raw" / "nyt_news_backfill.csv"
    processed_dir = project_root / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    output_file = processed_dir / "training_data.csv"

    # Load gold data
    gold_df = pd.read_csv(gold_file)

    # Load news from both sources
    news_frames = []

    if rss_news_file.exists():
        news_frames.append(pd.read_csv(rss_news_file))

    if backfill_news_file.exists():
        news_frames.append(pd.read_csv(backfill_news_file))

    if not news_frames:
        raise ValueError("No news files found. Expected nyt_news.csv and/or nyt_news_backfill.csv")

    news_df = pd.concat(news_frames, ignore_index=True)
    news_df = news_df.drop_duplicates(subset=["link"]).reset_index(drop=True)

    # Parse dates
    gold_df["date"] = pd.to_datetime(gold_df["date"]).dt.date
    news_df["date"] = pd.to_datetime(news_df["date"]).dt.date

    analyzer = SentimentIntensityAnalyzer()

    # Compute sentiment for each article
    news_df["compound"] = news_df["text_for_sentiment"].fillna("").apply(
        lambda text: analyzer.polarity_scores(text)["compound"]
    )

    news_df["sentiment_label"] = news_df["compound"].apply(classify_sentiment)

    # Aggregate by date
    daily_news = news_df.groupby("date").agg(
        news_count=("title", "count"),
        avg_sentiment=("compound", "mean"),
        max_sentiment=("compound", "max"),
        min_sentiment=("compound", "min"),
    ).reset_index()

    # Count positive / negative / neutral per day
    sentiment_counts = pd.crosstab(news_df["date"], news_df["sentiment_label"]).reset_index()

    for col in ["positive", "negative", "neutral"]:
        if col not in sentiment_counts.columns:
            sentiment_counts[col] = 0

    sentiment_counts = sentiment_counts.rename(columns={
        "positive": "positive_count",
        "negative": "negative_count",
        "neutral": "neutral_count"
    })

    daily_news = daily_news.merge(
        sentiment_counts[["date", "positive_count", "negative_count", "neutral_count"]],
        on="date",
        how="left"
    )

    # Merge with gold
    final_df = gold_df.merge(daily_news, on="date", how="left")

    fill_cols = [
        "news_count",
        "avg_sentiment",
        "max_sentiment",
        "min_sentiment",
        "positive_count",
        "negative_count",
        "neutral_count"
    ]
    final_df[fill_cols] = final_df[fill_cols].fillna(0)

    final_df.to_csv(output_file, index=False)

    print(f"Training data saved to: {output_file}")
    print(final_df.head())
    print("Columns:", final_df.columns.tolist())
    print(f"Total rows: {len(final_df)}")


if __name__ == "__main__":
    sentiment_and_merge()