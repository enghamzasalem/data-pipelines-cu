import argparse
import pickle
from pathlib import Path
import pandas as pd


def load_model(model_path: Path):
    with open(model_path, "rb") as f:
        data = pickle.load(f)
    return data["model"], data["features"]


def test_model(model_path: Path, data_dir: Path):
    model, features = load_model(model_path)

    training_csv = data_dir / "training_data.csv"
    if not training_csv.exists():
        raise FileNotFoundError(f"Training data not found: {training_csv}")

    df = pd.read_csv(training_csv)
    X = df[features].fillna(0)
    y = df["target"]

    accuracy = model.score(X, y)
    preds = model.predict(X)

    sample = df[["date", "close", "target"]].head(10).copy()
    sample["predicted"] = preds[:10]

    return accuracy, len(df), sample


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--data", type=Path, required=True)
    args = parser.parse_args()

    acc, n, sample = test_model(args.model, args.data)

    print("\n=== Model Test Results ===")
    print(f"Accuracy: {acc:.3f}")
    print(f"Samples: {n}")
    print("\nSample predictions:")
    print(sample.to_string(index=False))


if __name__ == "__main__":
    main()