from pathlib import Path
from datetime import datetime
import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv

WAR_KEYWORDS = [
    "war", "conflict", "invasion", "missile", "strike", "troops", "army",
    "military", "ceasefire", "bombing", "attack", "ukraine", "russia",
    "gaza", "israel", "iran", "syria", "hamas", "sudan", "lebanon"
]


def is_war_related(text: str) -> bool:
    text = (text or "").lower()
    return any(keyword in text for keyword in WAR_KEYWORDS)


def month_range(start_year=2024, start_month=1):
    today = datetime.today()
    year, month = start_year, start_month
    while (year < today.year) or (year == today.year and month <= today.month):
        yield year, month
        month += 1
        if month > 12:
            month = 1
            year += 1


def fetch_month(year: int, month: int, api_key: str, max_retries: int = 4):
    url = f"https://api.nytimes.com/svc/archive/v1/{year}/{month}.json"
    params = {"api-key": api_key}

    for attempt in range(max_retries):
        response = requests.get(url, params=params, timeout=60)

        if response.status_code == 429:
            wait_seconds = 60 * (attempt + 1)
            print(f"429 rate limited for {year}-{month:02d}. Waiting {wait_seconds}s...")
            time.sleep(wait_seconds)
            continue

        response.raise_for_status()
        return response.json()

    raise RuntimeError(f"Failed after retries for {year}-{month:02d}")


def fetch_nyt_backfill():
    project_root = Path(__file__).resolve().parent.parent
    raw_data_dir = project_root / "data" / "raw"
    raw_data_dir.mkdir(parents=True, exist_ok=True)

    output_file = raw_data_dir / "nyt_news_backfill.csv"

    load_dotenv(project_root / ".env")
    api_key = os.getenv("NYT_API_KEY")

    if not api_key:
        raise ValueError("NYT_API_KEY not found in .env")

    # Resume support: load existing file if present
    if output_file.exists():
        existing_df = pd.read_csv(output_file)
        rows = existing_df.to_dict("records")
        completed_months = set(existing_df.get("year_month", pd.Series(dtype=str)).dropna().tolist())
        print(f"Resuming from existing file. Existing rows: {len(existing_df)}")
    else:
        rows = []
        completed_months = set()

    for year, month in month_range(2024, 1):
        ym = f"{year}-{month:02d}"

        if ym in completed_months:
            print(f"Skipping {ym} (already saved)")
            continue

        print(f"Fetching {ym}...")
        data = fetch_month(year, month, api_key)
        docs = data.get("response", {}).get("docs", [])

        month_rows = []

        for doc in docs:
            headline = ""
            if isinstance(doc.get("headline"), dict):
                headline = doc.get("headline", {}).get("main", "") or ""
            else:
                headline = str(doc.get("headline", "") or "")

            abstract = doc.get("abstract", "") or ""
            snippet = doc.get("snippet", "") or ""
            lead_paragraph = doc.get("lead_paragraph", "") or ""
            web_url = doc.get("web_url", "") or ""
            pub_date = doc.get("pub_date", "") or ""
            news_desk = doc.get("news_desk", "") or ""
            section_name = doc.get("section_name", "") or ""

            text_for_filter = " ".join([headline, abstract, snippet, lead_paragraph]).strip()

            if is_war_related(text_for_filter):
                month_rows.append({
                    "source_feed": "nyt_archive_api",
                    "published": pub_date,
                    "title": headline,
                    "summary": abstract if abstract else snippet,
                    "link": web_url,
                    "text_for_sentiment": text_for_filter,
                    "news_desk": news_desk,
                    "section_name": section_name,
                    "year_month": ym,
                })

        rows.extend(month_rows)

        # Save progress after every month
        df = pd.DataFrame(rows)
        if not df.empty:
            df["published"] = pd.to_datetime(df["published"], errors="coerce", utc=True)
            df["date"] = df["published"].dt.date
            df = df.drop_duplicates(subset=["link"]).reset_index(drop=True)
        df.to_csv(output_file, index=False)

        print(f"Saved progress for {ym}. Total rows so far: {len(df)}")

        # Be polite to the API
        time.sleep(8)

    final_df = pd.read_csv(output_file)
    print(f"Historical NYT backfill saved to: {output_file}")
    print(final_df[["date", "title"]].head())
    print(f"Total rows: {len(final_df)}")


if __name__ == "__main__":
    fetch_nyt_backfill()