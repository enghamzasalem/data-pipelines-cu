import argparse
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import accuracy_score

FEATURES = [
    "price_change",
    "ma7",
    "ma14",
    "high_low_diff",
    "open_close_diff",
    "volume",
    "sentiment_mean",
    "news_count",
]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, help="Path to gold_model.pkl")
    parser.add_argument("--data", required=True, help="Path to directory containing training_data.csv")
    args = parser.parse_args()

    model_path = Path(args.model)
    data_dir = Path(args.data)
    train_file = data_dir / "training_data_sample.csv"

    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")
    if not train_file.exists():
        raise FileNotFoundError(f"training_data.csv not found in: {data_dir}")

    model = joblib.load(model_path)
    df = pd.read_csv(train_file, parse_dates=["date"]).sort_values("date").reset_index(drop=True)

    X = df[FEATURES]
    y = df["target"]

    split_idx = int(len(df) * 0.8)
    X_test = X.iloc[split_idx:]
    y_test = y.iloc[split_idx:]

    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)

    print(f"Test accuracy: {acc:.4f}")

if __name__ == "__main__":
    main()