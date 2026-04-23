import os
import yfinance as yf
import feedparser
import pandas as pd
import logging

logger = logging.getLogger(__name__)

BASE_DIR = "/Users/subhankarbiswas/data-pipelines-cu/lecture6/gold_war_pipeline"
DATA_DIR = os.path.join(BASE_DIR, "data")

os.makedirs(DATA_DIR, exist_ok=True)

def fetch_gold_prices():

    logger.info("Downloading gold price data")

    gold = yf.download("GC=F", start="2024-01-01")

    gold.reset_index(inplace=True)

    gold = gold[['Date','Open','High','Low','Close']]

    gold.columns = ['date','open','high','low','close']

    gold.to_csv(f"{DATA_DIR}/gold_prices.csv", index=False)

    logger.info("Gold prices saved")


def fetch_war_news():

    logger.info("Fetching NYT RSS feeds")

    rss_urls = [
        "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"
    ]

    keywords = [
        "war","conflict","attack","military","invasion","missile"
    ]

    articles = []

    for url in rss_urls:

        feed = feedparser.parse(url)

        for entry in feed.entries:

            text = entry.title + " " + entry.summary

            if any(k in text.lower() for k in keywords):

                date = entry.published[:10]

                articles.append({
                    "date": date,
                    "title": entry.title,
                    "summary": entry.summary
                })

    df = pd.DataFrame(articles)

    df.to_csv(f"{DATA_DIR}/war_news.csv", index=False)

    logger.info("War news saved")