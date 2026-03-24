from pathlib import Path
import pandas as pd
import joblib


def test_model():
    project_root = Path(__file__).resolve().parent

    model_file = project_root / "gold_model.pkl"
    data_file = project_root / "training_data_sample.csv"

    model = joblib.load(model_file)
    df = pd.read_csv(data_file)

    feature_cols = [
        "return_1d",
        "news_count",
        "avg_sentiment",
        "max_sentiment",
        "min_sentiment",
        "positive_count",
        "negative_count",
        "neutral_count",
    ]

    test_df = df[feature_cols].dropna().head(5).copy()
    predictions = model.predict(test_df)

    result_df = test_df.copy()
    result_df["prediction"] = predictions

    print("Model test predictions:")
    print(result_df)


if __name__ == "__main__":
    test_model()