"""
Gold Price & War News ML Pipeline
ETL + ML pipeline that fetches gold prices and war news, trains a sentiment-based prediction model
"""

from datetime import datetime, timedelta
import os
import sys
import pandas as pd
import numpy as np
import yfinance as yf
import feedparser
import requests
import time
from textblob import TextBlob
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import logging
import re
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration - Direct to airflow/data directory
DATA_DIR = os.path.expanduser("~/airflow/data/gold_war_pipeline")
MODEL_DIR = os.path.join(DATA_DIR, "models")
GOLD_PRICES_FILE = os.path.join(DATA_DIR, "gold_prices.csv")
WAR_NEWS_FILE = os.path.join(DATA_DIR, "war_news.csv")
TRAINING_DATA_FILE = os.path.join(DATA_DIR, "training_data.csv")
MODEL_FILE = os.path.join(MODEL_DIR, "gold_model.pkl")

# Create directories if they don't exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)
logger.info(f"Using data directory: {DATA_DIR}")

# War-related keywords for filtering news
WAR_KEYWORDS = [
    "war",
    "conflict",
    "attack",
    "military",
    "invasion",
    "troops",
    "missile",
    "bomb",
    "strike",
    "combat",
    "rebel",
    "insurgent",
    "terror",
    "explosion",
    "ceasefire",
    "artillery",
    "tank",
    "soldier",
    "casualty",
    "death toll",
    "refugee",
    "displaced",
    "escalation",
    "hostility",
    "battle",
    "offensive",
    "assault",
    "ambush",
    "raid",
    "hezbollah",
    "hamas",
    "israel",
    "gaza",
    "ukraine",
    "russia",
    "iran",
]

# RSS Feeds (completely free, no API keys needed) - CBC REMOVED
RSS_FEEDS = [
    {
        "name": "NYT World",
        "url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    },
    {
        "name": "NYT Home",
        "url": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    },
    {"name": "BBC World", "url": "http://feeds.bbci.co.uk/news/world/rss.xml"},
    {"name": "The Guardian", "url": "https://www.theguardian.com/world/rss"},
    {"name": "Reuters", "url": "https://feeds.reuters.com/reuters/worldnews"},
    {"name": "CNN World", "url": "https://rss.cnn.com/rss/edition_world.rss"},
    {"name": "Al Jazeera", "url": "https://www.aljazeera.com/xml/rss/all.xml"},
    {"name": "France24", "url": "https://www.france24.com/en/rss"},
    {"name": "DW News", "url": "https://rss.dw.com/xyz/rdf-en-world"},
    {
        "name": "ABC News",
        "url": "https://abcnews.go.com/abcnews/internationalheadlines",
    },
    {"name": "Independent", "url": "https://www.independent.co.uk/news/world/rss"},
    {"name": "Sky News", "url": "https://feeds.skynews.com/feeds/rss/world.xml"},
    {"name": "RT News", "url": "https://www.rt.com/rss/news/"},
    {"name": "South China Morning Post", "url": "https://www.scmp.com/rss/4/feed"},
    {"name": "The Telegraph", "url": "https://www.telegraph.co.uk/news/worldnews/rss"},
]

# GDELT DISABLED - REMOVED
GDELT_ENABLED = False

# Internet Archive's TV News Archive - Free
INTERNET_ARCHIVE_ENABLED = True

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "start_date": datetime(2024, 1, 1),
}


def fetch_gold_prices(**context):
    """
    Fetch gold prices from 2024-01-01 to today using yfinance
    """
    logger.info("Starting to fetch gold prices...")
    ti = context["ti"]

    try:
        # Fetch gold futures data
        gold = yf.Ticker("GC=F")

        # Get data from 2024-01-01 to today
        start_date = "2024-01-01"
        end_date = datetime.now().strftime("%Y-%m-%d")

        df = gold.history(start=start_date, end=end_date)

        if df.empty:
            raise ValueError("No gold price data retrieved")

        # Reset index to make date a column
        df = df.reset_index()

        # Rename columns to match requirements
        df = df.rename(
            columns={
                "Date": "date",
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
            }
        )

        # Keep only required columns
        df = df[["date", "open", "high", "low", "close"]]

        # Format date as YYYY-MM-DD
        df["date"] = df["date"].dt.strftime("%Y-%m-%d")

        # Save to CSV
        df.to_csv(GOLD_PRICES_FILE, index=False)
        logger.info(f"Saved {len(df)} gold price records to {GOLD_PRICES_FILE}")

        # Push to XCom for downstream tasks
        ti.xcom_push(key="gold_count", value=len(df))

        return len(df)

    except Exception as e:
        logger.error(f"Error fetching gold prices: {str(e)}")
        raise


def is_war_related(text):
    """
    Check if text contains war-related keywords
    """
    if pd.isna(text) or not isinstance(text, str):
        return False

    text_lower = text.lower()
    for keyword in WAR_KEYWORDS:
        if keyword in text_lower:
            return True
    return False


def fetch_from_rss_feeds():
    """
    Fetch war-related news from all RSS feeds
    """
    logger.info("=" * 60)
    logger.info("SOURCE 1: RSS FEEDS")
    logger.info("=" * 60)

    all_articles = []

    for feed in RSS_FEEDS:
        feed_count = 0
        try:
            logger.info(f"Fetching from {feed['name']}: {feed['url']}")
            feed_data = feedparser.parse(feed["url"])

            if not feed_data.entries:
                logger.warning(f"  → No entries from {feed['name']}")
                continue

            for entry in feed_data.entries[:30]:
                title = entry.get("title", "")
                summary = entry.get("summary") or entry.get("description") or ""

                if is_war_related(f"{title} {summary}"):
                    # Extract date
                    pub_date = None
                    if hasattr(entry, "published_parsed") and entry.published_parsed:
                        pub_date = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                        pub_date = datetime(*entry.updated_parsed[:6])

                    if pub_date:
                        date_str = pub_date.strftime("%Y-%m-%d")
                    else:
                        date_str = datetime.now().strftime("%Y-%m-%d")

                    all_articles.append(
                        {
                            "date": date_str,
                            "title": title,
                            "summary": summary[:500] + "..."
                            if len(summary) > 500
                            else summary,
                            "source": feed["name"],
                            "url": entry.get("link", ""),
                        }
                    )
                    feed_count += 1

            logger.info(
                f"  → Found {feed_count} war-related articles from {feed['name']}"
            )

        except Exception as e:
            logger.error(f"Error with {feed['name']}: {str(e)}")

    logger.info(f"Total RSS articles: {len(all_articles)}")
    return all_articles


def fetch_from_internet_archive():
    """
    Fetch from Internet Archive's TV News Archive - GETS ALL ITEMS
    """
    logger.info("=" * 60)
    logger.info("SOURCE 2: INTERNET ARCHIVE TV NEWS (GETTING ALL ITEMS)")
    logger.info("=" * 60)

    if not INTERNET_ARCHIVE_ENABLED:
        logger.info("Internet Archive fetching disabled")
        return []

    all_articles = []
    total_items_found = 0

    base_url = "https://archive.org/services/search/v1/scrape"

    for year in range(2024, 2027):
        for month in range(1, 13):
            if year == datetime.now().year and month > datetime.now().month:
                break

            date_str = f"{year}-{month:02d}"
            month_articles = []

            params = {
                "q": f'collection:tvnews AND ({ " OR ".join(WAR_KEYWORDS[:5]) }) AND date:{date_str}',
                "fields": "title,description,date,identifier",
                "count": 10000,  # Ask for more items
            }

            try:
                logger.info(f"Fetching Internet Archive for {date_str}")
                response = requests.get(base_url, params=params, timeout=60)

                if response.status_code == 200:
                    data = response.json()
                    items = data.get("items", [])
                    total_items_found += len(items)

                    logger.info(f"  → Found {len(items)} items for {date_str}")

                    for item in items:
                        item_date = item.get("date", "")
                        if item_date and len(item_date) >= 10:
                            formatted_date = item_date[:10]
                        else:
                            formatted_date = f"{year}-{month:02d}-01"

                        title = item.get("title", "")
                        description = item.get("description", "")

                        # Only include if war-related
                        if is_war_related(f"{title} {description}"):
                            month_articles.append(
                                {
                                    "date": formatted_date,
                                    "title": title,
                                    "summary": description[:500] + "..."
                                    if len(description) > 500
                                    else description,
                                    "source": "Internet Archive",
                                    "url": f"https://archive.org/details/{item.get('identifier', '')}",
                                }
                            )

                    logger.info(
                        f"    → After war filtering: {len(month_articles)} articles"
                    )
                    all_articles.extend(month_articles)

                else:
                    logger.warning(
                        f"  → Internet Archive returned {response.status_code}"
                    )

            except Exception as e:
                logger.error(f"Error with Internet Archive for {date_str}: {str(e)}")

            time.sleep(2)

    logger.info(f"Total Internet Archive items found (raw): {total_items_found}")
    logger.info(
        f"Total Internet Archive articles after war filtering: {len(all_articles)}"
    )

    # Show sample of what we got
    if all_articles:
        logger.info("Sample Internet Archive articles:")
        for i, article in enumerate(all_articles[:5]):
            logger.info(f"  {i+1}. {article['date']}: {article['title'][:50]}...")

    return all_articles


def fetch_war_news(**context):
    """
    Fetch war-related news from all free sources - GETS ALL ARTICLES
    """
    logger.info("=" * 60)
    logger.info("FETCHING WAR NEWS FROM ALL SOURCES")
    logger.info("=" * 60)
    ti = context["ti"]

    all_articles = []

    # Source 1: RSS Feeds
    rss_articles = fetch_from_rss_feeds()
    all_articles.extend(rss_articles)
    logger.info(f"RSS total: {len(rss_articles)} articles")

    # Source 2: Internet Archive
    ia_articles = fetch_from_internet_archive()
    all_articles.extend(ia_articles)
    logger.info(f"Internet Archive total: {len(ia_articles)} articles")

    logger.info(f" TOTAL RAW ARTICLES FROM ALL SOURCES: {len(all_articles)}")

    if len(all_articles) == 0:
        logger.warning("No articles found from any source!")
        if not os.path.exists(WAR_NEWS_FILE):
            pd.DataFrame(columns=["date", "title", "summary", "source", "url"]).to_csv(
                WAR_NEWS_FILE, index=False
            )
        ti.xcom_push(key="news_count", value=0)
        return 0

    # Convert to DataFrame
    new_df = pd.DataFrame(all_articles)
    logger.info(f"DataFrame created with {len(new_df)} rows")

    # Remove duplicates
    before_dedup = len(new_df)
    new_df = new_df.drop_duplicates(subset=["title", "date"])
    logger.info(f"After removing duplicates: {before_dedup} → {len(new_df)} articles")

    # Standardize date format
    new_df["date"] = pd.to_datetime(new_df["date"]).dt.strftime("%Y-%m-%d")

    # Load existing news if any
    if os.path.exists(WAR_NEWS_FILE):
        try:
            existing_df = pd.read_csv(WAR_NEWS_FILE)
            logger.info(
                f"Loaded {len(existing_df)} existing articles from {WAR_NEWS_FILE}"
            )

            if not existing_df.empty:
                existing_df["date"] = pd.to_datetime(existing_df["date"]).dt.strftime(
                    "%Y-%m-%d"
                )

                # Combine
                combined_df = pd.concat([existing_df, new_df])
                combined_df = combined_df.drop_duplicates(subset=["title", "date"])
                logger.info(f"Combined: {len(combined_df)} total articles")
            else:
                combined_df = new_df
        except Exception as e:
            logger.error(f"Error loading existing: {e}")
            combined_df = new_df
    else:
        combined_df = new_df
        logger.info(f"No existing file, using {len(combined_df)} new articles")

    # Sort by date (oldest first)
    combined_df = combined_df.sort_values("date", ascending=True)

    # Save
    combined_df.to_csv(WAR_NEWS_FILE, index=False)
    logger.info(f"Saved {len(combined_df)} articles to {WAR_NEWS_FILE}")

    # Show detailed stats
    logger.info("=" * 60)
    logger.info("FINAL NEWS DATASET STATISTICS:")
    logger.info(f"Total articles: {len(combined_df)}")
    logger.info(
        f"Date range: {combined_df['date'].min()} to {combined_df['date'].max()}"
    )

    # Count by source
    if "source" in combined_df.columns:
        source_counts = combined_df["source"].value_counts()
        logger.info("Articles by source:")
        for source, count in source_counts.items():
            logger.info(f"  {source}: {count}")

    # Count by year
    combined_df["year"] = pd.to_datetime(combined_df["date"]).dt.year
    year_counts = combined_df["year"].value_counts().sort_index()
    logger.info("Articles by year:")
    for year, count in year_counts.items():
        logger.info(f"  {year}: {count} articles")

    # Show first few rows
    logger.info("\nFirst 5 articles in CSV (oldest):")
    for idx, row in combined_df.head().iterrows():
        logger.info(f"  {row['date']}: {row['title'][:50]}...")

    logger.info("=" * 60)

    ti.xcom_push(key="news_count", value=len(combined_df))
    return len(combined_df)


def compute_sentiment(text):
    """
    Compute sentiment polarity of text using TextBlob
    """
    if pd.isna(text) or not isinstance(text, str):
        return 0.0
    try:
        return TextBlob(text).sentiment.polarity
    except:
        return 0.0


def compute_sentiment_and_merge(**context):
    """
    Compute sentiment for news, merge with gold prices, create target variable
    ALL articles for a date are included in both count AND average sentiment
    """
    logger.info("Computing sentiment and merging data...")
    ti = context["ti"]

    # Load gold prices
    if not os.path.exists(GOLD_PRICES_FILE):
        raise FileNotFoundError(f"Gold prices file not found: {GOLD_PRICES_FILE}")

    gold_df = pd.read_csv(GOLD_PRICES_FILE)
    gold_df["date"] = pd.to_datetime(gold_df["date"])
    logger.info(
        f"Gold prices: {len(gold_df)} records from {gold_df['date'].min().date()} to {gold_df['date'].max().date()}"
    )

    # Load war news
    if not os.path.exists(WAR_NEWS_FILE):
        raise FileNotFoundError(f"War news file not found: {WAR_NEWS_FILE}")

    news_df = pd.read_csv(WAR_NEWS_FILE)

    if news_df.empty:
        logger.warning(
            "No news data available. Creating training data with gold prices only."
        )
        training_df = gold_df.copy()
        training_df = training_df.sort_values("date")
        training_df["target"] = (
            training_df["close"].shift(-1) > training_df["close"]
        ).astype(int)
        training_df = training_df.dropna()
        training_df["sentiment_mean"] = 0.0
        training_df["news_count"] = 0
        training_df = training_df[
            ["date", "close", "sentiment_mean", "news_count", "target"]
        ]
    else:
        logger.info(f"Loaded {len(news_df)} news articles")
        logger.info(
            f"News date range: {news_df['date'].min()} to {news_df['date'].max()}"
        )

        # Convert dates
        news_df["date"] = pd.to_datetime(news_df["date"])

        # Filter to 2024 onwards
        news_df = news_df[news_df["date"] >= "2024-01-01"]
        logger.info(f"After filtering: {len(news_df)} articles")

        # Show year distribution
        news_df["year"] = news_df["date"].dt.year
        year_counts = news_df["year"].value_counts().sort_index()
        logger.info("Articles by year:")
        for year, count in year_counts.items():
            logger.info(f"  {year}: {count} articles")

        # Compute sentiment for EACH article
        logger.info("Computing sentiment for each article...")
        news_df["sentiment"] = (
            news_df["title"].fillna("") + " " + news_df["summary"].fillna("")
        )
        news_df["sentiment"] = news_df["sentiment"].apply(compute_sentiment)

        # CRITICAL: Group by date - THIS INCLUDES ALL ARTICLES
        # 'count' = number of articles that day
        # 'mean' = average sentiment of ALL articles that day
        daily_news = (
            news_df.groupby("date").agg({"sentiment": ["mean", "count"]}).reset_index()
        )
        daily_news.columns = ["date", "sentiment_mean", "news_count"]

        logger.info(f"Aggregated to {len(daily_news)} days with news")
        logger.info(
            f"Daily news date range: {daily_news['date'].min().date()} to {daily_news['date'].max().date()}"
        )

        # Show sample of daily aggregation
        logger.info("Sample of daily news (first 5 days):")
        for _, row in daily_news.head().iterrows():
            logger.info(
                f"  {row['date'].date()}: {row['news_count']} articles, avg sentiment={row['sentiment_mean']:.3f}"
            )

        # Ensure dates are same type for merge
        gold_df["date"] = pd.to_datetime(gold_df["date"])
        daily_news["date"] = pd.to_datetime(daily_news["date"])

        # Merge with gold prices
        training_df = pd.merge(gold_df, daily_news, on="date", how="left")
        logger.info(f"Merged dataframe: {len(training_df)} rows")

        # Check merge success
        merged_with_news = training_df["news_count"].notna().sum()
        logger.info(f"Rows with news after merge: {merged_with_news}")

        if merged_with_news == 0:
            logger.error("❌ NO DATES MATCHED BETWEEN GOLD AND NEWS!")
            logger.info(f"Gold dates sample: {gold_df['date'].head(3).tolist()}")
            logger.info(f"News dates sample: {daily_news['date'].head(3).tolist()}")

        # Fill NaN for days with no news
        training_df["sentiment_mean"] = training_df["sentiment_mean"].fillna(0.0)
        training_df["news_count"] = training_df["news_count"].fillna(0)

        # Sort by date
        training_df = training_df.sort_values("date")

        # Create target
        training_df["target"] = (
            training_df["close"].shift(-1) > training_df["close"]
        ).astype(int)
        training_df = training_df.dropna()

        # Keep required columns
        training_df = training_df[
            ["date", "close", "sentiment_mean", "news_count", "target"]
        ]

    # Save training data
    training_df.to_csv(TRAINING_DATA_FILE, index=False)
    logger.info(f"Saved {len(training_df)} training records to {TRAINING_DATA_FILE}")
    logger.info(
        f"Training data date range: {training_df['date'].min().date()} to {training_df['date'].max().date()}"
    )

    # Final statistics
    days_with_news = (training_df["news_count"] > 0).sum()
    logger.info(
        f"Days with news coverage: {days_with_news} out of {len(training_df)} ({days_with_news/len(training_df)*100:.1f}%)"
    )

    if days_with_news > 0:
        news_start = training_df[training_df["news_count"] > 0]["date"].min().date()
        news_end = training_df[training_df["news_count"] > 0]["date"].max().date()
        logger.info(f"News coverage period: {news_start} to {news_end}")
        logger.info(
            f"Average sentiment on news days: {training_df[training_df['news_count'] > 0]['sentiment_mean'].mean():.4f}"
        )

        # Show first few days with news
        logger.info("First 5 days with news in training data:")
        news_days = training_df[training_df["news_count"] > 0].head()
        for _, row in news_days.iterrows():
            logger.info(
                f"  {row['date'].date()}: count={int(row['news_count'])}, sentiment={row['sentiment_mean']:.3f}, target={int(row['target'])}"
            )

    class_dist = training_df["target"].value_counts().to_dict()
    logger.info(f"Target class distribution: {class_dist}")

    ti.xcom_push(key="training_count", value=len(training_df))
    return len(training_df)


def train_model(**context):
    """
    Train ML model ONLY on dates that actually have news
    """
    logger.info("Training ML model...")
    ti = context["ti"]

    if not os.path.exists(TRAINING_DATA_FILE):
        raise FileNotFoundError(f"Training data file not found: {TRAINING_DATA_FILE}")

    df = pd.read_csv(TRAINING_DATA_FILE)

    # ONLY use rows with actual news
    df_with_news = df[df["news_count"] > 0].copy()

    logger.info("=" * 60)
    logger.info("TRAINING DATA ANALYSIS:")
    logger.info(f"Total records available: {len(df)}")
    logger.info(f"Records WITH actual news: {len(df_with_news)}")

    if len(df_with_news) > 0:
        logger.info(
            f"News data date range: {df_with_news['date'].min()} to {df_with_news['date'].max()}"
        )
        logger.info(
            f"Average sentiment on news days: {df_with_news['sentiment_mean'].mean():.4f}"
        )
        logger.info(
            f"Average news count per day: {df_with_news['news_count'].mean():.1f}"
        )

        # Show sample
        logger.info("Sample of training data (first 5 news days):")
        for _, row in df_with_news.head().iterrows():
            logger.info(
                f"  {row['date']}: count={int(row['news_count'])}, sentiment={row['sentiment_mean']:.3f}, target={int(row['target'])}"
            )

    if len(df_with_news) < 5:
        logger.warning(f"⚠️ ONLY {len(df_with_news)} DAYS WITH NEWS!")
        logger.warning("Model will be weak but demonstrates pipeline functionality.")

    if len(df_with_news) == 0:
        raise ValueError("No training data with news features available!")

    # Prepare features and target
    feature_cols = ["sentiment_mean", "news_count"]
    X = df_with_news[feature_cols]
    y = df_with_news["target"]

    class_dist = y.value_counts().to_dict()
    logger.info(f"Target distribution (up=1, down=0): {class_dist}")

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    logger.info(f"Training on {len(X_train)} samples with actual news")
    logger.info(f"Testing on {len(X_test)} samples with actual news")

    # Train model
    model = RandomForestClassifier(
        n_estimators=100, max_depth=5, random_state=42, class_weight="balanced"
    )
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    logger.info(f"Model accuracy (on news-period data): {accuracy:.4f}")

    # Feature importance
    feature_importance = dict(zip(feature_cols, model.feature_importances_))
    logger.info(f"Feature importance: {feature_importance}")

    # Save model
    model_info = {
        "model": model,
        "accuracy": accuracy,
        "feature_importance": feature_importance,
        "training_date": datetime.now().isoformat(),
        "training_samples": len(X_train),
        "test_samples": len(X_test),
        "total_news_days": len(df_with_news),
        "news_date_range": f"{df_with_news['date'].min()} to {df_with_news['date'].max()}",
        "class_distribution": class_dist,
        "note": "Trained ONLY on dates with actual news.",
    }

    joblib.dump(model_info, MODEL_FILE)
    logger.info(f"Model saved to {MODEL_FILE}")
    logger.info("=" * 60)

    ti.xcom_push(key="model_accuracy", value=accuracy)
    ti.xcom_push(key="model_path", value=MODEL_FILE)
    ti.xcom_push(key="news_days", value=len(df_with_news))

    return accuracy


# Define the DAG
dag = DAG(
    "gold_war_ml_pipeline",
    default_args=default_args,
    description="ETL + ML pipeline for gold price prediction using war news sentiment",
    schedule_interval="@weekly",
    catchup=False,
    tags=["gold", "war", "ml", "sentiment"],
)

# Define tasks
t1 = PythonOperator(
    task_id="fetch_gold_prices",
    python_callable=fetch_gold_prices,
    dag=dag,
)

t2 = PythonOperator(
    task_id="fetch_war_news",
    python_callable=fetch_war_news,
    dag=dag,
)

t3 = PythonOperator(
    task_id="compute_sentiment_and_merge",
    python_callable=compute_sentiment_and_merge,
    dag=dag,
)

t4 = PythonOperator(
    task_id="train_model",
    python_callable=train_model,
    dag=dag,
)

# Create data directory check task
t_check_dir = BashOperator(
    task_id="check_data_directory",
    bash_command=f"ls -la {DATA_DIR}",
    dag=dag,
)

# Set dependencies
[t1, t2] >> t3 >> t4 >> t_check_dir
