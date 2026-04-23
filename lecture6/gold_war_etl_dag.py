#!/usr/bin/env python3
"""
Lecture 6: Gold price and war news ETL + ML pipeline.

This module can be:
- imported by Airflow as a DAG definition
- executed directly with Python to generate the submission artifacts
"""

from __future__ import annotations

import argparse
import os
import pickle
from datetime import datetime
from pathlib import Path
from typing import Iterable

import pandas as pd
from sklearn.ensemble import RandomForestClassifier

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_DIR = BASE_DIR / "data" / "gold_war_pipeline"
DEFAULT_MODEL_DIR = BASE_DIR / "models"
ROOT_MODEL_PATH = BASE_DIR / "gold_model.pkl"
GOLD_CSV = "gold_prices.csv"
NEWS_CSV = "war_news.csv"
TRAINING_CSV = "training_data.csv"
MODEL_FILENAME = "gold_model.pkl"
FEATURE_COLUMNS = [
    "close",
    "sentiment_mean",
    "news_count",
    "daily_return",
    "intraday_range",
]
RSS_FEEDS = [
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
]
WAR_KEYWORDS = {
    "war",
    "conflict",
    "attack",
    "military",
    "invasion",
    "missile",
    "troops",
    "battle",
    "ceasefire",
    "airstrike",
}


def resolve_data_dir(data_dir: str | os.PathLike | None = None) -> Path:
    configured = data_dir or os.getenv("DATA_DIR")
    return Path(configured) if configured else DEFAULT_DATA_DIR


def ensure_directories(data_dir: Path, model_dir: Path) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    model_dir.mkdir(parents=True, exist_ok=True)


def _load_yfinance():
    try:
        import yfinance as yf
    except ImportError as exc:
        raise RuntimeError(
            "yfinance is required. Install dependencies with `pip install -r requirements.txt`."
        ) from exc
    return yf


def _load_feedparser():
    try:
        import feedparser
    except ImportError as exc:
        raise RuntimeError(
            "feedparser is required. Install dependencies with `pip install -r requirements.txt`."
        ) from exc
    return feedparser


def _load_textblob():
    try:
        from textblob import TextBlob
    except ImportError as exc:
        raise RuntimeError(
            "textblob is required. Install dependencies with `pip install -r requirements.txt`."
        ) from exc
    return TextBlob


def _normalize_gold_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    if isinstance(df.columns, pd.MultiIndex):
        flattened = []
        for col in df.columns:
            if isinstance(col, tuple):
                flattened.append(col[0] if col[0] != "Date" else "Date")
            else:
                flattened.append(col)
        df.columns = flattened

    df = df.reset_index()
    df.columns = [str(col).lower() for col in df.columns]

    rename_map = {
        "date": "date",
        "open": "open",
        "high": "high",
        "low": "low",
        "close": "close",
    }
    available = [col for col in rename_map if col in df.columns]
    normalized = df[available].rename(columns=rename_map)
    normalized["date"] = pd.to_datetime(normalized["date"]).dt.strftime("%Y-%m-%d")
    return normalized


def fetch_gold_prices(data_dir: str | os.PathLike | None = None) -> str:
    data_path = resolve_data_dir(data_dir)
    ensure_directories(data_path, DEFAULT_MODEL_DIR)
    yf = _load_yfinance()

    df = yf.download("GC=F", start="2024-01-01", progress=False, auto_adjust=False)
    if df.empty:
        raise ValueError("No gold price data returned for GC=F.")

    gold_df = _normalize_gold_dataframe(df)
    output_path = data_path / GOLD_CSV
    gold_df.to_csv(output_path, index=False)
    return str(output_path)


def _entry_date(entry) -> str | None:
    for field in ("published_parsed", "updated_parsed"):
        value = getattr(entry, field, None)
        if value:
            return datetime(*value[:6]).strftime("%Y-%m-%d")
    for field in ("published", "updated"):
        value = getattr(entry, field, None)
        if value:
            parsed = pd.to_datetime(value, utc=True, errors="coerce")
            if pd.notna(parsed):
                return parsed.strftime("%Y-%m-%d")
    return None


def _is_war_related(text: str) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in WAR_KEYWORDS)


def fetch_war_news(data_dir: str | os.PathLike | None = None) -> str:
    data_path = resolve_data_dir(data_dir)
    ensure_directories(data_path, DEFAULT_MODEL_DIR)
    feedparser = _load_feedparser()

    records: list[dict[str, str]] = []
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in getattr(feed, "entries", []):
            title = getattr(entry, "title", "").strip()
            summary = getattr(entry, "summary", "").strip()
            combined = f"{title} {summary}".strip()
            if not combined or not _is_war_related(combined):
                continue

            published_date = _entry_date(entry)
            if not published_date:
                continue

            records.append(
                {
                    "date": published_date,
                    "title": title,
                    "summary": summary,
                }
            )

    news_df = pd.DataFrame(records, columns=["date", "title", "summary"])
    if news_df.empty:
        news_df = pd.DataFrame(columns=["date", "title", "summary"])
    else:
        news_df = news_df.drop_duplicates(subset=["date", "title"]).sort_values(
            ["date", "title"]
        )

    output_path = data_path / NEWS_CSV
    news_df.to_csv(output_path, index=False)
    return str(output_path)


def compute_sentiment_and_merge(data_dir: str | os.PathLike | None = None) -> str:
    data_path = resolve_data_dir(data_dir)
    TextBlob = _load_textblob()

    gold_df = pd.read_csv(data_path / GOLD_CSV)
    news_df = pd.read_csv(data_path / NEWS_CSV)

    gold_df["date"] = pd.to_datetime(gold_df["date"]).dt.strftime("%Y-%m-%d")
    if news_df.empty:
        aggregated = pd.DataFrame(
            columns=["date", "sentiment_mean", "news_count"]
        )
    else:
        news_df["date"] = pd.to_datetime(news_df["date"]).dt.strftime("%Y-%m-%d")
        news_df["text"] = (
            news_df["title"].fillna("") + " " + news_df["summary"].fillna("")
        ).str.strip()
        news_df["sentiment"] = news_df["text"].apply(
            lambda text: TextBlob(text).sentiment.polarity if text else 0.0
        )
        aggregated = (
            news_df.groupby("date", as_index=False)
            .agg(sentiment_mean=("sentiment", "mean"), news_count=("title", "count"))
            .sort_values("date")
        )

    merged = gold_df.merge(aggregated, on="date", how="left")
    merged["sentiment_mean"] = merged["sentiment_mean"].fillna(0.0)
    merged["news_count"] = merged["news_count"].fillna(0).astype(int)
    merged["daily_return"] = merged["close"].pct_change().replace([pd.NA], 0).fillna(0)
    merged["intraday_range"] = (
        (merged["high"] - merged["low"]) / merged["close"].replace(0, pd.NA)
    ).fillna(0)

    next_close = merged["close"].shift(-1)
    merged["target"] = (next_close > merged["close"]).astype("Int64")
    training_df = merged.iloc[:-1].copy()
    training_df["target"] = training_df["target"].astype(int)

    output_path = data_path / TRAINING_CSV
    training_df[
        [
            "date",
            "close",
            "sentiment_mean",
            "news_count",
            "daily_return",
            "intraday_range",
            "target",
        ]
    ].to_csv(output_path, index=False)
    return str(output_path)


def _write_submission_samples(data_dir: Path) -> None:
    latest_gold_date = pd.to_datetime(pd.read_csv(data_dir / GOLD_CSV)["date"]).max()
    window_start = (latest_gold_date - pd.DateOffset(months=4)).normalize()

    gold_sample = pd.read_csv(data_dir / GOLD_CSV)
    gold_sample["date"] = pd.to_datetime(gold_sample["date"])
    gold_sample = gold_sample[gold_sample["date"] >= window_start].copy()
    gold_sample["date"] = gold_sample["date"].dt.strftime("%Y-%m-%d")
    gold_sample.to_csv(BASE_DIR / "gold_prices_sample.csv", index=False)

    news_sample = pd.read_csv(data_dir / NEWS_CSV)
    if not news_sample.empty:
        news_sample["date"] = pd.to_datetime(news_sample["date"])
        news_sample = news_sample[news_sample["date"] >= window_start].copy()
        news_sample["date"] = news_sample["date"].dt.strftime("%Y-%m-%d")
    news_sample.to_csv(BASE_DIR / "war_news_sample.csv", index=False)

    training_sample = pd.read_csv(data_dir / TRAINING_CSV)
    training_sample["date"] = pd.to_datetime(training_sample["date"])
    training_sample = training_sample[training_sample["date"] >= window_start].copy()
    training_sample["date"] = training_sample["date"].dt.strftime("%Y-%m-%d")
    training_sample.to_csv(BASE_DIR / "training_data_sample.csv", index=False)


def _copy_model_to_submission_root(model_path: Path) -> None:
    with model_path.open("rb") as src, ROOT_MODEL_PATH.open("wb") as dst:
        dst.write(src.read())


def train_model(
    data_dir: str | os.PathLike | None = None,
    model_dir: str | os.PathLike | None = None,
) -> str:
    data_path = resolve_data_dir(data_dir)
    model_path = Path(model_dir) if model_dir else DEFAULT_MODEL_DIR
    ensure_directories(data_path, model_path)

    training_df = pd.read_csv(data_path / TRAINING_CSV)
    if training_df.empty:
        raise ValueError("Training data is empty. Cannot train a model.")

    X = training_df[FEATURE_COLUMNS].fillna(0)
    y = training_df["target"]

    model = RandomForestClassifier(
        n_estimators=200,
        min_samples_leaf=2,
        random_state=42,
    )
    model.fit(X, y)

    output_path = model_path / MODEL_FILENAME
    with output_path.open("wb") as model_file:
        pickle.dump({"model": model, "features": FEATURE_COLUMNS}, model_file)

    _copy_model_to_submission_root(output_path)
    _write_submission_samples(data_path)
    return str(output_path)


def run_pipeline(
    data_dir: str | os.PathLike | None = None,
    model_dir: str | os.PathLike | None = None,
) -> str:
    data_path = resolve_data_dir(data_dir)
    model_path = Path(model_dir) if model_dir else DEFAULT_MODEL_DIR
    fetch_gold_prices(data_path)
    fetch_war_news(data_path)
    compute_sentiment_and_merge(data_path)
    return train_model(data_path, model_path)


if __name__ != "__main__":
    try:
        from airflow import DAG
        from airflow.operators.python import PythonOperator
    except ImportError:  # pragma: no cover - Airflow is optional outside the scheduler
        DAG = None
        PythonOperator = None
else:
    DAG = None
    PythonOperator = None


if DAG is not None and PythonOperator is not None:
    with DAG(
        dag_id="lecture6_gold_war_pipeline",
        start_date=datetime(2024, 1, 1),
        schedule="@weekly",
        catchup=False,
        tags=["lecture6", "etl", "ml"],
    ) as dag:
        fetch_gold_prices_task = PythonOperator(
            task_id="fetch_gold_prices",
            python_callable=fetch_gold_prices,
        )
        fetch_war_news_task = PythonOperator(
            task_id="fetch_war_news",
            python_callable=fetch_war_news,
        )
        compute_sentiment_and_merge_task = PythonOperator(
            task_id="compute_sentiment_and_merge",
            python_callable=compute_sentiment_and_merge,
        )
        train_model_task = PythonOperator(
            task_id="train_model",
            python_callable=train_model,
        )

        [fetch_gold_prices_task, fetch_war_news_task] >> compute_sentiment_and_merge_task
        compute_sentiment_and_merge_task >> train_model_task
else:
    dag = None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Lecture 6 ETL + ML pipeline")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DEFAULT_DATA_DIR,
        help="Directory where CSV outputs should be written",
    )
    parser.add_argument(
        "--model-dir",
        type=Path,
        default=DEFAULT_MODEL_DIR,
        help="Directory where the trained model should be written",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    model_path = run_pipeline(args.data_dir, args.model_dir)
    print(f"Pipeline completed successfully. Model saved to {model_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
