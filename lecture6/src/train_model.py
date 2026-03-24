from pathlib import Path
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report


def train_model():
    project_root = Path(__file__).resolve().parent.parent

    input_file = project_root / "data" / "processed" / "training_data.csv"
    models_dir = project_root / "models"
    models_dir.mkdir(parents=True, exist_ok=True)

    output_model = models_dir / "gold_price_model.pkl"

    df = pd.read_csv(input_file)

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

    target_col = "target"

    # Keep only needed columns
    model_df = df[feature_cols + [target_col]].copy()

    # Drop missing values
    model_df = model_df.dropna()

    X = model_df[feature_cols]
    y = model_df[target_col]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, zero_division=0))

    joblib.dump(model, output_model)
    print(f"Model saved to: {output_model}")


if __name__ == "__main__":
    train_model()