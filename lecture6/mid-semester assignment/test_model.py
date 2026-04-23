import argparse
import pandas as pd
import joblib
from sklearn.metrics import accuracy_score

parser = argparse.ArgumentParser()

parser.add_argument("--model", required=True)
parser.add_argument("--data", required=True)

args = parser.parse_args()

model = joblib.load(args.model)

df = pd.read_csv(f"{args.data}/training_data.csv")

features = [
    "sentiment_mean",
    "sentiment_std",
    "news_count",
    "price_change",
    "rolling_mean_3",
    "rolling_mean_7",
    "sentiment_lag1",
    "sentiment_lag2"
]

X = df[features]
y = df["target"]

preds = model.predict(X)

acc = accuracy_score(y, preds)

print("Model accuracy:", acc)