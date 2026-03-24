from pathlib import Path
import pandas as pd
import feedparser


RSS_FEEDS = {
    "world": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "politics": "https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml",
    "homepage": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
}

WAR_KEYWORDS = [
    "war", "conflict", "invasion", "missile", "strike", "troops", "army",
    "military", "ceasefire", "bombing", "attack", "ukraine", "russia",
    "gaza", "israel", "iran", "syria", "hamas"
]


def is_war_related(text: str) -> bool:
    text = (text or "").lower()
    return any(keyword in text for keyword in WAR_KEYWORDS)


def fetch_nyt_news():
    project_root = Path(__file__).resolve().parent.parent
    raw_data_dir = project_root / "data" / "raw"
    raw_data_dir.mkdir(parents=True, exist_ok=True)

    output_file = raw_data_dir / "nyt_news.csv"
    all_rows = []

    for source_feed, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)

        for entry in feed.entries:
            title = entry.get("title", "")
            summary = entry.get("summary", "")
            link = entry.get("link", "")
            published = entry.get("published", "")

            text_for_filter = f"{title} {summary}"

            if is_war_related(text_for_filter):
                all_rows.append({
                    "source_feed": source_feed,
                    "published": published,
                    "title": title,
                    "summary": summary,
                    "link": link,
                    "text_for_sentiment": text_for_filter
                })

    df = pd.DataFrame(all_rows)

    if df.empty:
        print("No war-related NYT RSS articles found.")
        df.to_csv(output_file, index=False)
        return

    # convert published date to pandas datetime
    df["published"] = pd.to_datetime(df["published"], errors="coerce", utc=True)
    df["date"] = df["published"].dt.date

    # remove duplicates by link
    df = df.drop_duplicates(subset=["link"]).reset_index(drop=True)

    df.to_csv(output_file, index=False)

    print(f"NYT news saved to: {output_file}")
    print(df[["date", "source_feed", "title"]].head())
    print(f"Total war-related articles: {len(df)}")


if __name__ == "__main__":
    fetch_nyt_news()