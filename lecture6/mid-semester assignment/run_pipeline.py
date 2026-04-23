from src.data_ingestion import fetch_gold_prices, fetch_war_news
from src.feature_engineering import create_features
from src.model_training import train_models
from src.model_selection import select_best_model

print("Fetching data...")
fetch_gold_prices()
fetch_war_news()

print("Creating features...")
df = create_features()

print("Training models...")
results = train_models(df)

print("Selecting best model...")
select_best_model(results)

print("Pipeline finished.")