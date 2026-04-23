from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

def train_models(df):

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

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    models = {
        "logistic": LogisticRegression(),
        "random_forest": RandomForestClassifier(),
        "gradient_boost": GradientBoostingClassifier()
    }

    results = {}

    for name, model in models.items():

        model.fit(X_train, y_train)

        preds = model.predict(X_test)

        acc = accuracy_score(y_test, preds)

        results[name] = (model, acc)

    return results