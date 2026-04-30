from pathlib import Path
import pandas as pd
import yfinance as yf


def fetch_gold_prices():
    project_root = Path(__file__).resolve().parent.parent
    raw_data_dir = project_root / "data" / "raw"
    raw_data_dir.mkdir(parents=True, exist_ok=True)

    output_file = raw_data_dir / "gold_prices.csv"
    ticker = "GC=F"

    # Download gold futures data
    df = yf.download(ticker, start="2024-01-01", interval="1d", auto_adjust=False)

    if df.empty:
        raise ValueError("No gold price data was downloaded.")

    # If yfinance returns multi-level columns, flatten them
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] for col in df.columns]

    # Reset index so Date becomes a normal column
    df = df.reset_index()

    # Standardize column names
    df.columns = [str(col).strip().lower().replace(" ", "_") for col in df.columns]

    # Print columns so we can see what was downloaded
    print("Downloaded columns:", df.columns.tolist())

    # Rename date column if needed
    if "datetime" in df.columns:
        df = df.rename(columns={"datetime": "date"})
    elif "date" not in df.columns and df.columns[0] != "date":
        df = df.rename(columns={df.columns[0]: "date"})

    # Make sure required columns exist
    required_cols = ["date", "open", "high", "low", "close", "volume"]
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        raise ValueError(f"Missing expected columns: {missing_cols}. Found columns: {df.columns.tolist()}")

    # Keep only required columns
    df = df[required_cols].copy()

    # Create features
    df["return_1d"] = df["close"].pct_change()
    df["next_close"] = df["close"].shift(-1)
    df["target"] = (df["next_close"] > df["close"]).astype(int)

    # Drop last row because next_close is NaN
    df = df.dropna(subset=["next_close"])

    # Save to CSV
    df.to_csv(output_file, index=False)

    print(f"Gold prices saved to: {output_file}")
    print(df.head())
    print(f"Total rows: {len(df)}")


if __name__ == "__main__":
    fetch_gold_prices()